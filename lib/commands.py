import sys

def commands(arr):
    if arr[0] == "send" or arr[0] == "s" :
        # TODO: send arr[1] to automation
        print("text = ", arr[1:])
        arr.clear()

    elif arr[0] == "exit" or arr[0] == "e":
        sys.exit()

    elif arr[0] == "help" or arr[0] == "h":
        prompt()

def prompt(): 
    f = open("helpPrompt.txt", "r")
    print(f.read()) 