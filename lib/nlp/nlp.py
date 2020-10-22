import spacy
import re
import lib.nlp.time_convert as tc

from lib.automate import Automate
from datetime import datetime, timedelta


class NLP:
    def __init__(self, model):
        self.nlp = spacy.load(model)

    def getBodyBetweenQuotations(self, doc):
        matches = re.findall(r"\'(.+?)\'", doc)
        return ",".join(matches)

    def sendAutomate(self, verb, recipients, when, body):
        automate = Automate()
        return automate.run(verb, recipients, when, body)

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
            actions.append(v)

        verbs = []
        nouns = []
        to = []
        when = []
        body = []
        doc = self.nlp(text)

        for token in doc:
            if token.dep_ == "ROOT":
                verbs.append(token.text)
            elif token.dep_ == "NOUN":
                nouns.append(token.text)
            elif token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "WHEN":
                when.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)

        time = datetime.now()
        if len(when) == 0:
            time = time + timedelta(seconds=5)
        else:
            time = tc.parse_time(when)

        for verb in verbs:
            if verb in actions:
                text = " ".join(body)
                response = self.sendAutomate(verb, to, time, text)
                return response

        return "I did not understand"
