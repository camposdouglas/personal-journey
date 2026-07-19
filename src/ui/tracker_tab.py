from datetime import date, timedelta

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import tracker_repository as repo
from ui.tracker_dialog import CreateTrackerDialog
from ui.tracker_overall_page import OverallPage
from ui.tracker_page import TrackerPage
from week_utils import FOUNDING_WEEK_START, get_week_number, get_week_start


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
