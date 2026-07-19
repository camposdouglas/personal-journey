from datetime import date, datetime

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
