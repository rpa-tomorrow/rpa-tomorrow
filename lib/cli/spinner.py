import sys
import time
import threading


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in "|/-\\":
                yield cursor

    def __init__(self, delay=None):
        self.custom_message = ""
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        print(self.custom_message)
        while self.busy:
            sys.stdout.write("---" + next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write("\b")
            sys.stdout.flush()
        print("\n")

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False

    def setMessage(self, message):
        self.custom_message = message
