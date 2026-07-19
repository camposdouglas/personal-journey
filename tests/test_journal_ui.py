import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

import db
import journal_repository as repo
from ui.journal_tab import JournalTab
from ui.main_window import MainWindow


class CloseEventStub:
    def __init__(self):
        self.result = None

    def accept(self):
        self.result = "accepted"

    def ignore(self):
        self.result = "ignored"


class JournalUiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.original_db_path = db.DB_PATH
        self.temporary_directory = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temporary_directory.name) / "test.db"
        db.init_db()
        self.widgets = []

    def tearDown(self):
        for widget in self.widgets:
            widget.deleteLater()

        self.app.processEvents()
        db.DB_PATH = self.original_db_path
        self.temporary_directory.cleanup()

    def make_journal_tab(self):
        journal = JournalTab()
        self.widgets.append(journal)
        return journal

    def open_first_entry(self, journal):
        item = journal.entries_list.item(0)
        journal.entries_list.setCurrentItem(item)
        journal.open_entry(item)

    def test_literal_markup_is_preserved_as_plain_text(self):
        entry = repo.create_entry("Markup", "<b>literal markup</b>")
        journal = self.make_journal_tab()
        self.open_first_entry(journal)

        self.assertEqual(
            journal.content_editor.toPlainText(),
            "<b>literal markup</b>",
        )

        journal.enable_editing()
        journal.save_entry()

        self.assertEqual(
            repo.get_entry(entry["id"])["content"],
            "<b>literal markup</b>",
        )

    def test_create_save_and_cancel_new_entry(self):
        journal = self.make_journal_tab()
        journal.create_new_entry()
        journal.title_input.setText("First entry")
        journal.content_editor.setPlainText("Saved content")
        journal.save_entry()

        entries = repo.list_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "First entry")
        self.assertEqual(entries[0]["content"], "Saved content")

        journal.create_new_entry()
        journal.title_input.setText("Discarded entry")
        journal.cancel_editing()

        self.assertEqual(len(repo.list_entries()), 1)
        self.assertEqual(journal.entries_list.count(), 1)
        self.assertFalse(journal.is_editing)

    def test_existing_edit_can_be_cancelled_or_saved(self):
        entry = repo.create_entry("Original", "Original content")
        journal = self.make_journal_tab()
        self.open_first_entry(journal)

        journal.enable_editing()
        journal.title_input.setText("Discarded")
        journal.content_editor.setPlainText("Discarded content")
        journal.cancel_editing()

        self.assertEqual(journal.title_input.text(), "Original")
        self.assertEqual(journal.content_editor.toPlainText(), "Original content")
        self.assertEqual(repo.get_entry(entry["id"])["title"], "Original")

        journal.enable_editing()
        journal.title_input.setText("Updated")
        journal.content_editor.setPlainText("Updated content")
        journal.save_entry()

        updated = repo.get_entry(entry["id"])
        self.assertEqual(updated["title"], "Updated")
        self.assertEqual(updated["content"], "Updated content")

    def test_empty_click_stays_clear_after_switching_main_tabs(self):
        repo.create_entry("First", "Content")
        window = MainWindow()
        self.widgets.append(window)
        window.resize(1000, 650)
        window.show()
        self.app.processEvents()

        tabs = window.layout().itemAt(0).widget()
        tabs.setCurrentIndex(2)
        self.app.processEvents()
        journal = window.journal_tab
        empty_point = QPoint(20, journal.entries_list.viewport().height() - 10)
        QTest.mouseClick(
            journal.entries_list.viewport(),
            Qt.LeftButton,
            Qt.NoModifier,
            empty_point,
        )
        tabs.setCurrentIndex(1)
        self.app.processEvents()
        tabs.setCurrentIndex(2)
        self.app.processEvents()

        self.assertEqual(journal.entries_list.currentRow(), -1)
        self.assertEqual(journal.entries_list.selectedItems(), [])
        self.assertIsNone(journal.current_entry_id)

    def test_close_warning_includes_active_journal_edit(self):
        repo.create_entry("First", "Content")
        window = MainWindow()
        self.widgets.append(window)
        journal = window.journal_tab
        self.open_first_entry(journal)
        journal.enable_editing()
        event = CloseEventStub()

        with patch.object(
            QMessageBox,
            "warning",
            return_value=QMessageBox.Cancel,
        ) as warning:
            window.closeEvent(event)

        self.assertEqual(event.result, "ignored")
        warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
