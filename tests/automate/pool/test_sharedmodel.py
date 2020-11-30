import time
import threading


def acquire_and_keep(s):
    with s:
        time.sleep(1)


class TestSharedModel:
    def test_wait_if_locked(self, init_shared_model):
        """
        Check if a thread has to wait if the model in
        already in use.
        """
        s = init_shared_model("TEST", "TEST")

        t1 = threading.Thread(target=acquire_and_keep, args=s)
        t2 = threading.Thread(target=acquire_and_keep, args=s)
        t1.start()
        t2.start()
        assert t2.is_alive()

    def test_acquire_after_unlocked(self, init_shared_model):
        """
        Check if the model can be acquired after it's been
        unlocked.
        """
        s = init_shared_model("TEST", "TEST")

        t1 = threading.Thread(target=acquire_and_keep, args=s)
        t1.start()
        model = s.acquire_model()

        assert model == "TEST"
