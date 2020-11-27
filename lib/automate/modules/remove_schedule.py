from __future__ import print_function
import logging
import spacy
import lib.utils.ner as ner

from lib import Error
from lib.automate.followup import BooleanFollowup, MultiFollowup
from lib.utils import contacts
from lib.automate.google import Google
from lib.automate.modules import Module
import lib.utils.tools.time_convert as tc
from datetime import datetime, timedelta
from lib.utils.contacts import prompt_contact_choice

log = logging.getLogger(__name__)

# If modifying these scopes, delete the files *.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.owned",
    "https://www.googleapis.com/auth/calendar.readonly",
]


class RemoveSchedule(Module):
    verbs = ["unschedule", "remove"]

    def __init__(self, model_pool):
        super(RemoveSchedule, self).__init__(model_pool)
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["schedule"])
        to, when, body = self.nlp(text)

        # Get or create user credentials
        settings = sender["email"]
        username = settings.get("username")
        google = Google(username)
        calendar = google.calendar(settings)
        self.calendar = calendar

        self.events = []
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
            self.events = self.calendar.get_event_by_summary(body)

        # if no event could be found using the summary try to do it with the user inputed time
        if (not self.events) and self.when:
            self.events = self.calendar.get_event_by_timestamp(self.when)

        if (not self.events) and self.to:
            # get emails of participants where only the name was entered
            attendees = []
            parsed_attendees = contacts.get_emails(self.to)
            for email in parsed_attendees["emails"]:
                attendees.append(email)
            for (name, candidates) in parsed_attendees["uncertain"]:
                self.uncertain_attendee = (name, candidates)
                return prompt_contact_choice(name, candidates, self)

            contacts.get_emails(self.to)

            if len(attendees) > 0:
                self.events = self.calendar.get_event_by_participants(attendees)

        if len(self.events) == 1:
            self.event = self.events[0]
        elif len(self.events) > 1:

            def callback(followup):
                if followup.answer is not None:
                    self.event = followup.answer
                    return self.prepare_processed(self.to, self.when, self.body, self.sender)
                else:
                    raise NoEventFoundError("\nNo event was chosen for deletion")

            followup_str = "Found multiple events: \n"
            alternatives = []
            for event in self.events:
                start_time = event["start"]["dateTime"]
                start_time = datetime.fromisoformat(start_time)
                formated_time = start_time.strftime("%H:%M, %A, %d. %B %Y")
                alternatives.append((event, f"{event['summary']} at {formated_time}\n"))

            followup = MultiFollowup(followup_str, alternatives, callback, True)
            return followup
        else:
            raise NoEventFoundError("\nCould not find an event.")

        return self.prompt_remove_event()

    def prompt_remove_event(self):
        """ Prompt the user about deleting an event"""
        start_time = self.event["start"]["dateTime"]
        start_time = datetime.fromisoformat(start_time)
        formated_time = start_time.strftime("%H:%M, %A, %d. %B %Y")

        def callback(followup):
            if followup.answer:
                return None
            else:
                raise ActionInterruptedByUserError("Event Not removed.")

        question = (
            f"\nYou have the event '{self.event['summary']}' scheduled at {formated_time}.\n"
            "Do you want to remove it?"
        )
        followup = BooleanFollowup(question, callback, default_answer=True)
        return followup

    def execute(self):
        self.calendar.delete_event(self.event["id"])
        return f"\n'{self.event['summary']}' was removed from your calendar"

    def nlp(self, text):
        doc = self.nlp_model(text)

        to = []
        when = []
        body = []
        persons = []

        locked_ner_model = self.model_pool.get_shared_model("xx_ent_wiki_sm")
        with locked_ner_model:
            persons = ner.get_persons(locked_ner_model.acquire_model(), text)

        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "START":
                when.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)

            time = datetime.now() + timedelta(seconds=5)
            if len(when) > 0:
                time = tc.parse_time(when)

        to = ner.cross_check_names(to, persons)
        log.debug("Recipients: %s", ",".join(to))
        _body = " ".join(body)

        return (to, time, _body)


class NoEventFoundError(Error):
    pass


class ActionInterruptedByUserError(Error):
    pass
