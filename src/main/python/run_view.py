from PyQt5 import QtWidgets, QtCore
import sys
from datetime import datetime, timedelta

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

        self.text_output = QtWidgets.QTextBrowser()

        self.label = ProcessView("Execute tasks: ", self)
        self.label.setMaximumHeight(180)

        layout.addWidget(self.title)
        layout.addWidget(self.label)
        layout.addWidget(self.text_output, 1)

        self.setLayout(layout)

    def write_text_output(self):
        self.text_output.clear()
        self.text_output.append("Executing tasks...")
        next_proc = None
        for proc in self.model.processes.values():
            if proc.classname == "EntryPointModel":
                next_proc_id = proc.out_next
                if next_proc_id in self.model.processes:
                    next_proc = self.model.processes[next_proc_id]
                break

        while next_proc:
            proc = next_proc
            # NOTE: proc.when is converted back and forth somewhere!
            if proc.classname == "ScheduleModel":
                recipients = []
                recipients.append(proc.recipients)

                start_hour = proc.when[42:44].replace(",", "0")
                start_minute = proc.when[46:48].replace(",", "0")

                end_hour = proc.when[101:103].replace(",", "0")
                end_minute = proc.when[105:107].replace(",", "0")

                task = Schedule(ModelPool)
                timespan = task.timespan([start_hour + "." + start_minute], [end_hour + "." + end_minute])

                # If the end time could not be parsed assume standard duration
                if timespan["end"] is None:
                    timespan["end"] = timespan["start"] + timedelta(minutes=SETTINGS["meeting"]["standard_duration"])

                task.prepare_processed(recipients, timespan, proc.body, SETTINGS["user"])
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

            next_proc_id = proc.out_next
            if next_proc_id in self.model.processes:
                next_proc = self.model.processes[next_proc_id]
            else:
                break

            # NOTE: for safety avoid recusion, even though it should not be possible to create cycles.
            if proc == next_proc:
                break


class ProcessView(QtWidgets.QWidget):
    def __init__(self, name, run_view, *args, **kwargs):
        super(ProcessView, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        self.run_view = run_view

        self.name = QtWidgets.QLabel(name)
        self.run_btn = QtWidgets.QToolButton()
        self.run_btn.setText("\uf04b")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(self.run_view.write_text_output)

        layout.addWidget(self.name, 0, 0)
        layout.addWidget(self.run_btn, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(3)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
