"""
Automation module template
"""
import sys
import lib.utils.tools.time_convert as tc
import spacy
import logging

from datetime import datetime, timedelta
from lib import TimeIsInPastError
from lib.automate.followup import StringFollowup
from lib.automate.modules import Module


# Module logger
log = logging.getLogger(__name__)


class Template(Module):
    """
    A Template for creating a new automation module.
    """

    # The variable 'verbs' is a list of verbs which is used to identify if the input shoud be
    # interpreted by this module.
    # Example: ["remind", "reminder", "notify"]
    verbs = [] 

    def __init__(self, model_pool):
        """
        Creates an object of the module.
        """
        super(Reminder, self).__init__(model_pool)
        self.nlp_model = None


    def prepare(self, nlp_model_names, text, sender):
        """
        Prepares to execute the task that this module is desing to do.

        Preperations inclue loading and runing the nlp model, retriving the information
        needed from the nlp output and the user to execute the task.
        """
        if self.nlp_model is None:
            # Repalce "NLP_MODEL" with the name of the nlp models which this module shoud use.
            self.nlp_model = spacy.load(nlp_model_names["NLP_MODEL"])
        to, when, body = self.nlp(text)
        self.description = None
        return self.prepare_processed(to, when, body, sender)

    def prepare_processed(self, to, when, body, sender):
        """
        Extraces the wanted infromation form the NLP output and asks followup questions if somthing is missing.

        Note: All the values needed to execute the tasks need to be set as attributes here, so that they can be accesd in the execute function.
        """
        self.to = to
        self.when = when
        self.body = body
        self.sender = sender
        self.followup_type = None

        # An example of how to check the input and ask a followup question to the user if it dosen't exist.
        if not isinstance(when, datetime):
            return self.prompt_date()

        # An example of how to check if the input violates some constrain this modules has.
        when_delta = (when - datetime.now()).total_seconds()  # convert to difference in seconds
        if when_delta < 0.0:
            raise TimeIsInPastError(
                when.strftime("%Y-%m-%d %H:%M:%S"),
                "The specified time of the Template is in the past and violates a contrain",
            )

        # Other things can be done here as well. One example is to find the email of a user using only the inputed first name.



    def execute(self):
        """
        Executes the task that has been prepared in this module.
        """
        # Do the task that the module is supose to do.

        # Return a message telling the user that the task is done.
        return f"\nTemplate module did ..."

    def nlp(self, text):
        """
        Run the NLP module on the input. Group and return the nlp labels and enteties.
        """
        # Runs the nlp model on the input.
        doc = self.nlp_model(text)

        to = []
        when = []
        body = []

        # Group the lables into variables. 
        for token in doc:
            if token.dep_ == "TO":
                to.append(token.text)
            elif token.dep_ == "WHEN":
                when.append(token.text)
            elif token.dep_ == "BODY":
                body.append(token.text)
            log.debug("%s %s", token.text, token.dep_)

        # Get the time entity from the nlp model.
        time = datetime.now()
        if len(when) == 0:
            time = time + timedelta(seconds=5)
        else:
            time = tc.parse_time(when)

        _body = " ".join(body)

        return (to, time, _body)

    def prompt_date(self):
        """
        An example of how to define a function for asking the user a followup question on the input.
        """
        def callback(followup):
            try:
                when = datetime.fromisoformat(followup.answer)
            except Exception:
                when = None
            return self.prepare_processed(self.to, when, self.body, self.sender)

        question = "\nCould not parse date from input.\nPlease enter date in YYYYMMDD HH:MM format"
        followup = StringFollowup(question, callback)
        return followup

