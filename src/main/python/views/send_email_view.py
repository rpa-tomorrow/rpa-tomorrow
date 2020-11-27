
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

import datetime

class SendEmailView(QtWidgets.QFrame):
    def __init__(self, model):
        super(SendEmailView, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.model = model

        self.recipients = QtWidgets.QLineEdit(model.recipients)
        self.recipients.setPlaceholderText("Recipient1, Recipient2, ...")
        self.recipients.textChanged.connect(model.set_recipients)

        self.when = QtWidgets.QDateTimeEdit()
        try:
            dt = model.when
            if isinstance(model.when, str):
                dt = datetime.datetime.fromisoformat(model.when)
            self.when.setDateTime(QtCore.QDateTime(dt))
        except Exception:
            dt = datetime.datetime.now()
            self.when.setDateTime(QtCore.QDateTime(dt))
            model.when = str(dt)
        self.when.dateTimeChanged.connect(self.set_when)

        self.body = QtWidgets.QTextEdit(model.body)
        self.body.setPlaceholderText("Enter the body...")
        self.body.textChanged.connect(self.set_body)

        layout.addWidget(self.recipients)
        layout.addWidget(self.when)
        layout.addWidget(self.body)

        self.setLayout(layout)

    def set_when(self, dt):
        self.model.set_when(dt.toPyDateTime())

    def set_body(self):
        self.model.set_body(self.body.toPlainText())