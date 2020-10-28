"""
Tests regarding the contacts util functions
"""
from lib.utils.contacts import get_emails


class TestGetEmails:
    """Tests for getting the emails from a list of names"""

    def test_unknown(self, four_local_contacts):
        """
        Test that an input name that is not in the local contacts will be
        returned as unknown
        """
        names = ["aron"]
        res = get_emails(names)

        assert res["emails"] == []
        assert res["uncertain"] == []
        assert res["unknown"] == ["aron"]

    def test_known(self, four_local_contacts):
        """
        Test that names that exist in the contact book will return the email
        of the contacts
        """
        names = ["niklas", "mark"]
        res = get_emails(names)

        assert res["emails"] == ["niklas@email.com", "mark@email.com"]
        assert res["uncertain"] == []
        assert res["unknown"] == []

    def test_uncertain(self, four_local_contacts):
        """
        Test that names that can be connected to multiple contacts returns all
        the candidates as uncertain
        """
        names = ["hugo", "mark"]
        res = get_emails(names)

        assert res["emails"] == ["mark@email.com"]
        assert res["uncertain"] == [("hugo", [("hugo", "hugo@email.com"), ("hugotwo", "hugotwo@email.com")])]
        assert res["unknown"] == []

    def test_all(self, four_local_contacts):
        """
        Test that it correctly handles multiple names
        """
        names = ["hej@gmail.com", "hugo", "aron", "mark", "gustav", "niklas"]
        res = get_emails(names)

        assert res["emails"] == ["hej@gmail.com", "mark@email.com", "niklas@email.com"]
        assert res["uncertain"] == [("hugo", [("hugo", "hugo@email.com"), ("hugotwo", "hugotwo@email.com")])]
        assert res["unknown"] == ["aron", "gustav"]

    def test_name_is_email(self, four_local_contacts):
        """
        Test that an email will be added to the known emails
        """
        names = ["hej@email.com", "test@noemail"]
        res = get_emails(names)

        assert res["emails"] == ["hej@email.com"]
        assert res["uncertain"] == []
        assert res["unknown"] == ["test@noemail"]
