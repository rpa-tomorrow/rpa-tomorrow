from fuzzywuzzy import process as fuzzy
from email.message import EmailMessage
import smtplib

from lib.automate.modules import Module
from lib.settings import SETTINGS


class Send(Module):
    verbs = ["skicka", "maila", "mejla", "eposta", "e-posta"]

    def __init__(self):
        super(Send, self).__init__()

    def run(self, to, when, body, sender):
        user, _ = fuzzy.extractOne(sender, SETTINGS["users"].keys())
        settings = SETTINGS["users"][user]["email"]
        content = body + f"\n\nVänligen,\n{user}"

        msg = EmailMessage()
        msg["Subject"] = body.partition("\n")[0]
        msg["From"] = settings["address"]
        msg["To"] = ", ".join(to)
        msg.set_content(content)

        ssl_type = f"SMTP{'_SSL' if settings['ssl'] else ''}"
        smtp = getattr(smtplib, ssl_type)(
            host=settings["host"],
            port=settings["port"]
        )
        smtp.login(settings["username"], settings["password"])
        smtp.send_message(msg)
        smtp.quit()

        response = f"Skickade epost:\n"\
            + f"Från: {settings['address']}\n"\
            + f"Till: {msg['To']}\n"\
            + f"Ämne: {msg['Subject']}\n"\
            + f"Meddelande: {content}"

        return response, None
