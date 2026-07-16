from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


def create_tracker_tab():
    tab = QWidget()
    layout = QVBoxLayout()

    label = QLabel("Tracker tab")
    layout.addWidget(label)

    tab.setLayout(layout)
    return tab
