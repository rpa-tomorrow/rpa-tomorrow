import yaml
from lib.cli.config import config_user_name, config_email_address, config_email_host

SETTINGS = {}


def load_settings():
    """ Load settings from the config files located in /config"""
    load_user()
    load_local_contacts()


def load_user():
    """ Load user information from the config file
        if there are user settings missing then the user
        is prompted to input these """
    with open("config/user.yaml", "r") as stream:
        SETTINGS["user"] = yaml.safe_load(stream)

    # Flag for checking if there is a need to update the config by writing to a file
    update = False

    if SETTINGS["user"]["name"] == "":
        SETTINGS["user"]["name"] = config_user_name()
        update = True

    email_config = SETTINGS["user"]["email"]
    if email_config["address"] == "":
        email_config["address"] = config_email_address()
        update = True

    if email_config["host"] == "":
        email_config = config_email_host(email_config)
        update = True

    if update:
        update_settings("config/user", SETTINGS["user"])
        print("User config updated")


def load_local_contacts():
    """ Loads the local contact book from the config file """
    with open("config/contacts.yaml", "r") as stream:
        SETTINGS["contacts"] = yaml.safe_load(stream)


def update_settings(file_path: str, data: dict):
    """Writes to a yaml config file"""
    with open(file_path + ".yaml", "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile)
