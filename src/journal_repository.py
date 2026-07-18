from datetime import datetime

from db import get_connection


def _now():
    return datetime.now().isoformat(timespec="seconds")


def create_entry(title, content):
    timestamp = _now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO journal_entries (title, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, content, timestamp, timestamp),
        )
        new_id = cursor.lastrowid

    return get_entry(new_id)


def list_entries():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM journal_entries
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_entry(entry_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, title, content, created_at, updated_at
            FROM journal_entries
            WHERE id = ?
            """,
            (entry_id,),
        ).fetchone()

    return dict(row) if row is not None else None


def update_entry(entry_id, title, content):
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE journal_entries
            SET title = ?, content = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, content, _now(), entry_id),
        )

    return get_entry(entry_id)


def delete_entry(entry_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM journal_entries WHERE id = ?",
            (entry_id,),
        )
