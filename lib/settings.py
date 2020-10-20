import yaml
from lib.cli.config import config_user_name, config_email_address, config_email_host

SETTINGS = {}


def load_settings():
    load_user()

    load_local_contacts()


def load_user():
    with open("config/user.yaml", "r") as stream:
        SETTINGS["user"] = yaml.safe_load(stream)

    update = False

    if SETTINGS["user"]["name"] == "":
        SETTINGS["user"]["name"] = config_user_name()
        update = True

    email = SETTINGS["user"]["email"]
    if email["address"] == "":
        email["address"] = config_email_address()
        update = True

    if email["host"] == "":
        email = config_email_host(email)
        update = True

    if update:
        update_settings("config/user", SETTINGS["user"])
        print("User config updated")


def load_local_contacts():
    with open("config/contacts.yaml", "r") as stream:
        SETTINGS["contacts"] = yaml.safe_load(stream)


def update_settings(file_path, data):
    with open(file_path + ".yaml", "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile)
