from __future__ import print_function
import datetime
from datetime import timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

from fuzzywuzzy import process as fuzzy

from lib.automate.modules import Module, NoSenderError
from lib.settings import SETTINGS

class Schedule(Module):
    verbs = ["book", "schedule", "meeting", "set"]

    def __init__(self):
        super(Schedule, self).__init__()


    def credentials(self, username):
        """
        The file token.pickle stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        creds = None
        pickle_filename = f'{username}_token.pickle'

        if os.path.exists(pickle_filename):
            with open(pickle_filename, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(pickle_filename, 'wb') as token:
                pickle.dump(creds, token)

        return creds


    def parse_attendees(self, to):
        attendees = []

        for attende in to:
            attendees.append({'email': attende})

        return attendees


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

        user, _ = fuzzy.extractOne(sender, SETTINGS["users"].keys())
        settings = SETTINGS["users"][user]["email"]
        username = settings.get("username")

        # Parse summary
        summary = "rpc-tomorrow meeting"  # TODO: Parse from body.

        # Parse Time
        # TODO: Parse time form When
        duration = 20  # TODO: Parse from body.
        start_time = when.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        end_time = (when + timedelta(minutes=duration)).utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        # Define the event
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_time,
            },
            'end': {
                'dateTime': end_time,
            },
            'attendees': self.parse_attendees(to),
        }

        # Get or create user credentials
        creds = self.credentials(username)

        # Create Event using Google calendar API
        service = build('calendar', 'v3', credentials=creds)
        event = service.events().insert(calendarId='primary', body=event).execute()

        return 'Event created, see link: %s' % (event.get('htmlLink')), None

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

