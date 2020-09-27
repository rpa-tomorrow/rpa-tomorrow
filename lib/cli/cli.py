import sys
import commands


def cli():
    while True:
        txt = sys.stdin.readline().strip()

        if txt == "":
            continue
        else:
            txtArr = txt.split(" ")
            commands.commands(txtArr)


if __name__ == "__main__":
    cli()

