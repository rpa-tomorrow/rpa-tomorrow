import sys

sys.path.append(".")

from lib.settings import (  # noqa: E402
    SETTINGS,
    load_local_contacts,
    load_user,
    update_settings,
    load_nlp_models_config,
)


def load_settings_from_cli():
    """ Load settings from the config files located in /config
    and prompts user if some needed config is missing"""
    load_user_from_cli()
    load_local_contacts()


def load_user_from_cli():
    """Load user information from the config file
    if there are user settings missing then the user
    is prompted to input these"""
    load_user()

    # Flag for checking if there is a need to update the config by writing to a file
    update = False

    if SETTINGS["user"]["name"] is None:
        SETTINGS["user"]["name"] = config_user_name()
        update = True

    email_config = SETTINGS["user"]["email"]
    if email_config["address"] is None:
        email_config["address"] = config_email_address()
        update = True

    if email_config["host"] is None:
        email_config = config_email_host(email_config)
        update = True

    if SETTINGS["user"]["language"] is None:
        SETTINGS["user"]["language"] = config_model_language()
        update = True

    if SETTINGS["user"]["model_version"] is None:
        SETTINGS["user"]["model_version"] = choose_model_version(SETTINGS["user"]["language"])
        update = True

    SETTINGS["user"]["email"] = email_config
    if update:
        update_settings("../config/user", SETTINGS["user"])
        print("User config updated")

    load_nlp_models_config(SETTINGS["user"]["language"], SETTINGS["user"]["model_version"])


def config_user_name() -> str:
    """ Prompt the user about entering a name and return that name """
    print("User not configured.\nPlease enter your name: ")
    name = sys.stdin.readline().strip()

    return name


def config_email_address() -> str:
    """ Prompt the user about entering a email address and return that address """
    print("Email address not configured.\nPlease enter your email: ")
    email = sys.stdin.readline().strip()

    return email


def config_email_host(email_config: dict) -> dict:
    """ Prompt the user about entering email host information and return this information """
    print("Email host not configured.\nPlease enter host: ")
    email_config["host"] = sys.stdin.readline().strip()
    print("Enter Port: ")
    email_config["port"] = int(sys.stdin.readline().strip())

    if email_config["host"] != "localhost":
        print("Enter User Name: ")
        email_config["username"] = sys.stdin.readline().strip()

        print("Enter Password: ")
        email_config["password"] = sys.stdin.readline().strip()

        print("Does the Email service use SSL? (y/n): ")
        email_config["ssl"] = sys.stdin.readline().strip().lower() in [
            "true",
            "y",
            "yes",
        ]

    return email_config


def config_model_language(languages: [str]) -> str:
    """ Prompt the user about choosing language for the NLP models"""
    length = len(languages)
    prompt_msg = "Choose which language to use\n"
    for i in range(length):
        prompt_msg += f"[{i+1}] {languages[i]}\n"
    prompt_msg += f"Please choose one (1-{length})"
    print(prompt_msg)
    awnser = sys.stdin.readline().strip()
    try:
        choice = int(awnser) - 1
        if choice >= 0 and choice < length:
            return languages[choice]
    except ValueError:
        print("Input needs to be a integer")

    return config_model_language(languages)


def choose_model_version(versions: [str]) -> str:
    """ Prompt the user about choosing model version for the NLP models"""
    length = len(versions)
    prompt_msg = "Choose which version to use\n"
    for i in range(length):
        prompt_msg += f"[{i+1}] {versions[i]}\n"
    prompt_msg += f"Please choose one (1-{length})"
    print(prompt_msg)
    awnser = sys.stdin.readline().strip()
    try:
        choice = int(awnser) - 1
        if choice >= 0 and choice < length:
            return versions[choice]
    except ValueError:
        print("Input needs to be a integer")

    return config_model_language(versions)
