import logging

from lib import Error

# Module logger
log = logging.getLogger(__name__)


class Module:
    verbs = []
    model_pool = None

    def __init__(self, model_pool):
        self.model_pool = model_pool

    def prepare(self, nlp_model_names, text, sender):
        raise NotImplementedError("Method not implemented")

    def followup(self, answer):
        raise NotImplementedError("Method not implemented")

    def nlp(self, text):
        """
        Runs the text on the module's own NLP model
        Returns whatever the module is expecting
        """
        raise NotImplementedError("Method not implemented")


class NoSenderError(Error):
    pass
