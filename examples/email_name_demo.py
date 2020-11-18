import sys

sys.path.append(".")
sys.path.append("..")

from lib import Error  # noqa: E402
from lib.selector.selector import ModuleSelector  # noqa: E402
from lib.settings import load_settings  # noqa: E402

load_settings()
n = ModuleSelector("en_rpa_simple", "en_core_web_md")

# Enable the SMTP server before running the following
try:
    text = "send John an email saying Hello there"
    response = n.run(text)
    print(response)

    print("\nIf you have an Erik in your Gmail 'Other contacts', this should work as well::")
    text = "send an email to Erik saying Hello there"
    response = n.run(text)
    print(response)
except Error as err:
    print(err, file=sys.stdout)
