import pytest

from lib.automate.pool import NoModelFoundError


class TestPool:
    def test_not_found_exception(self, empty_pool):
        with pytest.raises(NoModelFoundError):
            empty_pool.get_shared_model("unknown")
