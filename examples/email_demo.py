import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.automate import Automate  # noqa: E402
from lib.selector.selector import ModuleSelector  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()

automate = Automate()
n = ModuleSelector()

# Enable the SMTP server before running the following
try:
    text = "send an email to test@example.com with the content hello world"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
