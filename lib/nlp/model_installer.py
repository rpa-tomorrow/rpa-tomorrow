import os
import sys
import subprocess
import yaml
from lib.settings import update_settings


class Model_Installer:
    def __init__(self):
        self.load_models()

    def load_models(self):
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("nlp_models.yaml", "r") as stream:
            self.lang_models = yaml.safe_load(stream)
        os.chdir(old_dir)

    def install(self, language: str, version="latest"):
        def is_v1_larger(version1: str, version2: str) -> bool:
            v1 = version1.split('.')
            v2 = version2.split('.')
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
            elif is_v1_larger(v["version"], selected["version"]):
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
        nlp_models = None
        old_dir = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open("../../config/nlp_models.yaml", "r") as stream:
            nlp_models = yaml.safe_load(stream)

        nlp_models[language + " v" + selected["version"]] = (self.format_dict(selected))

        update_settings("../../config/nlp_models", nlp_models)
        os.chdir(old_dir)


    def format_dict(self, selected: dict) -> dict:
        """Formats a dict to be in the format that """
        formated_dict = {}
        for module in selected["modules"]:
            formated_dict[module["module"]] = module["name"]

        return formated_dict

