from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from PySide6.QtGui import QGuiApplication

from ui.journal_tab import create_journal_tab
from ui.tracker_tab import create_tracker_tab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Journey")
        self.resize(1000, 650)

        tabs = QTabWidget()
        tabs.addTab(create_tracker_tab(), "Tracker")
        tabs.addTab(create_journal_tab(), "Journal")

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        self.setLayout(layout)

    def center_on_screen(self):
        screen = self.screen()

        if screen is None:
            screen = QGuiApplication.primaryScreen()

        if screen is None:
            return

        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()

        x = (
            screen_geometry.x()
            + (screen_geometry.width() - window_geometry.width()) // 2
        )
        y = (
            screen_geometry.y()
            + (screen_geometry.height() - window_geometry.height()) // 2
        )

        self.move(x, y)
