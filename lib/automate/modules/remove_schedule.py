from __future__ import print_function
from lib.automate.modules import Module, NoSenderError
from datetime import datetime, timedelta
from lib import Error
from fuzzywuzzy import process as fuzzy
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


class RemoveSchedule(Module):
    verbs = ["unschedule", "remove"]

    def __init__(self):
        super(RemoveSchedule, self).__init__()

    def run(self, to, when, body, sender):
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None
        self.event = None

        if not isinstance(when, datetime):
            self.followup_type = "when"
            return (
                None,
                "Could not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format",
            )

        # Parse Time
        duration = 20  # TODO: Parse from input
        start_time = self.when.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = (self.when + timedelta(minutes=duration)).isoformat() + "Z"  # 'Z' indicates UTC time

        # Get or create user credentials
        settings = sender["email"]
        username = settings.get("username")
        creds = self.credentials(username)

        service = build("calendar", "v3", credentials=creds)
        self.service = service

        if body:
            self.get_event_by_summary(body)
        elif start_time:
            self.get_event_by_timestamp(start_time, end_time)

        print(self.event)

        start_time = self.event["start"]["dateTime"]
        self.followup_type = "self_busy"
        return (
            None,
            f"You have the event '{self.event['summary']}' scheduled at {start_time}. Do you want to remove it? [Y/n]",
        )

    def followup(self, answer):
        """ """
        if self.followup_type == "self_busy":
            self.service.events().delete(calendarId="primary", eventId=self.event["id"]).execute()
            return f"'{self.event['summary']}' was removed from your calendar", None
        else:
            raise NotImplementedError("")

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

    def get_event_by_timestamp(self, start_time, end_time):
        # Check if we are busy
        freebusy = (
            self.service.freebusy()
            .query(body={"items": [{"id": "primary"}], "timeMin": start_time, "timeMax": end_time})
            .execute()
        )

        if len(freebusy["calendars"]["primary"]["busy"]):
            self.followup_type = "self_busy"
            start_time = freebusy["calendars"]["primary"]["busy"][0]["start"]
            end_time = freebusy["calendars"]["primary"]["busy"][0]["end"]

            self.event = (
                self.service.events()
                .list(calendarId="primary", timeMin=start_time, timeMax=end_time)
                .execute()["items"][0]
            )
        else:
            raise NoEventFoundError("Could not find anything scheduled at the given time")

    def get_event_by_summary(self, summary):
        events = self.service.events().list(calendarId="primary").execute()["items"]

        self.event = fuzzy.extractOne(summary, events)[0]


class NoEventFoundError(Error):
    pass
