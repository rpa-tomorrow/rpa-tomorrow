import sys
import commands
from lib.settings import load_settings


def cli():

    load_settings()

    while True:
        txt = sys.stdin.readline().strip()

        if txt == "":
            continue
        else:
            txtArr = txt.split(" ")
            commands.commands(txtArr)


if __name__ == "__main__":
    cli()
