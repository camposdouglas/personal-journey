from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class RoutineTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        placeholder_label = QLabel("Routine chart coming next.")
        placeholder_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(placeholder_label)
        self.setLayout(layout)


def create_routine_tab():
    return RoutineTab()
