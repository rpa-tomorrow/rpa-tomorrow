from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QFile

from design_view import DesignView
from settings_view import SettingsView

import sys

from lib.settings import load_settings

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RPA Tomorrow")

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.menu = SideMenuBar(self)
        self.content = ContentFrame(self)
        self.bottom = BottomInfoBar()

        layout.addWidget(self.menu,    0, 0, 2, 1)
        layout.addWidget(self.content, 0, 1)
        layout.addWidget(self.bottom,  1, 1)
        layout.setHorizontalSpacing(0);
        layout.setVerticalSpacing(0);

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_file_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        action_demo_process = QAction("Demo Process Editor", self)
        action_demo_process.triggered.connect(lambda: self.set_active_view(PROCESS_EDITOR_VIEW))

        action_demo_chatbot = QAction("Demo Chatbot", self)
        action_demo_chatbot.triggered.connect(lambda: self.set_active_view(CHATBOT_VIEW))

        action_demo_chatbot = QAction("Settings", self)
        action_demo_chatbot.triggered.connect(lambda: self.open_settings_window)

        action_file_exit = QAction("Exit", self)
        action_file_exit.triggered.connect(exit_program)

        file_menu.addAction(action_demo_process)
        file_menu.addAction(action_demo_chatbot)
        file_menu.addAction(action_file_exit)

    def set_active_view(self, view):
        self.content.set_active_view(view)
        self.update()

    def set_info_message(self, msg):
        self.bottom.info_label.setText(msg)
        self.update()

    def open_settings_window(self):
        if self.settings_view:
            self.settings_view = SettingsView();

class ContentFrame(QFrame):
    def __init__(self, main_window, *args, **kwargs):
        super(ContentFrame, self).__init__(*args, **kwargs)
        self.layout = QStackedLayout()

        self.main_window = main_window
        self.design_view = DesignView(main_window)
        self.settings_view = SettingsView()

        self.layout.addWidget(self.design_view)
        self.layout.addWidget(self.settings_view)
        self.setLayout(self.layout)

    def set_active_view(self, view):
        self.layout.setCurrentIndex(view);

class MenuBarButton(QToolButton):
    def __init__(self, parent, view_id, text, *args, **kwargs):
        super(MenuBarButton, self).__init__(*args, **kwargs)
        self.setFixedSize(56, 56)
        self.setMaximumHeight(56)
        self.setText(text)
        self.setCheckable(True)
        self.parent = parent
        self.view_id = view_id
        self.clicked.connect(self.set_active_view)

    def set_active_view(self):
        self.parent.set_active_view(self, self.view_id)

class SideMenuBar(QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SideMenuBar, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 0, 4)

        self.parent = parent;
        self.setMaximumWidth(48+12)

        self.items = []
        self.items.append(MenuBarButton(self, 0, "\uf044"))
        self.items.append(MenuBarButton(self, 1, "\uf0c7"))
        self.items.append(MenuBarButton(self, 2, "\uf07c"))
        self.items.append(MenuBarButton(self, 3, "\uf04b"))
        self.items.append(MenuBarButton(self, 4, "\uf013"))
        self.items.append(MenuBarButton(self, 5, "\uf05a"))

        self.items[0].setChecked(True)

        for item in self.items:
            layout.addWidget(item)
        layout.insertStretch(-1, 1);

        self.setLayout(layout)

    def set_active_view(self, target, view):
        for item in self.items:
            item.setChecked(False)
        target.setChecked(True)
        self.parent.set_active_view(view);

class BottomInfoBar(QFrame):
    def __init__(self, *args, **kwargs):
        super(BottomInfoBar, self).__init__(*args, **kwargs)
        layout = QHBoxLayout()
        # layout.setContentsMargins(8, 0, 8, )
        self.setMaximumHeight(32)

        self.info_label = QLabel("Done!")
        self.running_tasks_btn = QToolButton()
        self.running_tasks_btn.setText("\uf0ae")

        layout.addWidget(self.info_label)
        layout.addStretch(1)
        layout.addWidget(self.running_tasks_btn)

        self.setLayout(layout)

def exit_program():
    sys.exit(0)

if __name__ == '__main__':
    load_settings()
    appctxt = ApplicationContext()
    window = MainWindow()

    # Load base stylesheet
    stylesheet = ""
    with open("../qss/base.qss", "r") as fh:
        stylesheet += fh.read()

    with open("../qss/dark-theme.qss", "r") as fh:
        stylesheet += fh.read()

    window.setStyleSheet(stylesheet);
    window.resize(1200, 800)
    window.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
