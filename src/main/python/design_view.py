from PyQt5 import QtWidgets, QtGui, QtCore

import traceback
import sys
import datetime
import copy
import pyaudio
import uuid

import process_models as proc_models
import modal

from lib.speech.transcribe import transcribe
from lib.automate.modules.send import Send
from lib.automate.modules.schedule import Schedule
from lib.automate.modules.reminder import Reminder
from lib.selector.selector import ModuleSelector
from lib.settings import SETTINGS


class DesignView(QtWidgets.QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(DesignView, self).__init__(*args, **kwargs)
        self.main_window = main_window
        self.model = self.main_window.model

        layout = QtWidgets.QGridLayout()
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(8)

        # TODO(alexander): should all models be loaded before application starts instead?
        self.nlp = None

        self.title = QtWidgets.QLabel("Design")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)
        layout.addWidget(self.title)

        self.process_text_edit = ProcessTextEditView(self, "")
        self.process_text_edit.setMaximumHeight(180)

        self.main_process = proc_models.EntryPointModel()
        self.model.append_process(self.main_process)
        self.process_editor = ProcessEditorView(self, self.model)

        layout.addWidget(self.process_text_edit)
        layout.addWidget(self.process_editor)

        self.setLayout(layout)

        self.save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_model)

        self.load_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+F"), self)
        self.load_shortcut.activated.connect(self.load_model)

        self.select_all_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+A"), self)
        self.select_all_shortcut.activated.connect(self.process_editor.select_all_processes)

        self.copy_all_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        self.copy_all_shortcut.activated.connect(self.process_editor.copy_selection)

        self.paste_all_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), self)
        self.paste_all_shortcut.activated.connect(self.process_editor.paste_selection)

        self.delete_selected_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self)
        self.delete_selected_shortcut.activated.connect(self.process_editor.remove_selected_processes)

        self.cancel_actions_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self)
        self.cancel_actions_shortcut.activated.connect(self.cancel_actions)

    def save_model(self):
        if self.model.absolute_path:
            self.model.save()
            self.main_window.set_info_message("Wrote " + self.model.absolute_path)
        else:
            self.main_window.content.save_view.filename_view.setFocus()
            self.main_window.content.save_view.filename_view.selectAll()
            self.main_window.set_active_view(1)

    def load_model(self):
        self.main_window.content.load_view.filename_view.setFocus()
        self.main_window.content.load_view.filename_view.selectAll()
        self.main_window.set_active_view(2)

    def rebuild_from_loaded_model(self):
        for view in self.process_editor.process_views.values():
            view.close()
        self.process_editor.process_views.clear()

        for id, proc in self.model.processes.items():
            view = self.process_editor.create_process_view(proc)
            self.process_editor.process_views[id] = view
            view.show()

        for view in self.process_editor.process_views.values():
            try:
                other_view = self.process_editor.process_views[view.model.out_next]
                view.out_connector.connect(other_view.in_connector)
            except Exception:
                pass

        self.update()
        self.main_window.set_info_message("Loaded " + self.model.absolute_path)

    def handle_response(self, task, followup):
        self.main_window.set_info_message(str(followup).replace("\n", ". ") + ".")
        return task

    def cancel_actions(self):
        self.process_editor.deselect_all_processes()
        self.process_text_edit.cancel_editing()

    def submit_input_text(self, proc_view=None):
        if not self.nlp:
            self.nlp = ModuleSelector()
            self.nlp.automate.response_callback = self.handle_response

        self.process_text_edit.save_cursor_pos()

        query = self.process_text_edit.get_text()
        query_parts = query.split(".")
        if query == "":
            return

        tasks = []

        try:
            tasks = self.nlp.prepare(query)
        except Exception:
            traceback.print_exc()
            self.process_text_edit.restore_cursor_pos()
            modal.ModalMessageWindow(
                self.main_window, str(sys.exc_info()[1]), "Oops! Something went wrong!", modal.MSG_ERROR
            )
            return

        for i, task in enumerate(tasks):
            model = None
            view = None
            proc_query = ""
            if len(query_parts) > i:
                proc_query = query_parts[i].strip()
            if isinstance(task, Send):
                model = proc_models.SendModel()
                model.recipients = ", ".join(task.to)
                model.when = str(task.when)
                model.body = str(task.body)
            elif isinstance(task, Reminder):
                model = proc_models.ReminderModel()
                model.recipients = ", ".join(task.to)
                model.when = str(task.when)
                model.body = str(task.body)
            elif isinstance(task, Schedule):
                model = proc_models.ScheduleModel()
                model.recipients = ", ".join(task.to)
                model.when = str(task.when)
                model.body = str(task.body)
            else:
                modal.ModalMessageWindow(
                    self.main_window,
                    "Failed to understand what task you wanted to perform. Please check spelling mistakes "
                    + "or simplify your sentence and try again!",
                    "Error",
                    modal.MSG_ERROR,
                )
                return
            if model:
                model.query = proc_query
            # FIXME(alexander): uses same views for all tasks!!!
            view = SendEmailView(model)

            if not proc_view:
                proc_view = ProcessView(self.process_editor, view, model)
                proc_view.show()
                self.process_editor.append_process(proc_view, model)
                proc_view = None
            else:
                proc_view.title.setText(model.name)
                proc_view.layout.replaceWidget(proc_view.view, view)
                proc_view.view.close()
                proc_view.view = view
                self.model.remove_process(proc_view.model)
                self.model.append_process(model)
                proc_view.model = model
        self.update()

        self.process_text_edit.set_cursor_pos(0)
        self.process_text_edit.clear()


class ProcessEditorView(QtWidgets.QFrame):
    def __init__(self, design_view, model):
        super(ProcessEditorView, self).__init__()
        self.design_view = design_view
        self.model = model
        self.process_views = dict()

        self.in_connectors = []
        self.out_connectors = []
        self.snapped_connector = None
        self.active_connector = None

        self.grid_size = 32

        self.selecting = False
        self.selected_processes = []
        self.selection_box = QtWidgets.QWidget(self)
        self.selection_box.hide()
        self.selection_box.setObjectName("selectionBox")
        self.selection_pos = QtCore.QPoint(0, 0)

        self.clipboard = []

        self.pos = QtCore.QPoint(self.grid_size / 2, self.grid_size / 2)
        self.delta = QtCore.QPoint(0, 0)
        self.offset = QtCore.QPoint(0, 0)
        self.mouse_pos = QtCore.QPoint(0, 0)
        self.dragging = False

        self.setMouseTracking(True)
        self.update()

        # Create process views from provided model
        for id, proc in self.model.processes.items():
            view = self.create_process_view(proc)
            self.process_views[id] = view

        # Connect views
        for view in self.process_views.values():
            try:
                other_view = self.process_views[view.model.out_next]
                view.out_connector.connect(other_view.in_connector)
            except Exception:
                pass

    def create_process_view(self, model):  # TODO(alexander): SendEmailView is temporary
        if isinstance(model, proc_models.SendModel):
            return ProcessView(self, SendEmailView(model), model)
        elif isinstance(model, proc_models.ReminderModel):
            return ProcessView(self, SendEmailView(model), model)
        elif isinstance(model, proc_models.ScheduleModel):
            return ProcessView(self, SendEmailView(model), model)
        elif isinstance(model, proc_models.EntryPointModel):
            return ProcessView(self, QtWidgets.QFrame(), model, False)
        else:
            return ProcessView(self, QtWidgets.QFrame(), model)

    def get_entry_point(self):
        if len(self.process_views) == 0:
            return None

        for view in self.process_views.values():
            if isinstance(view.model, proc_models.EntryPointModel):
                return view
        return None

    def append_process(self, view, model):
        prev_view = self.get_entry_point()
        if prev_view:
            out_conn = prev_view.out_connector
            while out_conn.connected:
                prev_view = out_conn.connected.view
                out_conn = prev_view.out_connector
            model.x = prev_view.x() + prev_view.width() + 64
            model.y = prev_view.y()
            out_conn.connect(view.in_connector)

        self.process_views[model.id] = view
        self.model.append_process(model)
        view.setGeometry(model.x, model.y, model.width, model.height)
        view.pos = QtCore.QPoint(model.x, model.y)
        view.show()
        view.update_connectors()
        self.update()

    def remove_process(self, view):
        if isinstance(view.model, proc_models.EntryPointModel):
            return False
        if view in self.process_views.values():
            del self.process_views[view.model.id]
        self.model.remove_process(view.model)
        view.close()
        self.update()
        return True

    def remove_selected_processes(self):
        i = 0
        while i < len(self.selected_processes):
            p = self.selected_processes[i]
            if self.remove_process(p):
                self.selected_processes.remove(p)
            else:
                i += 1
        self.deselect_all_processes()

    def select_all_processes(self):
        self.selected_processes.clear()
        for p in self.process_views.values():
            self.selected_processes.append(p)
            p.set_selected(True)

    def deselect_all_processes(self):
        for p in self.selected_processes:
            p.set_selected(False)
        self.selected_processes.clear()

    def copy_selection(self):
        self.clipboard = copy.copy(self.selected_processes)

    def paste_selection(self):
        self.deselect_all_processes()
        id_translation = dict()  # NOTE(alexander): translates old ids to new model ids
        for proc in self.clipboard:
            if isinstance(proc.model, proc_models.EntryPointModel):
                continue
            new_model = copy.deepcopy(proc.model)
            new_model.x += 32
            new_model.y += 32
            new_model.id = str(uuid.uuid4())
            id_translation[proc.model.id] = new_model.id
            view = self.create_process_view(new_model)
            self.process_views[new_model.id] = view
            self.selected_processes.append(view)
            self.model.append_process(new_model)
            view.setGeometry(new_model.x, new_model.y, new_model.width, new_model.height)
            view.show()
            view.set_selected(True)

        for proc in self.clipboard:
            if isinstance(proc.model, proc_models.EntryPointModel):
                continue
            out_next = proc.model.out_next
            try:
                out_view = self.process_views[id_translation[out_next]]
                if out_view:
                    view = self.process_views[id_translation[proc.model.id]]
                    view.out_connector.connect(out_view.in_connector)
            except Exception:
                pass

        self.clipboard = copy.copy(self.selected_processes)

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
                p.drawLine(out_x, out_y, out_x + 16, out_y)
                p.drawLine(out_x + 16, out_y, in_x - 16, in_y)
                p.drawLine(in_x - 16, in_y, in_x, in_y)

        if self.active_connector:
            out_x = self.active_connector.x() + 7
            out_y = self.active_connector.y() + 7
            in_x = self.mouse_pos.x()
            in_y = self.mouse_pos.y()
            if self.snapped_connector:  # snap to nearby connector
                in_x = self.snapped_connector.x() + 7
                in_y = self.snapped_connector.y() + 7

            if not self.active_connector.output:  # swap connector position
                temp_x = in_x
                temp_y = in_y
                in_x = out_x
                in_y = out_y
                out_x = temp_x
                out_y = temp_y

            p.drawLine(out_x, out_y, out_x + 16, out_y)
            p.drawLine(out_x + 16, out_y, in_x - 16, in_y)
            p.drawLine(in_x - 16, in_y, in_x, in_y)
        p.end()

    def mousePressEvent(self, event):
        if event.buttons() & QtCore.Qt.RightButton and not self.selecting:
            self.offset = event.pos()
            for view in self.process_views.values():
                view.offset = event.pos()
            self.dragging = True

        if event.buttons() & QtCore.Qt.LeftButton and not self.dragging:
            pos = event.pos()
            self.selection_box.show()
            self.selection_box.raise_()
            self.selection_box.setGeometry(pos.x(), pos.y(), 0, 0)
            self.selecting = True
            self.selection_pos = pos
        self.setFocus()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        if event.buttons() & QtCore.Qt.RightButton and self.dragging:
            self.delta = self.offset - event.pos()
            for view in self.process_views.values():
                view.delta = event.pos() - view.offset
                view.move(view.pos + view.delta)
                view.update_connectors()
            self.update()
        elif self.active_connector:
            self.mouse_pos += QtCore.QPoint(self.active_connector.x(), self.active_connector.y())

            # Snapping to nearby connectors
            snapped = False
            connectors = self.in_connectors if self.active_connector.output else self.out_connectors
            for in_conn in connectors:
                if in_conn.view == self.active_connector.view:
                    continue
                rect = QtCore.QRect(QtCore.QPoint(in_conn.x() - 8, in_conn.y() - 8), QtCore.QSize(30, 30))
                if rect.contains(self.mouse_pos):
                    self.snapped_connector = in_conn
                    self.snapped_connector.setChecked(True)
                    snapped = True
                    break

                if not snapped:
                    if self.snapped_connector and not self.snapped_connector.connected:
                        self.snapped_connector.setChecked(False)
                    self.snapped_connector = None
            self.update()

        if event.buttons() & QtCore.Qt.LeftButton and self.selecting:
            mx = self.mouse_pos.x()
            my = self.mouse_pos.y()
            sx = self.selection_pos.x()
            sy = self.selection_pos.y()
            self.selection_box.setGeometry(sx if sx < mx else mx, sy if sy < my else my, abs(sx - mx), abs(sy - my))

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.pos = self.pos + self.delta
            self.delta = QtCore.QPoint(0, 0)
            for view in self.process_views.values():
                view.pos = view.pos + view.delta
                view.delta = QtCore.QPoint(0, 0)
            self.dragging = False

        if self.selecting:
            self.deselect_all_processes()
            self.selection_box.hide()
            for view in self.process_views.values():
                if self.selection_box.geometry().contains(view.geometry()):
                    if view not in self.selected_processes:
                        self.selected_processes.append(view)
                        view.set_selected(True)
            self.selecting = False

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


class ProcessTextEditView(QtWidgets.QFrame):
    def __init__(self, design_view, *args, **kwargs):
        super(ProcessTextEditView, self).__init__()
        self.design_view = design_view
        layout = QtWidgets.QGridLayout()

        self.text_edit = QtWidgets.QTextEdit(*args, **kwargs)
        self.text_edit.setPlaceholderText("Enter process query here")
        self.cursor_pos = 0

        self.speech_button = QtWidgets.QToolButton()
        self.speech_button.setText("\uF130")
        self.speech_button.setObjectName("iconButton")
        self.speech_button.clicked.connect(self.record_speech)

        self.submit_button = QtWidgets.QToolButton()
        self.submit_button.setText("\uF00C")
        self.submit_button.setObjectName("iconButton")
        self.submit_button.clicked.connect(self.submit_editing)

        self.cancel_button = QtWidgets.QToolButton()
        self.cancel_button.setObjectName("iconButton")
        self.cancel_button.setText("\uF00D")
        self.cancel_button.clicked.connect(self.cancel_editing)

        layout.addWidget(self.text_edit, 0, 0, 1, 4)
        layout.addWidget(self.speech_button, 1, 0)
        layout.addWidget(self.submit_button, 1, 1)
        layout.addWidget(self.cancel_button, 1, 2)
        self.cancel_button.hide()
        layout.setColumnStretch(3, 1)
        layout.setRowStretch(0, 1)
        self.setLayout(layout)
        self.text_edit.installEventFilter(self)
        self.editing = None

    def save_cursor_pos(self):
        self.cursor_pos = self.text_edit.textCursor().position()

    def restore_cursor_pos(self):
        self.set_cursor_pos(self.cursor_pos)

    def set_cursor_pos(self, pos):
        cursor = self.text_edit.textCursor()
        cursor.setPosition(pos)
        self.text_edit.setTextCursor(cursor)

    def get_text(self):
        return self.text_edit.toPlainText()

    def record_speech(self):
        try:
            self.set_cursor_pos(0)
            self.clear()
            self.text_edit.setFocus()
            audio_interface = pyaudio.PyAudio()
            transcribed_input = transcribe(audio_interface)
            self.text_edit.setText(transcribed_input)
            transcribed_input
        except Exception:
            traceback.print_exc()
            modal.ModalMessageWindow(
                self.design_view.main_window, str(sys.exc_info()[1]), "Oops! Something went wrong!", modal.MSG_ERROR
            )

    def submit_editing(self):
        self.design_view.submit_input_text(self.editing)

    def cancel_editing(self):
        if self.editing:
            self.cancel_button.hide()
            self.editing.set_editing(False)
            self.editing = None
            self.setProperty("editing", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.set_cursor_pos(0)
            self.clear()

    def edit_process(self, view, query):
        if self.editing:
            self.editing.set_editing(False)
        self.cancel_button.show()
        self.setProperty("editing", True)
        self.style().unpolish(self)
        self.style().polish(self)

        self.text_edit.setFocus()
        self.text_edit.setText(query)
        self.text_edit.selectAll()
        self.editing = view

    def clear(self):
        return self.text_edit.clear()

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.text_edit:
            if event.key() == QtCore.Qt.Key_Return and self.text_edit.hasFocus():
                self.design_view.submit_input_text(self.editing)
                self.cancel_editing()
                return True
        return super().eventFilter(obj, event)


class ProcessConnector(QtWidgets.QToolButton):
    def __init__(self, process_editor, view, output=True):
        super(ProcessConnector, self).__init__(process_editor)
        self.process_editor = process_editor
        self.view = view
        self.output = output
        self.connected = None
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
                    self.view.connection_changed(self, other_conn.view.model.id)
                    other_conn.connected = self
                    other_conn.setChecked(True)
                    other_conn.view.connection_changed(other_conn, self.view.model.id)

    def disconnect(self):
        if self.connected:
            self.connected.setChecked(False)
            self.view.connection_changed(self, -1)
            self.connected.view.connection_changed(self.connected, -1)
            self.connected.connected = None
            self.connected = None

    def mouseMoveEvent(self, event):
        self.process_editor.mouseMoveEvent(event)

    def mousePressEvent(self, event):
        self.disconnect()
        self.process_editor.active_connector = self

    def mouseReleasedEvent(self, event):
        self.setChecked(False)


class ProcessView(QtWidgets.QFrame):
    def __init__(self, process_editor, view, model, accept_input=True):
        super(ProcessView, self).__init__(process_editor)
        self.process_editor = process_editor
        self.accept_input = accept_input
        self.view = view
        self.name = model.name
        self.model = model

        self.layout = QtWidgets.QGridLayout()

        self.default_width = 260
        self.default_height = 320
        self.pos = QtCore.QPoint(model.x, model.y)
        self.offset = QtCore.QPoint(0, 0)
        self.delta = QtCore.QPoint(0, 0)
        self.title = QtWidgets.QLabel(self.name)
        self.title.setMinimumHeight(24)
        self.title.setMaximumHeight(24)

        self.layout.addWidget(self.title, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.view, 1, 0, 1, 1)
        self.layout.addWidget(QtWidgets.QLabel("Next"), 2, 0, 1, 1, QtCore.Qt.AlignRight)

        self.setLayout(self.layout)
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
        self.in_connector.move(self.pos.x() + self.delta.x() - 7, self.pos.y() + self.delta.y() + 13)
        self.out_connector.move(
            self.pos.x() + self.delta.x() + self.width() - 8, self.pos.y() + self.delta.y() + self.height() - 27
        )

    def connection_changed(self, connector, other_id):
        if connector == self.out_connector:
            self.model.out_next = other_id

    def close(self):
        super(ProcessView, self).close()
        self.in_connector.disconnect()
        self.in_connector.close()
        self.process_editor.in_connectors.remove(self.in_connector)

        self.out_connector.disconnect()
        self.out_connector.close()
        self.process_editor.out_connectors.remove(self.out_connector)

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def set_editing(self, editing):
        self.setProperty("editing", editing)
        self.style().unpolish(self)
        self.style().polish(self)

    def contextMenuEvent(self, event):
        contextMenu = QtWidgets.QMenu(self)
        edit = contextMenu.addAction("Edit")
        delete = contextMenu.addAction("Delete")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))
        if action == edit:
            self.set_editing(True)
            self.process_editor.design_view.process_text_edit.edit_process(self, self.model.query)
        elif action == delete:
            self.process_editor.remove_selected_processes()
        self.process_editor.update()

    def mousePressEvent(self, event):
        self.process_editor.setFocus()
        if event.buttons() & QtCore.Qt.LeftButton:
            if self not in self.process_editor.selected_processes:
                if not event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier):
                    self.process_editor.deselect_all_processes()
                self.process_editor.selected_processes.append(self)

            for v in self.process_editor.selected_processes:
                v.set_selected(True)
                v.raise_()
                v.in_connector.raise_()
                v.out_connector.raise_()
                v.offset = event.pos()
        elif event.buttons() & QtCore.Qt.RightButton:
            self.contextMenuEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            for v in self.process_editor.selected_processes:
                v.pos = v.mapToParent(event.pos() - v.offset)
                v.move(v.pos)
                v.update_connectors()
                v.parent().update()
                v.model.x = v.pos.x()
                v.model.y = v.pos.y()

    def setup(self, layout):
        return


class SendEmailView(QtWidgets.QFrame):
    def __init__(self, model):
        super(SendEmailView, self).__init__()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.model = model

        self.recipients = QtWidgets.QLineEdit(model.recipients)
        self.recipients.setPlaceholderText("Recipient1, Recipient2, ...")
        self.recipients.textChanged.connect(model.set_recipients)

        self.when = QtWidgets.QDateTimeEdit()
        try:
            dt = model.when
            if isinstance(model.when, str):
                dt = datetime.datetime.fromisoformat(model.when)
            self.when.setDateTime(QtCore.QDateTime(dt))
        except Exception:
            dt = datetime.datetime.now()
            self.when.setDateTime(QtCore.QDateTime(dt))
            model.when = str(dt)
        self.when.dateTimeChanged.connect(self.set_when)

        self.body = QtWidgets.QTextEdit(model.body)
        self.body.setPlaceholderText("Enter the body...")
        self.body.textChanged.connect(self.set_body)

        layout.addWidget(self.recipients)
        layout.addWidget(self.when)
        layout.addWidget(self.body)

        self.setLayout(layout)

    def set_when(self, dt):
        self.model.set_when(dt.toPyDateTime())

    def set_body(self):
        self.model.set_body(self.body.toPlainText())


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    view = window.content.design_view

    editor = view.process_editor
    time_now = datetime.datetime.now()

    model1 = proc_models.SendModel()
    model1.query = "Email John Doe Hello World"
    model1.recipients = "John Doe"
    model1.when = time_now
    model1.body = "Hello World"
    view1 = SendEmailView(model1)

    model2 = proc_models.ReminderModel()
    model2.query = "Remind John Doe Hello World"
    model2.recipients = "John Doe"
    model2.when = time_now
    model2.body = "Hello World"
    view2 = SendEmailView(model2)

    model3 = proc_models.ScheduleModel()
    model3.query = "Schedule a meeting with John Doe Hello World"
    model3.recipients = "John Doe"
    model3.when = time_now
    model3.body = "Hello World"
    view3 = SendEmailView(model3)

    editor.append_process(ProcessView(editor, view1, model1), model1)
    editor.append_process(ProcessView(editor, view2, model2), model2)
    editor.append_process(ProcessView(editor, view3, model3), model3)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
