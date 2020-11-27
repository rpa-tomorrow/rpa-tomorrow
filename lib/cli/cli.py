import commands
import logging
import spinner
import warnings
import click

from config import load_settings_from_cli
from lib.selector.selector import ModuleSelector  # noqa: E402


@click.command()
@click.option("--verbose", "-v", "verbose", is_flag=True, help="Enable verbose output")
@click.option("--debug", "-d", "debug", help="Set the debug logging level which will be output")
def cli(debug, verbose):
    click.clear()
    click.secho("RPA Tomorrow - managing tasks from natural text", fg="green", bold=True)

    spin = spinner.Spinner()
    load_prerequisites(spin, debug, verbose)
    module_selector = load_selector(spin)

    click.secho("\nType any task(s) and the robot will start working on it", bold=True)
    click.secho("(or type 'help' to display all options):", bold=True)
    try:
        while True:
            txt = click.prompt("", prompt_suffix="> ").strip()

            if txt == "":
                continue
            else:
                txt_arr = txt.split(" ")
                commands.commands(txt_arr, module_selector)
    except Exception:
        click.secho("\nGood bye!", fg="green", bold=True)
        click.clear()


def load_prerequisites(spinner, debug, verbose):
    click.secho("· Loading settings... ", bold=True)
    with spinner:
        load_settings_from_cli()
    print("", end="\x1b[1K\r")
    click.secho("---> DONE", fg="green", bold=True)

    click.secho("· Waking up the robot... ", bold=True)
    with spinner:
        setup_logger(debug, verbose)
    print("", end="\x1b[1K\r")
    click.secho("---> DONE", fg="green", bold=True)


def load_selector(spinner):
    click.secho("· Loading models... ", bold=True)
    with spinner:
        module_selector = ModuleSelector()
    print("", end="\x1b[1K\r")
    click.secho("---> DONE", fg="green", bold=True)
    click.secho("· Natural language processing ready!", bold=True)

    return module_selector


def setup_logger(debug, verbose):
    try:
        if debug is not None and verbose:
            click.echo("[WARNING]: Verbose and debug output are both enabled. Ignoring verbose flag!", err=True)

        if debug is not None:
            init_logger(debug)
        elif verbose:
            init_logger(logging.INFO)
        else:
            init_logger(logging.WARNING)
    except ValueError:
        init_logger(logging.WARNING)
        click.echo("[WARNING]: Could not parse debug flag. Using default log settings.", err=True)


def init_logger(level):
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


def supress_warnings():
    warnings.filterwarnings("ignore", message=r"\[W008\]", category=UserWarning)


if __name__ == "__main__":
    supress_warnings()
    cli()
