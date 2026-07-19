from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

import routine_repository as repo
from ui.routine_clock import RoutineClock


class RoutineSchedulePage(QWidget):
    def __init__(self, schedule_type):
        super().__init__()

        self.schedule_type = schedule_type

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

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #FF3131;")
        self.error_label.setWordWrap(True)

        self.name_input.textChanged.connect(self.update_form_state)
        self.start_time_input.timeChanged.connect(self.update_form_state)
        self.end_time_input.timeChanged.connect(self.update_form_state)
        self.color_input.textChanged.connect(self.update_form_state)
        self.add_button.clicked.connect(self.add_block)

        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Start", self.start_time_input)
        form_layout.addRow("End", self.end_time_input)
        form_layout.addRow("Color", self.color_input)
        form_layout.addRow(self.error_label)
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
        self.refresh_tasks()
        return panel

    def update_form_state(self):
        name = self.name_input.text().strip()
        color = self.color_input.text().strip()
        start_minute = time_to_minutes(self.start_time_input.time())
        end_minute = time_to_minutes(self.end_time_input.time())

        error = ""

        if color and not repo.HEX_COLOR_PATTERN.fullmatch(color):
            error = "Color must use #RRGGBB format."
        elif start_minute == end_minute:
            error = "Start and end times cannot be equal."

        is_valid = bool(
            name
            and repo.HEX_COLOR_PATTERN.fullmatch(color)
            and start_minute != end_minute
        )

        self.error_label.setText(error)
        self.add_button.setEnabled(is_valid)

    def add_block(self):
        block = repo.create_block(
            self.schedule_type,
            self.name_input.text(),
            time_to_minutes(self.start_time_input.time()),
            time_to_minutes(self.end_time_input.time()),
            self.color_input.text().strip(),
        )

        self.refresh_tasks()
        self.tasks_list.setCurrentRow(
            self.find_block_row(block["id"])
        )

        self.name_input.clear()
        self.color_input.clear()
        self.update_form_state()

    def refresh_tasks(self):
        self.tasks_list.clear()
        blocks = repo.list_blocks(self.schedule_type)

        for block in blocks:
            start_time = format_minutes(block["start_minute"])
            end_time = format_minutes(block["end_minute"])
            item = QListWidgetItem(
                f"{start_time}–{end_time}  {block['name']}  {block['color']}"
            )
            item.setData(Qt.UserRole, block["id"])
            self.tasks_list.addItem(item)

        self.empty_label.setVisible(not blocks)

    def find_block_row(self, block_id):
        for row in range(self.tasks_list.count()):
            item = self.tasks_list.item(row)

            if item.data(Qt.UserRole) == block_id:
                return row

        return -1


class RoutineTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.schedule_tabs = QTabWidget()
        self.weekdays_page = RoutineSchedulePage("weekdays")
        self.weekends_page = RoutineSchedulePage("weekends")

        self.schedule_tabs.addTab(self.weekdays_page, "Weekdays")
        self.schedule_tabs.addTab(self.weekends_page, "Weekends")

        layout.addWidget(self.schedule_tabs)
        self.setLayout(layout)


def create_routine_tab():
    return RoutineTab()


def time_to_minutes(time):
    return time.hour() * 60 + time.minute()


def format_minutes(minutes):
    hour, minute = divmod(minutes, 60)
    return f"{hour:02d}:{minute:02d}"
