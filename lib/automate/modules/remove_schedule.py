from __future__ import print_function
import pickle
import os.path
import logging
import spacy

from lib import Error
from lib.utils import contacts
from lib.automate.modules import Module, NoSenderError
import lib.utils.tools.time_convert as tc
from datetime import datetime, timedelta, date
from fuzzywuzzy import process as fuzzy

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

log = logging.getLogger(__name__)

# If modifying these scopes, delete the files *.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class RemoveSchedule(Module):
    verbs = ["unschedule", "remove"]

    def __init__(self):
        super(RemoveSchedule, self).__init__()
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["schedule"])
        to, when, body = self.nlp(text)

        # Get or create user credentials
        settings = sender["email"]
        username = settings.get("username")
        creds = self.credentials(username)
        self.service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        self.event = None

        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, to, when, body, sender):
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None

        # if the event has already been found then just prompt the user
        if self.event:
            return self.prompt_remove_event()

        # try to fetch the event by the summary
        if body:
            self.get_event_by_summary(body)

        # if no event could be found using the summary try to do it with the user inputed time
        if (not self.event) and self.when:
            self.get_event_by_timestamp(self.when)

        if (not self.event) and self.to:
            attendees = []
            parsed_attendees = contacts.get_emails(self.to)
            for email in parsed_attendees["emails"]:
                attendees.append(email)
            for (name, candidates) in parsed_attendees["uncertain"]:
                self.uncertain_attendee = (name, candidates)
                self.followup_type = "to_uncertain"
                followup_str = f"Found multiple contacts with the name {name}\n"
                for i in range(len(candidates)):
                    c_name, c_email = candidates[i]
                    followup_str += f"[{i+1}] {c_name} - {c_email}\n"
                followup_str += f"Please choose one (1-{len(candidates)})"
                return followup_str

            participants = contacts.get_emails(self.to)

            if len(attendees) > 0:
                self.get_event_by_participants(attendees)

        if len(self.events) == 1:
            self.event = self.events[0]
        elif len(self.events) > 1:
            self.followup_type = "to_many_events"

            followup_str = f"Found multiple events: \n"
            for n in range(len(self.events)):
                event = self.events[n]
                start_time = event["start"]["dateTime"]
                start_time = datetime.fromisoformat(start_time)
                formated_time = start_time.strftime("%H:%M, %A, %d. %B %Y")
                followup_str += f"[{n+1}] {event['summary']} at {formated_time}\n"
            followup_str += f"Please choose one (1-{len(self.events)})"
            return followup_str
        else:
            raise NoEventFoundError("Could not find an event.")

        return self.prompt_remove_event()

    def prompt_remove_event(self):
        # if an event could be found then ask the user if it should be removed
        start_time = self.event["start"]["dateTime"]
        start_time = datetime.fromisoformat(start_time)
        formated_time = start_time.strftime("%H:%M, %A, %d. %B %Y")

        self.followup_type = "self_busy"
        return f"You have the event '{self.event['summary']}' scheduled at {formated_time}. Do you want to remove it? [Y/n]"

    def followup(self, answer):
        """ """
        if self.followup_type == "self_busy":
            # if the user answers "yes" on the followup question then remove the event from the calendar
            if answer.lower() in ["y", "yes"]:
                return None
            else:
                raise ActionInterruptedByUserError("Event Not removed.")
        elif self.followup_type == "to_uncertain":
            try:
                choice = int(answer) - 1
            except Exception:
                return self.prepare_processed(self.to, self.when, self.body, self.sender)

            name, candidates = self.uncertain_attendee
            if choice >= 0 and choice < len(candidates):
                self.to.remove(name)  # update to so recursive call continues resolving new attendees
                self.to.append(candidates[choice][1])  # add email of chosen attendee
            return self.prepare_processed(self.to, self.when, self.body, self.sender)
        elif self.followup_type == "to_many_events":
            try:
                choice = int(answer) - 1
            except Exception:
                return self.prepare_processed(self.to, self.when, self.body, self.sender)

            if choice >= 0 and choice < len(self.events):
                self.event = self.events[choice]
                return self.prepare_processed(self.to, self.when, self.body, self.sender)
        else:
            raise NotImplementedError("")

    def execute(self):
        self.service.events().delete(calendarId="primary", eventId=self.event["id"]).execute()
        return f"'{self.event['summary']}' was removed from your calendar"

    def nlp(self, text):
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

            time = datetime.now() + timedelta(seconds=5)
            if len(when) > 0:
                time = tc.parse_time(when)

        _body = " ".join(body)

        return (to, time, _body)

    def credentials(self, username):
        """
        The file token.pickle stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first
        time.
        """
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/../../..")
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
        return creds

    def get_event_by_timestamp(self, time: datetime):
        """ 
        takes a ISO formated time and fetches an event from the calendar where the given time is between 
        the start and end time of the event, the method only looks for events happening in the future

        NOTE: as of now this does not handle multiple events occuring at the same time 
        """
        now = datetime.now()
        # ensure that the given time uses the same timezone as the computer
        time = time.astimezone(now.tzinfo)

        events = self.service.events().list(calendarId="primary", timeMin=(now.isoformat() + "Z")).execute()["items"]

        # find the wanted event
        for e in events:
            event_start = next(v for k, v in e["start"].items() if "date" in k)
            event_start = datetime.fromisoformat(event_start).astimezone(now.tzinfo)

            event_end = next(v for k, v in e["end"].items() if "date" in k)
            event_end = datetime.fromisoformat(event_end).astimezone(now.tzinfo)

            # check if the given time is between the start and end of an event
            if time >= event_start and time <= event_end:
                self.event.append(e)

    def get_event_by_summary(self, summary: str):
        """ 
        try to find a event based on the event summary
        the method only looks for events in the future
        """
        now = datetime.now()
        events = self.service.events().list(calendarId="primary", timeMin=(now.isoformat() + "Z")).execute()["items"]
        events = fuzzy.extractBests(summary, events, score_cutoff=50)

        self.events = list(filter(lambda e: e[0], events))

    def get_event_by_participants(self, participants: [str]):
        """
        Try to find an event based on the participants of the event
        """
        now = datetime.now()
        events = self.service.events().list(calendarId="primary", timeMin=(now.isoformat() + "Z")).execute()["items"]
        events = list(filter(lambda e: "attendees" in e.keys(), events))
        filtered_events = []
        for e in events:
            for attendee in e["attendees"]:
                if attendee["email"] in participants:
                    filtered_events.append(e)

        self.events = filtered_events


class NoEventFoundError(Error):
    pass


class ActionInterruptedByUserError(Error):
    pass
