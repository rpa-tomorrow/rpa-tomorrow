import sys

from lib import Error
from lib.automate import Automate

automate = Automate()
try:
    response = automate.run(
        "skikko",
        ["aron@antarkt.is"],
        None,
        "test\n\ndet är ett test",
        "Aron Widforss"
    )
    print(response)
except Error as err:
    print(err, file=sys.stdout)
