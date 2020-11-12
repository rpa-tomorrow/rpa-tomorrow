from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from functools import partial
import os, sys


class FileView(QWidget):
    def __init__(self, main_window, model, *args, **kwargs):
        super(FileView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = model

        layout = QGridLayout()

        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.files_view = QListView()
        self.files_view.setModel(self.file_system_model)
        self.files_view.setRootIndex(self.file_system_model.index(os.getcwd()))
        self.files_view.doubleClicked.connect(self.enter_directory_index)

        self.current_dir_view = CurrentDirectoryView(self.files_view, self.file_system_model)

        self.filename_view = QLineEdit(self.model.filename)

        layout.addWidget(self.current_dir_view, 0, 0)
        layout.addWidget(self.files_view, 1, 0)
        layout.addWidget(self.filename_view, 2, 0)
        layout.setVerticalSpacing(8)

        self.setLayout(layout)

    def enter_directory_index(self, index):
        self.files_view.setRootIndex(index)
        self.current_dir_view.set_current_directory_index(index)


class CurrentDirectoryView(QFrame):
    def __init__(self, files_view, file_system_model, *args, **kwargs):
        super(CurrentDirectoryView, self).__init__(*args, **kwargs)
        self.files_view = files_view
        self.file_system_model = file_system_model
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.set_current_directory_index(self.files_view.rootIndex())
        self.setLayout(self.layout)

    def set_current_directory_index(self, index):
        child = self.layout.takeAt(0)
        while child:
            self.layout.removeWidget(child.widget())
            del child
            child = self.layout.takeAt(0)

        while index and index.isValid():
            btn = QPushButton(str(index.data()))
            btn.index = index
            btn.clicked.connect(partial(self.directory_button_clicked, index))
            self.layout.insertWidget(0, btn)
            index = index.parent()
            if index and index.isValid():
                self.layout.insertWidget(0, QLabel(">"))

        self.layout.addStretch(1)
        self.update()

    def directory_button_clicked(self, index):
        if index and index.isValid():
            self.files_view.setRootIndex(index)
            self.update()


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(1)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
