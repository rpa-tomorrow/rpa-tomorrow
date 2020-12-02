from __future__ import print_function
import lib.utils.tools.time_convert as tc
import spacy
import logging
import lib.utils.ner as ner

from lib import Error
from lib.automate.followup import StringFollowup, BooleanFollowup
from lib.automate.google import Google
from lib.automate.modules import Module, NoSenderError
from lib.utils.contacts import get_emails, prompt_contact_choice
from datetime import datetime, timedelta
from lib.settings import SETTINGS

# Module logger
log = logging.getLogger(__name__)


class Schedule(Module):
    verbs = ["book", "schedule", "meeting"]

    def __init__(self, model_pool):
        super(Schedule, self).__init__(model_pool)
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["schedule"])
        to, when, body = self.nlp(text)

        self.description = ""
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
        if not isinstance(self.when["start"], datetime):
            return self.prompt_date()
        if not body:
            return self.prompt_body()

        settings = sender["email"]
        username = settings.get("username")

        google = Google(username)
        calendar = google.calendar(settings)
        self.calendar = calendar

        # Parse attendees (try to resolve email addresses)
        parsed_attendees = get_emails(self.to, sender)
        attendees = parsed_attendees["emails"]
        for (name, candidates) in parsed_attendees["uncertain"]:
            self.uncertain_attendee = (name, candidates)
            return prompt_contact_choice(name, candidates, self)

        for name in parsed_attendees["unknown"]:
            self.unknown_attendee = name
            return self.prompt_unknown_contact(name)

        attendees = [settings["address"]] + attendees
        event = calendar.event(self.when["start"], self.when["end"], attendees, self.body)
        self.event = event
        self.description = (
            f"The event {self.body} at {self.when['start'].strftime('%H:%M, %A, %d. %B %Y')} "
            + "was prepared\nDo you want to book it?"
        )

        # Check if we are busy
        me_busy = calendar.freebusy(self.when["start"], self.when["end"], ["primary"])
        to_busy = calendar.freebusy(self.when["start"], self.when["end"], to)
        other = f"{', '.join(to_busy[:-1])} and {to_busy[-1]}" if len(to_busy) > 1 else "".join(to_busy)
        if me_busy and to_busy:
            question = f"\nYou as well as {other} seem to be busy. Do you want to book the meeting anyway?"
            return self.busy_prompt(question)
        elif me_busy:
            question = "\nYou seem to be busy during this meeting. Do you want to book it anyway?"
            return self.busy_prompt(question)
        elif to_busy:
            question = f"\n{other} seem to be busy during this meeting. Do you want to book it anyway?"
            return self.busy_prompt(question)

    def execute(self):
        event = self.calendar.send_event(self.event)
        return "\rEvent created, see link: %s" % (event.get("htmlLink"))

    def busy_prompt(self, question):
        def callback(followup):
            if not followup.answer:
                raise ActionInterruptedByUserError("\nInterrupted due to busy attendees.")

        return BooleanFollowup(question, callback, default_answer=True)

    def prompt_body(self):
        def callback(followup):
            self.body = followup.answer
            return self.prepare_processed(self.to, self.when, self.body, self.sender)

        question = "\nFound no event summary. What is the event about"
        return StringFollowup(question, callback)

    def prompt_date(self):
        def callback(followup):
            try:
                start = datetime.fromisoformat(followup.answer)
                end = start + timedelta(minutes=self.get_meeting_duration())
                self.when = {"start": start, "end": end}
            except Exception:
                self.when = {"start": None, "end": None}
            return self.prepare_processed(self.to, self.when, self.body, self.sender)

        question = "\nCould not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format"
        return StringFollowup(question, callback)

    def prompt_unknown_contact(self, name):
        def callback(followup):
            if followup.answer:
                self.to.remove(self.unknown_attendee)
                return self.prepare_processed(self.to, self.when, self.body, self.sender)
            else:
                raise ActionInterruptedByUserError("\nInterrupted due to unknown attendee.")

        question = f"\nFound no contact named {name}. Do you want to continue scheduling the meeting anyway?"
        return BooleanFollowup(question, callback, default_answer=True)

    def nlp(self, text):
        doc = self.nlp_model(text)

        to = []
        start = []
        end = []
        body = []
        persons = []

        locked_ner_model = self.model_pool.get_shared_model("xx_ent_wiki_sm")
        with locked_ner_model:
            persons = ner.get_persons(locked_ner_model.acquire_model(), text)

        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "START":
                start.append(token.text)
            elif token.dep_ == "END":
                end.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)

        to = ner.cross_check_names(to, persons)
        log.debug("Recipients: %s", ",".join(to))

        start_time = datetime.now()
        if len(start) == 0:
            start_time = start_time + timedelta(seconds=5)
        else:
            start_time = tc.parse_time(start)

        end_time = 0
        if len(end) == 0:
            end_time = start_time + timedelta(minutes=self.get_meeting_duration())
        else:
            end_time = tc.parse_time(end)

        _body = " ".join(body)

        return (to, {"start": start_time, "end": end_time}, _body)

    def get_meeting_duration(self) -> str:
        """
        Retrieves the standard meeting duration from the settings file
        """
        try:
            return SETTINGS["meeting"]["standard_duration"]
        except KeyError:
            raise NoValueFoundError("No value for meeting duration found!")


class NoValueFoundError(Error):
    pass


class ActionInterruptedByUserError(Error):
    pass
