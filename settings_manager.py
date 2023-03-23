import os
import pickle
from qtvar import BooleanVar, StringVar, IntVar, FloatVar, DoubleVar


class PropertyBase:
    """
    A base class used for collections of properties that are stored in the database.
    This is an interface into the database with a tkinter var representation of
    the columns within the database. The TkVarMapperBase class is used to map
    the tkinter variable to the database column and update the database when
    the tkinter variable is changed.
    """
    settings = None
    def __init__(self, app):
        self.app = app
        self.mapped = {}

    def initialize(self):
        """
        Implement this class and initialize all tkinter variables within in.
        :return:
        """
        pass

    def read(self):
        """
        Implement this class - return the items from the database.
        :return:
        """
        pass


class Settings(PropertyBase):
    def reset_settings_to_default(self):
        self.initialize()

    def initialize(self):
        self.model_name = StringVar(self.app, "flan-t5-xl")



class SettingsManager:
    _instance = None
    app = None
    settings = None

    def __new__(cls, app=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__(app=app)
        cls.app = app
        return cls._instance

    def __init__(self, app=None):
        # if not app:
        #     raise Exception("SettingsManager must be initialized with an app")
        self.settings = Settings(app=self)
        self.settings.initialize()
        try:
            self.load_settings()
        except Exception as e:
            self.save_settings()

    def save_settings(self):
        HOME = os.path.expanduser("~")
        f = open(os.path.join(HOME, "airunner-llm.settings"), "wb")
        # create dict of all settings
        settings = {}
        for key, value in self.settings.__dict__.items():
            if isinstance(value, BooleanVar):
                settings[key] = value.get()
            elif isinstance(value, StringVar):
                settings[key] = value.get()
            elif isinstance(value, IntVar):
                settings[key] = value.get()
            elif isinstance(value, FloatVar):
                settings[key] = value.get()
            elif isinstance(value, DoubleVar):
                settings[key] = value.get()
        pickle.dump(settings, f)

    def load_settings(self):
        HOME = os.path.expanduser("~")
        f = open(os.path.join(HOME, "airunner-llm.settings"), "rb")
        settings = pickle.load(f)
        for key, value in self.settings.__dict__.items():
            if isinstance(value, BooleanVar):
                value.set(settings[key])
            elif isinstance(value, StringVar):
                value.set(settings[key])
            elif isinstance(value, IntVar):
                value.set(settings[key])
            elif isinstance(value, FloatVar):
                value.set(settings[key])
            elif isinstance(value, DoubleVar):
                value.set(settings[key])
