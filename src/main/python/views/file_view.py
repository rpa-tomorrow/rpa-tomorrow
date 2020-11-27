import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore


from views.current_directory_view import CurrentDirectory
from functools import partial
import os
import sys


class FileView(QtWidgets.QWidget):
    def __init__(self, main_window, model, *args, **kwargs):
        super(FileView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = model

        layout = QtWidgets.QGridLayout()

        self.file_system_model = QtWidgets.QFileSystemModel()
        self.file_system_model.setRootPath(QtCore.QDir.rootPath())
        self.files_view = QtWidgets.QListView()
        self.files_view.setModel(self.file_system_model)
        self.files_view.setRootIndex(self.file_system_model.index(os.getcwd()))
        self.files_view.doubleClicked.connect(self.enter_directory_index)

        self.current_dir_view = CurrentDirectory(self.files_view, self.file_system_model)

        self.filename_view = QtWidgets.QLineEdit(self.model.filename)

        layout.addWidget(self.current_dir_view, 0, 0)
        layout.addWidget(self.files_view, 1, 0)
        layout.addWidget(self.filename_view, 2, 0)
        layout.setVerticalSpacing(8)

        self.setLayout(layout)

    def enter_directory_index(self, index):
        self.files_view.setRootIndex(index)
        self.current_dir_view.set_current_directory_index(index)

# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(1)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
