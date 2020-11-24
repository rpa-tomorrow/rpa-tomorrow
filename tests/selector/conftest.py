import pytest

from lib.selector.selector import ModuleSelector


@pytest.fixture(scope="session", autouse=False)
def selector(monkeymodule, session_user_with_config):
    """
    Yields a module selector

    This fixture will only be executed once since the scope is
    session, this prevents having to load the models for every test.
    """

    # mock settings everywhere
    monkeymodule.setattr("lib.selector.selector.SETTINGS", session_user_with_config)
    monkeymodule.setattr("lib.automate.SETTINGS", session_user_with_config)
    monkeymodule.setattr("lib.automate.modules.schedule.SETTINGS", session_user_with_config)
    selector = ModuleSelector()
    yield selector


@pytest.fixture
def no_automate(monkeypatch):
    """
    Fixture that just returns the processed text instead of sending it to the
    automation module for execution
    """

    def mock_send_automate(self, verb, text):
        return {"verb": verb, "text": text}

    monkeypatch.setattr("lib.selector.selector.ModuleSelector._send_automate", mock_send_automate)


class MockTask:
    """
    A mocked task which has an execute function that just returns a response
    """

    def execute(self):
        """ The mocked response """
        return "this is a response"


@pytest.fixture
def mock_task_execute(monkeypatch):
    """
    Fixture that will mock the execute function of the prepared tasks
    """

    def mock_send_automate(self, verb, text):
        mock = MockTask()
        return mock

    monkeypatch.setattr("lib.selector.selector.ModuleSelector._send_automate", mock_send_automate)


@pytest.fixture
def example_tasks():
    reminder_task = "remind me to eat in 30 seconds"
    schedule_task = "schedule a meeting with Mark at 15:00"
    email_task = "send an email to John saying hello mate"
    remove_task = "remove the meeting at 15:00"

    yield {"remind": reminder_task, "schedule": schedule_task, "send": email_task, "remove": remove_task}
