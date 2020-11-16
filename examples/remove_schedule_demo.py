import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.automate import Automate  # noqa: E402
from lib.nlp import nlp  # noqa: E402
from datetime import datetime, timedelta  # noqa: E402
from lib.settings import load_settings  # noqa: E402

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
