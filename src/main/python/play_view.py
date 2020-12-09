from PyQt5 import QtWidgets, QtGui, QtCore
import sys

from design_view import tasks

responses = []

class PlayView(QtWidgets.QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(PlayView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        # self.threadpool = QThreadPool()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)

        self.title = QtWidgets.QLabel("Play")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)

        self.process_text_edit = ProcessTextEditView(self, "")
        self.process_text_edit.setMaximumHeight(180)

        self.label = ProcessView("Execute tasks: ", self.process_text_edit)
        
        layout.addWidget(self.title)
        layout.addWidget(self.label)
        layout.addWidget(self.process_text_edit)

        layout.addStretch(1)

        self.setLayout(layout)


class ProcessView(QtWidgets.QFrame):
    def __init__(self, name, process_text_edit, *args, **kwargs):
        super(ProcessView, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        self.process_text_edit = process_text_edit

        self.name = QtWidgets.QLabel(name)
        self.run_btn = QtWidgets.QToolButton()
        self.run_btn.setFont(QtGui.QFont("RPATomorrowIconFont", 24))
        self.run_btn.setText("\uf04b")
        self.run_btn.setObjectName("runButton")
        self.run_btn.clicked.connect(execute_tasks) 

        layout.addWidget(self.name, 0, 0)
        layout.addWidget(self.run_btn, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        layout.setColumnStretch(1, 1)

        self.run_btn.clicked.connect(self.process_text_edit.cleartest)
        self.run_btn.clicked.connect(self.process_text_edit.writetest)

        responses.clear()
        self.setLayout(layout)


class ProcessTextEditView(QtWidgets.QFrame):
    def __init__(self, design_view, *args, **kwargs):
        super(ProcessTextEditView, self).__init__()
        self.design_view = design_view
        layout = QtWidgets.QGridLayout()

        self.text_edit = QtWidgets.QTextEdit(*args, **kwargs)
        self.text_edit.setReadOnly(True)

        layout.addWidget(self.text_edit, 0, 0, 1, 4)
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(0, 1)
        self.setLayout(layout)
        self.text_edit.installEventFilter(self)

        self.text_output = QtWidgets.QTextBrowser(self.text_edit)

    def cleartest(self):
        self.text_output.clear() 

    def writetest(self):
        for response in responses:
            self.text_output.append(response) 


def execute_tasks():
    for task in tasks:
        response = task.execute()
        responses.append(response)




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
