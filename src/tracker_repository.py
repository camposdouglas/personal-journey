from datetime import date, datetime, timedelta

from db import get_connection
from week_utils import get_week_start


def _now():
    return datetime.now().isoformat(timespec="seconds")


def create_tracker(name, weekly_target):
    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Tracker name cannot be empty.")

    if not isinstance(weekly_target, int) or not 1 <= weekly_target <= 7:
        raise ValueError("Weekly target must be between 1 and 7.")

    timestamp = _now()
    week_start = get_week_start(date.today()).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO trackers (name, created_at)
            VALUES (?, ?)
            """,
            (cleaned_name, timestamp),
        )
        tracker_id = cursor.lastrowid

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
            (tracker_id, week_start, weekly_target, timestamp),
        )

    return {
        "id": tracker_id,
        "name": cleaned_name,
        "description": "",
        "weekly_target": weekly_target,
        "created_at": timestamp,
    }


def list_active_trackers():
    current_week_start = get_week_start(date.today()).isoformat()

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                trackers.id,
                trackers.name,
                trackers.description,
                tracker_weekly_targets.weekly_target,
                trackers.created_at
            FROM trackers
            JOIN tracker_weekly_targets
                ON tracker_weekly_targets.tracker_id = trackers.id
            WHERE trackers.archived_at IS NULL
              AND tracker_weekly_targets.week_start = (
                  SELECT MAX(target_history.week_start)
                  FROM tracker_weekly_targets AS target_history
                  WHERE target_history.tracker_id = trackers.id
                    AND target_history.week_start <= ?
              )
            ORDER BY trackers.created_at, trackers.id
            """,
            (current_week_start,),
        ).fetchall()

    return [dict(row) for row in rows]


def update_tracker(tracker_id, name, description, weekly_target):
    cleaned_name = name.strip()
    cleaned_description = description.strip()

    if not cleaned_name:
        raise ValueError("Tracker name cannot be empty.")

    if not isinstance(weekly_target, int) or not 1 <= weekly_target <= 7:
        raise ValueError("Weekly target must be between 1 and 7.")

    timestamp = _now()
    current_week_start = get_week_start(date.today()).isoformat()

    with get_connection() as connection:
        tracker_row = connection.execute(
            """
            SELECT created_at
            FROM trackers
            WHERE id = ? AND archived_at IS NULL
            """,
            (tracker_id,),
        ).fetchone()

        if tracker_row is None:
            raise ValueError("Active tracker not found.")

        connection.execute(
            """
            UPDATE trackers
            SET name = ?, description = ?
            WHERE id = ?
            """,
            (cleaned_name, cleaned_description, tracker_id),
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
            ON CONFLICT (tracker_id, week_start) DO UPDATE SET
                weekly_target = excluded.weekly_target
            """,
            (tracker_id, current_week_start, weekly_target, timestamp),
        )

    return {
        "id": tracker_id,
        "name": cleaned_name,
        "description": cleaned_description,
        "weekly_target": weekly_target,
        "created_at": tracker_row["created_at"],
    }


def archive_tracker(tracker_id):
    timestamp = _now()
    current_week_start = get_week_start(date.today()).isoformat()

    with get_connection() as connection:
        tracker_exists = connection.execute(
            """
            SELECT 1
            FROM trackers
            WHERE id = ? AND archived_at IS NULL
            """,
            (tracker_id,),
        ).fetchone()

        if tracker_exists is None:
            raise ValueError("Active tracker not found.")

        connection.execute(
            """
            UPDATE trackers
            SET archived_at = ?
            WHERE id = ?
            """,
            (timestamp, tracker_id),
        )

        connection.execute(
            """
            DELETE FROM tracker_daily_statuses
            WHERE tracker_id = ? AND status_date >= ?
            """,
            (tracker_id, current_week_start),
        )


def list_week_statuses(tracker_id, week_start):
    week_start = get_week_start(week_start)
    week_end = week_start + timedelta(days=6)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT status_date, status
            FROM tracker_daily_statuses
            WHERE tracker_id = ?
              AND status_date BETWEEN ? AND ?
            ORDER BY status_date
            """,
            (tracker_id, week_start.isoformat(), week_end.isoformat()),
        ).fetchall()

    return {
        date.fromisoformat(row["status_date"]): row["status"] for row in rows
    }


def toggle_daily_status(tracker_id, status_date, requested_status):
    if requested_status not in (-1, 1):
        raise ValueError("Daily status must be -1 or 1.")

    if status_date > date.today():
        raise ValueError("Future dates cannot be tracked.")

    timestamp = _now()
    status_date_text = status_date.isoformat()

    with get_connection() as connection:
        tracker_exists = connection.execute(
            """
            SELECT 1
            FROM trackers
            WHERE id = ? AND archived_at IS NULL
            """,
            (tracker_id,),
        ).fetchone()

        if tracker_exists is None:
            raise ValueError("Active tracker not found.")

        existing_row = connection.execute(
            """
            SELECT status
            FROM tracker_daily_statuses
            WHERE tracker_id = ? AND status_date = ?
            """,
            (tracker_id, status_date_text),
        ).fetchone()

        if existing_row is not None and existing_row["status"] == requested_status:
            connection.execute(
                """
                DELETE FROM tracker_daily_statuses
                WHERE tracker_id = ? AND status_date = ?
                """,
                (tracker_id, status_date_text),
            )
            return None

        connection.execute(
            """
            INSERT INTO tracker_daily_statuses (
                tracker_id,
                status_date,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (tracker_id, status_date) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                tracker_id,
                status_date_text,
                requested_status,
                timestamp,
                timestamp,
            ),
        )

    return requested_status
