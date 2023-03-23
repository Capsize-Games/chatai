class Conversation:
    summary_length = 20
    def __init__(self, app):
        self.app = app
        self.converation_summary = ""
        self._dialogue = []
        self._summaries = []

    @property
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
        return f"{self.dialogue}\n\nSummarize the conversation: </s>"

    @property
    def dialogue_length(self):
        return len(self._dialogue)

    @property
    def do_summary(self):
        #return self.dialogue_length >= self.summary_length
        return False

    def add_message(self, username, message):
        self._dialogue.append({
            "username": username,
            "message": message
        })

    @property
    def dialogue(self):
        return "\n".join([f"{message['username']} says: \"{message['message']}\"" for message in self._dialogue])

    @dialogue.setter
    def dialogue(self, dialogue):
        self._dialogue = dialogue

    def update_summary(self, summary):
        self.converation_summary = summary
        # keep last two items in dialogue
        self._dialogue = self._dialogue[-2:]

    def format_user_sentiment_prompt(self, botname, username):
        prompt = f"Context: {botname} and {username} are having a conversation. {self.converation_summary}\n\n{self.dialogue}\n\n{username}'s sentiment is "
        return prompt

    def format_prompt(self, botname, username, mood, user_sentiment):
        prompt = f"Context: {botname} and {username} are having a conversation.\n{self.converation_summary}\n{botname}'s mood: {mood}\n{username}'s sentiment: {user_sentiment}\n\n{self.dialogue}\n{botname} says: \""
        return prompt

    def format_conversation(self, user_name):
        pass

    def get_bot_mood_prompt(self, botname, username):
        return f"Context: {botname} and {username} are having a conversation. {self.converation_summary}\n\n{self.dialogue}\n\n{botname}'s mood is "
