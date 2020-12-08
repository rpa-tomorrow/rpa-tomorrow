import sys
import pytest

# This solves an issue with not being able to import modules from the lib/
# folder in the test files
sys.path.append(".")
sys.path.append("..")

from lib.utils.crypt import Crypt  # Noqa: E402


@pytest.fixture(scope="session", autouse=False)
def monkeymodule():
    """
    Fixture that makes it possible to use monkeypatch in another session scoped
    fixture
    """
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture
def user_with_config():
    """
    A mocked user with complete config, the yielded dictionary will have
    to be monkeypatched into your test to work.

    Example:
    mocking SETTINGS in lib.automate.modules.schedule is done by adding
    monkeypatch.setattr(
        "lib.automate.modules.schedule.SETTINGS",
        user_with_config
    )
    before the Schedule object is created and yielded
    """
    crypt = Crypt()
    user = {
        "email": {
            "address": "johndoe@email.com",
            "host": "localhost",
            "password": crypt.encrypt("mypass"),
            "port": None,
            "ssl": False,
            "username": "johndoe@email.com",
        },
        "language": "english",
        "language_version": "0.0.1",
        "name": "John Doe",
    }
    nlp_models = {
        "basic": "en_rpa_simple",
        "email": "en_rpa_simple_email",
        "reminder": "en_rpa_simple_reminder",
        "schedule": "en_rpa_simple_calendar",
        "spacy_md": "en_core_web_md",
        "spacy_sm": "en_core_web_sm",
        "ner": "xx_ent_wiki_sm",
    }
    meeting = {"standard_duration": 15}
    contacts = {
        "Hugo Wangler": {"email": {"address": "hugo@email.com"}},
        "Niklas": {"email": {"address": "niklas@email.com"}},
        "Viktor": {"email": {"address": "viktor@email.com"}},
        "Mark": {"email": {"address": "mark@email.com"}},
        "Aron": {"email": {"address": "aron@email.com"}},
        "Alexander": {"email": {"address": "alexander@email.com"}},
    }
    yield {"user": user, "nlp_models": nlp_models, "meeting": meeting, "contacts": contacts}


@pytest.fixture(scope="session", autouse=False)
def session_user_with_config():
    """ Fixture needed when mocking settings in session scoped fixtures """
    crypt = Crypt()
    user = {
        "email": {
            "address": "johndoe@email.com",
            "host": "localhost",
            "password": crypt.encrypt("mypass"),
            "port": None,
            "ssl": False,
            "username": "johndoe@email.com",
        },
        "language": "english",
        "language_version": "0.0.1",
        "name": "John Doe",
    }
    nlp_models = {
        "basic": "en_rpa_simple",
        "email": "en_rpa_simple_email",
        "reminder": "en_rpa_simple_reminder",
        "schedule": "en_rpa_simple_calendar",
        "spacy_md": "en_core_web_md",
        "spacy_sm": "en_core_web_sm",
        "ner": "xx_ent_wiki_sm",
    }
    meeting = {"standard_duration": 15}
    contacts = {
        "Hugo Wangler": {"email": {"address": "hugo@email.com"}},
        "Niklas": {"email": {"address": "niklas@email.com"}},
        "Viktor": {"email": {"address": "viktor@email.com"}},
        "Mark": {"email": {"address": "mark@email.com"}},
        "Aron": {"email": {"address": "aron@email.com"}},
        "Alexander": {"email": {"address": "alexander@email.com"}},
    }
    yield {"user": user, "nlp_models": nlp_models, "meeting": meeting, "contacts": contacts}
