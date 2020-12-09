"""
Automation module template
"""
import lib.utils.tools.time_convert as tc
import spacy
import logging

from datetime import datetime, timedelta
from lib.automate.modules import Module


# Module logger
log = logging.getLogger(__name__)


class Template(Module):
    """
    A Template for creating a new automation module.
    """

    # The variable 'verbs' is a list of verbs which is used to identify if the input should be
    # interpreted by this module.
    # Example: ["remind", "reminder", "notify"]
    verbs = []

    def __init__(self, model_pool):
        """
        Creates an object of the module.
        """
        super(Template, self).__init__(model_pool)
        self.nlp_model = None

    def prepare(self, nlp_model_names, text, sender):
        """
        Prepares to execute the task that this module is design to do.

        Preparations include loading and running the NLP model, retrieving the information
        needed from the NLP output and the user to execute the task.
        """
        if self.nlp_model is None:
            # Replace "NLP_MODEL" with the name of the NLP models which this module should use.
            self.nlp_model = spacy.load(nlp_model_names["NLP_MODEL"])
        to, when, body = self.nlp(text)
        self.description = None
        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, to, when, body, sender):
        """
        Extracts the wanted information form the NLP output and asks followup questions if something is missing.

        Note: All the values needed to execute the tasks need to be set as attributes here, so that they can be
        access in the execute function.
        """
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None

        # Ask followup questions if some information is missing.

        # Find necessary information.
        # Example: Find out the email of a contact in the contact book using only the inputted first name.

    def execute(self):
        """
        Executes the task that has been prepared in this module.
        """
        # Do the task that the module is suppose to do.

        # Return a message telling the user that the task is done.
        return "\nTemplate module did ..."

    def nlp(self, text):
        """
        Run the NLP module on the input. Group and return the NLP labels and entities.
        """
        # Runs the NLP model on the input.
        doc = self.nlp_model(text)

        to = []
        when = []
        body = []

        # Group the labels into variables.
        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "WHEN":
                when.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)

        # Get the time entity from the NLP model.
        time = datetime.now()
        if len(when) == 0:
            time = time + timedelta(seconds=5)
        else:
            time = tc.parse_time(when)

        _body = " ".join(body)

        return (to, time, _body)
