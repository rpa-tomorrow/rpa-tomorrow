from lib import Error


class Module:
    verbs = []

    def __init__(self):
        pass

    def run(self, to, when, body, sender):
        raise NotImplementedError("Method not implemented")

    def followup(self, answer):
        raise NotImplementedError("Method not implemented")


class NoSenderError(Error):
    pass