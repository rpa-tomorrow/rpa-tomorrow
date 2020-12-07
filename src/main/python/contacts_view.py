from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRegExp, pyqtSlot
from PyQt5.QtGui import QRegExpValidator, QValidator
from fuzzywuzzy import fuzz
import modal
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
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(8)

        self.initial_state = SETTINGS  # store the settings to restore it if needed

        self.title = QtWidgets.QLabel("Contacts")
        self.title.setObjectName("viewTitle")
        self.title.setMinimumHeight(48)
        self.layout.addWidget(self.title)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setMaximumWidth(960)
        scroll_area.setWidgetResizable(True)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(scroll_area)

        widget = QtWidgets.QWidget()
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        top_widget = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_widget.setLayout(top_layout)
        self.layout.addWidget(top_widget)

        self.search_name = QtWidgets.QLineEdit()
        self.search_name.setObjectName("searchContactName")
        self.search_name.setPlaceholderText("Search for a name in your contact list...")
        self.search_name.installEventFilter(self)
        top_layout.addWidget(self.search_name)
        
        self.add_contact = QtWidgets.QToolButton()
        self.add_contact.setText("\uf234 Create new contact")
        self.add_contact.clicked.connect(self.create_new_contact)
        top_layout.addWidget(self.add_contact)

        self.build_contact_list()

        # If needed make space below empty
        self.layout.addStretch(1)

        self.setLayout(main_layout)
        widget.setLayout(self.layout)
        scroll_area.setWidget(widget)


    def build_contact_list(self):
        row = 3
        self.no_contacts = NoContactsView(self)
        self.layout.addWidget(self.no_contacts)
        if len(SETTINGS["contacts"]) > 0:
            self.no_contacts.hide()

        self.entries = dict()
        for name, contact in SETTINGS["contacts"].items():
            row += 1
            entry = ContactEntryView(self, name, contact)
            self.entries[name] = entry
            self.layout.addWidget(entry)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyRelease and obj is self.search_name:
            if self.search_name.hasFocus():
                query = self.search_name.text()
                if len(query) == 0:
                    for view in self.entries.values():
                        view.show()
                    self.no_contacts.hide()
                else:
                    num_found = 0
                    for name, view in self.entries.items():
                        if fuzz.partial_ratio(name.lower(), query.lower()) >= 60:
                            view.show()
                            num_found += 1
                        else:
                            view.hide()
                    self.no_contacts.setVisible(num_found == 0)
        return super().eventFilter(obj, event)

    def add_contact(self, name, email):
        contact = dict()
        SETTINGS["contacts"][name] = contact
        contact["email"] = dict()
        contact["email"]["address"] = email
        entry = ContactEntryView(self, name, contact)
        self.entries[name] = entry
        self.layout.insertWidget(2, entry)
        self.search_name.clear()
        for view in self.entries.values():
            view.show()
        self.no_contacts.hide()
        self.update_contact_list()

    def remove_contact(self, name):
        if name in SETTINGS["contacts"]:
            del SETTINGS["contacts"][name]
        if name in self.entries:
            self.entries[name].close()
            del self.entries[name]

    def rename_contact(self, old_name, new_name):
        if old_name in SETTINGS["contacts"]:
            if new_name in SETTINGS["contacts"]:
                modal.ModalMessageWindow(
                    self.main_window,
                    f"Contact with name {new_name} is already stored in the this contact list.",
                    "Failed to rename contact!",
                    modal.MSG_ERROR)
                return False
                
            contact = SETTINGS["contacts"][old_name]
            del SETTINGS["contacts"][old_name]
            SETTINGS["contacts"][new_name] = contact
            return True
        else:
            print(f"contact `{old_name}` is not in contact list, this is likely a bug!")
        return False

    def update_contact_list(self):
        update_settings("../config/contacts", SETTINGS["contacts"])
        self.main_window.set_info_message("Contacts saved!")
    
    def create_new_contact(self):
        create_modal = CreateContactModal(self.main_window, self.search_name.text())
        create_modal.create_callback = lambda: self.add_contact(create_modal.name.text(),
                                                                create_modal.email.text())
        

class CreateContactModal(modal.ModalWindow):
    def __init__(self, parent, name):
        self.name = name
        self.create_callback = None
        super(CreateContactModal, self).__init__(parent)

    def build_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(0)
        
        label_icon = QtWidgets.QLabel("\uf234")
        label_icon.setObjectName("modalIconBlue")
        
        label_title = QtWidgets.QLabel("Create a new contact")
        label_title.setObjectName("modalTitle")

        self.name = QtWidgets.QLineEdit(self.name)
        self.name.setPlaceholderText("Enter the name of the contact...")
        self.name.setObjectName("hMargin")

        self.email = QtWidgets.QLineEdit("")
        self.email.setPlaceholderText("Enter the email address to your contact...")
        self.email.setObjectName("hMargin")

        self.modal_frame.setMinimumWidth(480)

        self.bottom_layout = self.build_bottom_layout()
        bottom_frame = QtWidgets.QFrame()
        bottom_frame.setObjectName("modalBottomFrame")
        bottom_frame.setLayout(self.bottom_layout)

        name_label = QtWidgets.QLabel("Name:")
        name_label.setObjectName("hMargin")
        email_label = QtWidgets.QLabel("Email:")
        email_label.setObjectName("hMargin")
        
        layout.addWidget(label_icon, 0, 0)
        layout.addWidget(label_title, 0, 1, 1, 2)
        layout.addWidget(name_label, 1, 0)
        layout.addWidget(self.name, 1, 1, 1, 2)
        layout.addWidget(email_label, 2, 0)
        layout.addWidget(self.email, 2, 1, 1, 2)
        layout.addWidget(bottom_frame, 3, 0, 1, 3)
        layout.setColumnStretch(1, 1)
        return layout
    
    def build_bottom_layout(self):
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        bottom_layout.setSpacing(12)

        create_button = QtWidgets.QToolButton()
        create_button.setText("Create")
        create_button.clicked.connect(self.answer_create)
        cancel_button = QtWidgets.QToolButton()
        cancel_button.setText("Cancel")
        cancel_button.clicked.connect(self.close_window)

        bottom_layout.addStretch(1)
        bottom_layout.addWidget(create_button)
        bottom_layout.addWidget(cancel_button)
        return bottom_layout

    def answer_create(self):        
        if self.create_callback:
            self.create_callback()
        self.close_window()
        

class ContactEntryView(QtWidgets.QFrame):
    def __init__(self, contact_view, name, contact):
        super(ContactEntryView, self).__init__()
        layout = QtWidgets.QGridLayout()
        self.contact_view = contact_view

        self.contact = contact;
        self.name = name;

        self.name_edit = QtWidgets.QLineEdit(name)
        self.name_edit.setObjectName("fontBold")
        self.name_edit.installEventFilter(self)
        layout.addWidget(self.name_edit, 0, 0)

        self.email_address_edit = QtWidgets.QLineEdit("")
        self.email_address_edit.setObjectName("fontFaint")
        if contact["email"] and contact["email"]["address"]:
            self.email_address_edit.setText(contact["email"]["address"])
        self.email_address_edit.installEventFilter(self)
        layout.addWidget(self.email_address_edit, 1, 0)

        self.save_button = QtWidgets.QToolButton()
        self.save_button.setObjectName("iconButton")
        self.save_button.setText("\uf00c")
        self.save_button.clicked.connect(self.save_contact)
        layout.addWidget(self.save_button, 0, 1, 2, 1)

        self.restore_button = QtWidgets.QToolButton()
        self.restore_button.setObjectName("iconButton")
        self.restore_button.setText("\uf00d")
        self.restore_button.clicked.connect(self.restore_contact)
        layout.addWidget(self.restore_button, 0, 2, 2, 1)

        self.remove_button = QtWidgets.QToolButton()
        self.remove_button.setObjectName("iconButton")
        self.remove_button.setText("\uf1f8")
        self.remove_button.clicked.connect(self.remove_contact)
        layout.addWidget(self.remove_button, 0, 3, 2, 1)

        self.save_button.hide()
        self.restore_button.hide()

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyRelease:
            if obj is self.name_edit or obj is self.email_address_edit:
                if self.name_edit.hasFocus() or self.email_address_edit.hasFocus():
                    new_name = self.name_edit.text()
                    new_email_address = self.email_address_edit.text()
                    email_address = self.contact["email"]["address"]
                    if (not new_name == self.name) or (not new_email_address == email_address):
                        self.save_button.show()
                        self.restore_button.show()
                    else:
                        self.save_button.hide()
                        self.restore_button.hide()

        if event.type() == QtCore.QEvent.KeyPress:
            if obj is self.name_edit or obj is self.email_address_edit:
                if event.key() == QtCore.Qt.Key_Return:
                    if self.name_edit.hasFocus() or self.email_address_edit.hasFocus():
                        self.save_contact()
                        return True
        return super().eventFilter(obj, event)

    def remove_contact(self):
        del_modal = modal.ModalYesNoQuestionWindow(
            self.contact_view.main_window,
            f"Are your sure you want to delete `{self.name}` from your contacts?",
            "Delete contact?")
        del_modal.yes_callback = self.remove_contact_impl

    def remove_contact_impl(self):
        self.contact_view.remove_contact(self.name)
        self.save_button.hide()
        self.restore_button.hide()
        self.contact_view.update_contact_list()

    def save_contact(self):
        is_dirty = False
        new_name = self.name_edit.text()
        if not new_name == self.name:
            if self.contact_view.rename_contact(self.name, new_name):
                self.contact = SETTINGS["contacts"][new_name]
                self.name = new_name
                is_dirty = True

        new_email_address = self.email_address_edit.text()
        if not new_email_address == self.contact["email"]["address"]:
            self.contact["email"]["address"] = new_email_address
            is_dirty = True

        if is_dirty:
            self.contact_view.update_contact_list()
        self.save_button.hide()
        self.restore_button.hide()

    def restore_contact(self):
        self.name_edit.setText(self.name)
        self.email_address_edit.setText(self.contact["email"]["address"])
        self.save_button.hide()
        self.restore_button.hide()

class NoContactsView(QtWidgets.QFrame):
    def __init__(self, contacts_view):
        super(NoContactsView, self).__init__()
        self.contacts_view = contacts_view
        
        layout = QtWidgets.QGridLayout()
        self.add_contact = QtWidgets.QToolButton()
        self.add_contact.setText("\uf234 Create new contact")
        self.add_contact.clicked.connect(self.contacts_view.create_new_contact)

        self.label = QtWidgets.QLabel("No contacts found")
        layout.addWidget(self.label, 1, 1, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.add_contact, 2, 1, 1, 1, QtCore.Qt.AlignCenter)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(3, 1)
        self.setMinimumHeight(128)
        self.setLayout(layout)

# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app
    import sys

    appctxt, window = initialize_app()
    window.set_active_view(4)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
