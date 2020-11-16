"""
Module for transcribing speech input using the google speech-to-text api (see
https://cloud.google.com/speech-to-text)
"""

import os

from google.cloud import speech

from lib import LanguageNotSupportedError, MissingServiceAccountKeyError
from lib.settings import SETTINGS, load_user

from .microphone import RATE, MicrophoneStream


def transcribe(audio_interface):
    """
    Transcribes a stream of microphone input using google cloud speech to
    convert speech to text.

    Takes a audio_interface (pyaudio.PyAudio()) as an argument because calling
    it produces output and the user needs to be informed that this is not a
    problem with this program from the caller of this function.
    """
    load_user()
    user_lang = SETTINGS["user"]["language"]
    if user_lang == "english":
        lang = "en-US"
    else:
        # The Google API support other languages but our models currently only work with English
        raise LanguageNotSupportedError(
            f"Speech-to-text is not supported for the current language ({user_lang}), please change the language to"
            + "English"
        )

    # Setup google cloud speech
    if not os.path.isfile("service_account.json"):
        raise MissingServiceAccountKeyError(
            "Required Google service account key does not exist. Speech-to-text does not work without it."
        )
    client = speech.SpeechClient.from_service_account_json("service_account.json")
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate_hertz=RATE, language_code=lang
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)

    with MicrophoneStream(audio_interface) as stream:
        # Transcribe one sentence of microphone stream input
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
        responses = client.streaming_recognize(streaming_config, requests)

    # Return the transcribed sentence
    for response in responses:
        return response.results[0].alternatives[0].transcript
