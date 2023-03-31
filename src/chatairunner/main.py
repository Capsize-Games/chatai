from aihandler.settings import LOG_LEVEL
import logging
logging.getLogger('h5py._conv').setLevel(LOG_LEVEL)
logging.getLogger('tensorflow').setLevel(LOG_LEVEL)
import os
from PyQt6 import uic
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QApplication
from aihandler.pyqt_offline_client import OfflineClient
from chatairunner.chatbot import ChatbotWindow
from chatairunner.main_llm import MainWindow
from aihandler.qtvar import TQDMVar, MessageHandlerVar, ErrorHandlerVar


class Launcher(QApplication):
    """
    This is the home window application for the LLMRunner which launches either the chatbot or the text generator.
    """
    def center(self):
        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        frameGeometry = self.ui.frameGeometry()
        frameGeometry.moveCenter(availableGeometry.center())
        self.ui.move(frameGeometry.topLeft())

    def load_template(self):
        self.ui = uic.loadUi("pyqt/home_window.ui")
        self.ui.chatbot_button.clicked.connect(lambda _val, client=self.client: self.launch_chatbot(client))
        self.ui.textedit_button.clicked.connect(lambda _val, client=self.client: self.launch_textedit(client))
        self.ui.actionQuit.triggered.connect(self.quit)
        self.center()
        self.ui.show()

    def quit(self):
        self.ui.close()
        self.exit()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # silent h5py._conv logging
        uic.properties.logger.setLevel(LOG_LEVEL)
        uic.uiparser.logger.setLevel(LOG_LEVEL)
        self.tqdm_var = TQDMVar()
        self.message_var = MessageHandlerVar()
        self.error_var = ErrorHandlerVar()
        self.client = OfflineClient(
            app=self,
            tqdm_var=self.tqdm_var,
            message_var=self.message_var,
            error_var=self.error_var,
            log_level=LOG_LEVEL
        )
        self.load_template()
        self.exec()

    def launch_chatbot(self, client):
        self.ui.close()
        print("launch chatbotwindow")
        ChatbotWindow(parent=self, client=client)

    def show(self):
        self.ui.show()

    def launch_textedit(self, client):
        self.ui.close()
        MainWindow(parent=self, client=client)


if __name__ == '__main__':
    Launcher([])

