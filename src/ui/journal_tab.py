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

from PySide6.QtCore import Qt, Signal


class ClearableListWidget(QListWidget):
    emptyAreaDoubleClicked = Signal()

    def mousePressEvent(self, event):
        clicked_item = self.itemAt(event.position().toPoint())

        if clicked_item is None:
            self.clearSelection()
            self.setCurrentRow(-1)

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        clicked_item = self.itemAt(event.position().toPoint())

        if clicked_item is None:
            self.clearSelection()
            self.setCurrentRow(-1)
            self.emptyAreaDoubleClicked.emit()
            return

        super().mouseDoubleClickEvent(event)


class JournalTab(QWidget):
    def __init__(self):
        super().__init__()

        self.current_entry_title = None
        self.is_editing = False

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
        self.entries_list.emptyAreaDoubleClicked.connect(self.clear_entry_viewer)

        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.save_entry)
        self.cancel_button.clicked.connect(self.cancel_editing)

        main_layout.addWidget(self.entries_panel, 2)
        main_layout.addWidget(self.entry_viewer_panel, 3)

        self.setLayout(main_layout)

    def open_entry(self, item):
        if self.is_editing:
            return

        title = item.text()
        self.current_entry_title = title

        content = self.mock_entries.get(title, "")

        self.title_input.setText(title)
        self.content_editor.setText(content)

        self.title_input.setReadOnly(True)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def enable_editing(self):
        self.is_editing = True

        self.title_input.setProperty("original_text", self.title_input.text())
        self.content_editor.setProperty(
            "original_text", self.content_editor.toPlainText()
        )

        self.title_input.setReadOnly(False)
        self.content_editor.setReadOnly(False)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.delete_button.setEnabled(False)

        self.title_input.setCursor(Qt.IBeamCursor)
        self.content_editor.viewport().setCursor(Qt.IBeamCursor)

    def save_entry(self):
        if self.current_entry_title is None:
            return

        old_title = self.current_entry_title
        new_title = self.title_input.text().strip()
        new_content = self.content_editor.toPlainText()

        if not new_title:
            return

        self.mock_entries.pop(old_title)
        self.mock_entries[new_title] = new_content
        self.current_entry_title = new_title

        matching_items = self.entries_list.findItems(old_title, Qt.MatchExactly)

        if matching_items:
            matching_items[0].setText(new_title)

        self.title_input.setText(new_title)

        self.is_editing = False

        self.title_input.setReadOnly(True)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def cancel_editing(self):
        self.is_editing = False

        original_title = self.title_input.property("original_text")
        original_content = self.content_editor.property("original_text")

        self.title_input.setText(original_title)
        self.content_editor.setText(original_content)

        self.title_input.setReadOnly(True)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def clear_entry_viewer(self):
        if self.is_editing:
            return

        self.current_entry_title = None

        self.title_input.clear()
        self.content_editor.clear()

        self.title_input.setReadOnly(True)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(False)


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
    title_input.setCursor(Qt.ArrowCursor)
    content_editor.viewport().setCursor(Qt.ArrowCursor)

    buttons_layout = QHBoxLayout()
    edit_button = QPushButton("Edit")
    save_button = QPushButton("Save")
    cancel_button = QPushButton("Cancel")
    delete_button = QPushButton("Delete")

    edit_button.setEnabled(False)
    save_button.setEnabled(False)
    cancel_button.setEnabled(False)
    delete_button.setEnabled(False)

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
