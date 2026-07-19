import sys
import tempfile
import unittest
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

import db
import routine_repository as repo


class RoutineRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.original_db_path = db.DB_PATH
        self.temporary_directory = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temporary_directory.name) / "test.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temporary_directory.cleanup()

    def test_create_supports_precision_cross_midnight_and_duplicate_names(self):
        one_minute = repo.create_block(
            "weekdays", "Study", 855, 856, "#39ff14"
        )
        cross_midnight = repo.create_block(
            "weekdays", "Study", 1380, 420, "#4d96ff"
        )
        nearly_full_day = repo.create_block(
            "weekends", "Rest", 0, 1439, "#ff3131"
        )

        self.assertNotEqual(one_minute["id"], cross_midnight["id"])
        self.assertEqual(one_minute["color"], "#39FF14")
        self.assertEqual(cross_midnight["start_minute"], 1380)
        self.assertEqual(cross_midnight["end_minute"], 420)
        self.assertEqual(nearly_full_day["end_minute"], 1439)

    def test_schedules_allow_overlaps_and_use_independent_layers(self):
        first = repo.create_block("weekdays", "Study", 840, 960, "#39FF14")
        overlapping = repo.create_block(
            "weekdays", "Reading", 900, 1020, "#FF3131"
        )
        weekend = repo.create_block(
            "weekends", "Reading", 900, 1020, "#FF3131"
        )

        self.assertEqual(first["layer_order"], 1)
        self.assertEqual(overlapping["layer_order"], 2)
        self.assertEqual(weekend["layer_order"], 1)
        self.assertEqual(len(repo.list_blocks("weekdays")), 2)
        self.assertEqual(len(repo.list_blocks("weekends")), 1)

    def test_list_sorts_blocks_by_start_time(self):
        late = repo.create_block("weekdays", "Late", 1200, 1260, "#111111")
        early = repo.create_block("weekdays", "Early", 360, 420, "#222222")
        middle = repo.create_block(
            "weekdays", "Middle", 840, 900, "#333333"
        )

        blocks = repo.list_blocks("weekdays")

        self.assertEqual(
            [block["id"] for block in blocks],
            [early["id"], middle["id"], late["id"]],
        )

    def test_update_preserves_identity_and_moves_block_to_top_layer(self):
        first = repo.create_block("weekdays", "First", 480, 540, "#111111")
        second = repo.create_block("weekdays", "Second", 540, 600, "#222222")

        updated = repo.update_block(
            first["id"],
            "Updated First",
            495,
            585,
            "#abcdef",
        )

        self.assertEqual(updated["id"], first["id"])
        self.assertEqual(updated["schedule_type"], "weekdays")
        self.assertEqual(updated["created_at"], first["created_at"])
        self.assertEqual(updated["color"], "#ABCDEF")
        self.assertGreater(updated["layer_order"], second["layer_order"])

    def test_validation_and_deletion(self):
        invalid_blocks = [
            ("daily", "Bad schedule", 0, 1, "#000000"),
            ("weekdays", "   ", 0, 1, "#000000"),
            ("weekdays", "Equal", 60, 60, "#000000"),
            ("weekdays", "Negative", -1, 60, "#000000"),
            ("weekdays", "Too late", 60, 1440, "#000000"),
            ("weekdays", "Bad color", 60, 120, "red"),
        ]

        for values in invalid_blocks:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    repo.create_block(*values)

        block = repo.create_block("weekdays", "Delete", 60, 120, "#000000")
        repo.delete_block(block["id"])

        self.assertIsNone(repo.get_block(block["id"]))
        self.assertIsNone(repo.get_block(999))


if __name__ == "__main__":
    unittest.main()
