"""
The reminder automation module
"""
from datetime import datetime
import sys
from threading import Timer
from subprocess import run

from lib import OSNotSupportedError, TimeIsInPastError
from lib.automate.modules import Module


class Reminder(Module):
    """
    The module of a reminder
    """

    verbs = ["remind", "reminder", "notify"]
    supported_os = ["linux"]

    def __init__(self):
        super(Reminder, self).__init__()

    def notify(self, os, body):
        """
        Creates a notification on the users machine. Currently supports Linux
        (using notify-send).

        :param os: The host machines os
        :type os: string
        :param body: The text shown in the notification
        :type body: string
        """

        if os == "linux":
            run(["/usr/bin/notify-send", "Reminder", body])
        elif os == "win32":
            # TODO: Add windows call here
            pass

    def run(self, _to, when, body, _sender):
        """
        Schedules a reminder which will show up in the users system at the
        specified time with the specified information. Raises an error if the
        host OS is not supported or if the time at which to schedule the
        reminder is in the past.

        :param _to: Unused
        :param _sender: Unused
        :param when: The time to schedule the notification for
        :type when: datetime.datetime
        :param body: The text to be shown in the notification
        :type body: text
        """
        when_delta = (
            when - datetime.now()
        ).total_seconds()  # convert to difference in seconds
        if when_delta < 0.0:
            raise TimeIsInPastError(
                when.strftime("%Y-%m-%d %H:%M:%S"),
                "The specified time of the reminder is in the past and can not"
                + " be scheduled",
            )

        if sys.platform not in self.supported_os:
            raise OSNotSupportedError(
                sys.platform,
                "Not able to create a reminder in the OS you are using because"
                + " it is currently not supported by the program",
            )

        t = Timer(when_delta, lambda: self.notify(sys.platform, body))
        t.start()
        return (
            f"Reminder scheduled for {when.strftime('%Y-%m-%d %H:%M:%S')}",
            None,
        )
