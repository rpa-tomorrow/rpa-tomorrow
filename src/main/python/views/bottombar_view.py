import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore

class BottomBar(QtWidgets.QFrame):
    def __init__(self, *args, **kwargs):
        super(BottomBar, self).__init__(*args, **kwargs)
        layout = QtWidgets.QHBoxLayout()
        # layout.setContentsMargins(8, 0, 8, )
        self.setMaximumHeight(32)
        # self.running_tasks_btn = QtWidgets.QToolButton()
        # self.running_tasks_btn.setText("\uf0ae")
        self.info_label = QtWidgets.QLabel("Done!")

        # layout.addWidget(self.running_tasks_btn)
        layout.addWidget(self.info_label)
        layout.addStretch(1)

        self.setLayout(layout)
