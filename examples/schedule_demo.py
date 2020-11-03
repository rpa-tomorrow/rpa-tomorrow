import sys
sys.path.append(".")
sys.path.append("..")

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.automate import Automate  # noqa: E402
from lib.nlp import nlp  # noqa: E402
from lib.settings import load_settings  # noqa: E402

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
