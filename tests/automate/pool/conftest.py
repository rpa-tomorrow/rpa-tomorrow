import pytest

from lib.automate.pool import ModelPool, SharedModel


@pytest.fixture
def empty_pool():
    return ModelPool([])


@pytest.fixture
def init_pool():
    yield ModelPool


@pytest.fixture
def init_shared_model():
    yield SharedModel
