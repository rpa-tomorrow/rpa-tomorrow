from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

from process_block_demo import ProcessEditorView
from chatbot_demo import ChatbotView

import sys

PROCESS_EDITOR_VIEW = 0
CHATBOT_VIEW = 1

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RPA Tomorrow")
        self.setFont(QFont("Segoe UI", 10))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Main frame, almost everything goes here
        self.main_layout = QStackedLayout()
        # self.main_layout.setContentsMargins(4, 4, 4, 4)
        main = QWidget()

        self.main_layout.addWidget(ProcessEditorView())
        self.main_layout.addWidget(ChatbotView())
        main.setLayout(self.main_layout)
        
        layout.addWidget(main)

        # Bottom frame, display info, e.g. running jobs etc.
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(8, 0, 8, 0)
        bottom = QWidget()
        bottom.setStyleSheet("background-color: lightgray")
        bottom.setMaximumHeight(24)
        bottom.setMinimumHeight(24)
        self.info_label = QLabel("Done!")
        bottom_layout.addWidget(self.info_label)
        bottom.setLayout(bottom_layout)

        layout.addWidget(bottom)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.create_file_menu()

    def create_file_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        action_demo_process = QAction("Demo Process Editor", self)
        action_demo_process.triggered.connect(lambda: self.set_active_view(PROCESS_EDITOR_VIEW))

        action_demo_chatbot = QAction("Demo Chatbot", self)
        action_demo_chatbot.triggered.connect(lambda: self.set_active_view(CHATBOT_VIEW))

        action_file_exit = QAction("Exit", self)
        action_file_exit.triggered.connect(exit_program)

        file_menu.addAction(action_demo_process)
        file_menu.addAction(action_demo_chatbot)
        file_menu.addAction(action_file_exit)

    def set_active_view(self, view):
        self.main_layout.setCurrentIndex(view)
        self.update()

    def set_info_message(self, msg):
        self.info_label.setText(msg)

def exit_program():
    sys.exit(0)

if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
