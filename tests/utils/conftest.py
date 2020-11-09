import pytest


@pytest.fixture
def four_local_contacts(monkeypatch):
    four_local_contacts = {
        "contacts": {
            "hugo": {"email": {"address": "hugo@email.com"}},
            "niklas": {"email": {"address": "niklas@email.com"}},
            "mark": {"email": {"address": "mark@email.com"}},
            "hugotwo": {"email": {"address": "hugotwo@email.com"}},
        }
    }
    monkeypatch.setattr("lib.utils.contacts.SETTINGS", four_local_contacts)
