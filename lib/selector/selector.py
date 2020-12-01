import spacy
import re
import logging

from lib.automate import Automate
from lib.settings import SETTINGS
from lib.automate.followup import BooleanFollowup

ROOT_LABEL = "ROOT"
SIMILARITY_MIN = 0.6
# This only works for English right now
FMT_ALLOWED_CHARS = r"[^a-zA-Z0-9.'@\-: ]"

# Module logger
log = logging.getLogger(__name__)


class ModuleSelector:
    def __init__(self):
        # Checks for task root/keywords
        self.root_model = spacy.load(SETTINGS["nlp_models"]["basic"])
        # Used for language structure and word similarities
        self.general_model = spacy.load(SETTINGS["nlp_models"]["spacy_md"])
        self.automate = Automate()
        self.tasks = []

    def _check_similarities(self, word, verbs):
        doc_verb = self.general_model(word)
        for verb in verbs:
            doc_action = self.general_model(verb)
            similarity = doc_action.similarity(doc_verb)
            if similarity > SIMILARITY_MIN:
                return doc_verb.text

        return None

    def _prepare_task(self, text):
        verbs = self.automate.get_verbs()
        root = None
        doc = self.root_model(text)

        for token in doc:
            if token.dep_ == ROOT_LABEL:
                root = token.text

        match = self._check_similarities(root, verbs)
        if match is not None:
            return self._send_automate(match, text)

        return None

    def _send_automate(self, verb, text):
        return self.automate.prepare(verb, text)

    def _format_sentence(self, text):
        fmtd = re.sub(FMT_ALLOWED_CHARS, "", text)
        # Remove possible end of sentence punctuation
        return fmtd.rstrip(".")

    def prepare(self, text):
        """
        Checks the text and forwards the correct sentences to any
        suitable modules. Then returns a list of prepared modules
        that are ready to be executed.

        :param text: The user natural language input to process
        :type text: string
        :return A list of processed automation modules
        """
        doc = self.general_model(text)
        sentences = [sentence.lower_ for sentence in doc.sents]
        prepared_tasks = []

        for sentence in sentences:
            fmt_sentence = self._format_sentence(sentence)
            log.debug("Preparing task for sentence: %s", fmt_sentence)
            task = self._prepare_task(fmt_sentence)
            prepared_tasks.append(task)

        return prepared_tasks

    def run(self, text):
        """
        Prepares the text and then executes the corresponding
        modules.

        :param: text The user natural language input to process
        :type text: string
        :return A list of responses
        :rtype list[string]
        """
        tasks = self.prepare(text)
        responses = []
        for task in tasks:
            if task is not None:

                def callback(followup):
                    if followup.answer:
                        response = task.execute()
                        responses.append(response)
                    else:
                        responses.append("Task aborted.")

                # prompt the user with the description of the task before executing it
                if task.description:
                    followup = BooleanFollowup(task.description, callback, default_answer=False)
                    followup.handle_cli()
                else:
                    # some tasks might not need prompting before execution,
                    # thus if there isn't a description of the task then execute it without prompt
                    response = task.execute()
                    responses.append(response)
            else:
                responses.append("I did not understand")

        return responses
