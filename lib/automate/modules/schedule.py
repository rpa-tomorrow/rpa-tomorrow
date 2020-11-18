from __future__ import print_function
import lib.utils.tools.time_convert as tc
import spacy
import logging
import asyncio
import lib.utils.ner as ner

from lib import Error
from lib.automate.google import Google
from lib.automate.modules import Module, NoSenderError
from lib.utils.contacts import get_emails, prompt_contact_choice, followup_contact_choice
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
            self.followup_type = "when"
            return "Could not parse date to schedule to.\nPlease enter date in YYYYMMDD HH:MM format"

        if not body:
            self.followup_type = "body"
            return "Found no event summary. What is the event about"

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
            self.followup_type = "to_uncertain"
            return prompt_contact_choice(name, candidates)

        for name in parsed_attendees["unknown"]:
            self.followup_type = "to_unknown"
            self.unknown_attendee = name
            return f"Found no contact named {name}. Do you want to continue scheduling the meeting anyway? [Y/n]"

        attendees = [settings["address"]] + attendees
        event = calendar.event(self.when["start"], self.when["end"], attendees, self.body)
        self.event = event

        # Check if we are busy
        me_busy = calendar.freebusy(self.when["start"], self.when["end"], ["primary"])
        to_busy = calendar.freebusy(self.when["start"], self.when["end"], to)
        other = f"{', '.join(to_busy[:-1])} and {to_busy[-1]}" if len(to_busy) > 1 else "".join(to_busy)
        if me_busy and to_busy:
            self.followup_type = "both_busy"
            return f"You as well as {other} seem to be busy. Do you want to book the meeting anyway? [Y/n]"
        elif me_busy:
            self.followup_type = "self_busy"
            return "You seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"
        elif to_busy:
            self.followup_type = "to_busy"
            return f"{other} seem to be busy during this meeting. Do you want to book it anyway? [Y/n]"

    def execute(self):
        event = self.calendar.send_event(self.event)
        return "\rEvent created, see link: %s" % (event.get("htmlLink"))

    def followup(self, answer):
        """
        Follow up method after the module have had to ask a question to clarify some parameter, or just
        want to check that it interpreted everything correctly.
        """
        if self.followup_type == "when":
            try:
                self.when = {"start": datetime.fromisoformat(answer), "end": None}
            except Exception:
                self.when = None
            return self.prepare_processed(self.to, self.when, self.body, self.sender)
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
            return followup_contact_choice(self, answer)
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

    def nlp(self, text):
        doc = self.nlp_model(text)
        ner_model = asyncio.run(self.model_pool.acquire_model("xx_ent_wiki_sm"))

        to = []
        start = []
        end = []
        body = []
        persons = ner.get_persons(ner_model, text)

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
        self.model_pool.release_model(ner_model)

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
