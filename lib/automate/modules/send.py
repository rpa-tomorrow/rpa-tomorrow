from fuzzywuzzy import process as fuzzy
from email.message import EmailMessage
import smtplib
import re

from lib.automate.modules import Module, NoSenderError
from lib import Error
from lib.settings import SETTINGS


class Send(Module):
    verbs = ["send", "mail", "e-mail", "email"]

    def __init__(self):
        super(Send, self).__init__()

    def run(self, to, when, body, sender):
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
            return None, "Found no receiver. Please enter the name of the receiver"
        elif len(to) == 1:
            receiver = to[0]
        else:
            raise ToManyReceiversError("Can only handle one (1) receiver at this time")

        if not body:
            self.followup_type = "body"
            return None, "Found no message body. What message should be sent"

        if not self.is_email(receiver):
            # filter out the contacts that does not need to be considered
            possible_receivers = fuzzy.extract(receiver, SETTINGS["contacts"].keys())
            possible_receivers = list(filter(lambda x: x[1] > 75, possible_receivers))

            # if there are multiple possible receivers then return a string of these that will
            # be displayed to the user.
            #
            # The user will then be able to enter a more precise name
            # that will be sent to the follow-up method
            if len(possible_receivers) > 1:
                names = "\n".join(list(map(lambda contact: contact[0], possible_receivers)))
                self.followup_type = "to2"
                return (
                    None,
                    "Found multiple contacts: \n" + names + "\nPlease enter the name",
                )
            elif len(possible_receivers) == 1:
                receiver = self.get_email(possible_receivers[0][0])
            else:
                raise NoContactFoundError("Could not find any contacts with name " + receiver)

        response = self.send_email(self.settings, receiver, self.subject, self.content)

        return response, None

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
                return self.run(None, self.when, self.body, self.sender)
            else:
                return self.run([answer], self.when, self.body, self.sender)

        elif self.followup_type == "to2":
            if not answer:
                return self.run(None, self.when, self.body, self.sender)
            elif not self.is_email(answer):
                possible_receivers = SETTINGS["contacts"].keys()
                receiver = self.get_email(fuzzy.extractOne(answer, possible_receivers)[0])
            else:
                receiver = answer

            response = self.send_email(self.settings, receiver, self.subject, self.content)

            return response, None

        elif self.followup_type == "body":
            return self.run(self.to, self.when, answer, self.sender)
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

    def is_email(self, email: str) -> bool:
        """ Uses regex to check if a incoming string is an email address"""
        regex = "^([a-z0-9]+[\\._-]?[a-z0-9]+)[@](\\w+[.])+\\w{2,3}$"
        return re.search(regex, email)


class NoContactFoundError(Error):
    pass


class ToManyReceiversError(Error):
    pass


class NoReceiverError(Error):
    pass
