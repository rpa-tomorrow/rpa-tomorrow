"""
The commands available in the CLI
"""

import sys
import os

sys.path.append(".")

from lib import Error
from lib.automate import Automate


def commands(arr):
    """
    Commands supported by the CLI
    """
    if arr[0] == "send" or arr[0] == "s":
        # TODO: send arr[1] to automation
        print("text = ", arr[1:])
        arr.clear()
    elif arr[0] == "exit" or arr[0] == "e":
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        prompt()
    else:
        # Try to let the automation decide what module to invoke depending on
        # the first word the user entered
        automate = Automate()
        try:
            response = automate.run(
                arr[0],
                ["substorm@email.com"],
                None,
                "Hello,\nThis message was sent automatically",
                "John Doe",
            )
            print(response)
        except Error as err:
            print(err)


def prompt():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())
