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


@plac.annotations(
    debug=("Set the debug logging level which will be output", "option", "d", str),
    verbose=("Enable verbose output", "flag", "v"),
)
def cli(debug, verbose):
    try:
        if debug is not None and verbose:
            print("WARNING: Verbose and debug output are both enabled. Ignoring verbose flag!")

        if debug is not None:
            setup_logger(debug)
        elif verbose:
            setup_logger(logging.INFO)
        else:
            setup_logger(logging.WARNING)
    except ValueError:
        setup_logger(logging.WARNING)
        print("WARNING: Could not parse debug flag. Using default log settings.")

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
