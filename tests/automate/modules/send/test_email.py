"""
Tests regarding the handling of email address in the Send automation module
"""

import pytest
from lib.automate.modules.send import Send, NoContactFoundError


class TestEmailAddress:
    """Tests for handling email addresses """

    def test_is_email(self):
        """
        Tests that a inputed email address is correctly interpreted as an email address
        and that a string that is not an email is interpreted as such
        """
        send = Send()

        assert send.is_email("first.last@email.com")
        assert send.is_email("studnt-5@student.ltu.se")
        assert send.is_email("firlas@student.ltu.se")
        assert send.is_email("studnt-5@ltu.se")
        assert send.is_email("10-first@email.com")
        assert send.is_email("10first@email.co.uk")

        assert not send.is_email("First Last")
        assert not send.is_email("Last")
        assert not send.is_email("")
        assert not send.is_email("First@Last")
        assert not send.is_email("First@")
        assert not send.is_email("@Last")

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
