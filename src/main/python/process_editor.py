import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import copy
import uuid

import process_models as proc_models

from lib.settings import SETTINGS

from process_view import ProcessView
from views.send_email_view import SendEmailView


class ProcessEditor(QtWidgets.QFrame):
    def __init__(self, design_view, model):
        super(ProcessEditor, self).__init__()
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