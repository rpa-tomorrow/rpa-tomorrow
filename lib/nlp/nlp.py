import spacy

from lib.automate import Automate


class NLP:
    def __init__(self, model):
        self.nlp = spacy.load(model)
        self.sim_model = spacy.load("en_core_web_md")

    def send_automate(self, verb, text):
        automate = Automate()
        return automate.prepare(verb, text)

    def prepare(self, text):
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
        doc = self.nlp(text)

        for token in doc:
            if token.dep_ == "ROOT":
                verbs.append(token.text)

        doc_verb = self.sim_model(verbs[0])
        for action in actions:
            doc_action = self.sim_model(action)
            similarity = doc_action.similarity(doc_verb)
            if similarity > 0.6:
                response = self.send_automate(doc_verb.text, text)
                return response

    def run(self, text):
        action = self.prepare(text)
        if action:
            response = action.execute()
            return response
        return "I did not understand"
