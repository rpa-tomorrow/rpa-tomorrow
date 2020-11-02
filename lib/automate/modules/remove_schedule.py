from __future__ import print_function
from lib.automate.modules import Module, NoSenderError
from datetime import datetime, timedelta, date
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

        # Parse Time
        time = self.when.isoformat()

        # Get or create user credentials
        settings = sender["email"]
        username = settings.get("username")
        creds = self.credentials(username)

        service = build("calendar", "v3", credentials=creds)
        self.service = service

        # try to fetch the event by the summary
        if body:
            self.get_event_by_summary(body)

        # if no event could be found using the summary try to do it with the user inputed time
        if (not self.event) and time:
            self.get_event_by_timestamp(time)

        if self.event:
            start_time = self.event["start"]["dateTime"]
            self.followup_type = "self_busy"
            return (
                None,
                f"You have the event '{self.event['summary']}' scheduled at {start_time}. Do you want to remove it? [Y/n]",
            )
        else:
            return

    def followup(self, answer):
        """ """
        if self.followup_type == "self_busy":
            if answer.lower() in ["y", "yes"]:
                self.service.events().delete(calendarId="primary", eventId=self.event["id"]).execute()
                return f"'{self.event['summary']}' was removed from your calendar", None
            else:
                return "Event not removed", None
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

    def get_event_by_timestamp(self, time):
        """ 
        takes a ISO formated time and fetches an event from the calendar where the given time is between 
        the start and end time of the event, the method only looks for events happening in the future

        NOTE: as of now this does not handle multiple events occuring at the same time 
        """
        now = datetime.now()
        time = datetime.fromisoformat(time).astimezone(now.tzinfo)
        events = self.service.events().list(calendarId="primary", timeMin=(now.isoformat() + "Z")).execute()["items"]

        for e in events:
            event_start = next(v for k, v in e["start"].items() if "date" in k)
            event_start = datetime.fromisoformat(event_start).astimezone(now.tzinfo)

            event_end = next(v for k, v in e["end"].items() if "date" in k)
            event_end = datetime.fromisoformat(event_end).astimezone(now.tzinfo)

            # check if the given time is between the start and end of an event
            if time >= event_start and time <= event_end:
                self.event = e
                break

        if self.event == None:
            raise NoEventFoundError("Could not find anything scheduled at the given time")

    def get_event_by_summary(self, summary):
        """ 
        try to find a event based on the event summary
        the method only looks for events in the future
        """
        now = datetime.now()
        events = self.service.events().list(calendarId="primary", timeMin=(now.isoformat() + "Z")).execute()["items"]
        event = fuzzy.extractOne(summary, events, score_cutoff=50)
        if event:
            self.event = event[0]


class NoEventFoundError(Error):
    pass
