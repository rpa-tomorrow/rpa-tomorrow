import plac
import sys
import commands
import logging
import spinner

from config import load_settings_from_cli
from lib.selector.selector import ModuleSelector  # noqa: E402


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

    spin = spinner.Spinner()
    spin.set_message("Loading settings and nlp models...")
    with spin:
        load_settings_from_cli()
        n = ModuleSelector()
        print("\nNatural language processing ready!")

    while True:
        txt = sys.stdin.readline().strip()

        if txt == "":
            continue
        else:
            txt_arr = txt.split(" ")
            commands.commands(txt_arr, n)


if __name__ == "__main__":
    plac.call(cli)
