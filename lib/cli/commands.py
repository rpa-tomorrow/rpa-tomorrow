"""
The commands available in the CLI
"""

import sys
import os

sys.path.append(".")

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp

def commands(arr):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    else:
        listToStr = ' '.join(map(str, arr)) 
        n = nlp.NLP()
        n.run(listToStr)

def prompt():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())
