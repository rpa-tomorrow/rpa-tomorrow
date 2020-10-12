from fuzzywuzzy import process as fuzzy
from email.message import EmailMessage
import smtplib
import re

from lib.automate.modules import Module
from lib import Error
from lib.settings import SETTINGS


class Send(Module):
    verbs = ["send", "mail", "e-mail", "email"]

    def __init__(self):
        super(Send, self).__init__()

    def run(self, to, when, body, sender):
        user, _ = fuzzy.extractOne(sender, SETTINGS["users"].keys())
        self.settings = SETTINGS["users"][user]["email"]
        self.username = self.settings.get("username")
        self.password = self.settings.get("password")
        self.subject = body.partition("\n")[0]
        self.content = body + f"\n\nRegards,\n{user}"

        reciever = ", ".join(to)

        if not self.is_email(reciever):
            # filter out the contacts that does not need to be considered
            possible_recievers = fuzzy.extract(reciever, SETTINGS["users"].keys())
            possible_recievers = list(filter(lambda x: x[1] > 75, possible_recievers))

            # if there are multiple possible recievers then return a string of these that will
            # be displayed to the user.
            #
            # The user will then be able to enter a more precise name
            # that will be sent to the follow-up method
            if len(possible_recievers) > 1:
                names = "\n".join(list(map(lambda contact: contact[0], possible_recievers)))
                return None, "Found multiple contacts: \n" + names + "\nPlease enter the name"
            elif len(possible_recievers) == 1:
                reciever = self.get_email(possible_recievers[0][0])
            else:
                raise NoContactFoundError("Could not find any contacts with name " + reciever)

        response = self.send_email(self.settings, reciever, self.subject, self.content)

        return response, None

    def send_email(self, settings, reciever, subject, content):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings["address"]
        msg["To"] = reciever
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

    def followup(self, answer):
        """Follow up method for after the user enters a inprecise name that has matched on
        multiple users. The user has then been prompted again and given the argument answer, this value should
        be more exakt and map to a single user.
        This method then takes that answer, checks if it is an email address, if it is then the email is sent.
        If the answer is not an email then it should be a name of a user thus
        the email address to the inputted user is fetched and the email is sent."""
        if not self.is_email(answer):
            reciever = self.get_email(fuzzy.extractOne(answer, SETTINGS["users"].keys())[0])
        else:
            reciever = answer

        response = self.send_email(self.settings, reciever, self.subject, self.content)

        return response, None

    def get_email(self, name):
        try:
            return SETTINGS["users"][name]["email"]["address"]
        except KeyError as error:
            raise NoContactFoundError("No contact with name " + name + " was found")

    def is_email(self, email: str) -> bool:
        """ Uses regex to check if a incoming string is an email"""
        regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
        return re.search(regex, email)


class NoContactFoundError(Error):
    pass