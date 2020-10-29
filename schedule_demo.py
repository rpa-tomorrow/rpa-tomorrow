import sys

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp
from lib.settings import load_settings

load_settings()
automate = Automate()
n = nlp.NLP("en_rpa_simple")

# Enable the CalDav server before running the following
try:
    text = "schedule meeting with Niklas at 20:00"
    response = n.run(text)

    print(response)
except Error as err:
    print(err, file=sys.stdout)
