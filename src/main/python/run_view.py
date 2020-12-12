from PyQt5 import QtWidgets, QtCore
import sys
from datetime import datetime

from lib.automate.modules.reminder import Reminder
from lib.automate.modules.schedule import Schedule
from lib.automate.modules.send import Send
from lib.settings import SETTINGS
from lib.automate.pool import ModelPool


class RunView(QtWidgets.QWidget):
    def __init__(self, main_window, process_editor, model, *args, **kwargs):
        super(RunView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = model
        # self.threadpool = QThreadPool()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)

        self.title = QtWidgets.QLabel("Play")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)

        self.process_text_edit = ProcessTextEditView(self, self.model)

        self.label = ProcessView("Execute tasks: ", self.process_text_edit)
        self.label.setMaximumHeight(180)

        layout.addWidget(self.title)
        layout.addWidget(self.label)
        layout.addWidget(self.process_text_edit, 1)

        self.setLayout(layout)


class ProcessView(QtWidgets.QWidget):
    def __init__(self, name, process_text_edit, *args, **kwargs):
        super(ProcessView, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        self.process_text_edit = process_text_edit

        self.name = QtWidgets.QLabel(name)
        self.run_btn = QtWidgets.QToolButton()
        self.run_btn.setText("\uf04b")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.process_text_edit.write_text_output)

        layout.addWidget(self.name, 0, 0)
        layout.addWidget(self.run_btn, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)


class ProcessTextEditView(QtWidgets.QTextEdit):
    def __init__(self, design_view, model, *args, **kwargs):
        super(ProcessTextEditView, self).__init__()
        self.design_view = design_view
        self.model = model

        layout = QtWidgets.QGridLayout()

        self.text_edit = QtWidgets.QTextEdit(*args, **kwargs)
        self.text_edit.setReadOnly(True)
        self.setLayout(layout)
        self.text_edit.installEventFilter(self)

        self.text_output = QtWidgets.QTextBrowser(self.text_edit)

        layout.addWidget(self.text_edit, 0, 0)
        layout.addWidget(self.text_output, 0, 0)

    def write_text_output(self):
        self.text_output.append("Executing tasks...")
        for proc in self.model.processes.values():
            if proc.classname != "EntryPointModel":
                # NOTE: proc.when is converted back and forth somewhere!
                if proc.classname == "ScheduleModel":
                    start_hour = proc.when[42:44].replace(",", "0")
                    start_minute = proc.when[46:48].replace(",", "0")

                    end_hour = proc.when[101:103].replace(",", "0")
                    end_minute = proc.when[105:107].replace(",", "0")

                    task = Schedule(ModelPool)
                    timespan = task.timespan([start_hour + "." + start_minute], [end_hour + "." + end_minute])
                    task.prepare_processed([], timespan, proc.body, SETTINGS["user"])
                    response = task.execute()
                    self.text_output.append(response)

                elif proc.classname == "ReminderModel":
                    if type(proc.when) == str:
                        year = int(proc.when[0:4])
                        month = int(proc.when[5:7])
                        day = int(proc.when[8:10])
                        hour = int(proc.when[11:13])
                        minute = int(proc.when[14:16])
                        second = int(proc.when[17:19])
                        dt = datetime(year, month, day, hour, minute, second)

                        task = Reminder(ModelPool)
                        task.prepare_processed([], dt, proc.body, SETTINGS["user"])
                        response = task.execute()
                        self.text_output.append(response)
                    else:
                        task = Reminder(ModelPool)
                        task.prepare_processed([], proc.when, proc.body, SETTINGS["user"])
                        response = task.execute()
                        self.text_output.append(response)

                elif proc.classname == "SendModel":
                    recipients = []
                    recipients.append(proc.recipients)

                    task = Send(ModelPool)
                    task.prepare_processed(recipients, proc.when, proc.body, SETTINGS["user"])
                    response = task.execute()
                    self.text_output.append(response)


class ProcessEntryView(QtWidgets.QFrame):
    def __init__(self, icon, heading, body):
        super(ProcessEntryView, self).__init__()
        layout = QtWidgets.QGridLayout()

        icon = QtWidgets.QLabel(icon)
        icon.setObjectName("processEntryIcon")

        heading = QtWidgets.QLabel(heading)
        heading.setObjectName("processEntryHeading")

        layout.addWidget(icon, 0, 0, 2, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(heading, 0, 1)
        layout.addWidget(QtWidgets.QLabel(body), 1, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)
        self.setMaximumHeight(48)


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(3)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
