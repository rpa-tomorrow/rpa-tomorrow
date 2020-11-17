from fuzzywuzzy import process as fuzzy
from importlib import import_module

from lib import Error
from lib.settings import SETTINGS


class Automate:
    def __init__(self):
        """ Register new modules here """
        self.modules = [
            import_module("lib.automate.modules.send").Send,
            import_module("lib.automate.modules.schedule").Schedule,
            import_module("lib.automate.modules.remove_schedule").RemoveSchedule,
            import_module("lib.automate.modules.reminder").Reminder,
        ]
        self.response_callback = None
        self.verbs = {}
        for module in self.modules:
            for verb in module.verbs:
                self.verbs[verb] = module

    def get_verbs(self):
        """
        :return: A list of keywords for the registered automation modules.
        :rtype: list[string]
        """
        return list(self.verbs.keys())

    def get_senders(self):
        """
        :return: A list of names of users listed in the SETTINGS.
        :rtype: list[string]
        """
        return list(SETTINGS["users"].keys())

    def prepare(self, module_name, text):
        """
        Run automation on registered module.
        :param module_name: Something close to a keyword of a automation
                            module. This is handled via fuzzy search.
        :type module_name: string
        :param text: The text to interpret.
        :type text: string
        :rtype: string
        """
        sender = SETTINGS["user"]

        def handle_response(response):
            if response:
                print(response, end=": ", flush=True)
                return handle_response(instance.followup(input()))
            else:
                return instance

        if module_name in self.verbs:
            instance = self.verbs[module_name]()
        else:
            fuzzy_match, score = fuzzy.extractOne(module_name, self.get_verbs())
            if score > 30:
                instance = self.verbs[fuzzy_match]()
            else:
                raise AutomationNotFoundError("Automation module not found")

        followup = instance.prepare(SETTINGS["nlp_models"], text, sender)
        if self.response_callback:
            return self.response_callback(instance, followup)
        else:
            return handle_response(followup)


class NoResponseError(Error):
    pass


class AutomationNotFoundError(Error):
    pass
