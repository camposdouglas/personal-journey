from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ui.routine_clock import RoutineClock


class RoutineSchedulePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.clock = RoutineClock()
        self.controls_panel = self.create_controls_panel()

        layout.addWidget(self.clock, 3)
        layout.addWidget(self.controls_panel, 2)
        self.setLayout(layout)

    def create_controls_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Routine block name")

        self.start_time_input = QTimeEdit(QTime(0, 0))
        self.start_time_input.setDisplayFormat("HH:mm")

        self.end_time_input = QTimeEdit(QTime(1, 0))
        self.end_time_input.setDisplayFormat("HH:mm")

        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#RRGGBB")

        self.add_button = QPushButton("Add")
        self.add_button.setEnabled(False)

        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Start", self.start_time_input)
        form_layout.addRow("End", self.end_time_input)
        form_layout.addRow("Color", self.color_input)
        form_layout.addRow(self.add_button)

        tasks_label = QLabel("Routine blocks")
        tasks_label.setStyleSheet("font-weight: bold;")

        self.tasks_list = QListWidget()
        self.empty_label = QLabel("No routine blocks yet.")

        layout.addLayout(form_layout)
        layout.addWidget(tasks_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.tasks_list)

        panel.setLayout(layout)
        return panel


class RoutineTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.schedule_tabs = QTabWidget()
        self.weekdays_page = RoutineSchedulePage()
        self.weekends_page = RoutineSchedulePage()

        self.schedule_tabs.addTab(self.weekdays_page, "Weekdays")
        self.schedule_tabs.addTab(self.weekends_page, "Weekends")

        layout.addWidget(self.schedule_tabs)
        self.setLayout(layout)


def create_routine_tab():
    return RoutineTab()
