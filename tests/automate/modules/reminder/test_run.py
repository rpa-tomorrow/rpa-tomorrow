"""
Tests regarding the running of the Reminder automation module
"""
import pytest
import datetime

from lib import TimeIsInPastError, OSNotSupportedError


class TestRunReminder:
    """Tests for running a reminder automation task"""

    # Note that the arguments run, mock_os_supported are fixtures defined in
    # the conftest.py file in this directory. This is how you can use fixtures
    # in your tests if you need to mock something, pytest will automatically
    # call the tests with the corresponding fixtures.
    def test_successful(self, run, mock_os_supported):
        """
        Tests that a reminder can be scheduled successfully. This does not test
        that a notification is actually created in the host OS.
        """
        valid_time = datetime.datetime.now() + datetime.timedelta(seconds=1.0)

        res, _ = run(valid_time, "body")
        assert "Reminder scheduled for" in res

    def test_when_in_past(self, run):
        """
        Tests that a reminder can not be scheduled for a time which has already
        passed.
        """
        time_in_past = datetime.datetime.min

        with pytest.raises(TimeIsInPastError) as excinfo:
            run(time_in_past, "body")
        assert "time of the reminder is in the past" in str(excinfo.value)

    def test_os_not_supported(self, run, mock_os_not_supported):
        """
        Tests that trying to create a reminder on a OS which is currently not
        supported will raise an error indicating this
        """
        valid_time = datetime.datetime.now() + datetime.timedelta(seconds=20.0)

        with pytest.raises(OSNotSupportedError) as excinfo:
            run(valid_time, "body")
        assert "Not able to create a reminder in the OS" in str(excinfo.value)
