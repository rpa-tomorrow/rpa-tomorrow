from fuzzywuzzy import process as fuzzy

from lib.automate.modules import Module
from lib.settings import SETTINGS

import caldav


class Schedule(Module):
    verbs = ["book", "schedule", "meeting", "set"]

    def __init__(self):
        super(Schedule, self).__init__()

    def run(self, to, when, body, sender):
        url = "http://localhost:5232/"
        client = caldav.DAVClient(url=url,
                                  username="test",
                                  password="test")
        my_principal = client.principal()

        my_new_calendar = my_principal.make_calendar(name="Test calendar")

        my_new_calendar.save_event("""BEGIN:VCALENDAR
        VERSION:2.0
        PRODID:-//Example Corp.//CalDAV Client//EN
        BEGIN:VEVENT
        UID:20200516T060000Z-123401@example.com
        DTSTAMP:20200516T060000Z
        DTSTART:20200517T060000Z
        DTEND:20200517T230000Z
        RRULE:FREQ=YEARLY
        SUMMARY:Do the needful
        END:VEVENT
        END:VCALENDAR
        """)

        return "", None
