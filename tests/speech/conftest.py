import pytest

from lib.speech.transcribe import transcribe


@pytest.fixture
def user_with_non_supported_lang(monkeypatch):
    _non_supported_lang = {"user": {"email": None, "language": "swedish", "language_version": None, "name": None}}
    monkeypatch.setattr("lib.speech.transcribe.SETTINGS", _non_supported_lang)


@pytest.fixture
def transcribe_no_key(monkeypatch):
    def mock_isfile(path):
        return False

    def helper():
        monkeypatch.setattr("lib.speech.transcribe.os.path.isfile", mock_isfile)
        return transcribe(None)

    yield helper
