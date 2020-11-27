"""
The commands available in the CLI
"""

import sys
import os
import pyaudio
import click
from config import config_model_language, choose_version

sys.path.append(".")

from lib.selector.model_installer import Model_Installer  # noqa: E402
from lib.settings import SETTINGS, get_model_languages, update_settings, get_language_versions  # noqa: E402
from lib.speech.transcribe import transcribe  # noqa: E402


def commands(arr, module_selector):
    """
    Commands supported by the CLI
    """
    if arr[0] == "exit" or arr[0] == "e":
        click.secho("\nGood bye!", fg="green", bold=True)
        click.clear()
        sys.exit()
    elif arr[0] == "help" or arr[0] == "h":
        help_output()
    elif arr[0] == "language" or arr[0] == "lang":
        SETTINGS["user"]["language"] = config_model_language(get_model_languages())
        SETTINGS["user"]["language_version"] = choose_version(get_language_versions(SETTINGS["user"]["language"]))
        update_settings("../config/user", SETTINGS["user"])
    elif arr[0] == "install" or arr[0] == "i":
        model_installer = Model_Installer()
        language = config_model_language(model_installer.get_languages())
        version = choose_version(model_installer.get_versions(language))
        model_installer.install(language, version)
    elif arr[0] == "record" or arr[0] == "r":
        # create audio interface and inform user that the output can be ignored
        audio_interface = pyaudio.PyAudio()
        click.echo(
            "\nIf you see warning messages above they can be ignored. It's caused by PyAudio"
            + " (used for micrpohone input) and cannot be removed.\n"
        )
        click.echo("Recording, please speak...")
        transcribed_input = transcribe(audio_interface)
        audio_interface.terminate()
        ans = input(f"This is what I heard:\n    {transcribed_input}\nExecute? [Y/n]: ").lower()
        if ans == "y" or ans == "yes" or ans == "":
            run_selector(transcribed_input, module_selector)
        else:
            click.echo("Canceled.")
    else:
        text = " ".join(map(str, arr))
        run_selector(text, module_selector)


def help_output():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "helpprompt.txt")
    f = open(filename, "r")
    print(f.read())


def run_selector(input, module_selector):
    try:
        responses = module_selector.run(input)
        for response in responses:
            click.echo(response + "\n")
    except Exception as e:
        print("Failed to execute action.\n", e, file=sys.stderr)
