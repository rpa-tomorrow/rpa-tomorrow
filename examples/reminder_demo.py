import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error
from lib.nlp import nlp
from lib.settings import load_settings

load_settings()
n = nlp.NLP("en_rpa_simple")

"""
Directly calls the automation module to run a reminder task.

Not using the NLP module since the time is not correctly parsed atm.
"""
try:
    text = "Remind me in 1 second to eat"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
