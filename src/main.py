import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from db import init_db
from ui.main_window import MainWindow


def main():
    init_db()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    QTimer.singleShot(0, window.center_on_screen)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
