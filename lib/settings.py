import os
import yaml

SETTINGS = {}


def load_user():
    """Load user information from the config file"""
    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("../config/user.yaml", "r") as stream:
        SETTINGS["user"] = yaml.safe_load(stream)
    os.chdir(old_dir)


def load_local_contacts():
    """ Loads the local contact book from the config file """
    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("../config/contacts.yaml", "r") as stream:
        SETTINGS["contacts"] = yaml.safe_load(stream)
    os.chdir(old_dir)


def update_settings(file_path: str, data: dict):
    """Writes to a yaml config file"""
    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(file_path + ".yaml", "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile)
    os.chdir(old_dir)


def get_model_languages():
    """Reads a list of languages from the nlp_model config file"""
    languages = []

    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("../config/nlp_models.yaml", "r") as stream:
        languages = list(yaml.safe_load(stream).keys())
    os.chdir(old_dir)

    return languages


def load_nlp_models_config(language):
    """Loads the language specific nlp model names from the config file"""
    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("../config/nlp_models.yaml", "r") as stream:
        SETTINGS["nlp_models"] = yaml.safe_load(stream)[language]
    os.chdir(old_dir)
