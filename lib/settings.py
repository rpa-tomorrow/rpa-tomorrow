import yaml
from lib.cli.config import config_user_name

SETTINGS = {}


def load_settings():
    load_user()

    load_local_contacts()


def load_user():
    with open("config/user.yaml", "r") as stream:
        SETTINGS["user"] = yaml.safe_load(stream)

    if SETTINGS["user"]["name"] == "":
        SETTINGS["user"]["name"] = config_user_name()
        update_settings("config/user", SETTINGS["user"])


def load_local_contacts():
    with open("config/contacts.yaml", "r") as stream:
        SETTINGS["contacts"] = yaml.safe_load(stream)


def update_settings(file_path, data):
    with open(file_path + ".yaml", "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile)
