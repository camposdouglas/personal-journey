from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget


class TrackerTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tracker_tabs = QTabWidget()
        self.tracker_tabs.addTab(self.create_overall_tab(), "Overall")

        self.add_tracker_tab_index = self.tracker_tabs.addTab(QWidget(), "+")
        self.tracker_tabs.setTabToolTip(
            self.add_tracker_tab_index, "Create a new tracker"
        )
        self.tracker_tabs.currentChanged.connect(self.handle_tab_changed)

        layout.addWidget(self.tracker_tabs)
        self.setLayout(layout)

    def create_overall_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        empty_label = QLabel("No trackers yet. Use + to create your first tracker.")

        layout.addWidget(empty_label)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def handle_tab_changed(self, index):
        if index == self.add_tracker_tab_index:
            self.tracker_tabs.setCurrentIndex(0)


def create_tracker_tab():
    return TrackerTab()
