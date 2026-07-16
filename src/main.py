import sys

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Journey")
        self.resize(900, 600)

        tabs = QTabWidget()

        journal_tab = self.create_journal_tab()
        tracker_tab = self.create_tracker_tab()

        tabs.addTab(journal_tab, "Journal")
        tabs.addTab(tracker_tab, "Tracker")

        self.setCentralWidget(tabs)

    def create_journal_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Journal tab")
        layout.addWidget(label)

        tab.setLayout(layout)
        return tab

    def create_tracker_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Tracker tab")
        layout.addWidget(label)

        tab.setLayout(layout)
        return tab


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
