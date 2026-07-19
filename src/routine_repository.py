import re
from datetime import datetime

from db import get_connection


SCHEDULE_TYPES = {"weekdays", "weekends"}
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _validate_schedule_type(schedule_type):
    if schedule_type not in SCHEDULE_TYPES:
        raise ValueError("Schedule type must be weekdays or weekends.")


def _validate_block(name, start_minute, end_minute, color):
    cleaned_name = name.strip()

    if not cleaned_name:
        raise ValueError("Routine block name cannot be empty.")

    for value in (start_minute, end_minute):
        if not isinstance(value, int) or not 0 <= value <= 1439:
            raise ValueError("Routine block times must be between 0 and 1439.")

    if start_minute == end_minute:
        raise ValueError("Routine block start and end times cannot be equal.")

    if not HEX_COLOR_PATTERN.fullmatch(color):
        raise ValueError("Routine block color must use #RRGGBB format.")

    return cleaned_name, color.upper()


def _next_layer_order(connection, schedule_type):
    return connection.execute(
        """
        SELECT COALESCE(MAX(layer_order), 0) + 1
        FROM routine_blocks
        WHERE schedule_type = ?
        """,
        (schedule_type,),
    ).fetchone()[0]


def create_block(schedule_type, name, start_minute, end_minute, color):
    _validate_schedule_type(schedule_type)
    cleaned_name, normalized_color = _validate_block(
        name, start_minute, end_minute, color
    )
    timestamp = _now()

    with get_connection() as connection:
        layer_order = _next_layer_order(connection, schedule_type)
        cursor = connection.execute(
            """
            INSERT INTO routine_blocks (
                schedule_type,
                name,
                start_minute,
                end_minute,
                color,
                layer_order,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_type,
                cleaned_name,
                start_minute,
                end_minute,
                normalized_color,
                layer_order,
                timestamp,
                timestamp,
            ),
        )
        block_id = cursor.lastrowid

    return get_block(block_id)


def list_blocks(schedule_type):
    _validate_schedule_type(schedule_type)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                schedule_type,
                name,
                start_minute,
                end_minute,
                color,
                layer_order,
                created_at,
                updated_at
            FROM routine_blocks
            WHERE schedule_type = ?
            ORDER BY start_minute, end_minute, id
            """,
            (schedule_type,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_block(block_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                schedule_type,
                name,
                start_minute,
                end_minute,
                color,
                layer_order,
                created_at,
                updated_at
            FROM routine_blocks
            WHERE id = ?
            """,
            (block_id,),
        ).fetchone()

    return dict(row) if row is not None else None


def update_block(block_id, name, start_minute, end_minute, color):
    cleaned_name, normalized_color = _validate_block(
        name, start_minute, end_minute, color
    )
    timestamp = _now()

    with get_connection() as connection:
        block_row = connection.execute(
            """
            SELECT schedule_type, created_at
            FROM routine_blocks
            WHERE id = ?
            """,
            (block_id,),
        ).fetchone()

        if block_row is None:
            raise ValueError("Routine block not found.")

        layer_order = _next_layer_order(
            connection, block_row["schedule_type"]
        )
        connection.execute(
            """
            UPDATE routine_blocks
            SET
                name = ?,
                start_minute = ?,
                end_minute = ?,
                color = ?,
                layer_order = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                cleaned_name,
                start_minute,
                end_minute,
                normalized_color,
                layer_order,
                timestamp,
                block_id,
            ),
        )

    return get_block(block_id)


def delete_block(block_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM routine_blocks WHERE id = ?",
            (block_id,),
        )
