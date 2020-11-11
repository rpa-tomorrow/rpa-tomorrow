
class Model():
    def __init__(self, filename, processes=None):
        self.filename = filename
        self.absolute_path = filename # TODO(alexander): maybe add default path in settings 
        self.processes = processes or []

    def save(self):
        return None

    def load(self):
        return None
        
    
class ProcessModel():
    def __init__(self, name, query, x=32, y=32, width=260, height=320):
        self.name = name
        self.query = query
        self.x = x # NOTE(alexander): not really useful for automation part, but needed to recreate the GUI
        self.y = y
        self.width = width
        self.height = height

class SendEmailModel(ProcessModel):
    def __init__(self, name, query, recipients, when, body, x=32, y=32, width=260, height=320):
        super(SendEmailModel, self).__init__(name, query, x, y, width, height)
        self.recipients = recipients
        self.when = when
        self.body = body

    def setRecipients(self, text):
        self.recipients = text
        
    def setWhen(self, date):
        self.when = date
        
    def setBody(self, text):
        self.body = text
