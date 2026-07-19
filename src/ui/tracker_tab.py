from datetime import date, timedelta

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import tracker_repository as repo
from week_utils import FOUNDING_WEEK_START, get_week_number, get_week_start


class DayStatusButton(QPushButton):
    statusRequested = Signal(int)

    COLORS = {
        None: "#7D7D7D",
        1: "#39FF14",
        -1: "#FF3131",
    }

    def __init__(self, status=None, blocked=False):
        super().__init__()

        self.status = status
        self.blocked = blocked

        self.setMinimumHeight(90)
        self.setEnabled(not blocked)
        self.set_status(status)

    def set_status(self, status):
        self.status = status

        if self.blocked:
            background_color = "rgba(125, 125, 125, 80)"
            symbol = ""
        else:
            background_color = self.COLORS[status]
            symbol = "+" if status == 1 else "−" if status == -1 else ""

        self.setText(symbol)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {background_color};
                border: none;
                border-radius: 6px;
                color: black;
                font-size: 32px;
                font-weight: bold;
            }}
            QPushButton:disabled {{
                background-color: rgba(125, 125, 125, 80);
                border: none;
            }}
            """
        )

    def mousePressEvent(self, event):
        if self.blocked:
            return

        if event.button() == Qt.LeftButton:
            self.statusRequested.emit(1)
            return

        if event.button() == Qt.RightButton:
            self.statusRequested.emit(-1)
            return

        super().mousePressEvent(event)


class CreateTrackerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create Tracker")
        self.setMinimumWidth(400)

        layout = QFormLayout()

        self.name_input = QLineEdit()

        self.weekly_target_input = QComboBox()
        for target in range(1, 8):
            label = "1 time per week" if target == 1 else f"{target} times per week"
            self.weekly_target_input.addItem(label, target)
        self.weekly_target_input.setCurrentIndex(6)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.create_button = self.buttons.button(QDialogButtonBox.Ok)
        self.create_button.setText("Create")
        self.create_button.setEnabled(False)

        self.name_input.textChanged.connect(self.update_create_button)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addRow("Tracker name", self.name_input)
        layout.addRow("Weekly target", self.weekly_target_input)
        layout.addRow(self.buttons)

        self.setLayout(layout)

    def update_create_button(self, name):
        self.create_button.setEnabled(bool(name.strip()))

    def tracker_name(self):
        return self.name_input.text().strip()

    def weekly_target(self):
        return self.weekly_target_input.currentData()


class TrackerPage(QWidget):
    trackerUpdated = Signal(dict)
    trackerArchived = Signal()
    progressChanged = Signal()

    def __init__(self, tracker, week_start, read_only=False):
        super().__init__()

        self.tracker = tracker
        self.week_start = week_start
        self.read_only = read_only
        self.is_editing = False

        layout = QVBoxLayout()

        today = date.today()

        target = self.tracker["weekly_target"]
        self.name_label = QLabel(self.tracker["name"])
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.name_input = QLineEdit()
        self.name_input.setAlignment(Qt.AlignCenter)
        self.name_input.setVisible(False)

        self.target_label = QLabel(f"Weekly goal: {target} days")
        self.target_label.setAlignment(Qt.AlignCenter)

        self.target_input = QComboBox()
        for weekly_target in range(1, 8):
            label = (
                "1 time per week"
                if weekly_target == 1
                else f"{weekly_target} times per week"
            )
            self.target_input.addItem(label, weekly_target)
        self.target_input.setVisible(False)

        target_input_layout = QHBoxLayout()
        target_input_layout.addStretch()
        target_input_layout.addWidget(self.target_input)
        target_input_layout.addStretch()

        blocks_layout = QHBoxLayout()
        statuses = repo.list_week_statuses(self.tracker["id"], self.week_start)
        self.status_buttons = []

        for offset in range(7):
            status_date = self.week_start + timedelta(days=offset)
            day_layout = QVBoxLayout()

            date_label = QLabel(str(status_date.day))
            date_label.setAlignment(Qt.AlignCenter)

            status_button = DayStatusButton(
                status=statuses.get(status_date),
                blocked=status_date > today,
            )
            status_button.statusRequested.connect(
                lambda requested_status,
                day=status_date,
                button=status_button: self.update_daily_status(
                    day, requested_status, button
                )
            )
            self.status_buttons.append(status_button)

            day_label = QLabel(status_date.strftime("%a"))
            day_label.setAlignment(Qt.AlignCenter)

            day_layout.addWidget(date_label)
            day_layout.addWidget(status_button)
            day_layout.addWidget(day_label)
            blocks_layout.addLayout(day_layout)

        description_title = QLabel("Description")
        description_title.setAlignment(Qt.AlignCenter)
        description_title.setStyleSheet("font-weight: bold;")

        self.description_label = QLabel()
        self.description_label.setAlignment(Qt.AlignCenter)
        self.description_label.setWordWrap(True)

        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(90)
        self.description_input.setVisible(False)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.edit_button.clicked.connect(self.enter_edit_mode)
        self.delete_button.clicked.connect(self.delete_tracker)
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.cancel_editing)
        self.name_input.textChanged.connect(self.update_save_button)

        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addStretch()

        layout.addStretch()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.target_label)
        layout.addLayout(target_input_layout)
        layout.addLayout(blocks_layout)
        layout.addWidget(description_title)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.setLayout(layout)
        self.update_display()
        self.enter_read_mode()

    def update_display(self):
        self.name_label.setText(self.tracker["name"])
        self.target_label.setText(
            f"Weekly goal: {self.tracker['weekly_target']} days"
        )

        description = self.tracker["description"]
        self.description_label.setText(description or "No description yet.")

        if description:
            self.description_label.setStyleSheet("")
        else:
            self.description_label.setStyleSheet(
                "color: #7D7D7D; font-style: italic;"
            )

    def enter_read_mode(self):
        self.is_editing = False

        self.name_label.setVisible(True)
        self.name_input.setVisible(False)
        self.target_label.setVisible(True)
        self.target_input.setVisible(False)
        self.description_label.setVisible(True)
        self.description_input.setVisible(False)

        self.edit_button.setEnabled(not self.read_only)
        self.delete_button.setEnabled(not self.read_only)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)

        for button in self.status_buttons:
            button.setEnabled(not button.blocked and not self.read_only)

    def enter_edit_mode(self):
        if self.read_only:
            return

        self.is_editing = True

        self.name_input.setText(self.tracker["name"])
        self.target_input.setCurrentIndex(
            self.target_input.findData(self.tracker["weekly_target"])
        )
        self.description_input.setPlainText(self.tracker["description"])

        self.name_label.setVisible(False)
        self.name_input.setVisible(True)
        self.target_label.setVisible(False)
        self.target_input.setVisible(True)
        self.description_label.setVisible(False)
        self.description_input.setVisible(True)

        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.update_save_button(self.name_input.text())
        self.cancel_button.setEnabled(True)

        for button in self.status_buttons:
            button.setEnabled(False)

        self.name_input.setFocus()

    def save_changes(self):
        name = self.name_input.text().strip()

        if not name:
            return

        self.tracker = repo.update_tracker(
            self.tracker["id"],
            name,
            self.description_input.toPlainText(),
            self.target_input.currentData(),
        )

        self.update_display()
        self.trackerUpdated.emit(self.tracker)
        self.enter_read_mode()

    def cancel_editing(self):
        self.enter_read_mode()

    def delete_tracker(self):
        answer = QMessageBox.question(
            self,
            "Delete Tracker",
            f"Delete '{self.tracker['name']}' from the current week?\n\n"
            "Completed-week history will be preserved.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        repo.archive_tracker(self.tracker["id"])
        self.trackerArchived.emit()

    def update_save_button(self, name):
        self.save_button.setEnabled(self.is_editing and bool(name.strip()))

    def update_daily_status(self, status_date, requested_status, status_button):
        new_status = repo.toggle_daily_status(
            self.tracker["id"], status_date, requested_status
        )
        status_button.set_status(new_status)
        self.progressChanged.emit()


class OverallPage(QWidget):
    def __init__(self, week_start):
        super().__init__()

        self.week_start = week_start

        layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout()
        self.rows_container.setLayout(self.rows_layout)
        self.scroll_area.setWidget(self.rows_container)

        layout.addWidget(self.scroll_area)

        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        progress_rows = repo.list_week_progress(self.week_start)

        if not progress_rows:
            empty_label = QLabel(
                "No trackers yet. Use + to create your first tracker."
            )
            empty_label.setAlignment(Qt.AlignCenter)
            self.rows_layout.addWidget(empty_label)
            self.rows_layout.addStretch()
            return

        for tracker_progress in progress_rows:
            self.rows_layout.addWidget(
                self.create_progress_row(tracker_progress)
            )

        self.rows_layout.addStretch()

    def create_progress_row(self, tracker_progress):
        row = QWidget()
        layout = QVBoxLayout()

        label_layout = QHBoxLayout()
        name_label = QLabel(tracker_progress["name"])

        target = tracker_progress["weekly_target"]
        completed = min(tracker_progress["completed_days"], target)
        count_label = QLabel(f"{completed} / {target}")

        label_layout.addWidget(name_label)
        label_layout.addStretch()
        label_layout.addWidget(count_label)

        progress_bar = QProgressBar()
        progress_bar.setRange(0, target)
        progress_bar.setValue(completed)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(24)
        progress_bar.setStyleSheet(
            """
            QProgressBar {
                background-color: #7D7D7D;
                border: none;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #39FF14;
                border-radius: 6px;
            }
            """
        )

        layout.addLayout(label_layout)
        layout.addWidget(progress_bar)

        row.setLayout(layout)
        return row


class TrackerTab(QWidget):
    def __init__(self):
        super().__init__()

        self.last_known_date = date.today()
        self.selected_week_start = get_week_start(self.last_known_date)

        layout = QVBoxLayout()

        week_navigation_layout = QHBoxLayout()
        week_navigation_layout.addStretch()

        self.previous_week_button = QPushButton("‹")
        self.previous_week_button.setFixedWidth(40)
        self.previous_week_button.clicked.connect(
            lambda: self.change_week(-1)
        )

        self.week_navigation_label = QLabel()
        self.week_navigation_label.setAlignment(Qt.AlignCenter)
        self.week_navigation_label.setMinimumWidth(240)
        self.week_navigation_label.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        self.next_week_button = QPushButton("›")
        self.next_week_button.setFixedWidth(40)
        self.next_week_button.clicked.connect(lambda: self.change_week(1))

        week_navigation_layout.addWidget(self.previous_week_button)
        week_navigation_layout.addWidget(self.week_navigation_label)
        week_navigation_layout.addWidget(self.next_week_button)
        week_navigation_layout.addStretch()

        self.tracker_tabs = QTabWidget()
        self.overall_page = OverallPage(self.selected_week_start)
        self.tracker_tabs.addTab(self.overall_page, "Overall")

        for tracker in repo.list_trackers_for_week(self.selected_week_start):
            self.add_tracker_tab(tracker)

        self.add_tracker_tab_index = self.tracker_tabs.addTab(QWidget(), "+")
        self.tracker_tabs.setTabToolTip(
            self.add_tracker_tab_index, "Create a new tracker"
        )
        self.last_selected_tab_index = 0
        self.tracker_tabs.currentChanged.connect(self.handle_tab_changed)
        self.update_week_navigation()

        layout.addLayout(week_navigation_layout)
        layout.addWidget(self.tracker_tabs)
        self.setLayout(layout)

        self.date_refresh_timer = QTimer(self)
        self.date_refresh_timer.setInterval(60_000)
        self.date_refresh_timer.timeout.connect(self.check_for_date_change)
        self.date_refresh_timer.start()

    def add_tracker_tab(self, tracker, index=None):
        read_only = self.selected_week_start != get_week_start(date.today())
        page = TrackerPage(
            tracker,
            self.selected_week_start,
            read_only=read_only,
        )
        page.trackerUpdated.connect(
            lambda updated_tracker, tracker_page=page: self.update_tracker_tab(
                tracker_page, updated_tracker
            )
        )
        page.trackerArchived.connect(
            lambda tracker_page=page: self.remove_tracker_tab(tracker_page)
        )
        page.progressChanged.connect(self.overall_page.refresh)

        if index is None:
            index = self.tracker_tabs.addTab(page, tracker["name"])
        else:
            index = self.tracker_tabs.insertTab(index, page, tracker["name"])

        self.tracker_tabs.tabBar().setTabData(index, tracker["id"])
        return index

    def change_week(self, direction):
        if self.has_active_tracker_edit():
            QMessageBox.information(
                self,
                "Finish Editing",
                "Save or cancel the current tracker edit before changing weeks.",
            )
            return

        new_week_start = self.selected_week_start + timedelta(
            days=direction * 7
        )
        current_week_start = get_week_start(date.today())

        if not FOUNDING_WEEK_START <= new_week_start <= current_week_start:
            return

        self.selected_week_start = new_week_start
        self.rebuild_week_tabs()

    def has_active_tracker_edit(self):
        for index in range(1, self.add_tracker_tab_index):
            page = self.tracker_tabs.widget(index)

            if isinstance(page, TrackerPage) and page.is_editing:
                return True

        return False

    def check_for_date_change(self):
        current_date = date.today()

        if current_date == self.last_known_date:
            return

        if self.has_active_tracker_edit():
            return

        previous_current_week = get_week_start(self.last_known_date)
        was_viewing_current_week = (
            self.selected_week_start == previous_current_week
        )

        self.last_known_date = current_date

        if was_viewing_current_week:
            self.selected_week_start = get_week_start(current_date)
            self.rebuild_week_tabs()
            return

        self.update_week_navigation()

    def rebuild_week_tabs(self):
        self.tracker_tabs.setCurrentIndex(0)

        for index in range(self.add_tracker_tab_index - 1, 0, -1):
            page = self.tracker_tabs.widget(index)
            self.tracker_tabs.removeTab(index)
            page.deleteLater()

        self.add_tracker_tab_index = 1
        self.overall_page.week_start = self.selected_week_start
        self.overall_page.refresh()

        for tracker in repo.list_trackers_for_week(self.selected_week_start):
            self.add_tracker_tab(tracker, self.add_tracker_tab_index)
            self.add_tracker_tab_index += 1

        is_current_week = self.selected_week_start == get_week_start(date.today())
        self.tracker_tabs.setTabEnabled(
            self.add_tracker_tab_index, is_current_week
        )

        self.last_selected_tab_index = 0
        self.update_week_navigation()

    def update_week_navigation(self):
        week_end = self.selected_week_start + timedelta(days=6)
        week_number = get_week_number(self.selected_week_start)
        current_week_start = get_week_start(date.today())

        self.week_navigation_label.setText(
            f"Week {week_number} · "
            f"{self.selected_week_start.strftime('%b %d')}–"
            f"{week_end.strftime('%b %d')}"
        )
        self.previous_week_button.setEnabled(
            self.selected_week_start > FOUNDING_WEEK_START
        )
        self.next_week_button.setEnabled(
            self.selected_week_start < current_week_start
        )

    def update_tracker_tab(self, page, tracker):
        index = self.tracker_tabs.indexOf(page)

        if index != -1:
            self.tracker_tabs.setTabText(index, tracker["name"])
            self.overall_page.refresh()

    def remove_tracker_tab(self, page):
        index = self.tracker_tabs.indexOf(page)

        if index == -1:
            return

        self.tracker_tabs.setCurrentIndex(0)
        self.tracker_tabs.removeTab(index)
        page.deleteLater()

        self.add_tracker_tab_index -= 1
        self.overall_page.refresh()

    def handle_tab_changed(self, index):
        if index == self.add_tracker_tab_index:
            previous_index = self.last_selected_tab_index
            dialog = CreateTrackerDialog(self)

            if dialog.exec() != QDialog.Accepted:
                self.tracker_tabs.setCurrentIndex(previous_index)
                return

            tracker = repo.create_tracker(
                dialog.tracker_name(), dialog.weekly_target()
            )

            self.tracker_tabs.setCurrentIndex(previous_index)
            new_tab_index = self.add_tracker_tab(
                tracker, self.add_tracker_tab_index
            )
            self.add_tracker_tab_index += 1
            self.overall_page.refresh()
            self.tracker_tabs.setCurrentIndex(new_tab_index)
            return

        self.last_selected_tab_index = index

        if index == 0:
            self.overall_page.refresh()


def create_tracker_tab():
    return TrackerTab()
