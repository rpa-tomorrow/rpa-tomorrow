import sys
from datetime import datetime, timedelta

from lib import Error
from lib.automate import Automate

automate = Automate()

"""
Directly calls the automation module to run a reminder task.

Not using the NLP module since the time is not correctly parsed atm.
"""
try:
    body = "Remind me in 1 second to eat"
    response = automate.run("remind", body, None)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
