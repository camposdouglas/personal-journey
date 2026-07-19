import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "personal_journey.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


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
                created_at TEXT NOT NULL,
                archived_at TEXT
            )
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
