import sys
import commands

def cli():
    while True: 
        txt = sys.stdin.readline().strip().split(' ')

        if len(txt) == 0:
            continue
        else:
            commands.commands(txt)

if __name__ == '__main__':
    cli()