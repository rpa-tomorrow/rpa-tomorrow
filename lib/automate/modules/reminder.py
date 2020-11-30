"""
The reminder automation module
"""
import sys
import lib.utils.tools.time_convert as tc
import spacy
import logging

from datetime import datetime, timedelta
from threading import Timer
from subprocess import run
from lib import OSNotSupportedError, TimeIsInPastError
from lib.automate.modules import Module


# Module logger
log = logging.getLogger(__name__)


class Reminder(Module):
    """
    The module of a reminder
    """

    verbs = ["remind", "reminder", "notify"]
    supported_os = ["linux", "win32"]

    def __init__(self, model_pool):
        super(Reminder, self).__init__(model_pool)
        self.nlp_model = None

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
            from win10toast import ToastNotifier

            toaster = ToastNotifier()
            toaster.show_toast("Reminder", body, icon_path=None, duration=10)

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["reminder"])
        to, when, body = self.nlp(text)
        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, _to, when, body, _sender):
        """
        Schedules a reminder which will show up in the users system at the
        specified time with the specified information. Raises an error if the
        host OS is not supported or if the time at which to schedule the
        reminder is in the past.

        :param _to: Unused
        :param when: The time to schedule the notification for
        :type when: datetime.datetime
        :param body: The text to be shown in the notification
        :type body: text
        :param _sender: Unused
        """
        self.to = _to
        self.when = when
        self.body = body
        self.sender = _sender
        self.followup_type = None

        if not isinstance(when, datetime):
            self.followup_type = "when"
            return "\nCould not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format"
        elif not body:
            self.followup_type = "body"
            return "\nFound no message body. What message should be sent"

        when_delta = (when - datetime.now()).total_seconds()  # convert to difference in seconds
        if when_delta < 0.0:
            raise TimeIsInPastError(
                when.strftime("%Y-%m-%d %H:%M:%S"),
                "The specified time of the reminder is in the past and can not be scheduled",
            )

        if sys.platform not in self.supported_os:
            raise OSNotSupportedError(
                sys.platform,
                "Not able to create a reminder in the OS you are using because"
                + " it is currently not supported by the program",
            )

        t = Timer(when_delta, lambda: self.notify(sys.platform, body))
        self.timer = t

    def execute(self):
        self.timer.start()
        return f"\nReminder scheduled for {self.when.strftime('%Y-%m-%d %H:%M:%S')}"

    def followup(self, answer: str) -> (str, str):
        """
        Follow up method after the module have had to ask a question to clarify some parameter, or just
        want to check that it interpreted everything correctly.
        """
        if self.followup_type == "when":
            try:
                when = datetime.fromisoformat(answer)
            except Exception:
                when = None
            return self.prepare_processed(self.to, when, self.body, self.sender)

        elif self.followup_type == "body":
            return self.prepare_processed(self.to, self.when, answer, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")

    def nlp(self, text):
        """
        Lets the reminder model work on the given text.
        """
        doc = self.nlp_model(text)

        to = []
        when = []
        body = []

        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "WHEN":
                when.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)

        time = datetime.now()
        if len(when) == 0:
            time = time + timedelta(seconds=5)
        else:
            time = tc.parse_time(when)

        _body = " ".join(body)

        return (to, time, _body)
