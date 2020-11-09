"""
Tests regarding the handling of email address in the Send automation module
"""

import pytest
from lib.automate.modules.send import NoContactFoundError


class TestEmailAddress:
    """Tests for handling email addresses """

    def test_get_email(self, get_test_email):
        """
        Tests that given a name the email address connected can be fetched from
        a dictionary of contacts
        """
        assert get_test_email("First Last") == "first.last@email.com"
        assert get_test_email("John Doe") == "johndoe@email.com"

        with pytest.raises(NoContactFoundError):
            get_test_email("")
            get_test_email("John")
