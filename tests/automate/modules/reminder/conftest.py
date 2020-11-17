"""
Fixtures of the reminder automation module
"""
import pytest
import sys

from lib.automate.modules.reminder import Reminder
from lib.automate.pool import ModelPool

@pytest.fixture
def run(monkeypatch):
    def mock_timer_start(self):
        pass

    def helper(when, body):
        reminder = Reminder(None)
        # mock the timer used to schedule the reminder
        monkeypatch.setattr("threading.Timer.start", mock_timer_start)
        reminder.prepare_processed(None, when, body, None)
        return reminder.execute()

    yield helper


@pytest.fixture
def notify(monkeypatch):
    called_with = []

    def mock_subprocess_run(*popenargs, input=None, capture_output=False, timeout=None, check=False, **kwargs):
        called_with.append(popenargs)

    def helper(os, body):
        reminder = Reminder(None)
        monkeypatch.setattr("lib.automate.modules.reminder.run", mock_subprocess_run)
        return reminder.notify(os, body)

    yield helper, called_with


@pytest.fixture
def mock_os_not_supported(monkeypatch):
    monkeypatch.setattr(sys, "platform", "MyAwesomeOS")


@pytest.fixture
def mock_os_supported(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
