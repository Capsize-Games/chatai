import random


class Conversation:
    summary_length = 20
    special_characters = [
        "</s>",
        "<pad>",
        "<unk>"
    ]
    def __init__(self, app):
        self.app = app
        self.converation_summary = ""
        self._dialogue = []
        self._summaries = []

    def strip_special_characters(self, string):
        for special_character in self.special_characters:
            string = string.replace(special_character, "")
        return string

    def summary_prompt(self, username, botname):
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

    def add_action(self, username, action, do_summary=False):
        self._dialogue.append({
            "username": username,
            "action": action
        })



    def add_message(self, username, message):
        self._dialogue.append({
            "username": username,
            "message": message
        })

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
        self.converation_summary = summary

    def format_user_sentiment_prompt(self, botname, username):
        prompt = f"{self.premise(botname, username)}\n{self.converation_summary}\n\n{self.dialogue}\n\n{username}'s sentiment is "
        return prompt

    def prompt_prep(self, botname, username, mood=None, user_sentiment=None):
        mood_segments = []
        if user_sentiment:
            sentiment_prompt = f"{username}'s sentiment is {user_sentiment}."
            mood_segments.append(user_sentiment)
        if mood:
            mood_prompt = f"{botname} mood is {mood}."
            mood_segments.append(mood)
        combined_sentiment_mood = " ".join(mood_segments)
        prompt_segments = [
            self.premise(botname, username),
            self.converation_summary,
            combined_sentiment_mood,
            self.dialogue
        ]
        return "\n\n".join([segment for segment in prompt_segments if segment])

    def generate_prompt(self, prompt, botname, username, mood=None, user_sentiment=None, prefix="", suffix=""):
        """
        Returns a prompt that has backstory mixed with a user defined prefix
        :param prefix:
        :param botname:
        :param username:
        :param mood:
        :param user_sentiment:
        :return:
        """
        prompt = f"{self.prompt_prep(botname, username, mood, user_sentiment)}\n<extra_id_0>{prefix}{prompt}:"
        return prompt

    def generate_response_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"{botname} says", botname, username, mood, user_sentiment)

    def generate_summary_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Generate a summary:", botname, username, mood, user_sentiment)

    def generate_emotional_state_prompt(self, user, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the emotional state of {user}:", botname, username, mood, user_sentiment)

    def generate_mood_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the mood of {botname}:", botname, username, mood, user_sentiment)

    def format_bot_alive_prompt(self, botname, username):
        return self.generate_prompt(f"{self.converation_summary}\n\n{self.dialogue}<extra_id_0>Is {botname} still alive, yes or no? </s>", botname, username)

    def generate_sentiment_prompt(self, user, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the sentiment of {user}:", botname, username, mood, user_sentiment)

    def generate_action_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Describe what happens next", botname, username, mood, user_sentiment)

    def generate_random_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Generate a random event:", botname, username, mood, user_sentiment)

    def premise(self, botname, username):
        mean_bot = f"{botname} hates {username}. {botname} is very mean. {botname} uses sarcasm, rude responses, curse words and hate speech. Everything {botname} says is mean. {botname} is hateful."
        nice_bot = f"{botname} loves {username}. {botname} is very nice. {botname} uses compliments, kind responses, and nice words. Everything {botname} says is nice. {botname} is kind."
        weird_bot = f"{botname} is weird. {botname} is very weird. {botname} uses weird responses, and weird words. Everything {botname} says is weird. {botname} is weird."
        insane_bot = f"{botname} is insane. {botname} is very insane. {botname} uses insane responses, and insane words. Everything {botname} says is insane. {botname} is insane."
        return random.choice([mean_bot, nice_bot, weird_bot, insane_bot])

    def format_random_prompt(self, botname, username, mood, user_sentiment, random_prompt):
        prompt = f"{self.premise(botname, username)}\n\n{self.converation_summary}\n<extra_id_0>Generate a random event that could happen next. <extra_id_1>{random_prompt}: "
        return prompt

    def format_conversation(self, user_name):
        pass

    def get_bot_mood_prompt(self, botname, username):
        return f"{self.premise(botname, username)}\n{self.converation_summary}\n\n{self.dialogue}\n\n{botname}'s mood is "
