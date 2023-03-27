import json
import random
from aihandler.pyqt_offline_client import OfflineClient


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
types_of_gods = ['greek', 'roman', 'pagan', 'egyption', 'norse', 'indian', 'chinese', 'japanese', 'jewish',
                 'christian', 'islamic']
character_prompts = [
    f"famous person from the {random.randint(4, 20)}th century",
    f"{random.choice(types_of_gods)} {random.choice(['god', 'goddess'])}",
    f"character from a {random.choice(choices)}",
    f"{random.choice(choices_a)}",
    f"famous {random.choice(choices_b)}",
]

class Conversation:
    client: OfflineClient = None
    username: str = ""
    botname: str = ""
    seed: int = 0
    properties: dict = {}
    conversation_summary: str = ""
    _dialogue: list = []
    _summaries: list = []
    summary_length: int = 20
    special_characters: dict = [
        "</s>",
        "<pad>",
        "<unk>"
    ]
    prompt_settings = {
        "chat": {
            "normal": {
                "max_length": 20,
                "min_length": 0,
                "num_beams": 1,
                "temperature": 1.0,
                "top_k": 1,
                "top_p": 0.9,
                "repetition_penalty": 1.0,
                "length_penalty": 1.0,
                "no_repeat_ngram_size": 1,
                "num_return_sequences": 1,
                "model": "flan-t5-xl",
            },
            "interesting": {
                "max_length": 512,
                "min_length": 0,
                "num_beams": 3,
                "temperature": 1.2,
                "top_k": 120,
                "top_p": 0.9,
                "repetition_penalty": 2.0,
                "length_penalty": 0.1,
                "no_repeat_ngram_size": 2,
                "num_return_sequences": 1,
                "model": "flan-t5-xl",
            },
            "wild": {
                "max_length": 512,
                "min_length": 0,
                "num_beams": 3,
                "temperature": 2.0,
                "top_k": 200,
                "top_p": 0.9,
                "repetition_penalty": 2.0,
                "length_penalty": 0.1,
                "no_repeat_ngram_size": 2,
                "num_return_sequences": 1,
                "model": "flan-t5-xl",
            }
        }
    }

    def __init__(self, client, **kwargs):
        """
        :param args:
        :param kwargs:
        :keyword client:OfflineClient The client class which is responsible for handling model requests / responses
        :keyword username:str The current name of the user
        :keyword botname:str The current name of the bot
        :keyword seed:int The seed for the random number generator
        :keyword properties:dict The properties for the model
        """
        self._initialize(client, **kwargs)  # Initialize the conversation

    def new_seed(self, seed: int = None):
        new_seed = seed
        if not new_seed:
            new_seed = self.seed
            while new_seed == self.seed:
                new_seed = random.randint(0, 100000)
        self.seed = new_seed
        self.llm_runner.do_set_seed(self.seed)


    def _initialize(self, client=None, **kwargs):
        if client:
            self.client = client
            self.llm_runner = client.llm_runner
        self.conversation_summary = ""
        self.username = kwargs.get("username", "User")
        self.botname = kwargs.get("botname", "ChatAI")
        self.seed = kwargs.get("seed", random.randint(0, 100000))
        self.chat_type = kwargs.get("chat_type", "normal")
        self.properties = self.prompt_settings["chat"][self.chat_type]
        self._dialogue = kwargs.get("dialogue", [])
        self._summaries = kwargs.get("summaries", [])

    def reset(self, **kwargs):
        """
        Reset the conversation.
        :param kwargs:
        :return:
        """
        self._initialize(**kwargs)

    def save(self, filename: str):
        """
        Save the conversation to a file
        :param filename: str The filename to save the conversation to
        :return:
        """
        if ".json" not in filename:
            filename += ".json"
        with open(filename, "w") as f:
            data = {
                "username": self.username,
                "botname": self.botname,
                "conversation": self._dialogue,
                "seed": self.seed,
                "properties": self.properties
            }
            f.write(json.dumps(data, indent=4))

    def load(self, filename: str):
        with open(filename, "r") as f:
            data = json.loads(f.read())
            self.username.setText(data["username"])
            self.botname.setText(data["botname"])
            self.dialogue = data["conversation"]
            self.new_seed(data["seed"])
            self.properties = data["properties"]

    def prep_properties(self):
        return {
            "max_length": self.properties["max_length"],
            "min_length": self.properties["min_length"],
            "num_beams": self.properties["num_beams"],
            "temperature": self.properties["temperature"],
            "top_k": self.properties["top_k"],
            "top_p": self.properties["top_p"],
            "repetition_penalty": self.properties["repetition_penalty"],
            "length_penalty": self.properties["length_penalty"],
            "no_repeat_ngram_size": self.properties["no_repeat_ngram_size"],
            "num_return_sequences": self.properties["num_return_sequences"],
            "model": self.properties["model"],
        }

    def send_generate_characters_message(self):
        """
        This method kicks of a generate characters request which is processed by the client.
        :return:
        """
        self.new_seed()
        self.client.message = {
            "prompt": None,
            "user_input": None,
            "action": "llm",
            "type": "generate_characters",
            "data": {
                "properties": self.prep_properties(),
                "seed": self.seed
            }
        }

    @property
    def response(self):
        """
        added for response setter - ignore
        :return:
        """
        return None

    @response.setter
    def response(self, data: dict):
        """
        Sends data response to the llm_runner which handles processing for the client.
        :param data:
        :return:
        """
        self.llm_runner.set_message(data)

    def do_generate_characters(self):
        """
        This method is called from the client when the client processes a generate characters request.
        :return:
        """
        self.username = self.generate_character()
        self.new_seed()
        self.botname = self.generate_character()
        self.response = {
            "type": "generate_characters",
            "username": self.username,
            "botname": self.botname,
        }

    def generate_character(self):
        """
        Crafts a prompt which is used to generate a character name.
        :return: str The generated character name
        """
        prefix = "Generate the name of a "
        prompt = prefix + random.choice(character_prompts) + ": "
        properties = self.properties.copy()
        properties["temperature"] = random.random() + 1.0
        properties["top_k"] = 40
        username = self.llm_runner.generate(
            prompt=prompt,
            seed=self.seed,
            **properties,
            return_result=True,
            skip_special_tokens=True
        )
        return username

    def strip_special_characters(self, string):
        for special_character in self.special_characters:
            string = string.replace(special_character, "")
        return string

    def summary_prompt(self):
        # print("Summarizing")
        # self.app.runner.load_summarizer()
        # prompt = self.dialogue
        # summary = self.app.runner.model(prompt)[0]['summary_text']
        # self._summaries.append(summary)
        #
        # if len(self._summaries) > 1:
        #     # now summarize up to the last self.summary_length summaries
        #     summary = "\n".join(self._summaries)
        #
        # print(summary)
        #
        # self.app.runner.load_model(self.app.runner.model_name)
        # return summary
        return f"<extra_id_0>{self.dialogue} <extra_id_1>Summarize:"

    @property
    def dialogue_length(self):
        return len(self._dialogue)

    @property
    def do_summary(self):
        #return self.dialogue_length >= self.summary_length
        return False

    def add_bot_action(self, action):
        self.add_action(self.botname, action)

    def add_user_action(self, action):
        self.add_action(self.username, action)

    def add_action(self, username, action, do_summary=False):
        self._dialogue.append({
            "username": username,
            "action": action
        })
        self.response = {
            "type": "action",
            "username": username,
            "response": action
        }

    def send_user_message(self, action, message):
        print("send_user_message", action, message)
        print("send_user_message")
        if action != "action":
            self.add_user_message(message)
        self.client.message = {
            "action": "llm",
            "type": action,
            "data": {
                "user_input": message,
                "prompt": None,
                "username": self.username,
                "botname": self.botname,
                "seed": self.seed,
                "conversation": self,
                "properties": self.properties,
            }
        }

    def add_user_message(self, message):
        self.add_message(self.username, message)

    def add_bot_message(self, message):
        self.add_message(self.botname, message)

    def add_message(self, username, message):
        self._dialogue.append({
            "username": username,
            "message": message
        })
        self.response = {
            "type": "chat",
            "username": username,
            "response": f"{username} says: \"{message}\""
        }

    @property
    def dialogue(self):
        formatted_messages = []
        for message in self._dialogue:
            if "action" in message:
                formatted_messages.append(f"  {message['username']} {message['action']}")
            else:
                formatted_messages.append(f"{message['username']} says: \"{message['message']}\"")
        return "\n".join(formatted_messages)

    @dialogue.setter
    def dialogue(self, dialogue):
        self._dialogue = dialogue

    def update_summary(self, summary):
        self.conversation_summary = summary

    def format_user_sentiment_prompt(self):
        prompt = f"{self.premise()}\n{self.conversation_summary}\n\n{self.dialogue}\n\n{self.username}'s sentiment is "
        return prompt

    def prompt_prep(self, mood=None, user_sentiment=None):
        mood_segments = []
        if user_sentiment:
            sentiment_prompt = f"{self.username}'s sentiment is {user_sentiment}."
            mood_segments.append(user_sentiment)
        if mood:
            mood_prompt = f"{self.botname} mood is {mood}."
            mood_segments.append(mood)
        combined_sentiment_mood = " ".join(mood_segments)
        prompt_segments = [
            self.premise(),
            self.conversation_summary,
            combined_sentiment_mood,
            self.dialogue
        ]
        return "\n\n".join([segment for segment in prompt_segments if segment])

    def generate_prompt(self, prompt, mood=None, user_sentiment=None, prefix="", suffix=""):
        """
        Returns a prompt that has backstory mixed with a user defined prefix
        :param prefix:
        :param botname:
        :param username:
        :param mood:
        :param user_sentiment:
        :return:
        """
        prompt = f"{self.prompt_prep(mood, user_sentiment)}\n<extra_id_0>{prefix}{prompt}:"
        return prompt

    def generate_response_prompt(self, mood, user_sentiment):
        return self.generate_prompt(f"{self.botname} says", self.botname, self.username, mood, user_sentiment)

    def generate_summary_prompt(self, mood, user_sentiment):
        return self.generate_prompt(f"Generate a summary:", self.botname, self.username, mood, user_sentiment)

    def generate_emotional_state_prompt(self, user, mood, user_sentiment):
        return self.generate_prompt(f"What is the emotional state of {user}:", self.botname, self.username, mood, user_sentiment)

    def generate_mood_prompt(self, mood, user_sentiment):
        return self.generate_prompt(f"What is the mood of {self.botname}:", self.botname, self.username, mood, user_sentiment)

    def format_bot_alive_prompt(self):
        return self.generate_prompt(f"{self.conversation_summary}\n\n{self.dialogue}<extra_id_0>Is {self.botname} still alive, yes or no? </s>", self.botname, self.username)

    def generate_sentiment_prompt(self, user, mood, user_sentiment):
        return self.generate_prompt(f"What is the sentiment of {user}:", self.botname, self.username, mood, user_sentiment)

    def generate_reaction_prompt(self, mood=None, user_sentiment=None):
        return self.generate_prompt(f"Describe what happens next", self.botname, self.username, mood, user_sentiment)

    def generate_random_prompt(self, mood, user_sentiment):
        return self.generate_prompt(f"Generate a random event:", self.botname, self.username, mood, user_sentiment)

    def premise(self):
        mean_bot = f"{self.botname} hates {self.username}. {self.botname} is very mean. {self.botname} uses sarcasm, rude responses, curse words and hate speech. Everything {self.botname} says is mean. {self.botname} is hateful."
        nice_bot = f"{self.botname} loves {self.username}. {self.botname} is very nice. {self.botname} uses compliments, kind responses, and nice words. Everything {self.botname} says is nice. {self.botname} is kind."
        weird_bot = f"{self.botname} is weird. {self.botname} is very weird. {self.botname} uses weird responses, and weird words. Everything {self.botname} says is weird. {self.botname} is weird."
        insane_bot = f"{self.botname} is insane. {self.botname} is very insane. {self.botname} uses insane responses, and insane words. Everything {self.botname} says is insane. {self.botname} is insane."
        bot_personality = random.choice([mean_bot, nice_bot, weird_bot, insane_bot])
        result = f"{self.username} and {self.botname} are talking. {bot_personality}"
        return result

    def format_random_prompt(self, mood, user_sentiment, random_prompt):
        prompt = f"{self.premise()}\n\n{self.conversation_summary}\n<extra_id_0>Generate a random event that could happen next. <extra_id_1>{random_prompt}: "
        return prompt

    def format_conversation(self, user_name):
        pass

    def get_bot_mood_prompt(self):
        return f"{self.premise()}\n{self.conversation_summary}\n\n{self.dialogue}\n\n{self.botname}'s mood is "

    def send_user_is_dead_message(self):
        self.response = {
            "type": "action",
            "botname": self.botname,
            "response": f"{self.botname} is dead"
        }

    def generate_bot_response(self):
        if self.do_summary:
            self.summarize()
        if not self.is_bot_alive:
            self.send_user_is_dead_message()
            return
        bot_mood = self.get_bot_mood()
        user_sentiment = self.get_user_sentiment()
        bot_response = self.get_bot_response(bot_mood, user_sentiment)
        self.add_bot_message(bot_response)

    def get_user_reaction(self):
        action_prompt = self.generate_reaction_prompt()
        reaction = self.llm_runner.generate(
            action_prompt,
            seed=self.seed,
            **self.properties,
            return_result=True,
            skip_special_tokens=True
        )
        return reaction

    def generate_reaction(self, user_input):
        if self.do_summary:
            self.summarize()
        self.add_user_action(user_input)
        reaction = self.get_user_reaction()
        formatted_action_reaction = f"{self.username} {user_input}."
        reaction = reaction.strip()
        formatted_action_reaction += f" {reaction}"
        self.add_bot_action(formatted_action_reaction)
        self.summarize()

    def process_chat_repsonse(self, string, username):
        """
        Removes specified substrings, whitespaces, and double quotes from a string.

        Args:
        string (str): The input string to process.
        username (str): The name of the user, which will be removed from the string.

        Returns:
        str: The processed string with specified substrings removed and whitespaces/double quotes stripped.
        """
        # strip all special tokens
        if not string:
            return ""
        for specialtoken in ["</s>", "<pad>", "<unk>", "<bos>", "<eos>"]:
            string = string.replace(specialtoken, "")

        substrings_to_remove = [f"{username} says:", f"{username}:"]
        for substring in substrings_to_remove:
            string = string.replace(substring, "")
        string = string.strip()
        string = string.replace('"', '')
        return string

    def get_bot_response(self, bot_mood: str, user_sentiment: str):
        properties = self.properties.copy()
        properties["top_k"] = 70
        properties["top_p"] = 1.0
        properties["num_beams"] = 8
        properties["repetition_penalty"] = 100.0
        properties["early_stopping"] = True
        properties["max_length"] = 512
        properties["min_length"] = 0
        properties["temperature"] = 1.75
        properties["skip_special_tokens"] = False
        prompt = self.generate_response_prompt(bot_mood, user_sentiment)
        response = self.llm_runner.generate(prompt, **properties)
        response = self.process_chat_repsonse(response, self.botname)
        return response

    def get_user_sentiment(self):
        properties = self.properties.copy()
        properties["temperature"] = 1.6
        properties["top_k"] = 70
        properties["repetition_penalty"] = 20.0
        properties["top_p"] = 1.0
        properties["num_beams"] = 6
        sentiment_prompt = self.format_user_sentiment_prompt()
        sentiment_results = self.llm_runner.generate(
            sentiment_prompt,
            seed=self.seed,
            **properties,
            return_result=True,
            skip_special_tokens=True
        )
        return sentiment_results

    def get_bot_mood(self):
        properties = self.properties.copy()
        properties["temperature"] = 1.6
        properties["top_k"] = 70
        properties["repetition_penalty"] = 20.0
        properties["top_p"] = 1.0
        properties["num_beams"] = 6
        mood_prompt = self.get_bot_mood_prompt()
        mood_results = self.llm_runner.generate(
            prompt=mood_prompt,
            seed=self.seed,
            **properties,
            return_result=True,
            skip_special_tokens=True
        )
        mood = mood_results
        mood = mood.strip()
        # strip period from end of mood
        if mood.endswith("."):
            mood = mood[:-1]
        # lower
        mood = mood.lower()
        return mood


    def is_bot_alive(self) -> bool:
        prompt = self.format_bot_alive_prompt()
        results = self.llm_runner.generate(
            prompt=prompt,
            seed=self.seed,
            **self.properties,
            return_result=True,
            skip_special_tokens=True
        )
        bot_alive = results
        bot_alive = bot_alive.strip()
        print("IS BOT ALIVE: ", bot_alive)
        return bot_alive != "no"

    def summarize(self):
        results = self.llm_runner.generate(
            prompt=self.summary_prompt(),
            seed=self.seed,
            **self.properties,
            return_result=True,
            skip_special_tokens=True)
        summary = results
        self.update_summary(summary)