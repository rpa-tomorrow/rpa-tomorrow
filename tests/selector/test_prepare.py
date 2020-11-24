"""
Module that tests the task preparation done on input
"""


class TestPrepare:
    """Tests for the preparation of input text"""

    def test_invalid_task(self, selector):
        """Test that an invalid task in the input is handled"""
        task = selector.prepare("hjasdalsdkjaslk jdlasjdalksjdak jkasljdajs")
        assert len(task) == 1
        assert task[0] is None

    def test_remind_task(self, selector, no_automate, example_tasks):
        """Test that a reminder task can be prepared"""
        task = selector.prepare(example_tasks["remind"])
        assert len(task) == 1
        assert task[0]["verb"] == "remind"

    def test_schedule_task(self, selector, no_automate, example_tasks):
        """Test that a schedule task can be prepared"""
        task = selector.prepare(example_tasks["schedule"])
        assert len(task) == 1
        assert task[0]["verb"] == "schedule"

    def test_send_task(self, selector, no_automate, example_tasks):
        """Test that a send task can be prepared"""
        task = selector.prepare(example_tasks["send"])
        assert len(task) == 1
        assert task[0]["verb"] == "send"

    def test_remove_task(self, selector, no_automate, example_tasks):
        """Test that a remove scheduled event task can be prepared"""
        task = selector.prepare(example_tasks["remove"])
        assert len(task) == 1
        assert task[0]["verb"] == "remove"

    def test_multiple_tasks(self, selector, no_automate, example_tasks):
        """Test that multiple tasks in the input can be prepared"""
        multiple_tasks_input = ". ".join(task for task in example_tasks.values())
        tasks = selector.prepare(multiple_tasks_input)
        assert len(tasks) == len(example_tasks)
        assert tasks[0]["verb"] == "remind"
        assert tasks[1]["verb"] == "schedule"
        assert tasks[2]["verb"] == "send"
        assert tasks[3]["verb"] == "remove"
