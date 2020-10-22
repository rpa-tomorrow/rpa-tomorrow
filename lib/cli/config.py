import sys


def config_user_name():
    print("User not configured.\nPlease enter your name: ")
    name = sys.stdin.readline().strip()

    return name


def config_email():
    pass
