from PyQt5 import QtWidgets, QtCore
import sys

from process_models import EntryPointModel
from design_view import tasks
from lib.automate.modules.reminder import Reminder
from lib.automate.modules.schedule import Schedule
from lib.automate.modules.send import Send
from lib.settings import SETTINGS
from lib.automate.pool import ModelPool
from datetime import datetime, timedelta

class RunView(QtWidgets.QWidget):
    def __init__(self, main_window, process_editor, model, sender, *args, **kwargs):
        super(RunView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = model
        # self.threadpool = QThreadPool()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)

        self.title = QtWidgets.QLabel("Play")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)

        self.process_text_edit = ProcessTextEditView(self, self.model, sender)

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
        self.run_btn.clicked.connect(self.process_text_edit.clear_text_output)
        self.run_btn.clicked.connect(self.process_text_edit.write_text_output)

        layout.addWidget(self.name, 0, 0)
        layout.addWidget(self.run_btn, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)


class ProcessTextEditView(QtWidgets.QTextEdit):
    def __init__(self, design_view, model, sender, *args, **kwargs):
        super(ProcessTextEditView, self).__init__()
        self.design_view = design_view
        self.model = model
        self.sender = sender

        layout = QtWidgets.QGridLayout()

        self.text_edit = QtWidgets.QTextEdit(*args, **kwargs)
        self.text_edit.setReadOnly(True)
        self.setLayout(layout)
        self.text_edit.installEventFilter(self)

        self.text_output = QtWidgets.QTextBrowser(self.text_edit)

        layout.addWidget(self.text_edit, 0, 0)
        layout.addWidget(self.text_output, 0, 0)

    def clear_text_output(self):
        self.text_output.clear()

    def write_text_output(self):
        for proc in self.model.processes.values(): 
            if proc.classname != "EntryPointModel":
                print("proc.classname = ", proc.classname)
                if proc.classname == "ScheduleModel":
                    print("query = ", proc.query)
                    print("to = ", proc.recipients)
                    print("when = ", proc.when)
                    print("body = ", proc.body)

                    # print("proc.when = ", proc.when) #2020-12-11 11:03:28.395766

                    asdasd = proc.when[10:13] + "." + proc.when[14:16]
                    asd = proc.when[10:13]
                    print("asd = ", type(asd))

                    task = Schedule(ModelPool)
                    timespan = task.timespan([asd], ["22"])
                    task.prepare_processed([], timespan, proc.body, self.sender)
                    # response = task.execute()
                    # self.text_output.append(response)
                elif proc.classname == "ReminderModel":
                    print("proc.classname = ", proc.classname)
                elif proc.classname == "SendModel":
                    print("proc.classname = ", proc.classname)

                


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