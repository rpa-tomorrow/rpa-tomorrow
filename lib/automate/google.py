import pickle
import os.path
from fuzzywuzzy import process as fuzzy
from datetime import datetime as dt
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from lib import Error
from lib.utils.tools import time_convert as tc

# If modifying these scopes, delete the files *.pickle.
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
        pickle_filename = f"pickle_jar/{username}_token.pickle"

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
    def __init__(self, start: dt, end: dt, attendees_email: [str], summary: str):
        self.start = start
        self.end = end
        self.attendees_email = attendees_email
        self.summary = summary

    def to_dict(self):
        # Parse Time
        start_time = tc.local_to_utc_time(self.start).isoformat()
        end_time = tc.local_to_utc_time(self.end).isoformat()

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
        self.service = build("calendar", "v3", credentials=google.creds, cache_discovery=False)

    def event(self, start: dt, end: dt, attendees_email: [str], summary: str):
        return Event(start, end, attendees_email, summary)

    def send_event(self, event: Event):
        return self.service.events().insert(calendarId="primary", body=event.to_dict()).execute()

    def freebusy(self, start: dt, end: dt, attendees_email):
        if not attendees_email:
            return []

        # Parse Time
        start_time = start.astimezone().isoformat()  # system timezone
        end_time = end.astimezone().isoformat()  # system timezone
        to_items = [{"id": email} for email in attendees_email]
        freebusy = (
            self.service.freebusy()
            .query(body={"items": to_items, "timeMin": start_time, "timeMax": end_time})
            .execute()
        )
        freebusy = list(map(lambda x: x[0], filter(lambda x: x[1]["busy"], freebusy["calendars"].items())))
        return freebusy

    def get_events(self):
        """
        Returns a list of events from the primary calendar
        Does not return past events that has already ended
        """
        now = dt.now()
        events = (
            self.service.events()
            .list(calendarId="primary", timeMin=(now.astimezone(now.tzinfo).isoformat()))
            .execute()["items"]
        )
        return events

    def delete_event(self, event_id: str):
        self.service.events().delete(calendarId="primary", eventId=event_id).execute()

    def update_event(self, event_id: str, event_body: dict):
        return self.service.events().patch(calendarId="primary", eventId=event_id, body=event_body).execute()

    def get_event_by_summary(self, summary: str):
        """
        Try to find events based on the event summary
        Does not return past events that has already ended

        Returns a list of events from the primary calendar
        """
        events = self.get_events()
        event_summaries = list(map(lambda e: e["summary"], events))

        # find the best matches for the event
        event_summaries = fuzzy.extractBests(summary, event_summaries, score_cutoff=50)

        # remove duplicate summaries,
        # the loop will find all occurances of events with the same summary
        event_summaries = list(set(event_summaries))
        filtered_events = []
        for s in event_summaries:
            filtered_events += list(filter(lambda e: e["summary"] == s[0], events))

        return filtered_events

    def get_event_by_participants(self, participants: [str]):
        """
        Try to find an event based on the participants of the event
        Does not return past events that has already ended

        Returns a list of events from the primary calendar
        """
        events = self.get_events()
        events = list(filter(lambda e: "attendees" in e.keys(), events))
        filtered_events = []
        for e in events:
            for attendee in e["attendees"]:
                if attendee["email"] in participants:
                    filtered_events.append(e)

        return filtered_events

    def get_event_by_timestamp(self, time: dt):
        """
        takes a ISO formated time and fetches events from the calendar where the given time is between
        the start and end time of the event, the method only looks for events happening in the future

        Returns a list of events from the primary calendar

        NOTE: as of now this does not handle multiple events occuring at the same time
        """
        # ensure that the given time uses the same timezone as the computer
        now = dt.now()
        time = time.astimezone(now.tzinfo)

        events = self.get_events()
        filtered_events = []
        # find the wanted event
        for e in events:
            event_start = next(v for k, v in e["start"].items() if "date" in k)
            event_start = dt.fromisoformat(event_start).astimezone(now.tzinfo)

            event_end = next(v for k, v in e["end"].items() if "date" in k)
            event_end = dt.fromisoformat(event_end).astimezone(now.tzinfo)

            # check if the given time is between the start and end of an event
            if time >= event_start and time <= event_end:
                filtered_events.append(e)
        return filtered_events


class People:
    def __init__(self, google: Google, username):
        self.username = username
        self.google = google
        self.service = build("people", "v1", credentials=google.creds, cache_discovery=False)
        self.contacts = None
        self.fetch()

    def fetch(self):
        pickle_filename = f"pickle_jar/{self.username}_contacts_v2.pickle"
        if os.path.exists(pickle_filename):
            with open(pickle_filename, "rb") as token:
                self.contacts = pickle.load(token)
                return

        contacts = {}
        mask = "names,emailAddresses"
        req = self.service.otherContacts().list(readMask=mask)
        while req:
            result = req.execute()
            if "otherContacts" in result:
                for contact in result["otherContacts"]:
                    if "emailAddresses" in contact and "names" in contact:
                        for email in contact["emailAddresses"]:
                            for name in contact["names"]:
                                contacts[name["displayName"]] = email["value"]
                req = self.service.otherContacts().list_next(req, result)
        req = self.service.people().connections().list(resourceName="people/me", personFields=mask)
        while req:
            result = req.execute()
            if "connections" in result:
                for contact in result["connections"]:
                    if "emailAddresses" in contact and "names" in contact:
                        for email in contact["emailAddresses"]:
                            for name in contact["names"]:
                                contacts[name["displayName"]] = email["value"]
                req = self.service.people().connections().list_next(req, result)
        self.contacts = contacts

        with open(pickle_filename, "wb") as token:
            pickle.dump(self.contacts, token)

    def search(self, queries: [str]):
        results = []
        for query in queries:
            match = fuzzy.extractBests(query, self.contacts.keys(), score_cutoff=75)
            results = list(map(lambda c: (c[0], self.contacts[c[0]]), match))
        results = list(set(results))

        return results


class ContactBookInterruptedByUserError(Error):
    pass
