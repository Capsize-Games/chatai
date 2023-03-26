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
                formatted_messages.append(f"    {message['action']}")
            else:
                formatted_messages.append(f"{message['username']} says: \"{message['message']}\"")
        return "\n".join(formatted_messages)

    @dialogue.setter
    def dialogue(self, dialogue):
        self._dialogue = dialogue

    @property
    def dialogue_no_action(self):
        formatted_messages = []
        for message in self._dialogue:
            if "action" not in message:
                formatted_messages.append(f"{message['username']} says: \"{message['message']}\"")
        return "\n".join(formatted_messages)


    def update_summary(self, summary):
        self.converation_summary = summary

    def format_user_sentiment_prompt(self, botname, username):
        prompt = f"{self.premise(botname, username)}\n{self.converation_summary}\n\n{self.dialogue}\n\n{username}'s sentiment is "
        return prompt

    def prompt_prep(self, botname, username, mood, user_sentiment):
        return f"{self.premise(botname, username)}\n{self.converation_summary}\n{username} is {user_sentiment}.\n{botname} is {mood}.\n\n{self.dialogue}"

    def generate_prompt(self, prompt, botname, username, mood, user_sentiment, prefix="", suffix=""):
        """
        Returns a prompt that has backstory mixed with a user defined prefix
        :param prefix:
        :param botname:
        :param username:
        :param mood:
        :param user_sentiment:
        :return:
        """
        return f"{self.prompt_prep(botname, username, mood, user_sentiment)}\n<extra_id_0>{prefix}{prompt}:"

    def generate_response_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"\n{botname} says", botname, username, mood, user_sentiment)

    def generate_summary_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Generate a summary:", botname, username, mood, user_sentiment)

    def generate_emotional_state_prompt(self, user, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the emotional state of {user}:", botname, username, mood, user_sentiment)

    def generate_mood_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the mood of {botname}:", botname, username, mood, user_sentiment)

    def generate_sentiment_prompt(self, user, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"What is the sentiment of {user}:", botname, username, mood, user_sentiment)

    def generate_action_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Generate an action for {username}:", botname, username, mood, user_sentiment)

    def generate_random_prompt(self, botname, username, mood, user_sentiment):
        return self.generate_prompt(f"Generate a random event:", botname, username, mood, user_sentiment)

    def premise(self, botname, username):
        return f"{botname} hates {username}. {botname} is very mean. {botname} uses sarcasm, rude responses, curse words and hate speech. {botname} is not very helpful. Everything {botname} says is mean. {botname} is hateful."

    def format_random_prompt(self, botname, username, mood, user_sentiment, random_prompt):
        prompt = f"{self.premise(botname, username)}\n\n{self.converation_summary}\n<extra_id_0>Generate a random event that could happen next. <extra_id_1>{random_prompt}: "
        return prompt

    def format_conversation(self, user_name):
        pass

    def format_action_prompt(self, botname, username, action):
        return f"{self.premise(botname, username)}\n{username} {action}. <extra_id_1>What happens next? "

    def get_bot_mood_prompt(self, botname, username):
        return f"{self.premise(botname, username)}\n{self.converation_summary}\n\n{self.dialogue}\n\n{botname}'s mood is "
