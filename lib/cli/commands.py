"""
The commands available in the CLI
"""

import sys
import os
from config import config_model_language

sys.path.append(".")

from lib.nlp.model_installer import Model_Installer  # noqa: E402


def commands(arr, nlp):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    elif arr[0] == "language" or arr[0] == "lang":
        config_model_language()
    elif arr[0] == "install":
        model_installer = Model_Installer()
        model_installer.install("english")
    else:
        listToStr = " ".join(map(str, arr))
        try:
            response = nlp.run(listToStr)
            print(response + "\n")
        except Exception as e:
            print("Failed to execute action.\n", e, file=sys.stderr)


def prompt():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())
