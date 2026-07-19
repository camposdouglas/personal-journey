from datetime import date, timedelta

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import tracker_repository as repo
from week_utils import get_week_number, get_week_start


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


class TrackerTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tracker_tabs = QTabWidget()
        self.tracker_tabs.addTab(self.create_overall_tab(), "Overall")

        for tracker in repo.list_active_trackers():
            self.add_tracker_tab(tracker)

        self.add_tracker_tab_index = self.tracker_tabs.addTab(QWidget(), "+")
        self.tracker_tabs.setTabToolTip(
            self.add_tracker_tab_index, "Create a new tracker"
        )
        self.last_selected_tab_index = 0
        self.tracker_tabs.currentChanged.connect(self.handle_tab_changed)

        self.update_overall_empty_state()

        layout.addWidget(self.tracker_tabs)
        self.setLayout(layout)

    def create_overall_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.overall_empty_label = QLabel(
            "No trackers yet. Use + to create your first tracker."
        )

        layout.addWidget(self.overall_empty_label)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_tracker_page(self, tracker):
        page = QWidget()
        layout = QVBoxLayout()

        today = date.today()
        week_start = get_week_start(today)
        week_end = week_start + timedelta(days=6)
        week_number = get_week_number(today)

        target = tracker["weekly_target"]
        name_label = QLabel(tracker["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        target_label = QLabel(f"Weekly goal: {target} days")
        target_label.setAlignment(Qt.AlignCenter)

        week_label = QLabel(
            f"Week {week_number} · {week_start.strftime('%b %d')}–"
            f"{week_end.strftime('%b %d')}"
        )
        week_label.setAlignment(Qt.AlignCenter)

        blocks_layout = QHBoxLayout()
        statuses = repo.list_week_statuses(tracker["id"], week_start)

        for offset in range(7):
            status_date = week_start + timedelta(days=offset)
            day_layout = QVBoxLayout()

            date_label = QLabel(str(status_date.day))
            date_label.setAlignment(Qt.AlignCenter)

            status_button = DayStatusButton(
                status=statuses.get(status_date),
                blocked=status_date > today,
            )
            status_button.statusRequested.connect(
                lambda requested_status,
                tracker_id=tracker["id"],
                day=status_date,
                button=status_button: self.update_daily_status(
                    tracker_id, day, requested_status, button
                )
            )

            day_label = QLabel(status_date.strftime("%a"))
            day_label.setAlignment(Qt.AlignCenter)

            day_layout.addWidget(date_label)
            day_layout.addWidget(status_button)
            day_layout.addWidget(day_label)
            blocks_layout.addLayout(day_layout)

        description_title = QLabel("Description")
        description_title.setAlignment(Qt.AlignCenter)
        description_title.setStyleSheet("font-weight: bold;")

        description = tracker["description"]
        description_label = QLabel(description or "No description yet.")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)

        if not description:
            description_label.setStyleSheet("color: #7D7D7D; font-style: italic;")

        layout.addStretch()
        layout.addWidget(name_label)
        layout.addWidget(target_label)
        layout.addWidget(week_label)
        layout.addLayout(blocks_layout)
        layout.addWidget(description_title)
        layout.addWidget(description_label)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def update_daily_status(
        self, tracker_id, status_date, requested_status, status_button
    ):
        new_status = repo.toggle_daily_status(
            tracker_id, status_date, requested_status
        )
        status_button.set_status(new_status)

    def add_tracker_tab(self, tracker, index=None):
        page = self.create_tracker_page(tracker)

        if index is None:
            index = self.tracker_tabs.addTab(page, tracker["name"])
        else:
            index = self.tracker_tabs.insertTab(index, page, tracker["name"])

        self.tracker_tabs.tabBar().setTabData(index, tracker["id"])
        return index

    def update_overall_empty_state(self):
        has_trackers = self.tracker_tabs.count() > 2
        self.overall_empty_label.setVisible(not has_trackers)

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
            self.update_overall_empty_state()
            self.tracker_tabs.setCurrentIndex(new_tab_index)
            return

        self.last_selected_tab_index = index


def create_tracker_tab():
    return TrackerTab()
