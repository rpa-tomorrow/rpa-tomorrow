import sys


def config_user_name():
    print("User not configured.\nPlease enter your name: ")
    name = sys.stdin.readline().strip()

    return name


def config_email_address():
    print("Email address not configured.\nPlease enter your email: ")
    email = sys.stdin.readline().strip()

    return email


def config_email_host(email_config):
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
        email_config["ssl"] = sys.stdin.readline().strip().lower() in ["true", "y", "yes"]

    return email_config