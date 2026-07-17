import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    QTimer.singleShot(200, window.center_on_screen)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
