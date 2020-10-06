from fuzzywuzzy import process as fuzzy
from email.message import EmailMessage
import smtplib

from lib.automate.modules import Module
from lib.settings import SETTINGS


class Send(Module):
    verbs = ["send", "mail", "e-mail", "email"]

    def __init__(self):
        super(Send, self).__init__()

    def run(self, to, when, body, sender):
        user, _ = fuzzy.extractOne(sender, SETTINGS["users"].keys())
        settings = SETTINGS["users"][user]["email"]
        username = settings.get("username")
        password = settings.get("password")
        content = body + f"\n\nRegards,\n{user}"

        msg = EmailMessage()
        msg["Subject"] = body.partition("\n")[0]
        msg["From"] = settings["address"]
        msg["To"] = ", ".join(to)
        msg.set_content(content)

        ssl_type = f"SMTP{'_SSL' if settings['ssl'] else ''}"
        smtp = getattr(smtplib, ssl_type)(host=settings["host"],
                                          port=settings["port"])

        # Dont try to authenticate if the smtp server used is local which is
        # assumed if the username or password is not specified
        if username and password:
            smtp.login(username, password)

        smtp.send_message(msg)
        smtp.quit()

        response = (
            "Sent mail:\n"
            + f"From: {settings['address']}\n"
            + f"To: {msg['To']}\n"
            + f"Subject: {msg['Subject']}\n"
            + f"Message: {content}"
        )

        return response, None
