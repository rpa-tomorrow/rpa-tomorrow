from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import sys
import resources  # noqa: F401

sys.path.append(".")
from lib.settings import load_settings, SETTINGS  # noqa: E402

import process_models as proc_model  # noqa: E402
from design_view import DesignView  # noqa: E402
from file_view import FileView  # noqa: E402
from play_view import PlayView  # noqa: E402
from contacts_view import ContactsView  # noqa: E402
from settings_view import SettingsView  # noqa: E402


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RPA Tomorrow")

        self.layout = QtWidgets.QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.model = proc_model.Model("untitled")

        self.bottom = BottomInfoBar()
        self.menu = SideMenuBar(self)
        self.content = ContentFrame(self)
        self.modal = None

        self.layout.addWidget(self.menu, 0, 0, 2, 1)
        self.layout.addWidget(self.content, 0, 1)
        self.layout.addWidget(self.bottom, 1, 1)
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)

        widget = QtWidgets.QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)

    def resizeEvent(self, event):
        QtWidgets.QMainWindow.resizeEvent(self, event)
        if self.modal:
            self.modal.resize(self.width(), self.height())

    def set_active_view(self, view):
        self.content.set_active_view(view)
        self.menu.set_active_view(view)
        self.update()

    def set_info_message(self, msg):
        self.bottom.info_label.setText(msg)
        self.update()

    def open_settings_window(self):
        if self.settings_view:
            self.settings_view = SettingsView()


class ContentFrame(QtWidgets.QFrame):
    def __init__(self, main_window, *args, **kwargs):
        super(ContentFrame, self).__init__(*args, **kwargs)
        self.layout = QtWidgets.QStackedLayout()

        self.main_window = main_window
        self.design_view = DesignView(main_window)
        self.save_view = FileView(main_window, self.design_view, self.main_window.model, True)
        self.load_view = FileView(main_window, self.design_view, self.main_window.model, False)
        self.play_view = PlayView(main_window, self.design_view.process_editor)
        self.contacts_view = ContactsView(main_window)
        self.settings_view = SettingsView(main_window)
        self.info_view = QtWidgets.QFrame()

        self.layout.addWidget(self.design_view)
        self.layout.addWidget(self.save_view)
        self.layout.addWidget(self.load_view)
        self.layout.addWidget(self.play_view)
        self.layout.addWidget(self.contacts_view)
        self.layout.addWidget(self.settings_view)
        self.layout.addWidget(self.info_view)
        self.setLayout(self.layout)

    def set_active_view(self, view):
        self.layout.setCurrentIndex(view)


class MenuBarButton(QtWidgets.QToolButton):
    def __init__(self, parent, view_id, name, text, *args, **kwargs):
        super(MenuBarButton, self).__init__(*args, **kwargs)
        self.setFixedSize(84, 84)
        self.setMaximumHeight(84)
        self.setText(text)
        self.setCheckable(True)
        self.parent = parent
        self.view_id = view_id
        self.clicked.connect(self.set_active_view)
        self.label = QtWidgets.QLabel(name, self)
        self.label.setMinimumWidth(84)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.move(0, 50)

    def set_active_view(self):
        self.parent.set_active_view(self.view_id)
        self.parent.parent.set_active_view(self.view_id)


class SideMenuBar(QtWidgets.QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SideMenuBar, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.parent = parent
        self.setMaximumWidth(84)

        self.items = []
        self.items.append(MenuBarButton(self, 0, "Design", "\uf044"))
        self.items.append(MenuBarButton(self, 1, "Save", "\uf0c7"))
        self.items.append(MenuBarButton(self, 2, "Load", "\uf115"))
        self.items.append(MenuBarButton(self, 3, "Run", "\uf04b"))
        self.items.append(MenuBarButton(self, 4, "Contacts", "\uf007"))
        self.items.append(MenuBarButton(self, 5, "Settings", "\uf013"))
        self.items.append(MenuBarButton(self, 6, "Info", "\uf05a"))

        self.items[0].setChecked(True)

        for item in self.items:
            layout.addWidget(item)
        layout.insertStretch(-1, 1)

        self.setLayout(layout)

    def set_active_view(self, view):
        for i in range(0, len(self.items)):
            item = self.items[i]
            if i == view:
                item.setChecked(True)
            else:
                item.setChecked(False)


class BottomInfoBar(QtWidgets.QFrame):
    def __init__(self, *args, **kwargs):
        super(BottomInfoBar, self).__init__(*args, **kwargs)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(8, 0, 8, 0)
        self.setMaximumHeight(32)
        self.info_label = QtWidgets.QLabel("Done!")
        self.info_label.setMinimumHeight(32)
        self.info_label.setMaximumHeight(32)
        layout.addWidget(self.info_label)
        self.setLayout(layout)


def exit_program():
    sys.exit(0)


def initialize_app():
    load_settings()
    appctxt = ApplicationContext()
    window = MainWindow()

    QtGui.QFontDatabase.addApplicationFont(":/fontawesome.ttf")

    # Load stylesheet
    font_family = "Roboto, Segoe UI, Arial"
    font_size = "12pt"
    if SETTINGS["editor"]["font-family"]:
        font_family = SETTINGS["editor"]["font-family"]
    if SETTINGS["editor"]["font-size"]:
        font_size = SETTINGS["editor"]["font-size"] + "pt"

    stylesheet = (
        """
* {
    font-family: """
        + font_family
        + """;
    font-size: """
        + font_size
        + """;
}
"""
    )

    old_dir = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open("../qss/base.qss", "r") as fh:
        stylesheet += fh.read()

    with open("../qss/" + SETTINGS["editor"]["theme"] + ".qss", "r") as fh:
        stylesheet += fh.read()
    os.chdir(old_dir)

    window.setStyleSheet(stylesheet)
    window.resize(1200, 800)
    window.show()
    window.set_info_message(
        "Hello welcome to RPA Tomorrow! Start by creating your "
        + "first automation task by writing something at the top of the window."
    )
    return appctxt, window


if __name__ == "__main__":
    appctxt, window = initialize_app()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
