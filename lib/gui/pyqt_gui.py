from PyQt5.QtWidgets import *

def create_app_window():
    app = QApplication([])
    label = QLabel('Hello World!')
    label.show()
    return app


if __name__ == "__main__":
    app = create_app_window()
    app.exec_()
    
