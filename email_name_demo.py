import sys

from lib import Error
from lib.automate import Automate

automate = Automate()

# Enable the SMTP server before running the following
try:
    module_name = "send"
    to = ["John"]
    body = "Hello World!"
    sender = "John Doe"
    response = automate.run(module_name, to, None, body, sender)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
