from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRegExp, pyqtSlot
from PyQt5.QtGui import QRegExpValidator, QValidator
from fuzzywuzzy import fuzz
import os

from lib.settings import SETTINGS, update_settings

VALID = 2  # value of state enum representing valid state after validation
EMAIL_REGEX = "^([a-zA-Z0-9]+[\\._-]?[a-zA-Z0-9]+)[@](\\w+[.])+\\w{2,3}$"


class InputValidator(QRegExpValidator):
    """
    A custom validator class that will set mark the parent object as invalid if
    the validator fails.
    """

    def __init__(self, *args, allow_empty=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_empty = allow_empty

    def validate(self, text: str, pos: int):
        state, text, pos = super(InputValidator, self).validate(text, pos)
        selector = {
            QValidator.Invalid: "invalid",
            QValidator.Intermediate: "intermediate",
            QValidator.Acceptable: "acceptable",
        }[state]

        if selector == "invalid" or (not self.allow_empty and selector == "intermediate"):
            self.parent().setProperty("invalid", True)
        else:
            self.parent().setProperty("invalid", False)

        self.parent().style().unpolish(self.parent())
        self.parent().style().polish(self.parent())
        return state, text, pos


class ContactsView(QtWidgets.QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(ContactsView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(8)

        self.initial_state = SETTINGS  # store the settings to restore it if needed

        self.title = QtWidgets.QLabel("Contacts")
        self.title.setObjectName("viewTitle")
        self.title.setMinimumHeight(48)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setMaximumWidth(960)
        scroll_area.setWidgetResizable(True)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(scroll_area)

        widget = QtWidgets.QWidget()
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(8)

        row = 0
        layout.addWidget(self.title, row, 0)

        row += 1
        self.search_name = QtWidgets.QLineEdit()
        self.search_name.setPlaceholderText("Search for a name in your contact list...")
        self.search_name.installEventFilter(self)
        layout.addWidget(self.search_name, row, 0)

        self.entries = dict()
        for name, contact in SETTINGS["contacts"].items():
            row += 1
            entry = ContactEntryView(name, contact)
            self.entries[name] = entry
            layout.addWidget(entry, row, 0)

        # If needed make space below empty
        row += 1
        layout.addWidget(QtWidgets.QLabel(""), row, 0)
        layout.setRowStretch(row, 1)
        layout.setColumnStretch(0, 1)

        self.setLayout(main_layout)
        widget.setLayout(layout)
        scroll_area.setWidget(widget)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.search_name:
            if self.search_name.hasFocus():
                query = self.search_name.text()
                if len(query) == 0 or (len(query) == 1 and event.key() == QtCore.Qt.Key_Backspace):
                    for view in self.entries.values():
                        view.show()
                else:
                    for name, view in self.entries.items():
                        if fuzz.partial_ratio(name, query) >= 50:
                            view.show()
                        else:
                            view.hide()
        return super().eventFilter(obj, event)
            

class ContactEntryView(QtWidgets.QFrame):
    def __init__(self, name, contact):
        super(ContactEntryView, self).__init__()
        layout = QtWidgets.QGridLayout()

        self.name_label = QtWidgets.QLineEdit(name)
        self.name_label.setObjectName("fontBold")
        layout.addWidget(self.name_label, 0, 0)

        self.email_address_label = QtWidgets.QLineEdit("")
        self.email_address_label.setObjectName("fontFaint")
        if contact["email"] and contact["email"]["address"]:
            self.email_address_label.setText(contact["email"]["address"])
            layout.addWidget(self.email_address_label, 1, 0)

        self.setLayout(layout)


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app
    import sys

    appctxt, window = initialize_app()
    window.set_active_view(4)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
