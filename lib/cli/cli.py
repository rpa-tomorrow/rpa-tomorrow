import sys
import commands
from lib.settings import load_settings

from lib.nlp import nlp  # noqa: E402

MODEL_NAME = "en_rpa_simple"


def cli():
    load_settings()
    print("Loading...")
    n = nlp.NLP(MODEL_NAME)
    print("Ready!")

    while True:
        txt = sys.stdin.readline().strip()

        if txt == "":
            continue
        else:
            txtArr = txt.split(" ")
            commands.commands(txtArr, n)


if __name__ == "__main__":
    cli()
