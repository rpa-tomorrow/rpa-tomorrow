import pytest
from datetime import datetime, timedelta
from lib.automate.google import Google, Calendar


class CalendarMock(Calendar):
    """
    A calendar mock where event creation just returns the parameters of the
    event
    """

    def __init__(self, settings):
        self.settings = settings

    def event(self, start, end, attendees, body):
        """ Returns the parameters of the event """
        return {"start": start, "end": end, "attendees": attendees, "body": body}

    def get_events(self):
        """ Returns a list of events in the mocked calendar """
        start_time_1 = datetime.now() + timedelta(hours=1.0)
        end_time_1 = datetime.now() + timedelta(hours=2.0)
        start_time_2 = datetime.now() + timedelta(hours=5.0)
        end_time_2 = datetime.now() + timedelta(hours=7.0)

        return [
            {
                "summary": "test",
                "attendees": [{"email": "niklas@email.com"}],
                "start": {"date": start_time_1.isoformat(), "dateTime": start_time_1.isoformat()},
                "end": {"date": end_time_1.isoformat(), "dateTime": end_time_1.isoformat()},
            },
            {
                "summary": "another one",
                "attendees": [{"email": "hugo@email.com"}],
                "start": {"date": start_time_2.isoformat(), "dateTime": start_time_2.isoformat()},
                "end": {"date": end_time_2.isoformat(), "dateTime": end_time_2.isoformat()},
            },
        ]


class CalendarNeverBusyMock(CalendarMock):
    """ Mock of a calendar where the user or attendees will never be busy """

    def __init__(self, settings):
        super().__init__(settings)

    def freebusy(self, start, end, attendees_email):
        """ Returns empty list to simulate no other meetings during time """
        return []


class GoogleMock(Google):
    def __init__(self, username):
        self.username = username

    def calendar(self, settings):
        return CalendarMock(settings)


class GoogleNeverBusyMock(GoogleMock):
    def __init__(self, username):
        super().__init__(username)

    def calendar(self, settings):
        return CalendarNeverBusyMock(settings)


@pytest.fixture
def calendar_not_busy(monkeypatch):
    def mock_execute(self):
        return self.event

    def mock_handle_cli(self):
        self.answer = "y"
        self.callback()

    monkeypatch.setattr("lib.automate.modules.schedule.Google", GoogleNeverBusyMock)
    monkeypatch.setattr("lib.automate.modules.schedule.Schedule.execute", mock_execute)
    monkeypatch.setattr("lib.automate.followup.BooleanFollowup.handle_cli", mock_handle_cli)


@pytest.fixture
def send_email(monkeypatch):
    """
    Fixture mocking the send email functionality to just return the email
    information instead of sending smtp
    """

    def mock_send_email(self, settings, receiver, subject, content):
        return {"settings": settings, "receiver": receiver, "subject": subject, "content": content}

    def mock_handle_cli(self):
        self.answer = "y"
        self.callback()

    monkeypatch.setattr("lib.automate.modules.send.Send.send_email", mock_send_email)
    monkeypatch.setattr("lib.automate.followup.BooleanFollowup.handle_cli", mock_handle_cli)


@pytest.fixture
def calendar_with_events(monkeypatch):
    """
    Fixture that mocks the google calendar object in remove schedule. The
    calendar has some predefined events that will be returned upon calling
    get_events.
    """

    def mock_handle_cli(self):
        self.answer = "y"
        self.callback()

    monkeypatch.setattr("lib.automate.modules.remove_schedule.Google", GoogleMock)
    monkeypatch.setattr("lib.automate.followup.BooleanFollowup.handle_cli", mock_handle_cli)


@pytest.fixture
def automate_no_handle_response(monkeypatch, user_with_config):
    """
    Fixture that simply returns the response instead of asking for input from
    the user
    """

    def mock_prepare(self, module_name, text):
        print("in mock prepare")
        sender = user_with_config["user"]
        instance = self._load_module(module_name)
        return instance.prepare(user_with_config["nlp_models"], text, sender)

    monkeypatch.setattr("lib.automate.Automate.prepare", mock_prepare)


@pytest.fixture
def remove_schedule_no_execute(monkeypatch):
    """
    Fixture that makes the remove schedule execute function just return
    the event that will be deleted
    """

    def mock_execute(self):
        return self.event

    monkeypatch.setattr("lib.automate.modules.remove_schedule.RemoveSchedule.execute", mock_execute)
