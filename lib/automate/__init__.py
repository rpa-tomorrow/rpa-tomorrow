from fuzzywuzzy import process as fuzzy
from importlib import import_module

from lib import Error
from lib.settings import SETTINGS
from lib.automate.pool import ModelPool


class Automate:
    def __init__(self):
        """ Register new modules here """
        self._modules = [
            import_module("lib.automate.modules.send").Send,
            import_module("lib.automate.modules.schedule").Schedule,
            import_module("lib.automate.modules.remove_schedule").RemoveSchedule,
            import_module("lib.automate.modules.update_schedule").UpdateSchedule,
            import_module("lib.automate.modules.reminder").Reminder,
        ]
        self.response_callback = None
        self.loaded_modules = []
        self.modules = []
        self.verbs = []
        self.pool = ModelPool([SETTINGS["nlp_models"]["ner"]])

        for module in self._modules:
            self.verbs.extend(module.verbs)
            self.modules.append((module.verbs, module))

    def _load_module(self, module_name):
        fuzzy_match, score = fuzzy.extractOne(module_name, self.get_verbs())

        if score > 30:
            # Checks if module is loaded and if so returns it
            for verbs, module in self.loaded_modules:
                if fuzzy_match in verbs:
                    return module

            # If module not yet loaded, init it and mark it as loaded
            for verbs, module in self.modules:
                if fuzzy_match in verbs:
                    loaded = module(self.pool)
                    self.loaded_modules.append((verbs, loaded))
                    return loaded

            raise AutomationNotFoundError("Automation module not found")

        else:
            raise AutomationNotFoundError("Automation module not found")

    def get_verbs(self):
        """
        :return: A list of keywords for all of the registered automation modules.
        :rtype: list[string]
        """
        return self.verbs

    def get_senders(self):
        """
        :return: A list of names of the users listed in the SETTINGS.
        :rtype: list[string]
        """
        return list(SETTINGS["users"].keys())

    def prepare(self, module_name, text):
        """
        Prepares the text on the module such that the task is ready to be executed.

        :param module_name: Something close to a keyword of a automation
                            module. This is handled via fuzzy search.
        :type module_name: string
        :param text: The text to interpret.
        :type text: string
        :return: Returns the instance of the module or a followup if information is missing.
        """

        sender = SETTINGS["user"]

        def handle_response(response):
            if response:
                return handle_response(response.handle_cli())
            else:
                return instance

        instance = self._load_module(module_name)

        followup = instance.prepare(SETTINGS["nlp_models"], text, sender)

        if followup is None:
            return handle_response(followup)
        if self.response_callback:
            return self.response_callback(text, instance, followup)
        return handle_response(followup)


class NoResponseError(Error):
    pass


class AutomationNotFoundError(Error):
    pass
