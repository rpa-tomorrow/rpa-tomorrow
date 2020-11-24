import yaml
import datetime
import uuid


class Model:
    def __init__(self, filename, processes=None):
        self.filename = filename
        self.absolute_path = None  # TODO(alexander): maybe add default path in settings
        self.processes = processes or []

    def save(self, filepath=None):
        path = filepath or self.absolute_path
        if not path:
            path = self.filename + ".yaml"
        if not self.absolute_path:
            self.absolute_path = path

        data = dict()
        data["filename"] = self.filename
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
            if proc["kind"].classname == "EntryPointModel":
                model = EntryPointModel()
                model.load(proc)
                self.processes.append(model)
            elif proc["kind"].classname == "SendModel":
                model = SendModel()
                model.load(proc)
                self.processes.append(model)
            elif proc["kind"].classname == "ReminderModel":
                model = ReminderModel()
                model.load(proc)
                self.processes.append(model)
            elif proc["kind"].classname == "ScheduleModel":
                model = ScheduleModel()
                model.load(proc)
                self.processes.append(model)
            else:
                return  # TODO(Alexander): report error


class ProcessModel:
    def __init__(self):
        self.classname = type(self).__name__
        self.id = uuid.uuid4()
        self.name = "Unknown"
        self.query = ""
        self.x = 32  # NOTE(alexander): not really useful for automation part, but needed to recreate the GUI
        self.y = 32
        self.width = 260
        self.height = 320
        self.out_next = -1  # NOTE(alexander): next process id, index into processes array in Model

    def save(self):
        data = dict()
        data["classname"] = self.classname
        data["id"] = self.id
        data["name"] = self.name
        data["query"] = self.query
        data["x"] = self.x
        data["y"] = self.y
        data["width"] = self.width
        data["height"] = self.height
        data["out_next"] = self.out_next
        return data

    def load(self, data):
        self.name = data["name"] or "Unknown"
        self.id = data["id"] or uuid.uuid4()
        self.query = data["query"] or ""
        self.x = data["x"] or 32
        self.y = data["y"] or 32
        self.width = data["width"] or 260
        self.height = data["height"] or 320
        self.out_next = data["out_next"] or -1


class EntryPointModel(ProcessModel):
    def __init__(self):
        super(EntryPointModel, self).__init__()
        self.name = "main"
        self.width = 120
        self.height = 70

    def save(self):
        return super(EntryPointModel, self).save()

    def load(self, data):
        super(EntryPointModel, self).load(data)


class BasicModel(ProcessModel):  # NOTE(alexander): abstract model, should never be used directlye
    def __init__(self):
        super(BasicModel, self).__init__()
        self.recipients = ""
        self.when = datetime.datetime.now()
        self.body = ""

    def save(self):
        data = super(BasicModel, self).save()
        data["recipients"] = [x.strip() for x in self.recipients.split(",")]
        print(data["recipients"])
        data["when"] = str(self.when)
        data["body"] = str(self.body)
        return data

    def load(self, data):
        super(BasicModel, self).load(data)
        self.recipients = ", ".join(str(data["recipients"])).strip()
        self.when = data["when"]
        self.body = data["body"]

    def setRecipients(self, text):
        self.recipients = text

    def setWhen(self, date):
        self.when = date

    def setBody(self, text):
        self.body = text


# NOTE(alexander): avoiding copy and paste I use inheritance instead, but this is not final!!!
class SendModel(BasicModel):
    def __init__(self):
        super(SendModel, self).__init__()
        self.name = "Send"

    def save(self):
        return super(SendModel, self).save()

    def load(self, data):
        super(SendModel, self).load(data)


class ReminderModel(BasicModel):
    def __init__(self):
        super(ReminderModel, self).__init__()
        self.name = "Reminder"

    def save(self):
        return super(ReminderModel, self).save()

    def load(self, data):
        super(ReminderModel, self).load(data)


class ScheduleModel(BasicModel):
    def __init__(self):
        super(ScheduleModel, self).__init__()
        self.name = "Schedule"

    def save(self):
        return super(ScheduleModel, self).save()

    def load(self, data):
        super(ScheduleModel, self).load(data)
