import sys
sys.path.append(".")
sys.path.append("..")

from lib import Error
from lib.automate import Automate
from lib.settings import load_settings

load_settings()
automate = Automate()

# Enable the SMTP server before running the following
try:
    text = "send Hello World! to John"
    response = automate.run("email", text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
