"""
Module testing that the use case remove scheduled event can be executed correctly
"""
from datetime import datetime, timedelta


class TestUseCaseRemoveSchedule:
    """
    Tests that a valid input for the remove scheduled meeting results in a response
    """

    def test_remove_by_summary(self, selector, calendar_with_events, remove_schedule_no_execute):
        """
        Tests that removing a meeeting by specifying the summary removes
        the correct event
        """
        task_text = "remove the meeting about test"
        response = selector.run(task_text)
        assert len(response) == 1
        removed = response[0]

        # should remove the event with the correct summary
        assert removed["summary"] == "test"

    def test_remove_by_timestamp(self, selector, calendar_with_events, remove_schedule_no_execute):
        """
        Tests that removing a meeting by specifying the time of the meeting
        removes the correct event

        The meetings in the mock have one starting now() + 1hr (1hr duration)
        and one starting now + 5hr (2hr duration)
        """
        # remove meeting starting now + 1hr
        time_meeting = datetime.now() + timedelta(hours=1.5)
        time_meeting_input = str(time_meeting.time())[0:5]  # convert to HH:MM
        task_text = f"remove the meeting at {time_meeting_input}"
        response = selector.run(task_text)
        assert len(response) == 1
        removed = response[0]

        # should remove the meeting which occurs during the specified time
        removed_start = datetime.fromisoformat(removed["start"]["date"])
        removed_end = datetime.fromisoformat(removed["end"]["date"])
        assert removed_start <= time_meeting and removed_end >= time_meeting

        # remove meeting starting now + 5hr
        time_meeting = datetime.now() + timedelta(hours=6)
        time_meeting_input = str(time_meeting.time())[0:5]  # convert to HH:MM
        task_text = f"remove the meeting at {time_meeting_input}"
        response = selector.run(task_text)
        assert len(response) == 1
        removed = response[0]

        # should remove the meeting which occurs during the specified time
        removed_start = datetime.fromisoformat(removed["start"]["date"])
        removed_end = datetime.fromisoformat(removed["end"]["date"])
        assert removed_start <= time_meeting and removed_end >= time_meeting

    def test_remove_by_participants(self, selector, calendar_with_events, remove_schedule_no_execute):
        """
        Tests that removing a meeting by specfifying the pariticipants of the
        meeting removes the correct event.

        The meetings in the mock have one meeting with Hugo and one with Niklas.
        """
        task_text = "remove the meeting with Hugo"
        response = selector.run(task_text)
        assert len(response) == 1
        removed = response[0]

        assert "hugo@email.com" in list(a["email"] for a in removed["attendees"])
