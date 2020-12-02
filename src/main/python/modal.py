from PyQt5 import QtWidgets, QtGui, QtCore
import sys


MSG_INFO = 0
MSG_QUESTION = 1
MSG_SUCCESS = 2
MSG_WARNING = 3
MSG_ERROR = 4


class ModalWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ModalWindow, self).__init__(parent)
        self.parent = parent
        if self.parent.modal:
            return

        self.setGeometry(0, 0, parent.width(), parent.height())
        self.modal_frame = QtWidgets.QFrame()
        self.modal_frame.setMaximumWidth(720)
        self.modal_frame.setFocus()

        center_layout = QtWidgets.QGridLayout()
        center_layout.addWidget(self.modal_frame, 1, 1)
        center_layout.setColumnStretch(0, 1)
        center_layout.setColumnStretch(2, 1)
        center_layout.setRowStretch(0, 1)
        center_layout.setRowStretch(2, 1)

        self.close_window_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self.modal_frame)
        self.close_window_shortcut.activated.connect(self.close_window)

        self.layout = self.build_layout()
        self.modal_frame.setLayout(self.layout)

        self.parent.modal = self
        self.setLayout(center_layout)
        self.show()

    def mousePressEvent(self, event):
        super(ModalWindow, self).mousePressEvent(event)
        relpos = event.pos() - self.modal_frame.pos()
        if not self.modal_frame.rect().contains(relpos):
            self.close_window()

    def close_window(self):
        self.parent.modal = None
        self.close()

    def build_layout(self):
        layout = QtWidgets.QGridLayout()
        return layout

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 180))
        p.end()


class ModalMessageWindow(ModalWindow):
    def __init__(self, parent, message, title, message_type):
        self.message = message
        self.title = title
        self.message_type = message_type
        super(ModalMessageWindow, self).__init__(parent)
        
    def build_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setVerticalSpacing(12)
        layout.setHorizontalSpacing(0)

        label_icon = QtWidgets.QLabel("")
        if self.message_type == MSG_INFO:
            label_icon = QtWidgets.QLabel("\uF05A")
            label_icon.setObjectName("modalIconBlue")
        elif self.message_type == MSG_QUESTION:
            label_icon = QtWidgets.QLabel("\uF059")
            label_icon.setObjectName("modalIconBlue")
        elif self.message_type == MSG_SUCCESS:
            label_icon = QtWidgets.QLabel("\uF058")
            label_icon.setObjectName("modalIconGreen")
        elif self.message_type == MSG_WARNING:
            label_icon = QtWidgets.QLabel("\uF06A")
            label_icon.setObjectName("modalIconOrange")
        elif self.message_type == MSG_ERROR:
            label_icon = QtWidgets.QLabel("\uF057")
            label_icon.setObjectName("modalIconRed")
            
        label_title = QtWidgets.QLabel(self.title)
        label_title.setObjectName("modalTitle")
        label_message = QtWidgets.QLabel(self.message)
        label_message.setObjectName("modalMessage")
        label_message.setWordWrap(True);

        self.bottom_layout = self.build_bottom_layout()
        bottom_frame = QtWidgets.QFrame()
        bottom_frame.setObjectName("modalBottomFrame")
        bottom_frame.setLayout(self.bottom_layout)

        layout.addWidget(label_icon, 0, 0)
        layout.addWidget(label_title, 0, 1, 1, 2)
        layout.addWidget(label_message, 1, 0, 1, 3)
        layout.addWidget(bottom_frame, 2, 0, 1, 3)
        layout.setColumnStretch(1, 1)
        return layout

    def build_bottom_layout(self):
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        bottom_layout.setSpacing(12)
        close_button = QtWidgets.QToolButton()
        close_button.setText("Close")
        close_button.setObjectName("primaryButton")
        close_button.clicked.connect(self.close_window)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(close_button)
        return bottom_layout

class ModalYesNoQuestionWindow(ModalMessageWindow):
    def __init__(self, parent, message, title):
        super(ModalYesNoQuestionWindow, self).__init__(parent, message, title, MSG_QUESTION)
        self.yes_callback = None
        self.no_callback = None

    def build_bottom_layout(self):
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        bottom_layout.setSpacing(12)

        yes_button = QtWidgets.QToolButton()
        yes_button.setText("Yes")
        yes_button.clicked.connect(self.answer_yes)
        no_button = QtWidgets.QToolButton()
        no_button.setText("No")
        no_button.clicked.connect(self.answer_no)
        
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(yes_button)
        bottom_layout.addWidget(no_button)
        return bottom_layout

    def answer_yes(self):
        if self.yes_callback:
            self.yes_callback()
        self.close_window()
        
    def answer_no(self):
        if self.no_callback:
            self.no_callback()
        self.close_window()
    
# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    ModalMessageWindow(window, "Hello world this is just a test error message! Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.", "Error", MSG_ERROR)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
