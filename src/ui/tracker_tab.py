from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

import tracker_repository as repo


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

        target = tracker["weekly_target"]
        target_label = QLabel(f"Weekly target: {target} of 7 days")
        placeholder_label = QLabel("Daily tracking blocks will appear here.")

        layout.addWidget(target_label)
        layout.addWidget(placeholder_label)
        layout.addStretch()

        page.setLayout(layout)
        return page

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
