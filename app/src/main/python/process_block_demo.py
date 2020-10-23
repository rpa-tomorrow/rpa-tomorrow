from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt

class ProcessEditorView(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProcessEditorView, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        self.sidebar = QFrame()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(QLabel("Outline"))
        self.sidebar.setMinimumWidth(240)
        self.sidebar.setStyleSheet("background-color: white")
        self.sidebar.setLayout(sidebar_layout)

        self.text_editor = QTextEdit("")
        self.text_editor.setPlaceholderText("Enter process query here")
        self.text_editor.setStyleSheet("border-style: none;")
        self.text_editor.setFont(QFont("Segoe UI", 10))
        self.text_editor.setMaximumHeight(180)

        self.process_viewer = ProcessViewer()

        separator = QFrame();
        separator.setFrameShape(QFrame.HLine);

        layout.addWidget(self.sidebar, 0, 0, 3, 1)
        layout.addWidget(self.text_editor, 0, 1)
        layout.addWidget(separator, 1, 1);
        layout.addWidget(self.process_viewer, 2, 1)
        self.setLayout(layout)

class ProcessViewer(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProcessViewer, self).__init__(*args, **kwargs)
        # self.setStyleSheet("background-color: lightgray;");
        self.grid_size = 32
        self.setStyleSheet("background-color: white;")
        self.update()
        SendEmailBlock(self)
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(0, 0, self.width(), self.height(), Qt.white)
        p.setPen(QPen(QColor("lightgray"), 1))
        for i in range(0, self.width(), self.grid_size):
            p.drawLine(i, 0, i, self.height())
        
        for i in range(0, self.width(), self.grid_size):
            p.drawLine(0, i, self.width(), i)
        p.end()

class ProcessBlock(QFrame):
    def __init__(self, name, min_width, min_height, *args, **kwargs):
        super(ProcessBlock, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()

        self.main_label = QLabel(name, self)
        self.main_label.setMinimumHeight(24)
        self.main_label.setMaximumHeight(24)

        layout.addWidget(self.main_label)
        self.setup(layout)
        self.setLayout(layout)
        self.setMinimumWidth(min_width)
        self.setMinimumHeight(min_height)
        self.setStyleSheet("""
ProcessBlock {
    background-color: white;
    border-radius: 6px;
    border-style: solid;
    border-width: 1px;
    border-color: lightgray;
}
""")
        self.update()

    def mousePressEvent(self, event):
        self.offset = event.pos();

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.offset:
            self.move(self.mapToParent(event.pos() - self.offset))

    def setup(self, layout):
        return

class SendEmailBlock(ProcessBlock):
    def __init__(self, *args, **kwargs):
        super(SendEmailBlock, self).__init__("Send Email", 100, 160, *args, **kwargs)
        self.setStyleSheet("""
SendEmailBlock {
    background-color: white;
    border-radius: 6px;
    border-style: solid;
    border-width: 1px;
    border-color: dodgerblue;
}
""")
        
    def setup(self, layout):
        self.recipient = QLineEdit("")
        self.recipient.setPlaceholderText("recipient")
        layout.addWidget(self.recipient)
        self.body = QTextEdit("")
        self.body.setPlaceholderText("Enter the body of the email here")
        layout.addWidget(self.body)

        
