"""
Module that tests the exception handling of the transcribe function
"""
import pytest

from lib.speech.transcribe import LanguageNotSupportedError, MissingServiceAccountKeyError, transcribe


class TestTranscribe:
    """Tests for the exceptions in the transcribe function"""

    def test_language_not_supported(self, user_with_non_supported_lang):
        """Test that an exception is raised when the user has a non-supported language"""
        with pytest.raises(LanguageNotSupportedError) as excinfo:
            transcribe(None)
        assert "not supported for the current language" in str(excinfo.value)

    def test_missing_service_account_key(self, transcribe_no_key):
        with pytest.raises(MissingServiceAccountKeyError) as excinfo:
            transcribe_no_key()
        assert "key does not exist" in str(excinfo.value)
