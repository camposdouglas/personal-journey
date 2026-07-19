from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import journal_repository as repo


class ClearableListWidget(QListWidget):
    emptyAreaClicked = Signal()

    def __init__(self):
        super().__init__()
        self.interaction_locked = False

    def mousePressEvent(self, event):
        if self.interaction_locked:
            return

        clicked_item = self.itemAt(event.position().toPoint())

        if clicked_item is None:
            self.clearSelection()
            self.setCurrentRow(-1)
            self.emptyAreaClicked.emit()

        super().mousePressEvent(event)


class JournalTab(QWidget):
    def __init__(self):
        super().__init__()

        self.current_entry_id = None
        self.is_editing = False
        self.is_new_entry = False
        self.pending_new_entry_item = None

        main_layout = QHBoxLayout()

        (
            self.entry_viewer_panel,
            self.title_input,
            self.title_error_label,
            self.metadata_label,
            self.content_editor,
            self.edit_button,
            self.save_button,
            self.cancel_button,
            self.delete_button,
        ) = create_entry_viewer_panel()

        self.entries_panel, self.entries_list, self.new_entry_button = (
            create_entries_panel(repo.list_entries())
        )

        self.entries_list.itemClicked.connect(self.open_entry)
        self.entries_list.emptyAreaClicked.connect(self.clear_entry_viewer)

        self.new_entry_button.clicked.connect(self.create_new_entry)

        self.edit_button.clicked.connect(self.enable_editing)
        self.save_button.clicked.connect(self.save_entry)
        self.cancel_button.clicked.connect(self.cancel_editing)
        self.delete_button.clicked.connect(self.delete_entry)

        main_layout.addWidget(self.entries_panel, 2)
        main_layout.addWidget(self.entry_viewer_panel, 3)

        self.setLayout(main_layout)

    def open_entry(self, item):
        if self.is_editing:
            return

        entry_id = item.data(Qt.UserRole)
        entry_data = repo.get_entry(entry_id)

        if entry_data is None:
            self.current_entry_id = None
            return

        self.current_entry_id = entry_id

        self.title_input.setText(entry_data["title"])
        self.content_editor.setText(entry_data["content"])
        self.update_metadata(entry_data)

        self.enter_read_mode()

    def find_entry_item_by_id(self, entry_id):
        for row in range(self.entries_list.count()):
            item = self.entries_list.item(row)

            if item.data(Qt.UserRole) == entry_id:
                return item

        return None

    def enable_editing(self):
        self.clear_title_error()

        self.title_input.setProperty("original_text", self.title_input.text())
        self.content_editor.setProperty(
            "original_text", self.content_editor.toPlainText()
        )

        self.enter_edit_mode()
        self.content_editor.setFocus()
        self.content_editor.moveCursor(QTextCursor.End)

    def save_entry(self):
        if not self.is_editing:
            return

        new_title = self.title_input.text().strip()
        new_content = self.content_editor.toPlainText()

        if not new_title:
            self.mark_title_invalid()
            return

        self.clear_title_error()

        if self.is_new_entry:
            entry = repo.create_entry(new_title, new_content)
            self.current_entry_id = entry["id"]

            if self.pending_new_entry_item is not None:
                self.pending_new_entry_item.setText(new_title)
                self.pending_new_entry_item.setData(Qt.UserRole, entry["id"])

            self.pending_new_entry_item = None
            self.is_new_entry = False

        else:
            if self.current_entry_id is None:
                return

            entry = repo.update_entry(
                self.current_entry_id, new_title, new_content
            )

            item = self.find_entry_item_by_id(self.current_entry_id)

            if item is not None:
                item.setText(new_title)

        self.title_input.setText(new_title)
        self.update_metadata(entry)

        self.enter_read_mode()

    def cancel_editing(self):
        if self.is_new_entry:
            if self.pending_new_entry_item is not None:
                row = self.entries_list.row(self.pending_new_entry_item)

                if row != -1:
                    self.entries_list.takeItem(row)

            self.pending_new_entry_item = None
            self.is_new_entry = False
            self.is_editing = False

            self.clear_title_error()
            self.clear_entry_viewer()
            return

        self.is_editing = False
        self.clear_title_error()

        original_title = self.title_input.property("original_text")
        original_content = self.content_editor.property("original_text")

        self.title_input.setText(original_title)
        self.content_editor.setText(original_content)

        self.enter_read_mode()

    def delete_entry(self):
        if self.current_entry_id is None:
            return

        if self.is_editing:
            return

        entry_id = self.current_entry_id
        entry_data = repo.get_entry(entry_id)

        if entry_data is None:
            return

        title_to_delete = entry_data["title"]

        confirmation_box = QMessageBox(self)
        confirmation_box.setWindowTitle("Delete Entry")
        confirmation_box.setText(
            f"Are you sure you want to delete '{title_to_delete}'?"
        )

        yes_button = confirmation_box.addButton("Yes", QMessageBox.AcceptRole)
        no_button = confirmation_box.addButton("No", QMessageBox.RejectRole)

        confirmation_box.setDefaultButton(no_button)
        confirmation_box.exec()

        if confirmation_box.clickedButton() != yes_button:
            return

        repo.delete_entry(entry_id)

        item = self.find_entry_item_by_id(entry_id)

        if item is not None:
            row = self.entries_list.row(item)
            self.entries_list.takeItem(row)

        self.clear_entry_viewer()

    def clear_entry_viewer(self):
        if self.is_editing:
            return

        self.current_entry_id = None

        self.title_input.clear()
        self.metadata_label.clear()
        self.content_editor.clear()

        self.enter_empty_mode()

    def enter_read_mode(self):
        self.is_editing = False
        self.entries_list.interaction_locked = False

        self.title_input.setReadOnly(True)
        self.title_input.setFocusPolicy(Qt.NoFocus)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(True)

    def enter_edit_mode(self):
        self.is_editing = True
        self.entries_list.interaction_locked = True

        self.title_input.setReadOnly(False)
        self.title_input.setFocusPolicy(Qt.StrongFocus)
        self.content_editor.setReadOnly(False)

        self.title_input.setCursor(Qt.IBeamCursor)
        self.content_editor.viewport().setCursor(Qt.IBeamCursor)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.delete_button.setEnabled(False)

    def enter_empty_mode(self):
        self.is_editing = False
        self.entries_list.interaction_locked = False

        self.title_input.setReadOnly(True)
        self.title_input.setFocusPolicy(Qt.NoFocus)
        self.content_editor.setReadOnly(True)

        self.title_input.setCursor(Qt.ArrowCursor)
        self.content_editor.viewport().setCursor(Qt.ArrowCursor)

        self.edit_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def create_new_entry(self):
        if self.is_editing:
            return

        self.clear_title_error()

        temporary_title = datetime.now().strftime("%d/%m/%Y · %H:%M:%S")

        new_item = QListWidgetItem(temporary_title)
        new_item.setData(Qt.UserRole, None)

        self.pending_new_entry_item = new_item

        self.entries_list.insertItem(0, new_item)
        self.entries_list.setCurrentItem(new_item)
        self.entries_list.scrollToItem(new_item)

        self.current_entry_id = None
        self.is_new_entry = True

        self.title_input.setText(temporary_title)
        self.metadata_label.clear()
        self.content_editor.clear()

        self.enter_edit_mode()
        self.content_editor.setFocus()

    def mark_title_invalid(self):
        self.title_error_label.setVisible(True)
        self.title_input.setToolTip("Title cannot be empty.")

    def clear_title_error(self):
        self.title_error_label.setVisible(False)
        self.title_input.setToolTip("")

    def update_metadata(self, entry):
        created_at = format_timestamp(entry["created_at"])
        updated_at = format_timestamp(entry["updated_at"])
        self.metadata_label.setText(
            f"Created: {created_at} · Updated: {updated_at}"
        )


def create_journal_tab():
    return JournalTab()


def format_timestamp(timestamp):
    parsed_timestamp = datetime.fromisoformat(timestamp)
    return parsed_timestamp.strftime("%b %d, %Y at %H:%M:%S")


def create_entries_panel(entries):
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

    for entry in entries:
        item = QListWidgetItem(entry["title"])
        item.setData(Qt.UserRole, entry["id"])
        entries_list.addItem(item)

    layout.addWidget(title_label)
    layout.addWidget(new_entry_button)
    layout.addWidget(entries_list)

    panel.setLayout(layout)
    return panel, entries_list, new_entry_button


def create_entry_viewer_panel():
    panel = QWidget()
    layout = QVBoxLayout()

    title_header_layout = QHBoxLayout()

    title_label = QLabel("Title")

    title_error_label = QLabel("Title cannot be empty.")
    title_error_label.setStyleSheet("color: #cc3333;")
    title_error_label.setVisible(False)

    title_header_layout.addWidget(title_label)
    title_header_layout.addStretch()
    title_header_layout.addWidget(title_error_label)

    title_input = QLineEdit()
    title_input.setPlaceholderText("Select an entry")
    title_input.setReadOnly(True)
    title_input.setFocusPolicy(Qt.NoFocus)

    metadata_label = QLabel()
    metadata_label.setStyleSheet("color: #7D7D7D;")

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

    layout.addLayout(title_header_layout)
    layout.addWidget(title_input)
    layout.addWidget(metadata_label)
    layout.addWidget(content_label)
    layout.addWidget(content_editor)
    layout.addLayout(buttons_layout)

    panel.setLayout(layout)
    return (
        panel,
        title_input,
        title_error_label,
        metadata_label,
        content_editor,
        edit_button,
        save_button,
        cancel_button,
        delete_button,
    )
