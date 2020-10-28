import sys

from lib import Error
from lib.automate import Automate
from lib.settings import load_settings

load_settings()
automate = Automate()

# Enable the SMTP server before running the following
try:
    module_name = "send"
    to = ["John"]
    body = "Hello World!"
    response = automate.run(module_name, to, None, body)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
