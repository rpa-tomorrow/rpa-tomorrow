import pickle
import os.path
from fuzzywuzzy import process as fuzzy
from datetime import datetime as dt, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the files *.pickle.
from lib import Error

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/contacts.other.readonly",
    "https://www.googleapis.com/auth/directory.readonly",
]


class Google:
    def __init__(self, username):
        """
        The file token.pickle stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../..")
        self.username = username
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

        os.chdir(old_dir)
        self.creds = creds

    def calendar(self, settings):
        return Calendar(self, settings)

    def people(self):
        return People(self, self.username)


class Event:
    def __init__(self, start: dt, duration: timedelta, attendees_email: [str], summary: str):
        self.start = start
        self.end = self.start + duration
        self.attendees_email = attendees_email
        self.summary = summary

    def to_dict(self):
        # Parse Time
        start_time = self.start.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = self.end.isoformat() + "Z"  # 'Z' indicates UTC time

        return {
            "summary": self.summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
            "attendees": list(map(lambda x: {"email": x}, self.attendees_email)),
        }


class Calendar:
    def __init__(self, google: Google, settings):
        self.settings = settings
        self.google = google
        self.service = build("calendar", "v3", credentials=google.creds)

    def event(self, start: dt, duration: timedelta, attendees_email: [str], summary: str):
        return Event(start, duration, attendees_email, summary)

    def send_event(self, event: Event):
        return self.service.events().insert(calendarId="primary", body=event.to_dict()).execute()

    def freebusy(self, start: dt, duration: timedelta, attendees_email):
        if not attendees_email:
            return []

        # Parse Time
        start_time = start.isoformat() + "Z"  # 'Z' indicates UTC time
        end_time = (start + duration).isoformat() + "Z"
        to_items = [{"id": email} for email in attendees_email]
        freebusy = (
            self.service.freebusy()
            .query(body={"items": to_items, "timeMin": start_time, "timeMax": end_time})
            .execute()
        )
        freebusy = map(lambda x: x[0], filter(lambda x: x[1]["busy"], freebusy["calendars"].items()))
        return list(freebusy)


class People:
    def __init__(self, google: Google, username):
        self.username = username
        self.google = google
        self.service = build("people", "v1", credentials=google.creds)
        self.contacts = None
        self.fetch()

    def fetch(self):
        pickle_filename = f"{self.username}_contacts.pickle"
        if os.path.exists(pickle_filename):
            with open(pickle_filename, "rb") as token:
                self.contacts = pickle.load(token)
                return

        contacts = {}
        mask = "names,emailAddresses"
        req = self.service.otherContacts().list(readMask=mask)
        while req:
            result = req.execute()
            for contact in result["otherContacts"]:
                if "emailAddresses" in contact and "names" in contact:
                    for email in contact["emailAddresses"]:
                        for name in contact["names"]:
                            contacts[name["displayName"]] = email["value"]
            req = self.service.otherContacts().list_next(req, result)
        self.contacts = contacts

        with open(pickle_filename, "wb") as token:
            pickle.dump(self.contacts, token)

    def search(self, queries: [str]):
        results = []
        for query in queries:
            match = fuzzy.extractOne(query, self.contacts.keys())[0]
            results.append(self.contacts[match])
        results = list(set(results))
        while len(results):
            question = "Contact book search returned {0}. Continue? [Y/n]".format(
                results[0] if len(results) == 1 else ", ".join(results[:-1]) + f"and {results[-1]}"
            )
            print(question, end=": ", flush=True)
            answer = input().lower()
            if answer == "y" or answer == "yes" or answer == "":
                break
            elif answer == "n" or answer == "no":
                raise ContactBookInterruptedByUserError("User interrupted contact book search result!")
        return results


class ContactBookInterruptedByUserError(Error):
    pass
