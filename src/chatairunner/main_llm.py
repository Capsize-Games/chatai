import json
import random
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QFileDialog
from aihandler.settings import TEXT_MODELS
from chatairunner.base_window import BaseWindow


class MainWindow(BaseWindow):
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
        self.conversation.properties[value_name] = value

    def initialize_form(self):
        self.set_form_defaults()
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

        # menu bar
        self.ui.actionNew.triggered.connect(self.handle_new)
        self.ui.actionSave.triggered.connect(self.handle_save)
        self.ui.actionLoad.triggered.connect(self.handle_load)
        self.ui.actionQuit.triggered.connect(self.handle_quit)

        # mdoels dropdown
        for model_name, model_data in TEXT_MODELS.items():
            self.ui.model_dropdown.addItem(model_name)

        # set default to settings_manager.settings.model_name
        self.ui.model_dropdown.setCurrentText(self.settings_manager.settings.model_name.get())

        self.ui.setWindowTitle("Chat AI")

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
