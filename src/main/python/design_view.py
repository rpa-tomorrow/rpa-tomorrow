import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import traceback
import sys
from datetime import datetime
from model import ProcessModel, EntryPointModel, SendEmailModel

from lib.automate.modules.send import Send
from lib.automate.modules.schedule import Schedule
from lib.automate.modules.reminder import Reminder
from lib.nlp.nlp import NLP
from lib.settings import SETTINGS


def display_error_message(message, title="Error"):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.resize(360, 280)
    msg.exec_()


class DesignView(QtWidgets.QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(DesignView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = self.main_window.model
        # self.threadpool = QThreadPool()

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)

        # Load nlp model somewhere else takes forever!!!
        self.nlp = None

        self.title = QtWidgets.QLabel("Design")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)
        layout.addWidget(self.title)

        self.process_text_edit = ProcessTextEditView("")
        self.process_text_edit.setMaximumHeight(180)

        self.main_process = EntryPointModel("main", 32, 32, 120, 70)
        self.model.processes.append(self.main_process)
        self.process_editor = ProcessEditorView(self.model)

        layout.addWidget(self.process_text_edit)
        layout.addWidget(self.process_editor)
        self.setLayout(layout)
        self.process_text_edit.installEventFilter(self)

    def handle_response(self, task, followup):
        self.main_window.set_info_message(str(followup).replace("\n", ". ") + ".")
        return task

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.process_text_edit:
            if event.key() == QtCore.Qt.Key_Return and self.process_text_edit.hasFocus():
                self.submit_input_text()
                return True
        return super().eventFilter(obj, event)

    def submit_input_text(self):
        if not self.nlp:
            self.nlp = NLP(SETTINGS["nlp_models"]["basic"], SETTINGS["nlp_models"]["spacy"])
            self.nlp.automate.response_callback = self.handle_response

        self.process_text_edit.save_cursor_pos()

        query = self.process_text_edit.toPlainText()
        model = None
        view = None

        try:
            task = self.nlp.prepare(query)
            # TODO(alexander): use different models, but they are all similar atm.
            model = SendEmailModel(self.process_editor, query, task.to, task.when, task.body)
            if isinstance(task, Send):
                model.name = "Send Email"
            elif isinstance(task, Reminder):
                model.name = "Reminder"
            elif isinstance(task, Schedule):
                model.name = "Schedule"
            else:
                display_error_message("Failed to understand what task you wanted to perform.")
                return
            view = SendEmailView(model)
        except Exception:  # noqa: E722
            traceback.print_exc()
            self.process_text_edit.restore_cursor_pos()
            display_error_message(str(sys.exc_info()[1]) + ".")
            return

        view = ProcessView(self.process_editor, view, model)
        view.show()

        self.process_text_edit.set_cursor_pos(0)
        self.process_text_edit.clear()
        self.process_editor.append_process(view, model)


class ProcessTextEditView(QtWidgets.QTextEdit):
    def __init__(self, *args, **kwargs):
        super(ProcessTextEditView, self).__init__(*args, **kwargs)
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


class ProcessEditorView(QtWidgets.QFrame):
    def __init__(self, model):
        super(ProcessEditorView, self).__init__()
        self.model = model
        self.process_views = []
        self.in_connectors = []
        self.out_connectors = []
        self.snapped_connector = None
        self.active_connector = None
        self.grid_size = 32
        self.update()
        self.pos = QtCore.QPoint(self.grid_size / 2, self.grid_size / 2)
        self.delta = QtCore.QPoint(0, 0)
        self.offset = QtCore.QPoint(0, 0)
        self.mouse_pos = QtCore.QPoint(0, 0)
        self.dragging = False
        self.setMouseTracking(True)

        for proc in self.model.processes:
            if isinstance(proc, SendEmailModel):  # TODO(alexander): might not be the most effective method!!!
                self.process_views.append(ProcessView(self, SendEmailView(proc), proc))
            elif isinstance(proc, EntryPointModel):
                self.process_views.append(ProcessView(self, QtWidgets.QFrame(), proc, False))
            else:
                self.process_views.append(ProcessView(self, QtWidgets.QFrame(), proc))

    def append_process(self, view, model):
        if len(self.process_views) > 0:
            prev_view = self.process_views[0]
            out_conn = prev_view.out_connector
            while out_conn.connected:
                prev_view = out_conn.connected.view
                out_conn = prev_view.out_connector
            model.x = prev_view.x() + prev_view.width() + 64
            model.y = prev_view.y()
            out_conn.connect(view.in_connector)

        self.process_views.append(view)
        self.model.processes.append(model)
        view.setGeometry(model.x, model.y, model.width, model.height)
        view.pos = QtCore.QPoint(model.x, model.y)
        view.show()
        view.update_connectors()
        self.update()

    def remove_process(self, view, model):
        self.process_views.delete(view)
        self.model.processes.remove(model)
        view.close()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QtGui.QPainter(self)
        p.setRenderHints(QtGui.QPainter.HighQualityAntialiasing)
        if SETTINGS["editor"]["theme"] == "light-theme":
            p.setPen(QtGui.QPen(QtGui.QColor("#e0e0e0"), 1))
        else:
            p.setPen(QtGui.QPen(QtGui.QColor("#2d333b"), 1))
        xoff = (self.pos.x() + self.delta.x()) % self.grid_size
        yoff = (self.pos.y() + self.delta.y()) % self.grid_size
        for i in range(0, self.width() + self.grid_size, self.grid_size):
            p.drawLine(i - xoff, 0, i - xoff, self.height())

        for i in range(0, self.height() + self.grid_size, self.grid_size):
            p.drawLine(0, i - yoff, self.width(), i - yoff)

        p.setPen(QtGui.QPen(QtGui.QColor("#1d8ac4"), 3))

        for out_conn in self.out_connectors:
            if out_conn.connected:
                out_x = out_conn.x() + 7
                out_y = out_conn.y() + 7
                in_x = out_conn.connected.x() + 7
                in_y = out_conn.connected.y() + 7
                p.drawLine(out_x,     out_y, out_x + 16, out_y)
                p.drawLine(out_x + 16, out_y,  in_x - 16,  in_y)
                p.drawLine( in_x - 16,  in_y, in_x, in_y)
            
        if self.active_connector:
            out_x = self.active_connector.x() + 7
            out_y = self.active_connector.y() + 7
            in_x = self.mouse_pos.x()
            in_y = self.mouse_pos.y()
            if self.snapped_connector: # snap to nearby connector
                in_x = self.snapped_connector.x() + 7
                in_y = self.snapped_connector.y() + 7

            if not self.active_connector.output: # swap connector position
                temp_x = in_x; temp_y = in_y
                in_x = out_x; in_y = out_y
                out_x = temp_x; out_y = temp_y

            p.drawLine(out_x,     out_y, out_x + 16, out_y)
            p.drawLine(out_x + 16, out_y,  in_x - 16,  in_y)
            p.drawLine( in_x - 16,  in_y, in_x, in_y)
        p.end()

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.RightButton:
            self.offset = event.pos()
            for view in self.process_views:
                view.offset = event.pos()
            self.dragging = True

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos();
        if event.buttons() & QtCore.Qt.RightButton and self.dragging:
            self.delta = self.offset - event.pos()
            for view in self.process_views:
                view.delta = event.pos() - view.offset
                view.move(view.pos + view.delta)
                view.update_connectors()
            self.update()
        elif self.active_connector:
            self.mouse_pos += QtCore.QPoint(self.active_connector.x(), self.active_connector.y())

            # Snapping to nearby connectors
            snapped = False
            connectors = self.in_connectors if self.active_connector.output else self.out_connectors;
            for in_conn in connectors:
                if in_conn.view == self.active_connector.view: continue
                rect = QtCore.QRect(QtCore.QPoint(in_conn.x() - 8, in_conn.y() - 8), QtCore.QSize(30, 30))
                if rect.contains(self.mouse_pos):
                    self.snapped_connector = in_conn;
                    self.snapped_connector.setChecked(True)
                    snapped = True
                    break
                
                if not snapped:
                    if self.snapped_connector and not self.snapped_connector.connected:
                        self.snapped_connector.setChecked(False)
                    self.snapped_connector = None;
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.pos = self.pos + self.delta
            self.delta = QtCore.QPoint(0, 0)
            for view in self.process_views:
                view.pos = view.pos + view.delta
                view.delta = QtCore.QPoint(0, 0)
            self.dragging = False

        # Connect two processes together
        if self.active_connector and self.snapped_connector:
            if not self.active_connector == self.snapped_connector:
                in_conn = self.snapped_connector
                out_conn = self.active_connector
                in_conn.disconnect()
                out_conn.disconnect()
                out_conn.connect(in_conn)

        self.snapped_connector = None
        self.active_connector = None
        self.update()


class ProcessConnector(QtWidgets.QToolButton):
    def __init__(self, process_editor, view, output=True):
        super(ProcessConnector, self).__init__(process_editor)
        self.process_editor = process_editor
        self.view = view
        self.output = output
        self.connected = None;
        self.setMinimumWidth(14)
        self.setMinimumHeight(14)
        self.setMaximumWidth(14)
        self.setMaximumHeight(14)
        self.setCheckable(True)
        self.setChecked(False)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

    def connect(self, other_conn):
        if not self.output == other_conn.output:
            if self.view.accept_input or self.output:
                if other_conn.view.accept_input or other_conn.output:
                    self.connected = other_conn
                    self.setChecked(True)
                    other_conn.connected = self
                    other_conn.setChecked(True)

    def disconnect(self):
        if self.connected:
            self.connected.setChecked(False)
            self.connected.connected = None
            self.connected = None
        
    def mouseMoveEvent(self, event):
        self.process_editor.mouseMoveEvent(event)
        
    def mousePressEvent(self, event):
        if self.connected:
            self.connected.setChecked(False)
            self.connected.connected = None
            self.connected = None
            self.setChecked(False)
        self.process_editor.active_connector = self

    def mouseReleasedEvent(self, event):
        self.setChecked(False)
        

class ProcessView(QtWidgets.QFrame):
    def __init__(self, process_editor, view, model, accept_input=True):
        super(ProcessView, self).__init__(process_editor)
        self.process_editor = process_editor
        self.accept_input = accept_input;
        self.view = view
        self.query = model.query
        self.name = model.name
        self.model = model

        layout = QtWidgets.QGridLayout()

        self.default_width = 260
        self.default_height = 320
        self.pos = QtCore.QPoint(model.x, model.y)
        self.offset = QtCore.QPoint(0, 0)
        self.delta = QtCore.QPoint(0, 0)
        self.title = QtWidgets.QLabel(self.name)
        self.title.setMinimumHeight(24)
        self.title.setMaximumHeight(24)

        layout.addWidget(self.title, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.view,  1, 0, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Next"), 2, 0, 1, 1, QtCore.Qt.AlignRight)

        self.setLayout(layout)
        self.setGeometry(model.x, model.y, model.width, model.height)

        self.in_connector = ProcessConnector(self.process_editor, self, False)
        self.out_connector = ProcessConnector(self.process_editor, self, True)
        self.process_editor.in_connectors.append(self.in_connector)
        self.process_editor.out_connectors.append(self.out_connector)
        self.update_connectors()
        if accept_input:
            self.in_connector.show()
        else:
            self.in_connector.hide()
        self.out_connector.show()

    def update_connectors(self):
        self.in_connector.move(self.pos.x() + self.delta.x() - 7,
                               self.pos.y() + self.delta.y() + 13);
        self.out_connector.move(self.pos.x() + self.delta.x() + self.width() - 8,
                                self.pos.y() + self.delta.y() + self.height() - 27);

    def contextMenuEvent(self, event):
        contextMenu = QtWidgets.QMenu(self)
        # edit = contextMenu.addAction("Edit")
        # change_type = QMenu("Change type")
        # contextMenu.addMenu(change_type)
        # change_to_email = change_type.addAction("Send Email")
        # change_to_reminder = change_type.addAction("Reminder")
        # change_to_schedule = change_type.addAction("Schedule")
        delete = contextMenu.addAction("Delete")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        # if action == edit:
        # self.process_editor.process_text_edit.setText(self.query)
        if action == delete:
            self.process_editor.remove_process(self, self.model)
        self.process_editor.update()

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.raise_()
            self.in_connector.raise_()
            self.out_connector.raise_()
            self.offset = event.pos()
        elif event.buttons() & QtCore.Qt.RightButton:
            self.contextMenuEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            self.pos = self.mapToParent(event.pos() - self.offset)
            self.move(self.pos)
            self.update_connectors()
            self.parent().update()

    def setup(self, layout):
        return


class SendEmailView(QtWidgets.QFrame):
    def __init__(self, model):
        super(SendEmailView, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.model = model

        self.recipients = QtWidgets.QLineEdit(", ".join(model.recipients))
        self.recipients.setPlaceholderText("Recipient1, Recipient2, ...")
        self.recipients.textChanged.connect(model.setRecipients)

        self.when = QtWidgets.QDateTimeEdit(QtCore.QDateTime(model.when))
        self.when.dateTimeChanged.connect(self.setWhen)

        self.body = QtWidgets.QTextEdit(model.body)
        self.body.setPlaceholderText("Enter the body...")
        self.body.textChanged.connect(model.setBody)

        layout.addWidget(self.recipients)
        layout.addWidget(self.when)
        layout.addWidget(self.body)

        self.setLayout(layout)

    def setWhen(self, dt):
        self.model.setWhen(dt.toPyDateTime())


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    view = window.content.design_view

    editor = view.process_editor
    time_now = datetime.now()
    model1 = SendEmailModel("Send email", "Email John Doe Hello World", ["John Doe"], time_now, "Hello World")
    model2 = SendEmailModel("Reminder", "Remind John Doe Hello World", ["John Doe"], time_now, "Hello World")
    model3 = SendEmailModel("Schedule", "Schedule John Doe Hello World", ["John Doe"], time_now, "Hello World")
    view1 = SendEmailView(model1)
    view2 = SendEmailView(model2)
    view3 = SendEmailView(model3)
    editor.append_process(ProcessView(editor, view1, model1), model1)
    editor.append_process(ProcessView(editor, view2, model2), model2)
    editor.append_process(ProcessView(editor, view3, model3), model3)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
