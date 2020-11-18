import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.selector.selector import ModuleSelector  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()
n = ModuleSelector("en_rpa_simple", "en_core_web_md")

# Enable the CalDav server before running the following
try:
    text = "schedule meeting with john@email.com at 20:00"
    response = n.run(text)

    print(response)
except Error as err:
    print(err, file=sys.stdout)
