import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path


SRC_PATH = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

import db
import tracker_repository as repo
from week_utils import get_week_start


class TrackerRepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.original_db_path = db.DB_PATH
        self.temporary_directory = tempfile.TemporaryDirectory()
        db.DB_PATH = Path(self.temporary_directory.name) / "test.db"
        db.init_db()

    def tearDown(self):
        db.DB_PATH = self.original_db_path
        self.temporary_directory.cleanup()

    def test_create_allows_duplicate_names_with_separate_ids(self):
        first = repo.create_tracker("Dutch", 7)
        second = repo.create_tracker("Dutch", 7)

        trackers = repo.list_active_trackers()

        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual([tracker["name"] for tracker in trackers], ["Dutch", "Dutch"])
        self.assertEqual(
            [tracker["weekly_target"] for tracker in trackers],
            [7, 7],
        )

    def test_create_rejects_invalid_name_and_target(self):
        invalid_trackers = [
            ("   ", 7),
            ("Gym", 0),
            ("Gym", 8),
        ]

        for name, target in invalid_trackers:
            with self.subTest(name=name, target=target):
                with self.assertRaises(ValueError):
                    repo.create_tracker(name, target)

        self.assertEqual(repo.list_active_trackers(), [])

    def test_daily_status_toggles_between_green_red_and_gray(self):
        tracker = repo.create_tracker("Reading", 7)
        today = date.today()

        self.assertEqual(repo.toggle_daily_status(tracker["id"], today, 1), 1)
        self.assertEqual(
            repo.list_week_statuses(tracker["id"], today),
            {today: 1},
        )

        self.assertEqual(repo.toggle_daily_status(tracker["id"], today, -1), -1)
        self.assertEqual(
            repo.list_week_statuses(tracker["id"], today),
            {today: -1},
        )

        self.assertIsNone(repo.toggle_daily_status(tracker["id"], today, -1))
        self.assertEqual(repo.list_week_statuses(tracker["id"], today), {})

        with self.assertRaises(ValueError):
            repo.toggle_daily_status(tracker["id"], today + timedelta(days=1), 1)

    def test_edit_preserves_statuses_and_previous_week_target(self):
        tracker = repo.create_tracker("Study", 7)
        current_week = get_week_start(date.today())
        previous_week = current_week - timedelta(days=7)
        previous_timestamp = datetime.combine(
            previous_week, datetime.min.time()
        ).isoformat(timespec="seconds")

        with db.get_connection() as connection:
            connection.execute(
                "UPDATE trackers SET created_at = ? WHERE id = ?",
                (previous_timestamp, tracker["id"]),
            )
            connection.execute(
                """
                INSERT INTO tracker_weekly_targets (
                    tracker_id,
                    week_start,
                    weekly_target,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (tracker["id"], previous_week.isoformat(), 7, previous_timestamp),
            )

        repo.toggle_daily_status(tracker["id"], date.today(), 1)
        updated = repo.update_tracker(
            tracker["id"],
            "Focused Study",
            "Review one subject.",
            4,
        )

        self.assertEqual(updated["name"], "Focused Study")
        self.assertEqual(updated["description"], "Review one subject.")
        self.assertEqual(updated["weekly_target"], 4)
        self.assertEqual(
            repo.list_week_statuses(tracker["id"], current_week),
            {date.today(): 1},
        )

        with db.get_connection() as connection:
            targets = {
                row["week_start"]: row["weekly_target"]
                for row in connection.execute(
                    """
                    SELECT week_start, weekly_target
                    FROM tracker_weekly_targets
                    WHERE tracker_id = ?
                    """,
                    (tracker["id"],),
                )
            }

        self.assertEqual(targets[previous_week.isoformat()], 7)
        self.assertEqual(targets[current_week.isoformat()], 4)

    def test_archive_erases_current_week_and_preserves_completed_week(self):
        tracker = repo.create_tracker("Gym", 6)
        current_week = get_week_start(date.today())
        previous_week = current_week - timedelta(days=7)
        previous_timestamp = datetime.combine(
            previous_week, datetime.min.time()
        ).isoformat(timespec="seconds")

        with db.get_connection() as connection:
            connection.execute(
                "UPDATE trackers SET created_at = ? WHERE id = ?",
                (previous_timestamp, tracker["id"]),
            )
            connection.execute(
                """
                INSERT INTO tracker_weekly_targets (
                    tracker_id,
                    week_start,
                    weekly_target,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (tracker["id"], previous_week.isoformat(), 6, previous_timestamp),
            )

        repo.toggle_daily_status(tracker["id"], previous_week, 1)
        repo.toggle_daily_status(tracker["id"], date.today(), -1)
        repo.archive_tracker(tracker["id"])

        self.assertEqual(repo.list_active_trackers(), [])
        self.assertEqual(
            repo.list_week_statuses(tracker["id"], previous_week),
            {previous_week: 1},
        )
        self.assertEqual(repo.list_week_statuses(tracker["id"], current_week), {})

        with self.assertRaises(ValueError):
            repo.update_tracker(tracker["id"], "Gym", "", 6)

        with self.assertRaises(ValueError):
            repo.toggle_daily_status(tracker["id"], date.today(), 1)

    def test_historical_listing_uses_tracker_lifecycle_and_weekly_target(self):
        current_week = get_week_start(date.today())
        previous_week = current_week - timedelta(days=7)
        previous_timestamp = datetime.combine(
            previous_week, datetime.min.time()
        ).isoformat(timespec="seconds")

        historical = repo.create_tracker("Dutch", 7)
        current = repo.create_tracker("Dutch", 4)

        with db.get_connection() as connection:
            connection.execute(
                "UPDATE trackers SET created_at = ?, archived_at = ? WHERE id = ?",
                (previous_timestamp, datetime.now().isoformat(), historical["id"]),
            )
            connection.execute(
                """
                INSERT INTO tracker_weekly_targets (
                    tracker_id,
                    week_start,
                    weekly_target,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    historical["id"],
                    previous_week.isoformat(),
                    7,
                    previous_timestamp,
                ),
            )

        previous_trackers = repo.list_trackers_for_week(previous_week)
        current_trackers = repo.list_trackers_for_week(current_week)

        self.assertEqual(
            [
                (tracker["id"], tracker["weekly_target"])
                for tracker in previous_trackers
            ],
            [(historical["id"], 7)],
        )
        self.assertEqual(
            [(tracker["id"], tracker["weekly_target"]) for tracker in current_trackers],
            [(current["id"], 4)],
        )


if __name__ == "__main__":
    unittest.main()
