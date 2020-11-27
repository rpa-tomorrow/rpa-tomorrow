from lib import NotImplementedError


class Followup:
    type = None
    question = None

    def handle_cli(self):
        raise NotImplementedError("Method not implemented")


class MultiFollowup(Followup):
    def __init__(self, question: str, options: [(str, str)], callback, enable_none: bool):
        self.question = question
        self.answer = None
        self.options = options
        self.callback = callback
        self.enable_none = enable_none

    def handle_cli(self):
        followup_str = f"{self.question}\n"
        for i, (_, text) in enumerate(self.options):
            followup_str += f"[{i+1}] {text}\n"
        followup_str += f"\n[0] None of the above \nPlease choose one (0-{len(self.options)})"

        print(followup_str, end=": ", flush=True)
        input_str = input()

        try:
            choice = int(input_str) - 1
        except Exception:
            return self.handle_cli()
        if choice < -1 or choice >= len(self.options):
            return self.handle_cli()
        self.answer = self.options[choice][0]
        return self.callback(self)


class StringFollowup(Followup):
    def __init__(self, question: str, callback, default_answer: str = None):
        self.question = question
        self.callback = callback
        self.answer = default_answer
        self.default_answer = default_answer

    def handle_cli(self):
        print(self.question, end=": ", flush=True)
        input_str = input()
        if input_str:
            self.answer = input_str
        elif self.default_answer is None:
            return self.handle_cli()
        return self.callback(self)


class BooleanFollowup(Followup):
    def __init__(self, question: str, callback, default_answer: bool = None):
        self.question = question
        self.callback = callback
        self.answer = default_answer
        self.default_answer = default_answer

    def handle_cli(self):
        if self.default_answer is None:
            end = " [y/n]:"
        elif self.default_answer:
            end = " [Y/n]:"
        else:
            end = " [y/N]:"
        print(self.question, end=end, flush=True)
        input_str = input()
        if input_str == "" and self.default_answer is not None:
            self.answer = self.default_answer
        elif input_str.lower() in ["y", "yes"]:
            self.answer = True
        elif input_str.lower() in ["n", "no"]:
            self.answer = False
        else:
            return self.handle_cli()
        return self.callback(self)
