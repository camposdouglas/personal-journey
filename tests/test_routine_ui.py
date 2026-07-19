import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

SRC_PATH = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from PySide6.QtCore import QPoint, Qt, QTime
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

import db
import routine_repository as repo
from ui.main_window import MainWindow
from ui.routine_tab import RoutineSchedulePage, RoutineTab


class CloseEventStub:
    def __init__(self):
        self.result = None

    def accept(self):
        self.result = "accepted"

    def ignore(self):
        self.result = "ignored"


class RoutineUiTestCase(unittest.TestCase):
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

    def make_schedule_page(self, schedule_type="weekdays"):
        page = RoutineSchedulePage(schedule_type)
        self.widgets.append(page)
        return page

    def test_add_refreshes_list_clock_and_database(self):
        page = self.make_schedule_page()
        page.name_input.setText("Study")
        page.start_time_input.setTime(QTime(14, 30))
        page.end_time_input.setTime(QTime(16, 15))
        page.color_input.setText("#123abc")

        self.assertTrue(page.add_edit_button.isEnabled())
        page.add_edit_button.click()

        blocks = repo.list_blocks("weekdays")
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["name"], "Study")
        self.assertEqual(blocks[0]["color"], "#123ABC")
        self.assertEqual(page.tasks_list.count(), 1)
        self.assertEqual(page.clock.blocks, blocks)

    def test_selection_is_read_only_until_edit_is_clicked(self):
        block = repo.create_block(
            "weekdays", "Study", 510, 615, "#112233"
        )
        page = self.make_schedule_page()

        page.tasks_list.setCurrentRow(0)

        self.assertEqual(page.name_input.text(), "Study")
        self.assertEqual(page.start_time_input.time(), QTime(8, 30))
        self.assertEqual(page.end_time_input.time(), QTime(10, 15))
        self.assertEqual(page.color_input.text(), "#112233")
        self.assertTrue(page.name_input.isReadOnly())
        self.assertIsNone(page.editing_block_id)

        page.add_edit_button.click()
        self.assertEqual(page.editing_block_id, block["id"])
        self.assertFalse(page.name_input.isReadOnly())

        page.name_input.setText("Focused Study")
        page.save_button.click()

        self.assertEqual(repo.get_block(block["id"])["name"], "Focused Study")
        self.assertIsNone(page.editing_block_id)

        page.tasks_list.setCurrentRow(0)
        page.add_edit_button.click()
        page.name_input.setText("Discarded Name")
        page.cancel_button.click()

        self.assertEqual(repo.get_block(block["id"])["name"], "Focused Study")
        self.assertIsNone(page.editing_block_id)

    def test_empty_click_stays_clear_after_switching_schedule_tabs(self):
        repo.create_block("weekdays", "NPC", 480, 900, "#7D7D7D")
        routine_tab = RoutineTab()
        self.widgets.append(routine_tab)
        routine_tab.resize(1000, 650)
        routine_tab.show()
        self.app.processEvents()

        page = routine_tab.weekdays_page
        empty_point = QPoint(20, page.tasks_list.viewport().height() - 10)
        QTest.mouseClick(
            page.tasks_list.viewport(),
            Qt.LeftButton,
            Qt.NoModifier,
            empty_point,
        )
        routine_tab.schedule_tabs.setCurrentIndex(1)
        self.app.processEvents()
        routine_tab.schedule_tabs.setCurrentIndex(0)
        self.app.processEvents()

        self.assertEqual(page.tasks_list.currentRow(), -1)
        self.assertEqual(page.tasks_list.selectedItems(), [])
        self.assertEqual(page.name_input.text(), "")
        self.assertIsNone(page.current_block_id())

    def test_delete_requires_confirmation_and_refreshes_clock(self):
        block = repo.create_block(
            "weekdays", "Study", 840, 960, "#112233"
        )
        page = self.make_schedule_page()
        page.tasks_list.setCurrentRow(0)

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Cancel):
            page.delete_button.click()

        self.assertIsNotNone(repo.get_block(block["id"]))

        with patch.object(QMessageBox, "question", return_value=QMessageBox.Yes):
            page.delete_button.click()

        self.assertIsNone(repo.get_block(block["id"]))
        self.assertEqual(page.tasks_list.count(), 0)
        self.assertEqual(page.clock.blocks, [])

    def test_close_warning_includes_active_weekend_edit(self):
        repo.create_block("weekends", "Rest", 1320, 480, "#003B5C")
        window = MainWindow()
        self.widgets.append(window)
        page = window.routine_tab.weekends_page
        page.tasks_list.setCurrentRow(0)
        page.start_edit()

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
