import smtplib
import spacy
import lib.utils.tools.time_convert as tc
import logging

from fuzzywuzzy import process as fuzzy
from email.message import EmailMessage
from lib.automate.modules import Module, NoSenderError
from lib import Error
from lib.settings import SETTINGS
from datetime import datetime, timedelta
from lib.utils.email import is_email


# Module logger
log = logging.getLogger(__name__)


class Send(Module):
    verbs = ["send", "mail", "e-mail", "email"]

    def __init__(self):
        super(Send, self).__init__()
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        if self.nlp_model is None:
            self.nlp_model = spacy.load(nlp_model_names["email"])
        to, when, body = self.nlp(text)
        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, to, when, body, sender):
        self.to = to
        self.when = when
        self.body = body

        if not sender:
            raise NoSenderError("No sender found!")

        self.followup_type = None
        self.sender = sender
        self.settings = sender["email"]
        self.username = self.settings.get("username")
        self.password = self.settings.get("password")
        self.subject = body.partition("\n")[0]
        self.content = body + f"\n\nRegards,\n{sender['name']}"

        if not to or len(to) == 0:
            self.followup_type = "to1"
            return "Found no receiver. Please enter the name of the receiver"
        elif len(to) == 1:
            receiver = to[0]
            self.receiver = receiver
        else:
            raise ToManyReceiversError("Can only handle one (1) receiver at this time")

        if not body:
            self.followup_type = "body"
            return "Found no message body. What message should be sent"

        if not is_email(receiver):
            # filter out the contacts that does not need to be considered
            possible_receivers = fuzzy.extract(receiver, SETTINGS["contacts"].keys())
            possible_receivers = list(filter(lambda x: x[1] > 87, possible_receivers))

            # if there are multiple possible receivers then return a string of these that will
            # be displayed to the user.
            #
            # The user will then be able to enter a more precise name
            # that will be sent to the follow-up method
            if len(possible_receivers) > 1:
                names = "\n".join(list(map(lambda contact: contact[0], possible_receivers)))
                self.followup_type = "to2"
                return "Found multiple contacts: \n" + names + "\nPlease enter the name"
            elif len(possible_receivers) == 1:
                receiver = self.get_email(possible_receivers[0][0])
                self.receiver = receiver
            else:
                raise NoContactFoundError("Could not find any contacts with name " + receiver)

    def execute(self):
        return self.send_email(self.settings, self.receiver, self.subject, self.content)

    def send_email(self, settings: dict, receiver: str, subject: str, content: str):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings["address"]
        msg["To"] = receiver
        msg.set_content(content)

        ssl_type = f"SMTP{'_SSL' if settings['ssl'] else ''}"
        smtp = getattr(smtplib, ssl_type)(host=settings["host"], port=settings["port"])

        # Dont try to authenticate if the smtp server used is local which is
        # assumed if the username or password is not specified
        if self.username and self.password:
            smtp.login(self.username, self.password)

        smtp.send_message(msg)
        smtp.quit()

        response = (
            "Sent mail:\n"
            + f"From: {settings['address']}\n"
            + f"To: {msg['To']}\n"
            + f"Subject: {msg['Subject']}\n"
            + f"Message: {content}"
        )

        return response

    def followup(self, answer: str) -> (str, str):
        """
        Follow up method after the module have had to ask a question to clarify some parameter, or just
        want to check that it interpreted everything correctly.
        """
        if self.followup_type == "to1":
            if not answer:
                return self.prepare_processed(None, self.when, self.body, self.sender)
            else:
                return self.prepare_processed([answer], self.when, self.body, self.sender)

        elif self.followup_type == "to2":
            if not answer:
                return self.prepare_processed(None, self.when, self.body, self.sender)
            else:
                return self.prepare_processed([answer], self.when, self.body, self.sender)

        elif self.followup_type == "body":
            return self.prepare_processed(self.to, self.when, answer, self.sender)
        else:
            raise NotImplementedError("Did not find any valid followup question to answer.")

    def get_email(self, name: str) -> str:
        """
        Retrieves the email of a user from the contact book in the settings file
        If no user is found, i.e. there are no key equal to the name given then an error is raised
        """
        try:
            return SETTINGS["contacts"][name]["email"]["address"]
        except KeyError:
            raise NoContactFoundError("No contact with name " + name + " was found")

    def nlp(self, text):
        """
        Lets the reminder model work on the given text.
        """
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

        time = datetime.now()
        if len(when) == 0:
            time = time + timedelta(seconds=5)
        else:
            time = tc.parse_time(when)

        _body = " ".join(body)

        return (to, time, _body)


class NoContactFoundError(Error):
    pass


class ToManyReceiversError(Error):
    pass


class NoReceiverError(Error):
    pass
