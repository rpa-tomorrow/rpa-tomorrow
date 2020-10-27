from __future__ import print_function
from lib.automate.modules import Module, NoSenderError
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the files *.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class Schedule(Module):
    verbs = ["book", "schedule", "meeting"]

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
            return (
                None,
                "Could not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format",
            )

        if not body:
            self.followup_type = "body"
            return None, "Found no event summary. What is the event about"

        settings = sender["email"]
        username = settings.get("username")

        summary = self.body

        # Parse Time
        duration = 20  # TODO: Parse from input
        start_time = self.when.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = (self.when + timedelta(minutes=duration)).isoformat() + "Z"  # 'Z' indicates UTC time

        # Define the event
        event = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
            "attendees": self.parse_attendees(settings["address"], self.to),
        }
        self.event = event

        # Get or create user credentials
        creds = self.credentials(username)

        # Create Event using Google calendar API
        service = build("calendar", "v3", credentials=creds)
        self.service = service

        # Check if we are busy
        to_items = [{"id": email} for email in to]
        freebusy = (
            service.freebusy()
            .query(body={"items": [{"id": "primary"}] + to_items, "timeMin": start_time, "timeMax": end_time})
            .execute()
        )
        to_busy = list(map(lambda x: x[0], filter(lambda x: x[1]["busy"], list(freebusy["calendars"].items())[1:])))

        other = f"{', '.join(to_busy[:-1])} and {to_busy[-1]}" if len(to_busy) > 1 else "".join(to_busy)
        if len(freebusy["calendars"]["primary"]["busy"]) and len(to_busy):
            self.followup_type = "both_busy"
            return None, f"You as well as {other} seem to be busy. Do you want to book the meeting anyway? [Y/n]"
        elif len(freebusy["calendars"]["primary"]["busy"]):
            self.followup_type = "self_busy"
            return None, "You seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"
        elif len(to_busy):
            self.followup_type = "to_busy"
            return None, f"{other} seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"

        event = service.events().insert(calendarId="primary", body=event).execute()

        return "Event created, see link: %s" % (event.get("htmlLink")), None

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
        elif self.followup_type == "body":
            return self.run(self.to, self.when, answer, self.sender)
        elif self.followup_type == "self_busy" or self.followup_type == "both_busy" or self.followup_type == "to_busy":
            if answer == "" or answer.lower() == "y" or answer.lower() == "yes":
                event = self.service.events().insert(calendarId="primary", body=self.event).execute()
                return "Event created, see link: %s" % (event.get("htmlLink")), None
            elif answer.lower() == "n" or answer.lower() == "no":
                return "No event created", None
            else:
                return self.run(self.to, self.when, self.body, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")

    def credentials(self, username):
        """
        The file token.pickle stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        creds = None
        pickle_filename = f"{username}_token.pickle"

        if os.path.exists(pickle_filename):
            with open(pickle_filename, "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_filename, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def parse_attendees(self, sender_address, to):
        """
        Parses the attendees of the event and creates a list of dicts containing
        there emails.
        """
        attendees = []
        attendees.append({"email": sender_address})
        for attende in to:
            attendees.append({"email": attende})

        return attendees
