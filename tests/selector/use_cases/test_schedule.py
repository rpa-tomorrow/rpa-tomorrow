"""
Module testing that the use case schedule can be executed correctly
"""


class TestUseCaseSchedule:
    """
    Tests that valid input for the schedule use case will result in a response
    """

    def test_schedule_basic(self, selector, calendar_not_busy, user_with_config):
        """
        Test that a schedule task with only a starting time will be executed
        """
        task_text = "schedule a meeting with hello@email.com at 10:00 about test"
        response = selector.run(task_text)
        assert len(response) == 1
        event = response[0]

        # The event should have correct starting time and duration
        assert event["start"].strftime("%H:%M") == "10:00"
        assert event["end"].strftime("%H:%M") == f"10:{user_with_config['meeting']['standard_duration']}"
        assert "hello@email.com" in event["attendees"]

    def test_schedule_interval(self, selector, calendar_not_busy):
        """
        Test that a schedule task with both a start and end time will be executed
        """
        task_text = "schedule a meeting at 12:00 to 15:00 with hello@email.com about test"
        response = selector.run(task_text)
        assert len(response) == 1
        event = response[0]

        assert event["start"].strftime("%H:%M") == "12:00"
        assert event["end"].strftime("%H:%M") == "15:00"
        assert "hello@email.com" in event["attendees"]
