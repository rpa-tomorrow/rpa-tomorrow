from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from worker_queue import Worker

from lib.automate.modules.send import Send
from lib.automate.modules.schedule import Schedule
from lib.automate.modules.reminder import Reminder
from lib.nlp.nlp import NLP
from lib.settings import SETTINGS

from multiprocessing import Process, Manager

import sys

def display_error_message(message, title="Error"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.resize(360, 280)
    msg.exec_()


def handle_response(task, followup):
    display_error_message(str(followup) + ".")

def load_nlp_model(basic_model, spacy_model, return_dict):
    return_dict['nlp'] = NLP(basic_model, spacy_model)

class DesignView(QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(DesignView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.threadpool = QThreadPool()
        
        layout = QVBoxLayout()
        layout.setSpacing(8);

        # Load a NLP model on separate thread
        self.nlp = None

        worker = Worker(self.load_nlp_model,
                        "Loading model en_rpa_simple",
                        SETTINGS["nlp_models"]["basic"],
                        SETTINGS["nlp_models"]["spacy"])
        worker.signals.result.connect(self.set_nlp_model)
        worker.signals.error.connect(self.load_nlp_model_error)
        
        self.threadpool.start(worker)

        # TODO(alexander): model should not be hardcoded
        
        self.title = QLabel("Design")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)
        layout.addWidget(self.title)

        self.process_text_edit = ProcessTextEdit("")
        self.process_text_edit.setMaximumHeight(180)
        self.process_viewer = ProcessViewer()

        layout.addWidget(self.process_text_edit)
        layout.addWidget(self.process_viewer)
        self.setLayout(layout)
        self.process_text_edit.installEventFilter(self)

    def set_nlp_model(self, nlp):
        self.nlp = nlp

    def load_nlp_model_error(self, error):
        display_error_message(error[2])

    def load_nlp_model(self, basic_model, spacy_model):
        manager = Manager()
        return_dict = manager.dict()
        proc = Process(target=load_nlp_model, args=(basic_model, spacy_model, return_dict,))
        proc.start()
        proc.join()
        return return_dict['nlp']

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.process_text_edit:
            if event.key() == Qt.Key_Return and self.process_text_edit.hasFocus():
                self.submit_input_text()
                return True
        return super().eventFilter(obj, event)

    def submit_input_text(self):
        self.process_text_edit.save_cursor_pos()

        query = self.process_text_edit.toPlainText()
        block = None

        if not self.nlp:
            display_error_message("NLP model has not been loaded yet!")
            return

        try:
            task, _ = self.nlp.prepare(query)
            if isinstance(task, Send):
                block = SendBlock(query, task.to, task.when, task.body, self.process_viewer)
            elif isinstance(task, Schedule):
                block = ScheduleBlock(query, task.to, task.when, task.body, task.sender, self.process_viewer)
            else:
                self.process_text_edit.restore_cursor_pos()
                display_error_message("Failed to register automation block.")
                return
        except:
            self.process_text_edit.restore_cursor_pos()
            display_error_message(str(sys.exc_info()[1]) + ".")
            return
        
        self.process_text_edit.set_cursor_pos(0)
        self.process_text_edit.clear()
        self.process_viewer.append_block(block)

class ProcessTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(ProcessTextEdit, self).__init__(*args, **kwargs)
        self.setPlaceholderText("Enter process query here")
        self.cursor_pos = 0

    def save_cursor_pos(self):
        self.cursor_pos = self.textCursor().position()

    def restore_cursor_pos(self):
        self.set_cursor_pos(self.cursor_pos)
        
    def set_cursor_pos(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
    
        
class ProcessViewer(QFrame):
    def __init__(self, *args, **kwargs):
        super(ProcessViewer, self).__init__(*args, **kwargs)
        self.grid_size = 32
        self.update()
        self.blocks = []
        self.pos = QPoint(self.grid_size/2, self.grid_size/2)
        self.delta = QPoint(0, 0)
        self.offset = QPoint(0, 0)
        self.dragging = False

    def append_block(self, block):
        self.blocks.append(block)
        block.setGeometry(self.width() / 2 - 130, self.height() / 2 - 160, 260, 320)
        block.show()
        
    def paintEvent(self, event):
        super().paintEvent(event)
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
        self.main_frame = QFrame()
        main_layout = QGridLayout()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
            
        self.query = query
        self.pos = QPoint(0, 0)
        self.delta = QPoint(0, 0)
        self.offset = QPoint(0, 0)
        self.main_label = QLabel(name, self)
        self.main_label.setMinimumHeight(24)
        self.main_label.setMaximumHeight(24)

        main_layout.addWidget(self.main_label, 0, 0)
        main_layout.addWidget(self.main_frame, 1, 0)

        self.setup(layout)
        self.setLayout(main_layout)
        self.main_frame.setLayout(layout)
        self.setMinimumWidth(min_width)
        self.setMinimumHeight(min_height)
        self.setStyleSheet("""
ProcessBlock {
    border-radius: 6px;
    border-style: solid;
    border-width: 2px;
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

    def setup(self, layout):
        self.recipient = QLineEdit("")
        self.recipient.setPlaceholderText("recipient")

        self.when = QDateTimeEdit()

        self.body = QTextEdit("")
        self.body.setPlaceholderText("Enter the body of the email here")
        layout.addWidget(self.recipient, 0, 0)
        layout.addWidget(self.when, 1, 0)
        layout.addWidget(self.body, 2, 0)
