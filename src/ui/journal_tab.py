from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def create_journal_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Journal tab")
    layout.addWidget(label)

    tab.setLayout(layout)
    return tab
