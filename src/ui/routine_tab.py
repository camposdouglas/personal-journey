from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

import routine_repository as repo
from ui.routine_clock import RoutineClock


class RoutineBlockList(QListWidget):
    def focusInEvent(self, event):
        super().focusInEvent(event)

        if not self.selectedItems():
            self.setCurrentRow(-1)

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.position().toPoint())

        if clicked_item is None:
            self.clearSelection()
            self.setCurrentRow(-1)

        super().mousePressEvent(event)


class RoutineSchedulePage(QWidget):
    def __init__(self, schedule_type):
        super().__init__()

        self.schedule_type = schedule_type
        self.editing_block_id = None
        self.loading_form = False

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

        self.add_edit_button = QPushButton("Add")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.delete_button = QPushButton("Delete")

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_edit_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.delete_button)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #FF3131;")
        self.error_label.setWordWrap(True)

        self.name_input.textChanged.connect(self.handle_form_changed)
        self.start_time_input.timeChanged.connect(self.handle_form_changed)
        self.end_time_input.timeChanged.connect(self.handle_form_changed)
        self.color_input.textChanged.connect(self.handle_form_changed)
        self.add_edit_button.clicked.connect(self.handle_add_edit)
        self.save_button.clicked.connect(self.save_edit)
        self.cancel_button.clicked.connect(self.cancel_edit)
        self.delete_button.clicked.connect(self.delete_block)

        form_layout.addRow("Name", self.name_input)
        form_layout.addRow("Start", self.start_time_input)
        form_layout.addRow("End", self.end_time_input)
        form_layout.addRow("Color", self.color_input)
        form_layout.addRow(self.error_label)
        form_layout.addRow(buttons_layout)

        tasks_label = QLabel("Routine blocks")
        tasks_label.setStyleSheet("font-weight: bold;")

        self.tasks_list = RoutineBlockList()
        self.tasks_list.itemSelectionChanged.connect(self.show_selected_block)
        self.empty_label = QLabel("No routine blocks yet.")

        layout.addLayout(form_layout)
        layout.addWidget(tasks_label)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.tasks_list)

        panel.setLayout(layout)
        self.refresh_tasks()
        self.update_form_state()
        return panel

    def handle_form_changed(self):
        if self.loading_form:
            return

        if self.editing_block_id is None:
            self.tasks_list.clearSelection()
            self.tasks_list.setCurrentItem(None)

        self.update_form_state()

    def show_selected_block(self):
        if self.editing_block_id is not None:
            return

        block_id = self.current_block_id()

        if block_id is None:
            self.set_form_editable(True)
            self.clear_form()
        else:
            block = repo.get_block(block_id)

            if block is None:
                self.refresh_tasks()
                return

            self.populate_form(block)
            self.set_form_editable(False)

        self.update_form_state()

    def update_form_state(self, *args):
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
        selected_block_id = self.current_block_id()
        is_editing = self.editing_block_id is not None

        self.add_edit_button.setText(
            "Edit" if selected_block_id is not None else "Add"
        )
        self.add_edit_button.setEnabled(
            not is_editing and (selected_block_id is not None or is_valid)
        )
        self.save_button.setEnabled(is_editing and is_valid)
        self.cancel_button.setEnabled(is_editing)
        self.delete_button.setEnabled(
            is_editing or selected_block_id is not None
        )

    def handle_add_edit(self):
        if self.current_block_id() is None:
            self.add_block()
        else:
            self.start_edit()

    def add_block(self):
        repo.create_block(
            self.schedule_type,
            self.name_input.text(),
            time_to_minutes(self.start_time_input.time()),
            time_to_minutes(self.end_time_input.time()),
            self.color_input.text().strip(),
        )

        self.refresh_tasks()
        self.name_input.clear()
        self.color_input.clear()
        self.update_form_state()

    def start_edit(self, *args):
        block_id = self.current_block_id()

        if block_id is None:
            return

        block = repo.get_block(block_id)

        if block is None:
            self.refresh_tasks()
            self.update_form_state()
            return

        self.editing_block_id = block_id
        self.tasks_list.setEnabled(False)
        self.populate_form(block)
        self.set_form_editable(True)
        self.update_form_state()

    def save_edit(self):
        if self.editing_block_id is None:
            return

        repo.update_block(
            self.editing_block_id,
            self.name_input.text(),
            time_to_minutes(self.start_time_input.time()),
            time_to_minutes(self.end_time_input.time()),
            self.color_input.text().strip(),
        )
        self.finish_edit()

    def cancel_edit(self):
        if self.editing_block_id is None:
            return

        self.finish_edit()

    def finish_edit(self):
        self.editing_block_id = None
        self.tasks_list.setEnabled(True)
        self.refresh_tasks()
        self.set_form_editable(True)
        self.clear_form()
        self.update_form_state()

    def delete_block(self):
        block_id = self.editing_block_id or self.current_block_id()

        if block_id is None:
            return

        answer = QMessageBox.question(
            self,
            "Delete Routine Block",
            "Delete this routine block permanently?",
            QMessageBox.Yes | QMessageBox.Cancel,
            QMessageBox.Cancel,
        )

        if answer != QMessageBox.Yes:
            return

        repo.delete_block(block_id)
        self.editing_block_id = None
        self.tasks_list.setEnabled(True)
        self.refresh_tasks()
        self.set_form_editable(True)
        self.clear_form()
        self.update_form_state()

    def populate_form(self, block):
        self.loading_form = True
        self.name_input.setText(block["name"])
        self.start_time_input.setTime(minutes_to_time(block["start_minute"]))
        self.end_time_input.setTime(minutes_to_time(block["end_minute"]))
        self.color_input.setText(block["color"])
        self.loading_form = False

    def clear_form(self):
        self.loading_form = True
        self.name_input.clear()
        self.start_time_input.setTime(QTime(0, 0))
        self.end_time_input.setTime(QTime(1, 0))
        self.color_input.clear()
        self.loading_form = False

    def set_form_editable(self, editable):
        self.name_input.setReadOnly(not editable)
        self.start_time_input.setReadOnly(not editable)
        self.end_time_input.setReadOnly(not editable)
        self.color_input.setReadOnly(not editable)

    def refresh_tasks(self):
        self.tasks_list.clear()
        blocks = repo.list_blocks(self.schedule_type)
        self.clock.set_blocks(blocks)

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

    def current_block_id(self):
        selected_items = self.tasks_list.selectedItems()

        if not selected_items:
            return None

        return selected_items[0].data(Qt.UserRole)


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


def minutes_to_time(minutes):
    hour, minute = divmod(minutes, 60)
    return QTime(hour, minute)
