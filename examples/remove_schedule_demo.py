import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error
from lib.automate import Automate
from lib.nlp import nlp
from datetime import datetime, timedelta
from lib.settings import load_settings

load_settings()
automate = Automate()
n = nlp.NLP("en_rpa_simple", "en_core_web_md")

# Enable the CalDav server before running the following
try:
    when = datetime.now() + timedelta(hours=5.0)  # timestamp at: now + 5 hrs
    text = "unschedule meeting with john"
    print("input:", text)
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
