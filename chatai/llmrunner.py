import gc
import os
import numpy as np
import random
import spacy
import torch
from aiengine.base_runner import BaseRunner
from aiengine.settings import TEXT_MODELS as MODELS
from aiengine.logger import logger

os.environ["DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TRANSFORMERS_OFFLINE"] = "0"
os.environ["BITSANDBYTES_NOWELCOME"] = "1"
import settings
logger.set_level(settings.LOG_LEVEL)


class LLMRunner(BaseRunner):
    _load_in_8bit = True
    summarizer = None
    model = None
    tokenizer = None
    model_name = None

    def move_to_cpu(self):
        do_gc = False
        if self.model is not None:
            del self.model
            do_gc = True
        if self.tokenizer is not None:
            del self.tokenizer
            do_gc = True
        if do_gc:
            torch.cuda.empty_cache()
            gc.collect()

    def generate_response(self, user_query, user_id):
        if self.model is None or self.tokenizer is None:
            self.load_model(self.model_name)

        conversation_text = ""

        # Encode the conversation history for the user
        if user_id in self.conversation_history:
            conversation_text = self.conversation_history[user_id]['text']
            conversation_vector = np.mean(self.model(self.tokenizer(conversation_text, return_tensors='pt'))[0].detach().numpy(),
                                          axis=1)
        else:
            conversation_vector = np.zeros(self.model.config.n_embd)

        # Encode the user's query
        # query_vector = np.mean(self.model(self.tokenizer(user_query, return_tensors='pt'))[0].detach().numpy(), axis=1)
        # same thing but use torch
        query_vector = self.tokenizer.encode(user_query, return_tensors='pt')

        # Concatenate the vectors
        # combined_vector = np.concatenate([conversation_vector, query_vector])
        combined_vector = torch.cat([conversation_vector, query_vector], dim=-1)

        # Generate a response from the LLM model
        input_ids = self.tokenizer.encode(user_query, return_tensors='pt')
        output = self.model.generate(input_ids=input_ids, max_length=50, pad_token_id=self.tokenizer.eos_token_id,
                                context=combined_vector)
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)


        # Store the response and update the conversation history
        self.conversation_history[user_id] = {'text': conversation_text + user_query + response, 'vector': combined_vector}
        return response

    def extract_named_entities(self, text):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        return entities

    @property
    def load_in_8bit(self):
        return self._load_in_8bit

    @load_in_8bit.setter
    def load_in_8bit(self, value):
        self._load_in_8bit = value

    models = MODELS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = kwargs.get("app")
        self.seed = random.randint(0, 100000)
        self.device_map = kwargs.get("device_map", "auto")
        self.load_in_8bit = kwargs.get("load_in_8bit", self._load_in_8bit)
        self.current_model = kwargs.get("model", "flan-t5-xl")
        self.model_name = MODELS[self.current_model]["path"]
        self.model_class = MODELS[self.current_model]["class"]
        self.tokenizer_class = MODELS[self.current_model]["tokenizer"]
        # self.app.message_signal.emit("initialized")

    def set_seed(self, seed=None):
        from transformers import set_seed
        seed = self.seed if seed is None else seed
        self.seed = seed
        set_seed(self.seed)
        # set model and token seed
        torch.manual_seed(self.seed)
        torch.cuda.manual_seed(self.seed)
        torch.cuda.manual_seed_all(self.seed)
        random.seed(self.seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        self.tokenizer.seed = self.seed
        self.model.seed = self.seed

    def clear_gpu_cache(self):
        torch.cuda.empty_cache()
        gc.collect()

    def load_model(self, model_name, pipeline_type=None, offline=True):
        if self.model_name == model_name and self.model and self.tokenizer:
            return
        local_files_only = offline
        from transformers import GPTNeoXForCausalLM, GPTNeoXTokenizerFast, GPTNeoForCausalLM, GPT2Tokenizer, \
            AutoModelForSeq2SeqLM, AutoTokenizer, T5ForConditionalGeneration, AutoModelForCausalLM
        class_names = {
            "GPTNeoXForCausalLM": GPTNeoXForCausalLM,
            "GPTNeoXTokenizerFast": GPTNeoXTokenizerFast,
            "GPTNeoForCausalLM": GPTNeoForCausalLM,
            "GPT2Tokenizer": GPT2Tokenizer,
            "AutoModelForSeq2SeqLM": AutoModelForSeq2SeqLM,
            "AutoModelForCausalLM": AutoModelForCausalLM,
            "AutoTokenizer": AutoTokenizer,
            "T5ForConditionalGeneration": T5ForConditionalGeneration,
        }
        from transformers import pipeline
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        self.clear_gpu_cache()
        try:
            tokenizer_class = class_names[self.tokenizer_class]
            if pipeline_type == "summarize":
                self.model = pipeline(
                    "summarization",
                    model=model_name,
                    device=0
                )
            else:
                # iterate over all models and find path matching model_name then set model_class
                for model in MODELS:
                    if model_name == MODELS[model]["path"]:
                        self.model_class = MODELS[model]["class"]
                model_class = class_names[self.model_class]
                self.model = model_class.from_pretrained(
                    model_name,
                    local_files_only=local_files_only,
                    device_map=self.device_map,
                    torch_dtype=torch.float16,
                    load_in_8bit=self.load_in_8bit,
                )
                self.model.eval()
            self.tokenizer = tokenizer_class.from_pretrained(
                model_name,
                local_files_only=local_files_only,
            )
        except torch.cuda.OutOfMemoryError:
            print("Out of memory")
            self.load_model(model_name)
        except OSError as e:
            print(e)
            if offline:
                return self.load_model(model_name, pipeline_type, offline=False)

    @property
    def device(self):
        return "cuda" if torch.cuda.is_available() else "cpu"

    def load_summarizer(self):
        self.load_model("./local/flan-t5-large-samsum", "summarize")

    def generate_character_prompt(self, **properties):
        choices = ['book', 'movie', 'tv show']
        choices_a = ['dog', 'cat', 'fish', 'bird', 'monster', 'national leader']
        choices_b = [
            'actor', 'actress', 'singer', 'musician',
            'scientist', 'inventor', 'engineer',
            'artist', 'painter', 'sculptor',
            'writer', 'poet', 'novelist',
            'athlete', 'sports player', 'sports team',
            'politician', 'politician', 'politician',
            'historical figure', 'historical figure', 'historical figure',
            'scientist', 'inventor', 'engineer',
        ]
        types_of_gods = ['greek', 'roman', 'pagan', 'egyption', 'norse', 'indian', 'chinese', 'japanese', 'jewish', 'christian', 'islamic']
        prefix = "Generate the name of a "
        prompts = [
            f"famous person from the {random.randint(4, 20)}th century",
            f"{random.choice(types_of_gods)} {random.choice(['god', 'goddess'])}",
            f"character from a {random.choice(choices)}",
            f"{random.choice(choices_a)}",
            f"famous {random.choice(choices_b)}",
        ]
        prompt = prefix + random.choice(prompts) + ": "
        properties["temperature"] = random.random() + 1.0
        properties["top_k"] = 40
        username = self.generate(prompt=prompt, seed=self.seed, **properties, return_result=True, skip_special_tokens = True)
        self.set_seed(random.randint(0, 100000))
        prompt = prefix + random.choice(prompts) + ": "
        botname = self.generate(prompt=prompt, seed=self.seed, **properties, return_result=True, skip_special_tokens = True)
        self.set_message({
            "type": "generate_characters",
            "username": username,
            "botname": botname,
        })


    def generate_chat_prompt(self, user_input, **kwargs):
        botname = kwargs.get("botname")
        username = kwargs.get("username")
        conversation = kwargs.get("conversation")
        properties = kwargs.get("properties", {})

        # summarize the conversation if needed
        if conversation.do_summary:
            results = self.generate(prompt=conversation.summary_prompt(username, botname), seed=self.seed, **properties, return_result=True, skip_special_tokens=True)
            summary = results
            conversation.update_summary(summary)

        # get the bot's mood
        mood_prompt = conversation.get_bot_mood_prompt(botname, username)
        mood_results = self.generate(mood_prompt, seed=self.seed, **properties, return_result=True, skip_special_tokens=True)
        mood = mood_results

        # get the user's sentiment
        sentiment_prompt = conversation.format_user_sentiment_prompt(botname, username)
        sentiment_results = self.generate(sentiment_prompt, seed=self.seed, **properties, return_result=True, skip_special_tokens=True)
        user_sentiment = sentiment_results

        # setup the prompt for the bot response
        prompt = conversation.format_prompt(botname, username, mood, user_sentiment)
        return prompt

    def generate_action_prompt(self, user_input, **kwargs):
        botname = kwargs.get("botname")
        username = kwargs.get("username")
        conversation = kwargs.get("conversation")
        action_prompt = conversation.format_action_prompt(botname, username, user_input)
        action_results = self.generate(action_prompt, seed=self.seed, **kwargs.get("properties", {}), return_result=True, skip_special_tokens=True)

        # format action and reaction
        formatted_action_result = f"{username} {user_input}."
        action_results = action_results.strip()
        # if not action_results.startswith(botname):
        #     formatted_action_result += f" {botname} {action_results}"
        # else:
        formatted_action_result += f" {action_results}"

        conversation.add_action(username, formatted_action_result)
        summary_prompt = conversation.summary_prompt(username, botname)
        properties = kwargs.get("properties", {})
        properties["temperature"] = 1
        properties["top_k"] = 40
        properties["repetition_penalty"] = 10.0
        properties["top_p"] = 0.9
        properties["num_beams"] = 3
        summary_results = self.generate(prompt=summary_prompt, seed=self.seed, **properties, return_result=True, skip_special_tokens=True)
        conversation.update_summary(summary_results)
        # Add summary prompt to conversation
        self.set_message({
            "type": "do_action",
            "botname": botname,
            "response": formatted_action_result
        })

    def generate(
        self,
        prompt=None,
        user_input=None,
        seed = 42,
        max_length = 20,
        min_length = 0,
        do_sample = True,
        early_stopping = True,
        num_beams = 1,
        temperature = 1.0,
        top_k = 1,
        top_p = 0.9,
        repetition_penalty = 50.0,
        bad_words_ids = None,
        bos_token_id = None,
        pad_token_id = None,
        eos_token_id = None,
        length_penalty = 1.0,
        no_repeat_ngram_size = 1,
        num_return_sequences = 1,
        attention_mask = None,
        decoder_start_token_id = None,
        use_cache = None,
        model = "flan-t5-xl",
        type="",
        botname=None,
        username=None,
        conversation=None,
        return_result=False,
        skip_special_tokens=False
    ):
        properties = {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": do_sample,
            "early_stopping": early_stopping,
            "num_beams": num_beams,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "repetition_penalty": repetition_penalty,
            "bad_words_ids": bad_words_ids,
            "bos_token_id": bos_token_id,
            "pad_token_id": pad_token_id,
            "eos_token_id": eos_token_id,
            "length_penalty": length_penalty,
            "no_repeat_ngram_size": no_repeat_ngram_size,
            "num_return_sequences": num_return_sequences,
            "attention_mask": attention_mask,
            "decoder_start_token_id": decoder_start_token_id,
            "use_cache": use_cache,
        }
        model_name = MODELS[model]["path"]
        self.load_model(model_name)
        if not self.tokenizer:
            print("failed to load model")
            return
        self.set_seed(seed)

        if not prompt:
            if type == "chat":
                prompt = self.generate_chat_prompt(user_input, properties=properties, botname=botname,username=username,conversation=conversation)
                top_k = 30
                top_p = 0.9
                num_beams = 6
                repetition_penalty = 20.0
                early_stopping = True
                max_length = 512
                min_length = 30
                temperature = 1.0
                skip_special_tokens = False
            elif type == "do_action":
                self.generate_action_prompt(
                    user_input, properties=properties, botname=botname,
                    username=username, conversation=conversation)
                return
            elif type == "generate_characters":
                self.generate_character_prompt(**properties)
                return
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
        try:
            outputs = self.model.generate(
                input_ids,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample,
                early_stopping=early_stopping,
                num_beams=num_beams,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                bad_words_ids=bad_words_ids,
                bos_token_id=bos_token_id,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                length_penalty=length_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                num_return_sequences=num_return_sequences,
                attention_mask=attention_mask,
                decoder_start_token_id=decoder_start_token_id,
                use_cache=use_cache
            )
            response = self.tokenizer.batch_decode(outputs, skip_special_tokens=skip_special_tokens)

        except Exception as e:
            print(e)
            response = [""]
            if "PYTORCH_CUDA_ALLOC_CONF" in str(e):
                self.error_handler("CUDA out of memory. Try to adjust your settings or using a smaller model.")
                return
            else:
                logger.error(e)
        if not return_result:
            self.set_message({
                "type": type,
                "response": response[0],
                "botname": botname,
            })
        else:
            return response[0]
