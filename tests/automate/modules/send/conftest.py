import pytest

from lib.automate.modules.send import Send
from lib.automate.pool import ModelPool

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
        pool = ModelPool(["xx_ent_wiki_sm"])
        send = Send(pool)
        monkeypatch.setattr("lib.automate.modules.send.SETTINGS", TEST_SETTINGS)
        return send.get_email(name)

    yield helper
