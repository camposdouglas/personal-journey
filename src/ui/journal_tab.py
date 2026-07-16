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


def create_journal_tab():
    tab = QWidget()
    main_layout = QHBoxLayout()

    entries_panel = create_entries_panel()
    entry_viewer_panel = create_entry_viewer_panel()

    main_layout.addWidget(entries_panel, 2)
    main_layout.addWidget(entry_viewer_panel, 3)

    tab.setLayout(main_layout)
    return tab


def create_entries_panel():
    panel = QWidget()
    layout = QVBoxLayout()

    title_label = QLabel("Entries")
    new_entry_button = QPushButton("New Entry")

    entries_list = QListWidget()
    entries_list.addItems(
        [
            "2026-07-16 13:20",
            "2026-07-15 22:40",
            "2026-07-14 05:19",
        ]
    )

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
    title_input.setText("2026-07-16 13:20")
    title_input.setReadOnly(True)

    content_label = QLabel("Content")
    content_editor = QTextEdit()
    content_editor.setText("Select an entry to read or edit its content.")
    content_editor.setReadOnly(True)

    buttons_layout = QHBoxLayout()
    edit_button = QPushButton("Edit")
    save_button = QPushButton("Save")
    delete_button = QPushButton("Delete")

    save_button.setEnabled(False)

    buttons_layout.addWidget(edit_button)
    buttons_layout.addWidget(save_button)
    buttons_layout.addWidget(delete_button)

    layout.addWidget(title_label)
    layout.addWidget(title_input)
    layout.addWidget(content_label)
    layout.addWidget(content_editor)
    layout.addLayout(buttons_layout)

    panel.setLayout(layout)
    return panel
