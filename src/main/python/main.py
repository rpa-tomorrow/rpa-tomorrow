from fbs_runtime.application_context.PyQt5 import ApplicationContext
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import os
import sys
import resources  # noqa: F401

sys.path.append(".")
from lib.settings import load_settings, SETTINGS  # noqa: E402

import process_models as proc_model  # noqa: E402
from design_view import DesignView  # noqa: E402
from file_view import FileView  # noqa: E402
from play_view import PlayView  # noqa: E402
from settings_view import SettingsView  # noqa: E402


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("RPA Tomorrow")

        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.model = proc_model.Model("untitled")

        self.bottom = BottomInfoBar()
        self.menu = SideMenuBar(self)
        self.content = ContentFrame(self)

        layout.addWidget(self.menu, 0, 0, 2, 1)
        layout.addWidget(self.content, 0, 1)
        layout.addWidget(self.bottom, 1, 1)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def set_active_view(self, view):
        self.content.set_active_view(view)
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
        self.save_view = FileView(main_window, self.main_window.model)
        self.load_view = FileView(main_window, self.main_window.model)
        self.play_view = PlayView(main_window, self.design_view.process_editor)
        self.settings_view = SettingsView()
        self.info_view = QtWidgets.QFrame()

        self.layout.addWidget(self.design_view)
        self.layout.addWidget(self.save_view)
        self.layout.addWidget(self.load_view)
        self.layout.addWidget(self.play_view)
        self.layout.addWidget(self.settings_view)
        self.layout.addWidget(self.info_view)
        self.setLayout(self.layout)

    def set_active_view(self, view):
        self.layout.setCurrentIndex(view)


class MenuBarButton(QtWidgets.QToolButton):
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


class SideMenuBar(QtWidgets.QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SideMenuBar, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(4, 4, 0, 4)

        self.parent = parent
        self.setMaximumWidth(48 + 12)

        self.items = []
        self.items.append(MenuBarButton(self, 0, "\uf044"))
        self.items.append(MenuBarButton(self, 1, "\uf0c7"))
        self.items.append(MenuBarButton(self, 2, "\uf115"))
        self.items.append(MenuBarButton(self, 3, "\uf04b"))
        self.items.append(MenuBarButton(self, 4, "\uf013"))
        self.items.append(MenuBarButton(self, 5, "\uf05a"))

        self.items[0].setChecked(True)

        for item in self.items:
            layout.addWidget(item)
        layout.insertStretch(-1, 1)

        self.setLayout(layout)

    def set_active_view(self, target, view):
        for item in self.items:
            item.setChecked(False)
        target.setChecked(True)
        self.parent.set_active_view(view)


class BottomInfoBar(QtWidgets.QFrame):
    def __init__(self, *args, **kwargs):
        super(BottomInfoBar, self).__init__(*args, **kwargs)
        layout = QtWidgets.QHBoxLayout()
        # layout.setContentsMargins(8, 0, 8, )
        self.setMaximumHeight(32)
        # self.running_tasks_btn = QtWidgets.QToolButton()
        # self.running_tasks_btn.setText("\uf0ae")
        self.info_label = QtWidgets.QLabel("Done!")

        # layout.addWidget(self.running_tasks_btn)
        layout.addWidget(self.info_label)
        layout.addStretch(1)

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
        font_size = SETTINGS["editor"]["font-size"]

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
    return appctxt, window


if __name__ == "__main__":
    appctxt, window = initialize_app()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
