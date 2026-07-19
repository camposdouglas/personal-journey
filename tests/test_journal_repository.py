import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_PATH = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

import db
import journal_repository as repo


class JournalRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.original_db_path = db.DB_PATH
        self.temporary_directory = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temporary_directory.name) / "test.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temporary_directory.cleanup()

    def test_create_and_get_entry(self):
        timestamp = "2026-07-19T10:30:00"

        with patch.object(repo, "_now", return_value=timestamp):
            created = repo.create_entry("First entry", "Journal content")

        retrieved = repo.get_entry(created["id"])

        self.assertEqual(
            created,
            {
                "id": created["id"],
                "title": "First entry",
                "content": "Journal content",
                "created_at": timestamp,
                "updated_at": timestamp,
            },
        )
        self.assertEqual(retrieved, created)

    def test_list_entries_returns_newest_first(self):
        with patch.object(repo, "_now", return_value="2026-07-19T09:00:00"):
            first = repo.create_entry("First", "Older entry")

        with patch.object(repo, "_now", return_value="2026-07-19T10:00:00"):
            second = repo.create_entry("Second", "Newer entry")

        entries = repo.list_entries()

        self.assertEqual(
            [entry["id"] for entry in entries],
            [second["id"], first["id"]],
        )

    def test_update_preserves_creation_time_and_changes_update_time(self):
        created_at = "2026-07-19T09:00:00"
        updated_at = "2026-07-19T11:00:00"

        with patch.object(repo, "_now", return_value=created_at):
            entry = repo.create_entry("Original title", "Original content")

        with patch.object(repo, "_now", return_value=updated_at):
            updated = repo.update_entry(
                entry["id"],
                "Updated title",
                "Updated content",
            )

        self.assertEqual(updated["id"], entry["id"])
        self.assertEqual(updated["title"], "Updated title")
        self.assertEqual(updated["content"], "Updated content")
        self.assertEqual(updated["created_at"], created_at)
        self.assertEqual(updated["updated_at"], updated_at)

    def test_delete_removes_only_selected_entry(self):
        first = repo.create_entry("First", "Keep this entry")
        second = repo.create_entry("Second", "Delete this entry")

        repo.delete_entry(second["id"])

        self.assertIsNone(repo.get_entry(second["id"]))
        self.assertEqual(repo.get_entry(first["id"]), first)
        self.assertEqual(repo.list_entries(), [first])

    def test_get_missing_entry_returns_none(self):
        self.assertIsNone(repo.get_entry(999))


if __name__ == "__main__":
    unittest.main()
