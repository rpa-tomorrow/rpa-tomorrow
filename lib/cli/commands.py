"""
The commands available in the CLI
"""

import sys
import os

sys.path.append(".")

from lib.settings import set_language  # noqa: E402


def commands(arr, nlp):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    elif arr[0] == "language" or arr[0] == "lang":
        set_language()
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
