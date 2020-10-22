import sys

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp
from lib.settings import SETTINGS, load_settings

load_settings()

automate = Automate()
n = nlp.NLP("en_rpa_simple")

# Enable the SMTP server before running the following
try:
    text = "send an email with the content 'hello world' to substorm@email.com"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
