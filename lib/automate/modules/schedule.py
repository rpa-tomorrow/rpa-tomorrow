from datetime import datetime
from datetime import timedelta

from fuzzywuzzy import process as fuzzy

from lib.automate.modules import Module, NoSenderError
from lib.settings import SETTINGS

import caldav

time_format = "%Y%m%dT%H%M%SZ"


class Schedule(Module):
    verbs = ["book", "schedule", "meeting", "set"]

    def __init__(self):
        super(Schedule, self).__init__()

    def run(self, to, when, body, sender):
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None

        if not sender:
            raise NoSenderError("No sender found!")

        if not isinstance(when, datetime):
            self.followup_type = "when"
            return None, ("Could not parse date to schedule to.\n"
                          "Please enter date in YYYYMMDD HH:MM format")

        user, _ = fuzzy.extractOne(sender, SETTINGS["users"].keys())
        settings = SETTINGS["users"][user]["email"]
        username = settings.get("username")
        password = settings.get("password")
        url = f'http://{settings["host"]}:{settings["port"]}/'

        duration = 20  # TODO: Parse from body.
        summary = "rpc-tomorrow meeting"  # TODO: Parse from body.

        client = caldav.DAVClient(url=url, username=username, password=password)
        my_principal = client.principal()

        my_new_calendar = my_principal.make_calendar(name="Test calendar")

        start = when.strftime(time_format)
        end = (when + timedelta(minutes=duration)).strftime(time_format)
        now = datetime.now().strftime(time_format)
        my_event = my_new_calendar.save_event(
            f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//rpa-tomorrow.//CalDAV Client//EN
BEGIN:VEVENT
UID:{now}-{settings["address"]}
DTSTART:{start}
DTEND:{end}
SUMMARY:{summary}
END:VEVENT
END:VCALENDAR
"""
        )

        return my_event.data, None

    def followup(self, answer):
        """
        Follow up method after the module have had to ask a question to clarify some parameter, or just
        want to check that it interpreted everything correctly.
        """
        if self.followup_type == "when":
            try:
                when = datetime.fromisoformat(answer)
            except Exception:
                when = None
            return self.run(self.to, when, self.body, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")
