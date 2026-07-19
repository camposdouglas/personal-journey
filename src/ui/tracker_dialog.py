from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
)


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
