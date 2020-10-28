from __future__ import print_function
import lib.automate.modules.tools.time_convert as tc
import pickle
import os.path
import spacy
import logging

from lib import Error
from lib.automate.modules import Module, NoSenderError
from lib.utils.contacts import get_emails
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Module logger
log = logging.getLogger(__name__)

# If modifying these scopes, delete the files *.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class Schedule(Module):
    verbs = ["book", "schedule", "meeting"]

    def __init__(self):
        super(Schedule, self).__init__()

    def prepare(self, text, sender):
        to, when, body = self.nlp(text)
        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, to, when, body, sender):
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None
        # stores the available choices when the user needs to clarify the correct attendee
        self.uncertain_attendee = None
        self.unknown_attendee = None

        if not sender:
            raise NoSenderError("No sender found!")

        if not isinstance(when, datetime):
            self.followup_type = "when"
            return "Could not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format"

        if not body:
            self.followup_type = "body"
            return "Found no event summary. What is the event about"

        settings = sender["email"]
        username = settings.get("username")

        summary = self.body

        # Parse Time
        duration = 20  # TODO: Parse from input
        start_time = tc.local_to_utc_time(self.when).isoformat()
        end_time = (tc.local_to_utc_time(self.when) + timedelta(minutes=duration)).isoformat()

        # Parse attendees (try to resolve email addresses)
        attendees = []
        parsed_attendees = get_emails(self.to)
        for email in parsed_attendees["emails"]:
            attendees.append({"email": email})
        for (name, candidates) in parsed_attendees["uncertain"]:
            self.uncertain_attendee = (name, candidates)
            self.followup_type = "to_uncertain"
            followup_str = f"Found multiple contacts with the name {name}\n"
            for i in range(len(candidates)):
                c_name, c_email = candidates[i]
                followup_str += f"[{i+1}] {c_name} - {c_email}\n"
            followup_str += f"Please choose one (1-{len(candidates)})"
            return followup_str
        for name in parsed_attendees["unknown"]:
            self.followup_type = "to_unknown"
            self.unknown_attendee = name
            return f"Found no contact named {name}. Do you want to continue scheduling the meeting anyway? [Y/n]"

        # Define the event
        event = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
            "attendees": attendees,
        }
        self.event = event

        # Get or create user credentials
        creds = self.credentials(username)

        # Create Event using Google calendar API
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        self.service = service

        # Check if we are busy
        to_items = [{"id": email} for email in to]
        freebusy = (
            service.freebusy()
            .query(body={"items": [{"id": "primary"}] + to_items, "timeMin": start_time, "timeMax": end_time})
            .execute()
        )
        to_busy = list(
            map(
                lambda x: x[0],
                filter(lambda x: x[1]["busy"], list(freebusy["calendars"].items())[1:]),
            )
        )

        other = f"{', '.join(to_busy[:-1])} and {to_busy[-1]}" if len(to_busy) > 1 else "".join(to_busy)
        if len(freebusy["calendars"]["primary"]["busy"]) and len(to_busy):
            self.followup_type = "both_busy"
            return f"You as well as {other} seem to be busy. Do you want to book the meeting anyway? [Y/n]"
        elif len(freebusy["calendars"]["primary"]["busy"]):
            self.followup_type = "self_busy"
            return "You seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"
        elif len(to_busy):
            self.followup_type = "to_busy"
            return f"{other} seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"

    def execute(self):
        event = self.service.events().insert(calendarId="primary", body=self.event).execute()
        return "Event created, see link: %s" % (event.get("htmlLink"))

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
            return self.prepare_processed(self.to, when, self.body, self.sender)
        elif self.followup_type == "body":
            return self.prepare_processed(self.to, self.when, answer, self.sender)
        elif self.followup_type == "self_busy" or self.followup_type == "both_busy" or self.followup_type == "to_busy":
            if answer == "" or answer.lower() == "y" or answer.lower() == "yes":
                return None
            elif answer.lower() == "n" or answer.lower() == "no":
                raise ActionInterruptedByUserError("Interrupted due to busy attendees.")
            else:
                return self.prepare_processed(self.to, self.when, self.body, self.sender)
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
        elif self.followup_type == "to_unknown":
            if answer == "" or answer.lower() == "y" or answer.lower() == "yes":
                self.to.remove(self.unknown_attendee)
                return self.prepare_processed(self.to, self.when, self.body, self.sender)
            elif answer.lower() == "n" or answer.lower() == "no":
                raise ActionInterruptedByUserError("Interrupted due to unknown attendee.")
            else:
                return self.prepare_processed(self.to, self.when, self.body, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")

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

    def nlp(self, text):

        nlp = spacy.load("en_rpa_simple_calendar")
        doc = nlp(text)

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


class ActionInterruptedByUserError(Error):
    pass
