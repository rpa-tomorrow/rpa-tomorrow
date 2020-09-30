import spacy
import re

from spacy.matcher import Matcher
from lib.automate import Automate
from lib import Error


class NLP:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")

    def getBodyBetweenQuotations(self, doc):
        matches = re.findall(r"\'(.+?)\'", doc)
        return ",".join(matches)

    def sendAutomate(self, verb, recipients, when, body, sender):
        automate = Automate()
        return automate.run(verb, recipients, when, body, sender,)

    def run(self, text):
        """
        Start NLP on the given text. Takes a few seconds to process if your 
        computer is slow.
        :param text: The user NL input to process
        :type text: string
        """
        # Currently only supports mail, only looks for synonyms of "send"
        send = self.nlp("send")
        send = send[0]

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
        recipients = [doc[start:end].text for match_id, start, end in to_matches]

        # Looks for any synonym to "send"
        for verb in verbs:
            similarity = verb.similarity(send)
            if similarity > 0.8:
                body = self.getBodyBetweenQuotations(text)
                response = self.sendAutomate(
                    verb.text, recipients, None, body, "John Doe"
                )
                return response

        return "I did not understand"
