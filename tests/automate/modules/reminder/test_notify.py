"""
Tests regarding the notificitaion of the Reminder automation module
"""


class TestNotifyReminder:
    """Tests for creating a system notifiction"""

    def test_linux(self, notify):
        """
        Tests that a notification is made (by calling notify-send with the
        correct arguments) when the host OS is linux
        """
        # the notify fixture returns two fixture values the first one is the
        # helper function which can call the notify in Reminder and the second
        # one is the arguments with which subprocess.run was called with
        notifyFn = notify[0]
        notifyFn("linux", "this is a test reminder")
        called = notify[1]
        assert called

        # should call the notify-send package with correct arguments
        args = called[0][0]
        assert "/usr/bin/notify-send" in args
        assert "Reminder" in args
        assert "this is a test reminder" in args

    def test_unknown_os(self, notify):
        """Tests that nothing is called if the OS is not supported"""
        notifyFn = notify[0]
        notifyFn("MyAwesomeOS", "body")
        called = notify[1]
        assert not called
