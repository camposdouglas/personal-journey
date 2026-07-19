from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import tracker_repository as repo


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
