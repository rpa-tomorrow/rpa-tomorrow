import PyQt5.QtWidgets as QtWidgets

from lib.settings import SETTINGS


class SettingsView(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(8)

        self.title = QtWidgets.QLabel("Settings")
        self.title.setObjectName("viewTitle")
        self.title.setMinimumHeight(48)

        row = 0
        layout.addWidget(self.title, row, 0)

        row += 1
        self.theme = QtWidgets.QComboBox()
        self.theme.addItem("Light Theme", "light-theme")
        self.theme.addItem("Dark Theme", "dark-theme")
        self.theme.setCurrentIndex(self.theme.findData(SETTINGS["editor"]["theme"]))
        layout.addWidget(QtWidgets.QLabel("Editor theme"), row, 0)
        layout.addWidget(self.theme, row, 1)

        row += 1
        self.font_family = QtWidgets.QLineEdit(SETTINGS["editor"]["font-family"])
        layout.addWidget(QtWidgets.QLabel("Editor font"), row, 0)
        layout.addWidget(self.font_family, row, 1)

        row += 1
        self.font_size = QtWidgets.QLineEdit(SETTINGS["editor"]["font-size"])
        layout.addWidget(QtWidgets.QLabel("Editor font size"), row, 0)
        layout.addWidget(self.font_size, row, 1)

        # If needed make space below empty
        row += 1
        layout.addWidget(QtWidgets.QLabel(""), row, 0)
        layout.setRowStretch(row, 1)

        self.setLayout(layout)
