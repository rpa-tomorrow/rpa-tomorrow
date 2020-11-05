import sys


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
    except:
        print("Input needs to be a integer")

    return config_model_language(languages)

