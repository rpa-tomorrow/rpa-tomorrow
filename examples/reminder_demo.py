import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.selector.selector import ModuleSelector  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()
n = ModuleSelector()

"""
Directly calls the automation module to run a reminder task.

Not using the NLP module since the time is not correctly parsed atm.
"""
try:
    text = "Remind me in 1 second to eat"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
