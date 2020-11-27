import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from process_connector import ProcessConnector

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