import os
import sys
import subprocess
import yaml
from lib.settings import update_settings


class Model_Installer:
    def __init__(self):
        self.load_models()

    def load_models(self):
        """Loads the information in ../../config/language_releases.yaml into self.lang_models"""
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("../../config/language_releases.yaml", "r") as stream:
            self.lang_models = yaml.safe_load(stream)
        os.chdir(old_dir)

    def get_languages(self) -> [str]:
        """
        :return: A list of available languages.
        """
        return list(self.lang_models.keys())

    def get_versions(self, language: str) -> [str]:
        """
        :return: A list of available versions for a specific language.
        """
        versions = [v["version"] for v in self.lang_models[language]]
        versions.insert(0, "latest")
        return versions

    def install(self, language: str, version="latest"):
        """Gets information from nlp_models.yaml and installs the models listed
        for that specific language and version"""

        def is_v1_greater(version1: str, version2: str) -> bool:
            """Compares two strings and checks if version1 is greater then version2"""
            v1 = version1.split(".")
            v2 = version2.split(".")
            for i in range(3):
                if v1[i] > v2[i]:
                    return True
                elif v1[i] < v2[i]:
                    return False

            return False

        versions = self.lang_models[language]

        # Loops trough all the model versions for that language and picks the correct version
        selected = {"version": "0.0.0"}
        for v in versions:
            if v["version"] == version:
                selected = v
                break
            elif is_v1_greater(v["version"], selected["version"]):
                selected = v

        if selected["version"] == "0.0.0":
            return  # TODO: Add error

        # Loops trough all the modules and installs them
        for module in selected["modules"]:
            subprocess_comand = [sys.executable]
            if "tar" in module:
                subprocess_comand = [sys.executable, "-m", "pip", "install"]
                subprocess_comand.append(module["tar"])
            else:
                for c in module["command"]:
                    subprocess_comand.append(c)
            subprocess.check_call(subprocess_comand)

        self.update_model_config(selected, language)

    def update_model_config(self, selected: dict, language: str):
        """Updates the config/nlp_models.yaml file with the selected models"""
        nlp_models = None
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("../../config/nlp_models.yaml", "r") as stream:
            nlp_models = yaml.safe_load(stream)
        os.chdir(old_dir)

        nlp_models[language][selected["version"]] = self.format_dict(selected)

        update_settings("../config/nlp_models", nlp_models)

    def format_dict(self, selected: dict) -> dict:
        """
        :return: A dict of models in the format seen in config/nlp_models.yaml.
        """
        formated_dict = {}
        for module in selected["modules"]:
            formated_dict[module["module"]] = module["name"]

        return formated_dict
