import os
import random
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QGuiApplication
from settings_manager import SettingsManager


class LLMWindow(QMainWindow):
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
        # self.client = OfflineClient(
        #     app=self,
        #     tqdm_var=self.tqdm_var,
        #     image_var=None,
        #     error_var=self.error_var,
        #     message_var=self.message_var,
        # )
        # print("initializing_offline_client ", self.message_var)
        # self.parent.client._tqdm_var = self.tqdm_var
        # self.parent.client._error_var = self.error_var
        # self.parent.client._message_var = self.message_var
        pass

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
        seed = self.get_seed()
        properties = self.prep_properties()
        prompt = self.ui.generated_text.toPlainText()
        self.client.message = {
            "action": "llm",
            "type": "generate",
            "data": {
                "prompt": prompt,
                "seed": seed,
                "properties": properties,
            }

        }
        # self.stop_progress_bar()
        # self.enable_generate_button()

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
        try:
            self.client = kwargs.pop("client")
        except KeyError:
            pass
        try:
            self.parent = kwargs.pop("parent")
        except KeyError:
            pass

        super().__init__(*args, **kwargs)
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
        self.initialize_offline_client()
        self.ui.closeEvent = self.handle_quit
        self.initialize_form()
        # self.exec()

    def handle_quit(self, *args, **kwargs):
        pass

    def initialize_form(self):
        pass

    def load_template(self):
        HERE = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(os.path.join(HERE, f"pyqt/llmrunner/{self.template}.ui")))
        # self.ui.setWindowIcon(QIcon('./assets/icon.png'))

    def tqdm_callback(self, *args, **kwargs):
        pass