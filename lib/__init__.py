class Error(Exception):
    pass


class NotImplementedError(Error):
    pass


class TimeIsInPastError(Error):
    """
    Raised when the time that something is supposed to happen has already
    passed.
    """

    def __init__(self, time, message="The specifed time is in the past"):
        self.time = time
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}, time={self.time}"


class OSNotSupportedError(Error):
    """Raised when a feature is not currently supported on the host OS"""

    def __init__(self, os, message="The feature is not supported on the current OS"):
        self.os = os
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}, os={self.os}"
