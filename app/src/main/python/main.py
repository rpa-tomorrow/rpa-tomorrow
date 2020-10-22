from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import *

import sys

def create_main_window(*args, **kwargs):
    window = QMainWindow(*args, **kwargs)
    window.setWindowTitle("RPA Tomorrow")

    menu_bar = window.menuBar()
    file_menu = menu_bar.addMenu("File")
    action_file_exit = QAction("Exit", window)
    action_file_exit.triggered.connect(exit_program)

    file_menu.addAction(action_file_exit)

    layout = QGridLayout()
    widget = QWidget()
    widget.setLayout(layout)
    window.setCentralWidget(widget)
    return window

def exit_program():
    sys.exit(0)

if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = create_main_window()
    window.resize(640, 480)
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
