import sys

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp
from datetime import datetime, timedelta

automate = Automate()
n = nlp.NLP("en_rpa_simple")

# Enable the CalDav server before running the following
try:
    text = "set meeting with Niklas at 20:00"
    # Have to use automation module directly because the NLP model does not
    # support Schedule yet
    # response = n.run(text)
    when = datetime.utcnow() + timedelta(hours=5.0)  # timestamp at: now + 5 hrs
    response = automate.run("schedule", ["rpa@substorm.com"], when, "Schedule demo", "Niklas")

    print(response)
except Error as err:
    print(err, file=sys.stdout)
