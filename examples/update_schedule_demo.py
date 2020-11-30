import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.selector.selector import ModuleSelector  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()
n = ModuleSelector()

# Enable the CalDav server before running the following
try:
    text = "Reschedule meeting with John to 21:00"
    response = n.run(text)

    print(response)
except Error as err:
    print(err, file=sys.stdout)
