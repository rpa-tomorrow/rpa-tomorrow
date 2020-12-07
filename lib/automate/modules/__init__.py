import logging

from lib import Error

# Module logger
log = logging.getLogger(__name__)


class Module:
    """
    RPA Tomorrow Module Specification.

    * This contains the ABSOLUTE minimum required functions of a module.
    * All new modules need to inherit from this Module class.
    * All functions may raise any possible exceptions and should be handled
    by the caller.
    """

    verbs = []
    """list[string]: The verbs to associate with this module's functionality."""
    model_pool = None
    """ModelPool: The shared model pool all modules can access."""

    def __init__(self, model_pool):
        """
        The Automate API will try to initialize the module with the
        shared model pool.

        :param model_pool: The shared model pool to use between all modules.
        :type model_pool: ModelPool
        """
        self.model_pool = model_pool

    def prepare(self, nlp_model_names, text, sender):
        """
        Prepare should take a text sentence and complete the necessary processing of it, such
        that the module is prepared to be executed by the caller.

        Prepare can return two things, depending on if further information is needed or not.
            1. All necessary information was received and processing completed:
               Return 'None'
            2. More information is needed to finish processing:
               Return a fitting Followup object. This will be used by the originator of this
               prepare request if the prepare does not return None. In order to complete
               the preparation.

        :param nlp_model_names: A list of the spacy models to load.
        :type nlp_model_names: list[string]
        :param text: The user input (sentence) to process.
        :type text: string
        :param sender: Information about the user from its configuration file.
        :type sender: dict
        """
        raise NotImplementedError("Method not implemented")

    def execute(self):
        """
        Executes the prepared module such that the task is run.
        """
        raise NotImplementedError("Method not implemented")


class NoSenderError(Error):
    pass
