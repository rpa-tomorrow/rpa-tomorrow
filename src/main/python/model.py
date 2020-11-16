import yaml


INVALID_MODEL = 0
PROCESS_MODEL = 1
SEND_EMAIL_MODEL = 2


class Model:
    def __init__(self, filename, processes=None):
        self.filename = filename
        self.absolute_path = None  # TODO(alexander): maybe add default path in settings
        self.processes = processes or []

    def save(self, filepath=None):
        path = filepath or self.absolute_path
        if not self.absolute_path:
            self.absolute_path = path

        data = dict()
        data["filename"] = self.filename
        data["absolute_path"] = self.absolute_path
        data["processes"] = list()
        for proc in self.processes:
            data["processes"].append(proc.save())

        with open(path, "w") as fh:
            yaml.dump(data, fh, default_flow_style=False)

    def load(self, filepath):
        data = None
        with open(filepath, "r") as fh:
            data = yaml.safe_load(fh)
        if not data:
            return  # TODO(alexander): report loading errors
        self.filename = data["filename"]
        self.absolute_path = filepath
        self.processes.clear()
        for proc in data["processes"]:
            if proc["kind"] == INVALID_MODEL:
                return  # TODO(Alexander): report error
            if proc["kind"] == PROCESS_MODEL:
                model = ProcessModel()
                model.load(proc)
                self.processes.append(model)
            if proc["kind"] == SEND_EMAIL_MODEL:
                model = SendEmailModel()
                model.load(proc)
                self.processes.append(model)


class ProcessModel:
    def __init__(self, name="", query="", x=32, y=32, width=260, height=320):
        self.kind = PROCESS_MODEL
        self.name = name
        self.query = query
        self.x = x  # NOTE(alexander): not really useful for automation part, but needed to recreate the GUI
        self.y = y
        self.width = width
        self.height = height

    def save(self):
        data = dict()
        data["name"] = self.name
        data["kind"] = self.kind
        data["query"] = self.query
        data["x"] = self.x
        data["y"] = self.y
        data["width"] = self.width
        data["height"] = self.height
        return data

    def load(self, data):
        self.name = data["name"]
        self.query = data["query"]
        self.x = data["x"]
        self.y = data["y"]
        self.width = data["width"]
        self.height = data["height"]


class SendEmailModel(ProcessModel):
    def __init__(self, name="", query="", recipients="", when=None, body="", x=32, y=32, width=260, height=320):
        super(SendEmailModel, self).__init__(name, query, x, y, width, height)
        self.kind = SEND_EMAIL_MODEL
        self.recipients = recipients
        self.when = when
        self.body = body

    def save(self):
        data = super(SendEmailModel, self).save()
        data["recipients"] = [x.strip() for x in ",".split(self.recipients)]
        data["when"] = str(self.when)
        data["body"] = str(self.body)

    def load(self, data):
        super(SendEmailModel, self).load(data)
        self.recipients = ", ".join(str(data["recipients"])).strip()
        self.when = data["when"]
        self.body = data["body"]

    def setRecipients(self, text):
        self.recipients = text

    def setWhen(self, date):
        self.when = date

    def setBody(self, text):
        self.body = text
