import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import datetime

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




