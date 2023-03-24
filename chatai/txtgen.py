import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["DISABLE_TELEMETRY"] = "1"
import random
import torch
from torch.cuda import OutOfMemoryError
class Cell:
    def __init__(self, *args, **kwargs):
        pass
from fewshot.fewshot import chat, location_generator_text, locations_text, monsters_text, sd_prompts
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline


class TextGenerator:
    model_path = "google/flan-t5-xl"
    #model_path = "./local/flan-t5-large-samsum"
    load_in_8bit = True

    def __init__(self, **kwargs):
        self.model = kwargs.get("model", self.model_path)  # google/flan-t5-xl
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)

        # use half
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model, device_map="auto", load_in_8bit=self.load_in_8bit)
        self.model.eval()

    # def generate(
    #     self,
    #     input_ids,
    #     max_length = 512,
    #     min_length = 50,
    #     do_sample = True,
    #     early_stopping = False,
    #     num_beams = 1,
    #     temperature = 0.5,
    #     top_k = 10,
    #     top_p = 0.5,
    #     repetition_penalty = 2.0,
    #     bad_words_ids = None,
    #     bos_token_id = None,
    #     pad_token_id = None,
    #     eos_token_id = None,
    #     length_penalty = 2.0,
    #     no_repeat_ngram_size = 1,
    #     num_return_sequences = 1,
    #     attention_mask = None,
    #     decoder_start_token_id = None,
    #     use_cache = None
    # ):
    #     return self.model.generate(
    #         input_ids,
    #         max_length=max_length,
    #         min_length=min_length,
    #         do_sample=do_sample,
    #         early_stopping=early_stopping,
    #         num_beams=num_beams,
    #         temperature=temperature,
    #         top_k=top_k,
    #         top_p=top_p,
    #         repetition_penalty=repetition_penalty,
    #         bad_words_ids=bad_words_ids,
    #         bos_token_id=bos_token_id,
    #         pad_token_id=pad_token_id,
    #         eos_token_id=eos_token_id,
    #         length_penalty=length_penalty,
    #         no_repeat_ngram_size=no_repeat_ngram_size,
    #         num_return_sequences=num_return_sequences,
    #         attention_mask=attention_mask,
    #         decoder_start_token_id=decoder_start_token_id,
    #         use_cache=use_cache
    #     )

    def few_shot_generate(self, prompt, num_return_sequences=1):
        inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
        outputs = self.generate(inputs, num_return_sequences=num_return_sequences)
        return self.tokenizer.batch_decode(outputs, skip_special_tokens=True)

    def generate_profile(self):
        # read input from fewshot/mosters.txt
        with open("fewshot/magic_spells.txt", "r") as f:
            example_profiles = f.read()
        return self.few_shot_generate(example_profiles, num_return_sequences=1)[0]

    def train_model(self, chat_history):
        input_ids = self.tokenizer(chat_history, return_tensors="pt").input_ids.to("cuda")
        outputs = self.model(input_ids, input_ids)
        loss = outputs.loss
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss.item()

    chat_history = []

    cells = []

    def generate_cells(self):
        for y in range(5):
            for x in range(5):
                cell = Cell(
                    x=x,
                    y=y,
                )


    def chat(self):
        inp = "You are standing in a dark room. There is a door to your left and right. Which one do you take?\n"
        chat_history = []
        while True:
            print(inp)
            user_inp = input("> ")
            user_inp = inp + user_inp + "\n"
            inputs = self.tokenizer(user_inp, return_tensors="pt").input_ids.to("cuda")
            outputs = self.generate(inputs)
            ai_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            inp = ai_output + "\n"

    def chat_bots(self, seed=42, save_dir=None, save_every=10):
        self.tokenizer.seed = seed
        self.model.seed = seed
        # get input from characters.txt
        # with open("fewshot/characters.txt", "r") as f:
        #     previous_user_input = f.read()
        #previous_user_input = chat[1]
        previous_user_input = ""
        chat_history = previous_user_input
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-5)
        step = 0
        regenerate = False
        people_typesa = [
            "THE PRESIDENT OF THE USA", "SATAN", "SANTA CLAUS", "FBI AGENT", "A DEMON", "A REINDEER"
        ]
        # seed random
        while True:
            seed+=1
            random.seed(seed)
            person_a = people_typesa[random.randint(0, len(people_typesa) - 1)]
            print("\033[H\033[J")
            do_run = True
            previous_user_input = f"{person_a} says:"
            chat_history = ""
            user_input = "Hello"
            while do_run:
                person_a = people_typesa[random.randint(0, len(people_typesa) - 1)]
                previous_user_input += f"{person_a} says:"
                print(previous_user_input)
                if not regenerate:
                    prompt = f"{previous_user_input}"
                else:
                    user_input = None
                    prompt = previous_user_input
                    regenerate = False
                if user_input == "next":
                    do_run = False
                    break
                inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
                try:
                    outputs = self.generate(inputs)
                    ai_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
                    ai_output = ai_output.replace("\n", " ")
                    previous_user_input = f"{prompt}{ai_output}\n"
                    chat_history += previous_user_input
                    step += 1
                except OutOfMemoryError:
                    self.chat_history.append(previous_user_input)
                    previous_user_input = prompt
                    regenerate = True
                    continue
                print("\033[H\033[J")


    def get_mood(self, prompt, person_type):
        mood_inputs = self.tokenizer(
            prompt,
            return_tensors="pt").input_ids.to("cuda")
        mood_outputs = self.generate(mood_inputs, length_penalty=0.1)
        mood = self.tokenizer.batch_decode(mood_outputs, skip_special_tokens=True)[0]
        mood = f"{person_type} is {mood}"
        return mood

    # wrong, no q. remaining letters are abcdefghijklmnop____uv__yz word is __T.guess a leter
    # t is not avaiable. remaining letters are abcdefghijklmnop____uv__yz word is __T.guess a leter
    # good guess, there is a T. remaining letters are abcdefghijklmnopqrs_uv__yz word is __T.guess a leter
    summarizer = None
    def chat_bot(self, seed=42, save_dir=None, save_every=10):
        self.tokenizer.seed = seed
        self.model.seed = seed
        # get input from characters.txt
        # with open("fewshot/characters.txt", "r") as f:
        #     previous_user_input = f.read()
        #previous_user_input = chat[1]
        previous_user_input = ""
        chat_history = previous_user_input
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-5)
        step = 0
        regenerate = False
        people_types = [
            #"Batman", "Superman", "Jesus", "Satan", "Santa", "FBI Agent", "Demon"
            "Donald Trump"
        ]
        # seed random
        while True:
            person_name = input("What is your name?\n> ")
            seed+=1
            random.seed(seed)
            person_type = people_types[random.randint(0, len(people_types) - 1)]
            print("\033[H\033[J")
            print(f"You have connected with a {person_type}")
            do_run = True
            previous_user_input = ""
            chat_history = ""
            # get a random mood
            # mood = random.choice(["happy", "sad", "angry", "confused", "bored", "excited"])
            # mood = f"{person_type} is {mood}"

            mood = self.get_mood(f"{person_type} sees {person_name} approaching. based on this, {person_type} is in what mood?\n{person_type} is: ", person_type)

            while do_run:
                print(previous_user_input)
                print(mood)
                if not regenerate:
                    user_input = input("> ")
                    prompt = f"{previous_user_input}{person_name}: {user_input}\n{person_type}: "
                else:
                    user_input = None
                    prompt = previous_user_input
                    regenerate = False
                if user_input == "next":
                    do_run = False
                    break

                if chat_history != "":
                    mood = self.get_mood(prompt, person_type)

                inputs = self.tokenizer(f"{mood}\n\n{prompt}", return_tensors="pt").input_ids.to("cuda")
                try:
                    outputs = self.generate(inputs)
                    ai_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
                    ai_output = ai_output.replace("\n", " ")
                    previous_user_input = f"{prompt}{ai_output}\n"
                    chat_history += previous_user_input
                    # if (step + 1) % save_every == 0:
                    #     if save_dir:
                    #         model_path = os.path.join(save_dir, f"model_{step + 1}.pt")
                    #         torch.save(self.model.state_dict(), model_path)
                    #     loss = self.train_model(chat_history)
                    #     print(f"Step {step + 1}: Loss = {loss:.4f}")

                    # get the mood of person_type

                    step += 1
                except OutOfMemoryError:
                    # store chat history in self.chat_history
                    self.chat_history.append(previous_user_input)
                    previous_user_input = f"{person_name}:: {user_input}\nAI: "
                    regenerate = True
                    continue
                print("\033[H\033[J")

    def sentence_complete(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
        outputs = self.generate(inputs)
        return self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]



    def load_model(self, model_path):
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def generate(
        self,
        input_ids,
        max_length = 512,
        min_length = 50,
        do_sample = True,
        early_stopping = False,
        num_beams = 1,
        temperature = 0.85,
        top_k = 90,
        top_p = 0.9,
        repetition_penalty = 2.0,
        bad_words_ids = None,
        bos_token_id = None,
        pad_token_id = None,
        eos_token_id = None,
        length_penalty = 2.0,
        no_repeat_ngram_size = 1,
        num_return_sequences = 1,
        attention_mask = None,
        decoder_start_token_id = None,
        use_cache = None
    ):
        return self.model.generate(
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

    def story_generator(self):
        seed = random.randint(0, 100000)
        self.tokenizer.seed = seed
        self.model.seed = seed

        story = ["The sun was hot. Too hot. Jack had been walking alone in the "]
        while True:
            prompt = "".join(story)
            inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
            outputs = self.generate(inputs, eos_token_id=1, pad_token_id=1)
            ai_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            story.append(ai_output)

    def location_generator(self):
        seed = random.randint(0, 100000)
        self.tokenizer.seed = seed
        self.model.seed = seed
        print("\033[H\033[J")
        while True:
            user_input = input("> ")

            # genreate location_output
            prompt = f"{locations_text}location:{user_input}\n"
            print("generating...")
            inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
            outputs = self.generate(inputs, eos_token_id=1, pad_token_id=1)
            location_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            print(location_output)

            # generate monsters for this location
            prompt = f"{monsters_text}location:{user_input}\n"
            print("generating...")
            inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
            outputs = self.generate(inputs, eos_token_id=1, pad_token_id=1)
            monster_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            print(monster_output)

    def sd_prompt_generator(self):
        seed = random.randint(0, 100000)
        self.tokenizer.seed = seed
        self.model.seed = seed
        print("\033[H\033[J")
        while True:
            user_input = input("> ")

            # genreate location_output
            prompt = f"{sd_prompts}\nme:{user_input}\n"
            print("generating...")
            inputs = self.tokenizer(prompt, return_tensors="pt").input_ids.to("cuda")
            outputs = self.generate(inputs, eos_token_id=1, pad_token_id=1)
            location_output = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
            print(location_output)

    def world_generator(self):
        self.location_generator(location_generator_text)


txtgen = TextGenerator()
seed = random.randint(0, 100000)
save_dir = "saved_models"
os.makedirs(save_dir, exist_ok=True)
#txtgen.chat()
print("Loading model with seed:", seed)
txtgen.chat_bot(seed=seed, save_dir=save_dir)
#output = txtgen.sentence_complete("The cat in the hat sat on ")
#print(output)
#print(txtgen.generate_profile())
#txtgen.world_generator()
#txtgen.location_generator()
#txtgen.sd_prompt_generator()
