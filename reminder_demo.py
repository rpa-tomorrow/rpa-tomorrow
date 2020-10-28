import sys
from datetime import datetime, timedelta

from lib import Error
from lib.automate import Automate
from lib.settings import load_settings

load_settings()
automate = Automate()

"""
Directly calls the automation module to run a reminder task.
Not using the NLP module since the time is not correctly parsed atm.
"""
try:
    when = datetime.now() + timedelta(seconds=5.0)  # timestamp at: now + 5s
    body = "This is a test."
    response = automate.run("remind", None, when, body)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
