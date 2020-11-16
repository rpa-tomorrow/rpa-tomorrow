import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.automate import Automate  # noqa: E402
from lib.nlp import nlp  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()

automate = Automate()
n = nlp.NLP("en_rpa_simple", "en_core_web_md")

# Enable the SMTP server before running the following
try:
    text = "reschedule meeting with John"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
