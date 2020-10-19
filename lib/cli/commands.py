"""
The commands available in the CLI
"""

import sys
import os

sys.path.append(".")

from lib.nlp import nlp  # noqa: E402

MODEL_NAME = "en_rpa_simple"


def commands(arr):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    else:
        listToStr = " ".join(map(str, arr))
        n = nlp.NLP(MODEL_NAME)
        try:
            response = n.run(listToStr)
            print(response + "\n")
        except Exception:
            print("Failed to execute action.\n", file=sys.stderr)


def prompt():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())
