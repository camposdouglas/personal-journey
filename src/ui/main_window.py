from PySide6.QtWidgets import QMessageBox, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtGui import QGuiApplication

from ui.journal_tab import create_journal_tab
from ui.tracker_tab import create_tracker_tab


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Journey")
        self.resize(1000, 650)

        self.tracker_tab = create_tracker_tab()
        self.journal_tab = create_journal_tab()

        tabs = QTabWidget()
        tabs.addTab(self.tracker_tab, "Tracker")
        tabs.addTab(self.journal_tab, "Journal")

        layout = QVBoxLayout()
        layout.addWidget(tabs)

        self.setLayout(layout)

    def closeEvent(self, event):
        has_unsaved_changes = (
            self.journal_tab.is_editing
            or self.tracker_tab.has_active_tracker_edit()
        )

        if not has_unsaved_changes:
            event.accept()
            return

        answer = QMessageBox.warning(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Close the application and discard them?",
            QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if answer == QMessageBox.Discard:
            event.accept()
        else:
            event.ignore()

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
