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


def create_journal_tab():
    tab = QWidget()
    main_layout = QHBoxLayout()

    (
        entry_viewer_panel,
        title_input,
        content_editor,
        edit_button,
        save_button,
        delete_button,
    ) = create_entry_viewer_panel()

    entries_panel = create_entries_panel(
        title_input,
        content_editor,
        edit_button,
        delete_button,
    )

    main_layout.addWidget(entries_panel, 2)
    main_layout.addWidget(entry_viewer_panel, 3)

    tab.setLayout(main_layout)
    return tab


def create_entries_panel(title_input, content_editor, edit_button, delete_button):
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
    mock_entries = {
        "2026-07-16 13:20": "Mock journal entry for July 16.",
        "2026-07-15 22:40": "Mock journal entry for July 15.",
        "2026-07-14 05:19": "Mock journal entry for July 14.",
    }

    entries_list.addItems(list(mock_entries.keys()))

    def open_entry(item):
        title = item.text()
        content = mock_entries.get(title, "")

        title_input.setText(title)
        content_editor.setText(content)

        title_input.setReadOnly(True)
        content_editor.setReadOnly(True)

        edit_button.setEnabled(True)
        delete_button.setEnabled(True)

    entries_list.itemDoubleClicked.connect(open_entry)

    layout.addWidget(title_label)
    layout.addWidget(new_entry_button)
    layout.addWidget(entries_list)

    panel.setLayout(layout)
    return panel


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
    delete_button = QPushButton("Delete")

    edit_button.setEnabled(False)
    save_button.setEnabled(False)
    delete_button.setEnabled(False)

    buttons_layout.addWidget(edit_button)
    buttons_layout.addWidget(save_button)
    buttons_layout.addWidget(delete_button)

    layout.addWidget(title_label)
    layout.addWidget(title_input)
    layout.addWidget(content_label)
    layout.addWidget(content_editor)
    layout.addLayout(buttons_layout)

    panel.setLayout(layout)
    return panel, title_input, content_editor, edit_button, save_button, delete_button
