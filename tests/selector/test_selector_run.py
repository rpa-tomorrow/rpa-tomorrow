"""
Module testing the running of tasks
"""


class TestRun:
    """ Tests that supported tasks can be run from the selector module """

    def test_invalid_task(self, selector):
        """
        Test that an invalid task will return something indicating that
        it is invalid.
        """
        response = selector.run("jashdkjsahd kjashdkjashdkjashd jahs kdh")
        assert len(response) == 1
        assert response[0] == "I did not understand"

    def test_valid_task(self, mock_task_execute, selector, example_tasks):
        """ Test that a valid task will return a response after execution """
        response = selector.run(example_tasks["remind"])
        assert len(response) == 1
        assert response[0] == "this is a response"

    def test_multiple_tasks(self, mock_task_execute, selector, example_tasks):
        """ Test that multiple tasks result in a response from each task """
        multiple_tasks_input = ". ".join(task for task in example_tasks.values())
        response = selector.run(multiple_tasks_input)
        assert len(response) == len(example_tasks)
        assert (r is not None for r in response)

    def test_multiple_tasks_mixed(self, mock_task_execute, selector, example_tasks):
        """
        Test that a mix of valid and invalid tasks will return a response
        from each executed task
        """
        multiple_tasks_input = ". ".join(task for task in example_tasks.values())
        multiple_tasks_input += "asjdasd kjaskdjas askjdkj"
        response = selector.run(multiple_tasks_input)
        assert len(response) == len(example_tasks)
        assert (r is not None for r in response)
