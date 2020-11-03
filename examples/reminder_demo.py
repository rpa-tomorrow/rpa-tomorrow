import sys
sys.path.append(".")
sys.path.append("..")

from lib import Error
from lib.automate import Automate
from lib.settings import load_settings

load_settings()
automate = Automate()

"""
Directly calls the automation module to run a reminder task.

Not using the NLP module since the time is not correctly parsed atm.
"""
try:
    body = "Remind me in 1 second to eat"
    response = automate.run("Remind", body)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
