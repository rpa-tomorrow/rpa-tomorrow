from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent

class ChatbotView(QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatbotView, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        self.message_editor = QTextEdit("")
        self.message_editor.setPlaceholderText("Write a message...")
        self.message_editor.setStyleSheet("border-style: none;")
        self.message_editor.setFont(QFont("Segoe UI", 10))
        self.message_editor.setMaximumHeight(180)
        self.message_editor.installEventFilter(self)
        self.message_editor.textChanged.connect(self.showCurrentText)

        separator = QFrame();
        separator.setFrameShape(QFrame.HLine);

        self.message_viewer = MessageViewer()
        
        layout.addWidget(self.message_viewer)
        layout.addWidget(self.message_editor)
        self.setLayout(layout)

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and
            source is self.message_editor):
            print('key press:', (event.key(), event.text()))
        return super(ChatbotView, self).eventFilter(source, event)

    def showCurrentText(self):
        print('current-text:', self.message_editor.getText())
        self.message_editor.setText("")

class MessageViewer(QWidget):
    def __init__(self, *args, **kwargs):
        super(MessageViewer, self).__init__(*args, **kwargs)
        
