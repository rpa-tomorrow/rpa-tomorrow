from PyQt5 import QtWidgets, QtGui, QtCore

def display_error_message(main_window, message, title="Error"):
    msg_background = QtWidgets.QWidget(main_window)
    msg_background.setGeometry(0, 0, main_window.width(), main_window.height())
    msg_background.setObjectName("modalBackground")
    msg_background.show()
    
    main_layout = QtWidgets.BoxLayout()
    
    msg_box = QtWidgets.QWidget(main_window)

    layout = QtWidgets.QGridLayout()
    label_title = QtWidgets.QLabel(title)
    label_message = QtWidgets.QLabel(message)

    layout.addWidget(label_title, 0, 0)
    layout.addWidget(label_message, 1, 0)
    msg_box.setLayout(layout)
    
    msg_background.show()
    msg_box.show()

# NOTE(alexander): DEV mode entry point only!!!
if __name__ == "__main__":
    from main import initialize_app

    appctxt, window = initialize_app()
    display_error_message(window, "Hello world this is just a test error message")
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
