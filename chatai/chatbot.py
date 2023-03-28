import pkg_resources
import os
import queue
import random
from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QApplication
from conversation import Conversation
from main_llm import LLMWindow


class ChatbotWindow(LLMWindow):
    template = "chatbot"
    chatbot_result_queue = queue.Queue()
    conversation: Conversation = None
    chat_type = "interesting"

    @property
    def username(self):
        return self.ui.username.text()

    @username.setter
    def username(self, value):
        self.ui.username.setText(value)

    @property
    def botname(self):
        return self.ui.botname.text()

    @botname.setter
    def botname(self, value):
        self.ui.botname.setText(value)

    @property
    def action(self):
        return self.ui.action.currentText()

    @property
    def prompt(self):
        return self.ui.prompt.text()

    @prompt.setter
    def prompt(self, value):
        self.ui.prompt.setText(value)

    @pyqtSlot(dict)
    def process_response(self, response):
        self.enable_buttons()
        self.stop_progress_bar()
        self.chatbot_result_queue.put((response["text"], response["botname"]))

    def __init__(self, *args, **kwargs):
        self.seed = random.randint(0, 1000000)

        # when user clicks the close window button call self.closeEvent

        super().__init__(*args, **kwargs)

        self.client.llm_runner.conversation = self.conversation

    def message_handler(self, *args, **kwargs):
        message = args[0]["response"]
        type = message["type"]
        if type == "generate_characters":
            self.username = message["username"]
            self.botname = message["botname"]
        else:
            self.ui.generated_text.appendPlainText(message["response"])
        self.stop_progress_bar()
        self.enable_buttons()

    def clear_prompt(self):
        print("clear prompt")
        self.ui.prompt.clear()

    def tqdm_callback(self, *args, **kwargs):
        pass

    def initialize_form(self):
        self.conversation = Conversation(
            client=self.client,
            username=self.username,
            botname=self.botname,
            chat_type=self.chat_type
        )
        self.client.conversation = self.conversation
        self.set_tab_order()
        self.initialize_name_inputs()
        self.initilize_action_dropdown()
        self.ui.username.setFocus()
        self.connect_send_pressed()
        self.initialize_buttons()
        self.initialiizse_toolbar()
        version = pkg_resources.require("chatairunner")[0].version
        self.ui.setWindowTitle(f"Chat AI v{version}")
        self.ui.generated_text.setReadOnly(True)
        self.center()
        self.ui.show()

    def initialize_name_inputs(self):
        self.ui.username.textChanged.connect(self.update_conversation_names)
        self.ui.botname.textChanged.connect(self.update_conversation_names)

    def update_conversation_names(self):
        self.conversation.username = self.username
        self.conversation.botname = self.botname

    def initilize_action_dropdown(self):
        actions = ["chat", "action"]
        self.ui.action.addItems(actions)
        self.ui.action.setCurrentIndex(0)

    def set_tab_order(self):
        self.ui.username.setTabOrder(self.ui.username, self.ui.botname)
        self.ui.botname.setTabOrder(self.ui.botname, self.ui.prompt)
        self.ui.prompt.setTabOrder(self.ui.prompt, self.ui.send_button)

    def initialize_buttons(self):
        self.ui.send_button.clicked.connect(self.send_message)
        self.ui.clear_conversation_button.clicked.connect(self.clear_conversation)
        self.ui.button_generate_characters.clicked.connect(self.generate_characters)

    def initialiizse_toolbar(self):
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionNew.triggered.connect(self.new_conversation)
        self.ui.actionSave.triggered.connect(self.save_conversation)
        self.ui.actionLoad.triggered.connect(self.load_conversation)
        self.ui.actionQuit.triggered.connect(self.handle_quit)
        self.ui.actionAdvanced.triggered.connect(self.advanced_settings)

    @staticmethod
    def advanced_settings():
        HERE = os.path.dirname(os.path.abspath(__file__))
        advanced_settings_window = uic.loadUi(os.path.join(HERE, "pyqt/advanced_settings.ui"))
        advanced_settings_window.exec()

    def about(self):
        # display pyqt/about.ui popup window
        HERE = os.path.dirname(os.path.abspath(__file__))
        about_window = uic.loadUi(os.path.join(HERE, "pyqt/about.ui"))
        about_window.setWindowTitle(f"About Chat AI")
        about_window.title.setText(f"Chat AI v{self.version}")
        about_window.exec()

    def new_conversation(self):
        self.clear_conversation()
        self.ui.username.setText("")
        self.ui.botname.setText("")

    def handle_quit(self, *args, **kwargs):
        self.ui.close()
        self.parent.show()

    def generate_characters(self):
        self.disable_generate()
        self.conversation.send_generate_characters_message()
        self.seed = self.conversation.seed

    def save_conversation(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save Conversation", "", "JSON files (*.json)"
        )
        if filename:
            self.conversation.save(filename)

    def load_conversation(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "Load Conversation", "", "JSON files (*.json)"
        )
        if filename:
            self.conversation.load(filename)
            self.ui.generated_text.setPlainText(self.conversation.dialogue)

    def clear_conversation(self):
        self.conversation.reset()
        self.seed = self.conversation.seed
        self.ui.generated_text.setPlainText("")

    def start_progress_bar(self):
        self.ui.progressBar.setRange(0, 0)
        self.ui.progressBar.setValue(0)

    def connect_send_pressed(self):
        self.ui.prompt.returnPressed.connect(self.send_message)

    def disconnect_send_pressed(self):
        self.ui.prompt.returnPressed.disconnect()

    def disable_generate(self):
        self.disable_buttons()
        self.start_progress_bar()
        self.disconnect_send_pressed()
        self.ui.send_button.setEnabled(False)

    def send_message(self):
        self.disable_generate()
        self.conversation.send_user_message(self.action, self.prompt)
        self.clear_prompt()

    def enable_buttons(self):
        self.ui.send_button.setEnabled(True)
        self.ui.button_generate_characters.setEnabled(True)
        self.connect_send_pressed()

    def disable_buttons(self):
        self.ui.send_button.setEnabled(False)
        self.ui.button_generate_characters.setEnabled(False)


if __name__ == '__main__':
    if __name__ == '__main__':
        class Runner(QApplication):
            def __init__(self, args):
                super().__init__(args)
                self.main_window = ChatbotWindow(client=None, parent=self)
                self.exec()

            def show(self):
                pass

        Runner([])
