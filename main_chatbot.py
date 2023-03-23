import json
import os
import queue
import random
from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QFileDialog
from llmrunner.conversation import Conversation
from main_llm import LLMWindow
from settings import CHAT_AI_VERSION


class ChatbotWindow(LLMWindow):
    template = "chatbot"

    def message_handler(self, *args, **kwargs):
        message = args[0]["response"]
        botname = message["botname"]
        type = message["type"]
        if type == "generate_characters":
            self.username = message["username"]
            self.botname = message["botname"]
            self.ui.username.setText(self.username)
            self.ui.botname.setText(self.botname)
        else:
            response = message["response"]
            response = response.replace("<pad>", "")
            response = response.replace("<unk>", "")
            incomplete = False
            if "</s>" not in response:
                # remove all tokens after </s> and </s> itself
                incomplete = True
            else:
                response = response[: response.find("</s>")]
            response = response.strip()

            if not incomplete:
                formatted_response = f"{botname} says: \"{response}\"\n"
                self.conversation.add_message(botname, response)
                self.ui.generated_text.appendPlainText(formatted_response)
            else:
                self.chatbot_generate()

        self.stop_progress_bar()
        self.enable_buttons()

    chatbot_result_queue = queue.Queue()

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

    def __init__(self, *args, **kwargs):
        chat_prompt_keys = self.prompt_settings["chat"].keys()
        prompt_key = "interesting"#random.choice(list(chat_prompt_keys))
        settings = self.prompt_settings["chat"][prompt_key]
        self.properties = kwargs.pop("properties", settings)
        self.seed = random.randint(0, 1000000)

        # when user clicks the close window button call self.closeEvent

        super().__init__(*args, **kwargs)

    def initialize_form(self):
        self.ui.send_button.clicked.connect(self.chatbot_generate)
        self.conversation = Conversation(self)

        # create a thread safe queue variable that will store results

        # set the tab focus order for self.chatbot_ui.username, self.chatbot_ui.botname, self.chatbot_ui.prompt
        self.ui.username.setTabOrder(self.ui.username, self.ui.botname)
        self.ui.botname.setTabOrder(self.ui.botname, self.ui.prompt)
        self.ui.prompt.setTabOrder(self.ui.prompt, self.ui.send_button)

        # set dropdown menu values
        actions = ["chat", "act"]
        self.ui.action.addItems(actions)
        self.ui.action.setCurrentIndex(0)
        # delete self.ui.action from the widget
        self.ui.action.deleteLater()

        self.ui.username.setFocus()
        self.ui.prompt.returnPressed.connect(self.chatbot_generate)

        self.ui.clear_conversation_button.clicked.connect(self.clear_conversation)

        self.ui.button_generate_characters.clicked.connect(self.generate_characters)

        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionNew.triggered.connect(self.new_conversation)
        self.ui.actionSave.triggered.connect(self.save_conversation)
        self.ui.actionLoad.triggered.connect(self.load_conversation)
        self.ui.actionQuit.triggered.connect(self.handle_quit)
        self.ui.actionAdvanced.triggered.connect(self.advanced_settings)

        self.ui.setWindowTitle(f"Chat AI v{CHAT_AI_VERSION}")

        self.ui.generated_text.setReadOnly(True)

        self.center()

        self.ui.show()

    def advanced_settings(self):
        HERE = os.path.dirname(os.path.abspath(__file__))
        advanced_settings_window = uic.loadUi(os.path.join(HERE, "pyqt/llmrunner/advanced_settings.ui"))
        advanced_settings_window.exec()

    def about(self):
        # display pyqt/about.ui popup window
        HERE = os.path.dirname(os.path.abspath(__file__))
        about_window = uic.loadUi(os.path.join(HERE, "pyqt/llmrunner/about.ui"))
        about_window.setWindowTitle(f"About Chat AI")
        about_window.title.setText(f"Chat AI v{CHAT_AI_VERSION}")
        about_window.exec()

    def new_conversation(self):
        self.clear_conversation()
        self.ui.username.setText("")
        self.ui.botname.setText("")

    def handle_quit(self, *args, **kwargs):
        self.ui.close()
        self.parent.show()

    def generate_characters(self):
        self.seed += 1
        self.disable_buttons()
        self.start_progress_bar()
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

    def save_conversation(self):
        filename = filename, _ = QFileDialog.getSaveFileName(
            None, "Save Conversation", "", "JSON files (*.json)"
        )
        if filename:
            if ".json" not in filename:
                filename += ".json"
            username = self.ui.username.text()
            botname = self.ui.botname.text()
            with open(filename, "w") as f:
                data = {
                    "username": username,
                    "botname": botname,
                    "conversation": self.conversation._dialogue,
                    "seed": self.seed,
                    "properties": self.properties
                }
                f.write(json.dumps(data, indent=4))

    def load_conversation(self):
        filename = filename, _ = QFileDialog.getOpenFileName(
            None, "Load Conversation", "", "JSON files (*.json)"
        )
        if filename:
            with open(filename, "r") as f:
                data = json.loads(f.read())
                self.ui.username.setText(data["username"])
                self.ui.botname.setText(data["botname"])
                self.conversation.dialogue = data["conversation"]
                self.ui.generated_text.setPlainText(self.conversation.dialogue)
                self.seed = data["seed"]
                self.properties = data["properties"]

    def clear_conversation(self):
        self.seed += 1
        self.conversation = Conversation(self)
        self.ui.generated_text.setPlainText("")

    def chatbot_generate(self):
        # disable the generate button
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 0)
        self.ui.send_button.setEnabled(False)
        username = self.ui.username.text()
        botname = self.ui.botname.text()
        user_input = self.ui.prompt.text()
        self.ui.prompt.setText("")
        self.conversation.add_message(username, user_input)
        self.ui.generated_text.setPlainText(f"{self.conversation.dialogue}")
        self.ui.prompt.setText("")
        properties = self.prep_properties()
        # get current action and set it on properties
        self.client.message = {
            "action": "llm",
            "type": "chat",
            "data": {
                "user_input": user_input,
                "prompt": None,
                "username": username,
                "botname": botname,
                "seed": self.seed,
                "conversation": self.conversation,
                "properties": properties,
            }
        }

    def enable_buttons(self):
        self.ui.send_button.setEnabled(True)
        self.ui.button_generate_characters.setEnabled(True)

    def disable_buttons(self):
        self.ui.send_button.setEnabled(False)
        self.ui.button_generate_characters.setEnabled(False)

    @pyqtSlot(dict)
    def process_response(self, response):
        self.enable_buttons()
        self.stop_progress_bar()
        self.chatbot_result_queue.put((response["text"], response["botname"]))

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


if __name__ == '__main__':
    ChatbotWindow([])
