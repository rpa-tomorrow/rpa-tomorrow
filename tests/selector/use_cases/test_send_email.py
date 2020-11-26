"""
Module testing that the use case email can be executed correctly
"""


class TestUseCaseEmail:
    """
    Tests that valid input for the email use case results in a respones
    """

    def test_email_receiver_address(self, selector, send_email):
        """ Test that an email can be sent using the full address of the receiver """
        task_text = "send an email to hej@email.com about how is it going?"
        response = selector.run(task_text)
        assert len(response) == 1
        email = response[0]

        assert len(email["receiver"]) == 1
        assert "hej@email.com" in email["receiver"]
        # should include a signature
        assert "Regards,\nJohn Doe" in email["content"]

    def test_email_receiver_name(self, selector, send_email, user_with_config):
        """ Test that an email can be sent using the name of the receiver """
        task_text = "send an email to Hugo about hello there"
        response = selector.run(task_text)
        assert len(response) == 1
        email = response[0]

        assert len(email["receiver"]) == 1
        assert user_with_config["contacts"]["Hugo Wangler"]["email"]["address"] in email["receiver"]
        # should include a signature
        assert "Regards,\nJohn Doe" in email["content"]
