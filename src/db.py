import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "personal_journey.db"


@contextmanager
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        with connection:
            yield connection
    finally:
        connection.close()


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trackers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                archived_at TEXT
            )
            """
        )

        tracker_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(trackers)").fetchall()
        }

        if "description" not in tracker_columns:
            connection.execute(
                """
                ALTER TABLE trackers
                ADD COLUMN description TEXT NOT NULL DEFAULT ''
                """
            )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tracker_weekly_targets (
                tracker_id INTEGER NOT NULL,
                week_start TEXT NOT NULL,
                weekly_target INTEGER NOT NULL CHECK (weekly_target BETWEEN 1 AND 7),
                created_at TEXT NOT NULL,
                PRIMARY KEY (tracker_id, week_start),
                FOREIGN KEY (tracker_id) REFERENCES trackers (id) ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tracker_daily_statuses (
                tracker_id INTEGER NOT NULL,
                status_date TEXT NOT NULL,
                status INTEGER NOT NULL CHECK (status IN (-1, 1)),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (tracker_id, status_date),
                FOREIGN KEY (tracker_id) REFERENCES trackers (id) ON DELETE CASCADE
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS routine_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_type TEXT NOT NULL CHECK (
                    schedule_type IN ('weekdays', 'weekends')
                ),
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                start_minute INTEGER NOT NULL CHECK (
                    start_minute BETWEEN 0 AND 1439
                ),
                end_minute INTEGER NOT NULL CHECK (
                    end_minute BETWEEN 0 AND 1439
                ),
                color TEXT NOT NULL CHECK (
                    length(color) = 7
                    AND substr(color, 1, 1) = '#'
                    AND substr(color, 2) NOT GLOB '*[^0-9A-Fa-f]*'
                ),
                layer_order INTEGER NOT NULL CHECK (layer_order > 0),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                CHECK (start_minute != end_minute),
                UNIQUE (schedule_type, layer_order)
            )
            """
        )
