import spacy
import re

from spacy.matcher import Matcher
from lib.automate import Automate
from datetime import datetime


class NLP:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")

    def getBodyBetweenQuotations(self, doc):
        matches = re.findall(r"\'(.+?)\'", doc)
        return ",".join(matches)

    def sendAutomate(self, verb, recipients, when, body, sender):
        automate = Automate()
        return automate.run(verb, recipients, when, body, sender)

    def run(self, text):
        """
        Start NLP on the given text. Takes a few seconds to process if your
        computer is slow.
        :param text: The user NL input to process
        :type text: string
        """
        # Currently only supports mail and schedule.
        actions = []
        for v in Automate().get_verbs():
            actions.append(self.nlp(v)[0])
        doc = self.nlp(text)

        # Match patterns VERBS, EMAIL
        matcher = Matcher(self.nlp.vocab)
        mail_pattern = [{"POS": "VERB"}]
        to_pattern = [{"LIKE_EMAIL": True}]

        matcher.add("MAIL_PATTERN", None, mail_pattern)
        mail_matches = matcher(doc)
        matcher.remove("MAIL_PATTERN")

        matcher.add("TO_PATTERN", None, to_pattern)
        to_matches = matcher(doc)

        verbs = [doc[start:end] for match_id, start, end in mail_matches]
        recipients = [
            doc[start:end].text for match_id, start, end in to_matches
        ]

        # Get all known names and time.
        persons = []
        date_time = datetime.now()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                persons.append(ent.text)
            elif ent.label_ == "TIME":
                time = datetime.strptime(ent.text, "%H:%M")
                date_time = date_time.replace(
                    hour=time.hour, minute=time.minute, second=0
                )
            elif ent.label_ == "DATE":
                date_time = datetime.strptime(ent.text, "%Y-%m-%d %H:%M")
        if len(persons) < 1:
            persons.append("John Doe")

        # Looks for any synonym to the verbs
        for verb in verbs:
            for action in actions:
                similarity = verb.similarity(action)
                if similarity > 0.8:
                    body = self.getBodyBetweenQuotations(text)
                    response = self.sendAutomate(
                        verb.text, recipients, date_time, body, persons[0]
                    )
                    return response

        return "I did not understand"
