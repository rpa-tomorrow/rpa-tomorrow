import sys

sys.path.append(".")
sys.path.append("..")

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.automate import Automate  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()
automate = Automate()

# Enable the SMTP server before running the following
try:
    text = "send Hello World! to John"
    response = automate.run("email", text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
