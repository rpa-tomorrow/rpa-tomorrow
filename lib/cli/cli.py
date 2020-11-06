import plac
import sys
import commands
import logging
from config import load_settings_from_cli
from lib.settings import SETTINGS
from lib.nlp import nlp  # noqa: E402


def setup_logger(level):
    # create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # create formatter
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


@plac.annotations(debug=("Enable debug output", "flag", "d"))
def cli(debug):
    if debug:
        setup_logger(logging.DEBUG)
    else:
        setup_logger(logging.WARNING)

    load_settings_from_cli()
    print("Loading...")
    n = nlp.NLP(SETTINGS["nlp_models"]["basic"], SETTINGS["nlp_models"]["spacy"])
    print("Ready!")

    while True:
        txt = sys.stdin.readline().strip()

        if txt == "":
            continue
        else:
            txtArr = txt.split(" ")
            commands.commands(txtArr, n)


if __name__ == "__main__":
    plac.call(cli)
