from lib.utils.emails import is_email


class TestIsEmail:
    def test_is_email(self):
        """
        Tests that a inputed email address is correctly interpreted as an email address
        and that a string that is not an email is interpreted as such
        """

        assert is_email("first.last@email.com")
        assert is_email("studnt-5@student.ltu.se")
        assert is_email("firlas@student.ltu.se")
        assert is_email("studnt-5@ltu.se")
        assert is_email("10-first@email.com")
        assert is_email("10first@email.co.uk")
        assert is_email("jAndersson@email.com")

        assert not is_email("First Last")
        assert not is_email("Last")
        assert not is_email("")
        assert not is_email("First@Last")
        assert not is_email("First@")
        assert not is_email("@Last")
