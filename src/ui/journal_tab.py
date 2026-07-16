from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from PySide6.QtCore import Qt


class ClearableListWidget(QListWidget):
    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.position().toPoint())

        if clicked_item is None:
            self.clearSelection()
            self.setCurrentRow(-1)

        super().mousePressEvent(event)


class JournalTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()

        (
            self.entry_viewer_panel,
            self.title_input,
            self.content_editor,
            self.edit_button,
            self.save_button,
            self.cancel_button,
            self.delete_button,
        ) = create_entry_viewer_panel()

        self.mock_entries = {
            "2026-07-16 13:20": "Mock journal entry for July 16.",
            "2026-07-15 22:40": "Mock journal entry for July 15.",
            "2026-07-14 05:19": "Mock journal entry for July 14.",
        }

        self.entries_panel, self.entries_list = create_entries_panel(self.mock_entries)

        self.entries_list.itemDoubleClicked.connect(self.open_entry)

        main_layout.addWidget(self.entries_panel, 2)
        main_layout.addWidget(self.entry_viewer_panel, 3)

        self.setLayout(main_layout)

    def open_entry(self, item):
        title = item.text()
        content = self.mock_entries.get(title, "")

        self.title_input.setText(title)
        self.content_editor.setText(content)

        self.title_input.setReadOnly(True)
        self.content_editor.setReadOnly(True)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(True)


def create_journal_tab():
    return JournalTab()


def create_entries_panel(mock_entries):
    panel = QWidget()
    layout = QVBoxLayout()

    title_label = QLabel("Entries")
    new_entry_button = QPushButton("New Entry")

    entries_list = ClearableListWidget()
    entries_list.setStyleSheet("""
    QListWidget::item:hover {
        background-color: #444444;
        color: white;
    }
""")

    entries_list.addItems(list(mock_entries.keys()))

    layout.addWidget(title_label)
    layout.addWidget(new_entry_button)
    layout.addWidget(entries_list)

    panel.setLayout(layout)
    return panel, entries_list


def create_entry_viewer_panel():
    panel = QWidget()
    layout = QVBoxLayout()

    title_label = QLabel("Title")
    title_input = QLineEdit()
    title_input.setPlaceholderText("Select an entry")
    title_input.setReadOnly(True)

    content_label = QLabel("Content")
    content_editor = QTextEdit()
    content_editor.setPlaceholderText("Select an entry to read or edit its content.")
    content_editor.setReadOnly(True)

    buttons_layout = QHBoxLayout()
    edit_button = QPushButton("Edit")
    save_button = QPushButton("Save")
    cancel_button = QPushButton("Cancel")
    delete_button = QPushButton("Delete")

    edit_button.setEnabled(False)
    save_button.setEnabled(False)
    cancel_button.setEnabled(False)
    delete_button.setEnabled(False)

    def enable_editing():
        title_input.setProperty("original_text", title_input.text())
        content_editor.setProperty("original_text", content_editor.toPlainText())

        title_input.setReadOnly(False)
        content_editor.setReadOnly(False)

        edit_button.setEnabled(False)
        save_button.setEnabled(True)
        cancel_button.setEnabled(True)
        delete_button.setEnabled(False)

    def cancel_editing():
        original_title = title_input.property("original_text")
        original_content = content_editor.property("original_text")

        title_input.setText(original_title)
        content_editor.setText(original_content)

        title_input.setReadOnly(True)
        content_editor.setReadOnly(True)

        edit_button.setEnabled(True)
        save_button.setEnabled(False)
        cancel_button.setEnabled(False)
        delete_button.setEnabled(True)

    edit_button.clicked.connect(enable_editing)
    cancel_button.clicked.connect(cancel_editing)

    edit_button.clicked.connect(enable_editing)

    buttons_layout.addWidget(edit_button)
    buttons_layout.addWidget(save_button)
    buttons_layout.addWidget(cancel_button)
    buttons_layout.addWidget(delete_button)

    layout.addWidget(title_label)
    layout.addWidget(title_input)
    layout.addWidget(content_label)
    layout.addWidget(content_editor)
    layout.addLayout(buttons_layout)

    panel.setLayout(layout)
    return (
        panel,
        title_input,
        content_editor,
        edit_button,
        save_button,
        cancel_button,
        delete_button,
    )
