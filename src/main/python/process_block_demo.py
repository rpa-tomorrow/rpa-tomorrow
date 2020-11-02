from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QEvent, QPoint, pyqtSlot
from lib.automate.modules.send import Send

class ProcessEditorView(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProcessEditorView, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        layout.setContentsMargins(4, 4, 4, 4)

        self.sidebar = QFrame()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(QLabel("Outline"))
        self.sidebar.setMinimumWidth(240)
        # self.sidebar.setStyleSheet("background-color: white")
        self.sidebar.setLayout(sidebar_layout)

        self.text_editor = QTextEdit("")
        self.text_editor.setPlaceholderText("Enter process query here")
        self.text_editor.setStyleSheet("border-style: none;")
        self.text_editor.setFont(QFont("Segoe UI", 10))
        self.text_editor.setMaximumHeight(180)
        self.text_editor.installEventFilter(self)

        self.submit_button = QPushButton("Submit");
        self.submit_button.clicked.connect(self.submit_input_text)

        self.process_viewer = ProcessViewer()

        layout.addWidget(self.sidebar, 0, 0, 3, 1)
        layout.addWidget(self.text_editor, 0, 1)
        layout.addWidget(self.submit_button, 1, 1)
        layout.addWidget(self.process_viewer, 2, 1)
        self.setLayout(layout)

        # test_block = SendEmailBlock("test", ["Alexander"], "", "Hello World", self.process_viewer)
        # self.process_viewer.append_block(test_block)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.text_editor:
            if event.key() == Qt.Key_Return and self.text_editor.hasFocus():
                self.submit_input_text()
        return super().eventFilter(obj, event)

    def submit_input_text(self):
        query = self.text_editor.toPlainText()
        self.text_editor.clear()

        to, time, body = Send().nlp(query)
        email_block = SendEmailBlock(query, to, time, body, self.process_viewer)
        self.process_viewer.append_block(email_block)

class ProcessViewer(QWidget):
    def __init__(self, *args, **kwargs):
        super(ProcessViewer, self).__init__(*args, **kwargs)
        self.grid_size = 32
        self.update()
        self.blocks = []
        self.pos = QPoint(0, 0)
        self.delta = QPoint(0, 0)
        self.offset = QPoint(0, 0)
        self.dragging = False

    def append_block(self, block):
        self.blocks.append(block)
        block.setGeometry(self.width() / 2 - 130, self.height() / 2 - 160, 260, 320)
        block.show()
        
    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(QColor("#304357"), 1))
        xoff = (self.pos.x() + self.delta.x()) % self.grid_size
        yoff = (self.pos.y() + self.delta.y()) % self.grid_size
        for i in range(0, self.width() + self.grid_size, self.grid_size):
            p.drawLine(i-xoff, 0, i-xoff, self.height())
        
        for i in range(0, self.height() + self.grid_size, self.grid_size):
            p.drawLine(0, i-yoff, self.width(), i-yoff)
        p.end()
        
    def mousePressEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.offset = event.pos()
            for block in self.blocks:
                block.offset = event.pos()
            self.dragging = True

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.RightButton and self.dragging:
            self.delta = self.offset - event.pos()
            for block in self.blocks:
                block.delta = event.pos() - block.offset
                block.move(block.pos + block.delta)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.pos = self.pos + self.delta
            self.delta = QPoint(0, 0)
            for block in self.blocks:
                block.pos = block.pos + block.delta
                block.delta = QPoint(0, 0)
            self.dragging = False
        

class ProcessBlock(QFrame):
    def __init__(self, query, name, min_width, min_height, *args, **kwargs):
        super(ProcessBlock, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
            
        self.query = query
        self.pos = QPoint(0, 0)
        self.delta = QPoint(0, 0)
        self.offset = QPoint(0, 0)
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
    border-radius: 6px;
    border-style: solid;
    border-width: 2px;
    border-color: lightgray;
}
""")
        self.update()

    def mousePressEvent(self, event):
        self.offset = event.pos();

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.delta = self.mapToParent(event.pos() - self.offset)
            self.move(self.delta)

    def mouseReleaseEvent(self, event):
        self.pos = self.delta
        self.delta = QPoint(0, 0)

    def setup(self, layout):
        return

class SendEmailBlock(ProcessBlock):
    def __init__(self, query, recipient, when, body, *args, **kwargs):
        super(SendEmailBlock, self).__init__(query, "Send Email", 100, 160, *args, **kwargs)
        self.recipient.setText(", ".join(recipient))
        # self.when.setDateTime(QDateTime(str(when)))
        self.body.setText(body)
        self.setStyleSheet("""
SendEmailBlock {
    border-radius: 6px;
    border-style: solid;
    border-width: 2px;
    border-color: dodgerblue;
}
""")
        
    def setup(self, layout):
        self.recipient = QLineEdit("")
        self.recipient.setPlaceholderText("recipient")

        self.when = QDateTimeEdit()

        self.body = QTextEdit("")
        self.body.setPlaceholderText("Enter the body of the email here")
        layout.addWidget(self.recipient)
        layout.addWidget(self.when)
        layout.addWidget(self.body)

        
