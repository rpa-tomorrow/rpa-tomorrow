import sys

from lib import Error
from lib.automate import Automate

automate = Automate()

# Enable the SMTP server before running the following
try:
    text = "send Hello World! to John"
    sender = "John Doe"
    response = automate.run(module_name, text, sender)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
