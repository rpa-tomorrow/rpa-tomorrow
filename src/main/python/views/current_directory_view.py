import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
from functools import partial

class CurrentDirectory(QtWidgets.QFrame):
    def __init__(self, files_view, file_system_model, *args, **kwargs):
        super(CurrentDirectory, self).__init__(*args, **kwargs)
        self.files_view = files_view
        self.file_system_model = file_system_model
        self.layout = QtWidgets.QHBoxLayout()
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
            btn = QtWidgets.QPushButton(str(index.data()))
            btn.index = index
            btn.clicked.connect(partial(self.directory_button_clicked, index))
            self.layout.insertWidget(0, btn)
            index = index.parent()
            if index and index.isValid():
                self.layout.insertWidget(0, QtWidgets.QLabel(">"))

        self.layout.addStretch(1)
        self.update()

    def directory_button_clicked(self, index):
        if index and index.isValid():
            self.files_view.setRootIndex(index)
            self.update()