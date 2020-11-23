import pytest

from lib.automate.modules.send import Send

TEST_SETTINGS = {
    "contacts": {
        "First Last": {
            "email": {
                "address": "first.last@email.com",
                "username": "first.last@email.com",
                "password": "password",
                "ssl": True,
                "host": "localhost",
                "port": 465,
            }
        },
        "John Doe": {
            "email": {
                "address": "johndoe@email.com",
                "username": None,
                "password": None,
                "ssl": False,
                "host": "localhost",
                "port": 1025,
            }
        },
    },
}


@pytest.fixture
def get_test_email(monkeypatch):
    def helper(name):
        send = Send(None)
        monkeypatch.setattr("lib.automate.modules.send.SETTINGS", TEST_SETTINGS)
        return send.get_email(name)

    yield helper
