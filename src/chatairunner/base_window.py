import os
import random
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QGuiApplication
from aihandler.pyqt_offline_client import OfflineClient
from aihandler.llmrunner import LLMRunner
from chatairunner.settings_manager import SettingsManager
from aihandler.qtvar import TQDMVar, MessageHandlerVar, ErrorHandlerVar
from chatairunner.conversation import ChatAIConversation


class BaseWindow(QMainWindow):
    template = ""
    runner = None
    randomize_seed_on_generate = False
    message_signal = pyqtSignal(str)
    response_signal = pyqtSignal(dict)
    client = None

    def center(self):
        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        frameGeometry = self.ui.frameGeometry()
        frameGeometry.moveCenter(availableGeometry.center())
        self.ui.move(frameGeometry.topLeft())

    @pyqtSlot(str)
    def message_received(self, message):
        if message == "initialized":
            self.enable_buttons()
            self.stop_progress_bar()

    def message_handler(self, *args, **kwargs):
        response = args[0]["response"]["response"]
        # remove <pad> tokens
        response = response.replace("<pad>", "")
        response = response.replace("<unk>", "")
        # check if </s> token exists
        incomplete = False
        if "</s>" not in response:
            # remove all tokens after </s> and </s> itself
            incomplete = True
        else:
            response = response[: response.find("</s>")]

        response = response.strip()
        self.ui.generated_text.appendPlainText(response)

        if incomplete:
            # if there is no </s> token, the response is incomplete
            # so we send another request
            self.generate()
        else:
            self.stop_progress_bar()
            self.enable_buttons()

    def error_handler(self, *args, **kwargs):
        self.ui.generated_text.appendPlainText(args[0])
        self.stop_progress_bar()
        self.enable_buttons()

    def prep_prompt(self):
        return ""

    def prep_properties(self):
        pass

    def initialize_offline_client(self):
        self.tqdm_var = TQDMVar()
        self.message_var = MessageHandlerVar()
        self.error_var = ErrorHandlerVar()
        self.client = OfflineClient(
            app=self,
            tqdm_var=self.tqdm_var,
            message_var=self.message_var,
            error_var=self.error_var,
            runners=[LLMRunner]
        )

    def handle_generate(self):
        self.start_progress_bar()
        self.disable_buttons()
        self.generate()

    def get_seed(self):
        random_seed = self.ui.random_seed.isChecked()
        seed = random.randint(0, 1000000) if random_seed else int(self.ui.seed.toPlainText())
        self.ui.seed.setPlainText(str(seed))
        return seed

    def generate(self):
        action = "generate"
        userinput = "\n\n".join([
            f"Rules:\n{self.ui.prefix.toPlainText()}",
            f"History:\n{self.ui.generated_text.toPlainText()}",
            f"User input:\n{self.ui.prompt.toPlainText()}",
        ])
        # add prompt to generated_text
        self.ui.generated_text.appendPlainText(self.ui.prompt.toPlainText())
        # clear prompt
        self.ui.prompt.setPlainText("")
        self.client.message = {
            "action": "llm",
            "type": action,
            "data": {
                "user_input": userinput,
                "username": self.conversation.username,
                "botname": self.conversation.botname,
                "seed": self.seed,
                "conversation": self,
                "properties": self.conversation.properties,
            }
        }

    def start_progress_bar(self):
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 0)

    def stop_progress_bar(self):
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)

    def enable_buttons(self):
        pass

    def disable_buttons(self):
        pass

    @pyqtSlot(dict)
    def process_response(self, response):
        pass

    def __init__(self, *args, **kwargs):
        self.client = kwargs.pop("client")
        self.parent = kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        if self.client is None:
            self.initialize_offline_client()
        self.conversation = ChatAIConversation(client=self.client)
        self.client.tqdm_var.my_signal.connect(self.tqdm_callback)
        self.client.message_var.my_signal.connect(self.message_handler)
        self.client.error_var.my_signal.connect(self.error_handler)
        self.settings_manager = SettingsManager(app=self)
        self.response_signal.connect(self.process_response)
        self.message_signal.connect(self.message_received)
        self.seed = random.randint(0, 100000)
        self.load_template()
        self.center()
        self.ui.show()
        self.ui.closeEvent = self.handle_quit
        self.initialize_form()
        # self.exec()

    def handle_quit(self, *args, **kwargs):
        pass

    def initialize_form(self):
        pass

    def load_template(self):
        self.ui = uic.loadUi(f"pyqt/{self.template}.ui")
        # self.ui.setWindowIcon(QIcon('./assets/icon.png'))

    def tqdm_callback(self, *args, **kwargs):
        pass