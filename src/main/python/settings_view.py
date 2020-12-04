from PyQt5 import QtWidgets
from PyQt5.QtCore import QRegExp, pyqtSlot
from PyQt5.QtGui import QRegExpValidator, QValidator
import os
import sys

from lib.settings import SETTINGS, get_language_versions, get_model_languages, update_settings
from lib.utils.crypt import Crypt

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


class SettingsView(QtWidgets.QWidget):
    # Dict containing the fields which are not allowed to be submitted empty
    empty_fields = {"name": False}

    def __init__(self, main_window, *args, **kwargs):
        super(SettingsView, self).__init__(*args, **kwargs)
        self.main_window = main_window

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setMaximumWidth(960)
        scroll_area.setWidgetResizable(True)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(scroll_area)

        widget = QtWidgets.QWidget()
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(8)

        self.initial_state = SETTINGS  # store the settings to restore it if needed

        self.title = QtWidgets.QLabel("Settings")
        self.title.setObjectName("viewTitle")
        self.title.setMinimumHeight(48)

        row = 0
        layout.addWidget(self.title, row, 0, 1, 4)

        # Editor settings
        row += 1
        self.editor_title = QtWidgets.QLabel("Editor")
        self.editor_title.setObjectName("settingsSectionTitle")
        layout.addWidget(self.editor_title, row, 0, 1, 4)

        row += 1
        self.theme = QtWidgets.QComboBox()
        self.theme.addItem("Light Theme", "light-theme")
        self.theme.addItem("Dark Theme", "dark-theme")
        self.theme.setCurrentIndex(self.theme.findData(SETTINGS["editor"]["theme"]))
        layout.addWidget(QtWidgets.QLabel("Theme"), row, 0)
        layout.addWidget(self.theme, row, 1, 1, 3)

        row += 1
        self.font_family = QtWidgets.QLineEdit(SETTINGS["editor"]["font-family"])
        layout.addWidget(QtWidgets.QLabel("Font"), row, 0)
        layout.addWidget(self.font_family, row, 1, 1, 3)

        row += 1
        self.font_size = QtWidgets.QLineEdit(SETTINGS["editor"]["font-size"])
        layout.addWidget(QtWidgets.QLabel("Font size"), row, 0)
        self.font_size_validator = InputValidator(QRegExp("^[0-9]+$"), self.font_size)
        self.font_size.setValidator(self.font_size_validator)
        layout.addWidget(self.font_size, row, 1, 1, 3)

        # Meeting settings
        row += 1
        self.meetings_title = QtWidgets.QLabel("Meetings")
        self.meetings_title.setObjectName("settingsSectionTitle")
        layout.addWidget(self.meetings_title, row, 0, 1, 4)

        row += 1
        self.standard_duration = QtWidgets.QLineEdit(str(SETTINGS["meeting"]["standard_duration"]))
        self.std_dur_validator = InputValidator(QRegExp("^[0-9]+$"), self.standard_duration)
        self.standard_duration.setValidator(self.std_dur_validator)
        layout.addWidget(QtWidgets.QLabel("Standard duration (min)"), row, 0)
        layout.addWidget(self.standard_duration, row, 1, 1, 3)

        # User settings section
        row += 1
        self.email_title = QtWidgets.QLabel("User")
        self.email_title.setObjectName("settingsSectionTitle")
        layout.addWidget(self.email_title, row, 0, 1, 4)

        # Name
        row += 1
        self.name = QtWidgets.QLineEdit(str(SETTINGS["user"]["name"]))
        self.name.textChanged.connect(self.is_empty)
        layout.addWidget(QtWidgets.QLabel("Name"), row, 0)
        layout.addWidget(self.name, row, 1, 1, 3)

        # Email
        row += 1
        self.email_address = QtWidgets.QLineEdit(str(SETTINGS["user"]["email"]["address"]))
        self.email_validator = InputValidator(QRegExp(EMAIL_REGEX), self.email_address)
        self.email_address.setValidator(self.email_validator)
        layout.addWidget(QtWidgets.QLabel("Email"), row, 0)
        layout.addWidget(self.email_address, row, 1, 1, 3)

        # SMTP server section
        row += 1
        self.smtp_title = QtWidgets.QLabel("SMTP server")
        self.smtp_title.setObjectName("settingsSectionTitle")
        layout.addWidget(self.smtp_title, row, 0, 1, 4)

        # SMTP username (email)
        row += 1
        conf_username = SETTINGS["user"]["email"]["username"]
        self.smtp_username = QtWidgets.QLineEdit(str(conf_username))
        layout.addWidget(QtWidgets.QLabel("Username"), row, 0)
        layout.addWidget(self.smtp_username, row, 1, 1, 3)

        # SMTP password (email)
        row += 1
        self.email_password = QtWidgets.QLineEdit()
        self.email_password.setPlaceholderText("Change password")
        self.email_password.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(QtWidgets.QLabel("Password"), row, 0)
        layout.addWidget(self.email_password, row, 1, 1, 3)

        # SMTP host
        row += 1
        self.smtp_host = QtWidgets.QLineEdit(str(SETTINGS["user"]["email"]["host"]))
        layout.addWidget(QtWidgets.QLabel("Host"), row, 0)
        layout.addWidget(self.smtp_host, row, 1, 1, 3)

        # SMTP port
        row += 1
        self.smtp_port = QtWidgets.QLineEdit(str(SETTINGS["user"]["email"]["port"]))
        self.port_validator = InputValidator(QRegExp("^[0-9]+$"), self.smtp_port, allow_empty=True)
        self.smtp_port.setValidator(self.port_validator)
        layout.addWidget(QtWidgets.QLabel("Port"), row, 0)
        layout.addWidget(self.smtp_port, row, 1, 1, 3)

        # SMTP SSL
        row += 1
        self.smtp_ssl = QtWidgets.QCheckBox()
        if SETTINGS["user"]["email"]["ssl"]:
            self.smtp_ssl.setChecked(True)
        layout.addWidget(QtWidgets.QLabel("SSL"), row, 0)
        layout.addWidget(self.smtp_ssl, row, 1, 1, 3)

        # Model config
        row += 1
        self.model_title = QtWidgets.QLabel("Model")
        self.model_title.setObjectName("settingsSectionTitle")
        layout.addWidget(self.model_title, row, 0, 1, 4)

        # Model language selection
        row += 1
        self.model_language = QtWidgets.QComboBox()
        lang_options = get_model_languages()
        for opt in lang_options:
            self.model_language.addItem(opt, opt)
        self.model_language.setCurrentIndex(self.model_language.findData(SETTINGS["user"]["language"]))
        self.model_language.currentTextChanged.connect(self.language_changed)
        layout.addWidget(QtWidgets.QLabel("Language"), row, 0)
        layout.addWidget(self.model_language, row, 1, 1, 3)

        # Model language versions
        row += 1
        self.model_lang_version = QtWidgets.QComboBox()
        version_options = get_language_versions(SETTINGS["user"]["language"])
        for opt in version_options:
            self.model_lang_version.addItem(opt, opt)
        self.model_lang_version.setCurrentIndex(self.model_lang_version.findData(SETTINGS["user"]["language_version"]))
        layout.addWidget(QtWidgets.QLabel("Version"), row, 0)
        layout.addWidget(self.model_lang_version, row, 1, 1, 3)

        # empty row
        row += 1
        layout.addWidget(QtWidgets.QLabel(""), row, 0, 1, 4)

        # Button row
        # Update and restore
        row += 1
        button_row = QtWidgets.QGridLayout()
        button_row.setHorizontalSpacing(10)
        submit_button = QtWidgets.QToolButton()
        submit_button.setText("Update")
        submit_button.clicked.connect(self.submit_on_click)
        restore_button = QtWidgets.QToolButton()
        restore_button.setText("Restore")
        restore_button.clicked.connect(self.restore_on_click)
        button_row.addWidget(submit_button, 0, 3)
        button_row.addWidget(restore_button, 0, 2)
        layout.addLayout(button_row, row, 1)

        # If needed make space below empty
        row += 1
        layout.addWidget(QtWidgets.QLabel(""), row, 0)
        layout.setRowStretch(row, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(main_layout)
        widget.setLayout(layout)
        scroll_area.setWidget(widget)

    @pyqtSlot()
    def language_changed(self):
        """
        Update the version options whenever the user selects another language
        """
        version_options = get_language_versions(self.model_language.currentData())
        self.model_lang_version.clear()
        for opt in version_options:
            self.model_lang_version.addItem(opt, opt)
        self.model_lang_version.setCurrentIndex(0)

    @pyqtSlot()
    def is_empty(self):
        """ Checks if the text in the widget is empty and updates the empty state """
        if self.sender() == self.name:
            if self.name.text() == "":
                self.empty_fields["name"] = True
                self.name.setProperty("invalid", True)
            else:
                self.empty_fields["name"] = False
                self.name.setProperty("invalid", False)
            self.name.style().unpolish(self.name)
            self.name.style().polish(self.name)

    @pyqtSlot()
    def restore_on_click(self):
        """ Restores the users settings to the initial values loaded from config """
        # Editor
        self.theme.setCurrentIndex(self.theme.findData(self.initial_state["editor"]["theme"]))
        self.font_family.setText(self.initial_state["editor"]["font-family"])
        self.font_size.setText(self.initial_state["editor"]["font-size"])

        # Meetings
        self.standard_duration.setText(str(self.initial_state["meeting"]["standard_duration"]))

        # User
        self.name.setText(self.initial_state["user"]["name"])
        self.email_address.setText(self.initial_state["user"]["email"]["address"])
        self.email_password.setText("")

        # SMTP
        self.smtp_username.setText(self.initial_state["user"]["email"]["username"])
        self.smtp_host.setText(self.initial_state["user"]["email"]["host"])
        self.smtp_port.setText(str(self.initial_state["user"]["email"]["port"]))
        self.smtp_ssl.setChecked(self.initial_state["user"]["email"]["ssl"])

        # Model
        self.model_language.setCurrentIndex(self.model_language.findData(self.initial_state["user"]["language"]))
        self.model_lang_version.setCurrentIndex(
            self.model_lang_version.findData(self.initial_state["user"]["language_version"])
        )

        self.main_window.set_info_message("Restored settings.")

    def valid_fields(self):
        """ Returns a boolean indicating if all the settings are valid """
        form_states = []
        state, _, _ = self.std_dur_validator.validate(self.standard_duration.text(), 0)
        form_states.append(state)
        state, _, _ = self.font_size_validator.validate(self.font_size.text(), 0)
        form_states.append(state)
        state, _, _ = self.email_validator.validate(self.email_address.text(), 0)
        form_states.append(state)
        state, _, _ = self.port_validator.validate(self.smtp_port.text(), 0)
        form_states.append(state)

        # If any of the settings contain invalid input or are empty dont update
        # settings
        invalid_form_states = [state for state in form_states if state != VALID]
        if len(invalid_form_states) or True in self.empty_fields.values():
            return False

        return True

    @pyqtSlot()
    def submit_on_click(self):
        """
        Update the users config files if all the settings are valid and the
        required fields are not empty.
        """

        if not self.valid_fields():
            self.main_window.set_info_message("Failed to update settings. Some fields are either invalid or empty.")
            return

        crypt = Crypt()

        # Editor
        SETTINGS["editor"]["theme"] = self.theme.currentData()
        SETTINGS["editor"]["font-family"] = self.font_family.text()
        SETTINGS["editor"]["font-size"] = self.font_size.text()
        update_settings(os.path.abspath("config/editor"), SETTINGS["editor"])

        # Meetings
        SETTINGS["meeting"]["standard_duration"] = int(self.standard_duration.text())
        update_settings(os.path.abspath("config/meetings"), SETTINGS["meeting"])

        # User
        SETTINGS["user"]["name"] = self.name.text()
        SETTINGS["user"]["email"] = {
            "address": self.email_address.text(),
            "host": self.smtp_host.text(),
            # Only update password if a new password was given
            "password": crypt.encrypt(self.email_password.text())
            if self.email_password.text() != ""
            else self.initial_state["user"]["email"]["password"],
            "port": int(self.smtp_port.text()),
            "ssl": self.smtp_ssl.isChecked(),
            "username": self.smtp_username.text(),
        }
        SETTINGS["user"]["language"] = self.model_language.currentData()
        SETTINGS["user"]["language_version"] = self.model_lang_version.currentData()

        update_settings(os.path.abspath("config/user"), SETTINGS["user"])
        self.main_window.set_info_message("Updated settings.")
        self.email_password.setText("")  # show placeholder again


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    window.set_active_view(4)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
