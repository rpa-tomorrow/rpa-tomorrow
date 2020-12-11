#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore

class InfoView(QtWidgets.QWidget):
    def __init__(self, main_window, *args, **kwargs):
        super(InfoView, self).__init__(*args, **kwargs)
        self.main_window = main_window

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setMaximumWidth(960)
        scroll_area.setWidgetResizable(True)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(scroll_area)

        widget = QtWidgets.QWidget()
        widget.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(8)

        self.title = QtWidgets.QLabel("Info")
        self.title.setObjectName("viewTitle")
        self.title.setMaximumHeight(48)
        layout.addWidget(self.title)

        self.doc = QtWidgets.QLabel(
            """<h2>RPA Tomorrow</h2>
<h3>About</h3>

RPA Tomorrow is an open source project for Robotic Process Automation (RPA) created powered by Natural Language 
Processing. RPA Tomorrow project was proposed by Substorm AI and written by students at Luleå University of Technology.

<h3>RPA Tomorrow Team</h3>

""")
        self.doc.setMaximumWidth(860)
        self.doc.setWordWrap(True)
        
        layout.addWidget(self.doc)
        layout.addWidget(ContributorView(":hugowangler.png", "Hugo Wangler", "Automation Developer"))
        layout.addWidget(ContributorView(":markhakansson.jpg", "Mark Håkansson", "AI Developer"))
        layout.addWidget(ContributorView(":blinningjr.png", "Niklas Lundberg", "Automation Developer"))
        layout.addWidget(ContributorView(":widforss.jpg", "Aron Widforss", "Automation Developer"))
        layout.addWidget(ContributorView(":97gushan.png", "Gustav Hansson", "Automation Developer"))
        layout.addWidget(ContributorView(":aleman778.jpg", "Alexander Mennborg", "GUI Developer"))
        layout.addWidget(ContributorView(":viktorfrom.jpg", "Viktor From", "AI Developer"))

        layout.addStretch(1)

        self.setLayout(main_layout)
        widget.setLayout(layout)
        scroll_area.setWidget(widget)

class ContributorView(QtWidgets.QWidget):
    def __init__(self, avatar_file, name, task):
        super(ContributorView, self).__init__()
        layout = QtWidgets.QGridLayout()
        layout.setHorizontalSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        # Make rounded avatar bitmap
        avatar_pixmap = QtGui.QPixmap(avatar_file)
        bitmap = QtGui.QBitmap(avatar_pixmap.width(), avatar_pixmap.height())
        bitmap.fill(QtCore.Qt.color0)
        p = QtGui.QPainter(bitmap)
        p.setBrush(QtCore.Qt.color1)
        p.drawRoundedRect(0, 0, bitmap.width(), bitmap.height(), bitmap.width()/2, bitmap.height()/2)
        avatar_pixmap.setMask(bitmap)
        p.end()

        self.avatar_label = QtWidgets.QLabel()
        self.avatar_label.setPixmap(avatar_pixmap)
        self.avatar_label.setScaledContents(True);
        self.avatar_label.setObjectName("roundedAvatar")
        layout.addWidget(self.avatar_label, 0, 0, 2, 1)

        self.name_label = QtWidgets.QLabel(name)
        layout.addWidget(self.name_label, 0, 1)
        
        self.task_label = QtWidgets.QLabel(task)
        self.task_label.setObjectName("fontFaint")
        layout.addWidget(self.task_label, 1, 1)

        self.setLayout(layout)


# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app
    import sys
    
    appctxt, window = initialize_app()
    window.set_active_view(6)
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
