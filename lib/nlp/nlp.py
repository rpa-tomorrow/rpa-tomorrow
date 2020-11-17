import spacy

from lib.automate import Automate
import time
import asyncio


class NLP:
    def __init__(self, model, spacy_model_name):
        self.loop = asyncio.get_event_loop()
        self.testbool = True
        self.nlp = None
        self.sim_model = None
        self.automate = None
        
        try:
            asyncio.ensure_future(self.firstWorker())
            asyncio.ensure_future(self.secondWorker(model, spacy_model_name))
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("Ready!")

    def send_automate(self, verb, text):
        return self.automate.prepare(verb, text)

    def prepare(self, text):
        """
        Start NLP on the given text. Takes a few seconds to process if your
        computer is slow.
        :param text: The user NL input to process
        :type text: string
        """
        # Currently only supports mail and schedule.
        actions = []
        for v in self.automate.get_verbs():
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
                return self.send_automate(doc_verb.text, text)
        return None

    def run(self, text):
        action = self.prepare(text)
        if action:
            response = action.execute()
            return response
        return "I did not understand"

    async def firstWorker(self):
        animation = "|/-\\"
        idx = 0
        while self.testbool:
            print("Processing input... " + animation[idx % len(animation)], end="\r")
            idx += 1
            await asyncio.sleep(0.1)
            # print("First Worker Executed")
            # await asyncio.sleep(1)


    async def secondWorker(self, model, spacy_model_name):
        while self.testbool:
            print("Second Worker Executed")
            # self.nlp = spacy.load(model)
            # self.sim_model = spacy.load(spacy_model_name)
            # self.automate = Automate()
            await asyncio.sleep(5)
            self.testbool = False
        print("\r")
        raise KeyboardInterrupt
    