import json
import os
import pickle
import random
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QFileDialog, QMainWindow
from PyQt6.QtGui import QGuiApplication
from aiengine.pyqt_offline_client import OfflineClient
from aiengine.settings import TEXT_MODELS
from llmrunner import LLMRunner
from settings_manager import SettingsManager
from aiengine.qtvar import TQDMVar, MessageHandlerVar, ErrorHandlerVar
from settings import VERSION


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
        self.client = kwargs.pop("client")
        self.parent = kwargs.pop("parent")
        super().__init__(*args, **kwargs)
        if self.client is None:
            self.initialize_offline_client()
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
        HERE = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(os.path.join(HERE, f"pyqt/{self.template}.ui")))
        # self.ui.setWindowIcon(QIcon('./assets/icon.png'))

    def tqdm_callback(self, *args, **kwargs):
        pass


class MainWindow(LLMWindow):
    template = "main_window"
    chatbot_window = None

    @pyqtSlot(dict)
    def process_response(self, response):
        self.enable_buttons()
        self.stop_progress_bar()
        self.ui.generated_text.setPlainText(response["text"])

    def enable_buttons(self):
        self.enable_generate_button()

    def disable_buttons(self):
        self.disable_generate_button()

    def set_form_defaults(self):
        self.ui.max_length_slider.setValue(20)
        self.ui.max_length_spinbox.setValue(20)
        self.ui.min_length_slider.setValue(0)
        self.ui.min_length_spinbox.setValue(0)
        self.ui.num_beams_slider.setValue(1)
        self.ui.num_beams_spinbox.setValue(1)
        self.ui.top_k_slider.setValue(1)
        self.ui.top_k_spinbox.setValue(1)
        self.ui.no_repeat_ngram_size_slider.setValue(1)
        self.ui.no_repeat_ngram_size_spinbox.setValue(1)
        self.ui.num_return_sequences_slider.setValue(1)
        self.ui.num_return_sequences_spinbox.setValue(1)
        self.ui.top_p_slider.setValue(90)
        self.ui.top_p_spinbox.setValue(0.9)
        self.ui.temperature_slider.setValue(100)
        self.ui.temperature_spinbox.setValue(1.0)
        self.ui.repetition_penalty_slider.setValue(100)
        self.ui.repetition_penalty_spinbox.setValue(1.0)
        self.ui.length_penalty_slider.setValue(100)
        self.ui.length_penalty_spinbox.setValue(1.0)

    def handle_value_change(self, value_name, value, widget_name):
        self.ui.__getattribute__(widget_name).setValue(value)
        if self.chatbot_window:
            self.chatbot_window.properties[value_name] = value

    def initialize_form(self):
        # initialize sliders and spinboxes
        # set default values
        self.set_form_defaults()

        # integers first
        self.ui.max_length_slider.valueChanged.connect(lambda val: self.handle_value_change("max_length", val, "max_length_spinbox"))
        self.ui.max_length_spinbox.valueChanged.connect(lambda val: self.handle_value_change("max_length", val, "max_length_slider"))
        self.ui.min_length_slider.valueChanged.connect(lambda val: self.handle_value_change("min_length", val, "min_length_spinbox"))
        self.ui.min_length_spinbox.valueChanged.connect(lambda val: self.handle_value_change("min_length", val, "min_length_slider"))
        self.ui.num_beams_slider.valueChanged.connect(lambda val: self.handle_value_change("num_beams", val, "num_beams_spinbox"))
        self.ui.num_beams_spinbox.valueChanged.connect(lambda val: self.handle_value_change("num_beams", val, "num_beams_slider"))
        self.ui.top_k_slider.valueChanged.connect(lambda val: self.handle_value_change("top_k", val, "top_k_spinbox"))
        self.ui.top_k_spinbox.valueChanged.connect(lambda val: self.handle_value_change("top_k", val, "top_k_slider"))
        self.ui.no_repeat_ngram_size_slider.valueChanged.connect(lambda val: self.handle_value_change("no_repeat_ngram_size", val, "no_repeat_ngram_size_spinbox"))
        self.ui.no_repeat_ngram_size_spinbox.valueChanged.connect(lambda val: self.handle_value_change("no_repeat_ngram_size", val, "no_repeat_ngram_size_slider"))
        self.ui.num_return_sequences_slider.valueChanged.connect(lambda val: self.handle_value_change("num_return_sequences", val, "num_return_sequences_spinbox"))
        self.ui.num_return_sequences_spinbox.valueChanged.connect(lambda val: self.handle_value_change("num_return_sequences", val, "num_return_sequences_slider"))

        # now floats converting to int (1000 / 100 for float)
        self.ui.top_p_spinbox.valueChanged.connect(lambda val: self.handle_value_change("top_p", int(self.ui.top_p_spinbox.value() * 100), "top_p_slider"))
        self.ui.top_p_slider.valueChanged.connect(lambda val: self.handle_value_change("top_p", self.ui.top_p_slider.value() / 100, "top_p_spinbox"))
        self.ui.repetition_penalty_spinbox.valueChanged.connect(lambda val: self.handle_value_change("repetition_penalty", int(self.ui.repetition_penalty_spinbox.value() * 100), "repetition_penalty_slider"))
        self.ui.repetition_penalty_slider.valueChanged.connect(lambda val: self.handle_value_change("repetition_penalty", self.ui.repetition_penalty_slider.value() / 100, "repetition_penalty_spinbox"))
        self.ui.temperature_spinbox.valueChanged.connect(lambda val: self.handle_value_change("temperature", int(self.ui.temperature_spinbox.value() * 100), "temperature_slider"))
        self.ui.temperature_slider.valueChanged.connect(lambda val: self.handle_value_change("temperature", self.ui.temperature_slider.value() / 100, "temperature_spinbox"))
        self.ui.length_penalty_slider.valueChanged.connect(lambda val: self.handle_value_change("length_penalty", self.ui.length_penalty_slider.value() / 100, "length_penalty_spinbox"))
        self.ui.length_penalty_spinbox.valueChanged.connect(lambda val: self.handle_value_change("length_penalty", int(self.ui.length_penalty_spinbox.value() * 100), "length_penalty_slider"))

        # set a random seed in seed text box
        self.ui.seed.setPlainText(str(random.randint(0, 1000000)))

        # on generate_button clicked
        self.ui.generate_button.clicked.connect(self.handle_generate)

        self.ui.actionNew.triggered.connect(self.handle_new)
        self.ui.actionSave.triggered.connect(self.handle_save)
        self.ui.actionLoad.triggered.connect(self.handle_load)
        self.ui.actionQuit.triggered.connect(self.handle_quit)

        # iterate over MODELS dict
        for model_name, model_data in TEXT_MODELS.items():
            self.ui.model_dropdown.addItem(model_name)
        # set default to settings_manager.settings.model_name
        self.ui.model_dropdown.setCurrentText(self.settings_manager.settings.model_name.get())

        self.ui.setWindowTitle("Chat AI v{}".format(VERSION))

    def disable_generate_button(self):
        self.ui.generate_button.setEnabled(False)

    def enable_generate_button(self):
        self.ui.generate_button.setEnabled(True)

    def handle_new(self):
        # reset the form
        self.ui.generated_text.setPlainText("")
        self.ui.seed.setPlainText(str(random.randint(0, 1000000)))
        self.set_form_defaults()

    def handle_quit(self, *args, **kwargs):
        self.ui.close()
        self.parent.show()

    def handle_load(self):
        # display a load dialogue
        filename, _ = QFileDialog.getOpenFileName(
            None, "Load File", "", "JSON files (*.json)"
        )
        if filename:
            # current values
            if filename.lower().endswith(".json"):
                with open(filename, "rb") as f:
                    # load properties
                    properties = json.load(f)
                    self.ui.max_length_spinbox.setValue(properties["max_length"])
                    self.ui.min_length_spinbox.setValue(properties["min_length"])
                    self.ui.num_beams_spinbox.setValue(properties["num_beams"])
                    self.ui.top_k_spinbox.setValue(properties["top_k"])
                    self.ui.no_repeat_ngram_size_spinbox.setValue(properties["no_repeat_ngram_size"])
                    self.ui.num_return_sequences_spinbox.setValue(properties["num_return_sequences"])
                    self.ui.top_p_spinbox.setValue(properties["top_p"])
                    self.ui.temperature_spinbox.setValue(properties["temperature"])
                    self.ui.repetition_penalty_spinbox.setValue(properties["repetition_penalty"])
                    self.ui.length_penalty_spinbox.setValue(properties["length_penalty"])
                    self.ui.seed.setPlainText(properties["seed"])
                    self.ui.generated_text.setPlainText(properties["generated_text"])

    def handle_save(self):
        # display a save dialogue for .txtrunner and .llmrunner files
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "JSON files (*.json)"
        )
        if filename:
            if not filename.lower().endswith(".json"):
                filename += ".json"
            with open(filename, "w") as f:
                # save properties
                properties = self.prep_properties()
                properties["seed"] = self.ui.seed.toPlainText()
                # set prompt and few shot prompt
                # set generated text
                properties["generated_text"] = self.ui.generated_text.toPlainText()
                json.dump(properties, f)

    def prep_properties(self):
        num_beams = self.ui.num_beams_spinbox.value()
        if num_beams == 0:
            num_beams = None
        repetition_penalty = self.ui.repetition_penalty_spinbox.value()
        if repetition_penalty == 0.0:
            repetition_penalty = 0.01
        top_p = self.ui.top_p_spinbox.value()
        top_p_min = 0.01
        if top_p <= top_p_min:
            top_p = top_p_min
        min_length = self.ui.min_length_spinbox.value()
        max_length = self.ui.max_length_spinbox.value()
        if max_length < min_length:
            max_length = min_length
        return {
            "max_length": max_length,
            "min_length": min_length,
            "num_beams": num_beams,
            "temperature": self.ui.temperature_spinbox.value(),
            "top_k": self.ui.top_k_spinbox.value(),
            "top_p": self.ui.top_p_spinbox.value(),
            "repetition_penalty": repetition_penalty,
            "length_penalty": self.ui.length_penalty_spinbox.value(),
            "no_repeat_ngram_size": self.ui.no_repeat_ngram_size_spinbox.value(),
            "num_return_sequences": self.ui.num_return_sequences_spinbox.value(),
            "model": self.ui.model_dropdown.currentText(),
        }


if __name__ == '__main__':
    MainWindow([])
