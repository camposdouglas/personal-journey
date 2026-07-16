from PySide6.QtWidgets import QMainWindow, QTabWidget

from ui.journal_tab import create_journal_tab
from ui.tracker_tab import create_tracker_tab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Journey")
        self.resize(900, 600)

        tabs = QTabWidget()

        journal_tab = create_journal_tab()
        tracker_tab = create_tracker_tab()

        tabs.addTab(journal_tab, "Journal")
        tabs.addTab(tracker_tab, "Tracker")

        self.setCentralWidget(tabs)
