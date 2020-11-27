import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class SideBarMenu(QtWidgets.QFrame):
    def __init__(self, parent, *args, **kwargs):
        super(SideBarMenu, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.parent = parent
        self.setMaximumWidth(84)

        self.items = []
        self.items.append(MenuBarButton(self, 0, "Design", "\uf044"))
        self.items.append(MenuBarButton(self, 1, "Save", "\uf0c7"))
        self.items.append(MenuBarButton(self, 2, "Load", "\uf115"))
        self.items.append(MenuBarButton(self, 3, "Run", "\uf04b"))
        self.items.append(MenuBarButton(self, 4, "Settings", "\uf013"))
        self.items.append(MenuBarButton(self, 5, "Info", "\uf05a"))

        self.items[0].setChecked(True)

        for item in self.items:
            layout.addWidget(item)
        layout.insertStretch(-1, 1)

        self.setLayout(layout)

    def set_active_view(self, target, view):
        for item in self.items:
            item.setChecked(False)
        target.setChecked(True)
        self.parent.set_active_view(view)

class MenuBarButton(QtWidgets.QToolButton):
    def __init__(self, parent, view_id, name, text, *args, **kwargs):
        super(MenuBarButton, self).__init__(*args, **kwargs)
        self.setFixedSize(84, 84)
        self.setMaximumHeight(84)
        self.setText(text)
        self.setCheckable(True)
        self.parent = parent
        self.view_id = view_id
        self.clicked.connect(self.set_active_view)
        self.label = QtWidgets.QLabel(name, self)
        self.label.setMinimumWidth(84)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.move(0, 50)

    def set_active_view(self):
        self.parent.set_active_view(self, self.view_id)