import sys

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp
from datetime import datetime, timedelta
from lib.settings import load_settings

load_settings()
automate = Automate()
n = nlp.NLP("en_rpa_simple")

# Enable the CalDav server before running the following
try:
    text = "set meeting with Niklas at 20:00"
    # Have to use automation module directly because the NLP model does not
    # support Schedule yet
    # response = n.run(text)
    when = datetime.now() + timedelta(hours=5.0)  # timestamp at: now + 5 hrs
    # when = datetime.fromisoformat("2020-11-02T15:40:00")
    response = automate.run("unschedule", ["rpa@substorm.com"], when, None)

    print(response)
except Error as err:
    print(err, file=sys.stdout)
