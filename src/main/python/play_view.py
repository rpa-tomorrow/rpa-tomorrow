from PyQt5 import QtWidgets, QtGui, QtCore
import sys


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
        layout.addWidget(self.title)

        self.example_process = ProcessView("Example Process #1")
        layout.addWidget(self.example_process)

        layout.addStretch(1)

        self.setLayout(layout)


class ProcessView(QtWidgets.QFrame):
    def __init__(self, name, *args, **kwargs):
        super(ProcessView, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()

        self.name = QtWidgets.QLabel(name)
        self.run_btn = QtWidgets.QToolButton()
        self.run_btn.setFont(QtGui.QFont("RPATomorrowIconFont", 24))
        self.run_btn.setText("\uf04b")
        self.run_btn.setObjectName("runButton")

        self.proc1 = ProcessEntryView("\uf0e0", "Send email - John Doe", "Hello world 1")
        self.proc2 = ProcessEntryView("\uf0f3", "Remind - John Doe", "Hello world 2")
        self.proc3 = ProcessEntryView("\uf271", "Schedule - John Doe", "Hello world 3")

        layout.addWidget(self.name, 0, 0)
        layout.addWidget(self.run_btn, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        layout.addWidget(self.proc1, 1, 0, 1, 2)
        layout.addWidget(self.proc2, 2, 0, 1, 2)
        layout.addWidget(self.proc3, 3, 0, 1, 2)
        layout.setColumnStretch(1, 1)
        self.setLayout(layout)


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
