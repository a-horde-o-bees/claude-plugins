"""Per-exchange descriptions.

Stores descriptions for individual exchanges in the `exchanges` annotations
table. Each is written per [[description-authoring]] — one line, scope +
role, no mechanics, no history. Persists across ingest runs — sync only
adds events, never touches stored descriptions. Wiped only by `reset`.

Once an agent reads an exchange's content and authors a description, it
calls `set_description` to persist. Subsequent reads via `sessions` and
`exchanges` surface the description for fast at-a-glance navigation.

The `exchanges` table holds annotations only — view-derived metrics (like
exchange numbering and gap_s) come from `events_with_gaps`. Each annotation
column has its own setter module; `description` is the first.
"""

import sqlite3


def get(conn: sqlite3.Connection, session: str, exchange: int) -> str | None:
    """Return the stored description for an exchange, or None when unset."""
    row = conn.execute(
        "SELECT description FROM exchanges "
        "WHERE parent_session = ? AND exchange = ?",
        (session, exchange),
    ).fetchone()
    return row[0] if row else None


def set_description(
    conn: sqlite3.Connection, session: str, exchange: int, description: str,
) -> None:
    """Upsert the description for an exchange. Updates `description_updated_at` on overwrite."""
    if not description or not description.strip():
        raise ValueError("description text must be non-empty")
    conn.execute(
        """
        INSERT INTO exchanges (parent_session, exchange, description, description_updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(parent_session, exchange) DO UPDATE SET
            description = excluded.description,
            description_updated_at = CURRENT_TIMESTAMP
        """,
        (session, exchange, description.strip()),
    )
    conn.commit()


def clear(conn: sqlite3.Connection, session: str, exchange: int) -> bool:
    """Clear the stored description. Returns True when a description was actually cleared."""
    cursor = conn.execute(
        """
        UPDATE exchanges
        SET description = NULL, description_updated_at = NULL
        WHERE parent_session = ? AND exchange = ? AND description IS NOT NULL
        """,
        (session, exchange),
    )
    conn.commit()
    return cursor.rowcount > 0


def set_many(
    conn: sqlite3.Connection,
    session: str,
    descriptions: dict[int, str],
) -> dict[int, str]:
    """Batch upsert descriptions for a session. Single transaction.

    Keys are exchange numbers, values are description text. Each text is
    validated (non-empty after strip) and trimmed before storage. Returns
    the dict of {exchange: trimmed_description} actually written.
    """
    if not descriptions:
        return {}
    written: dict[int, str] = {}
    for exchange, description in descriptions.items():
        if not description or not description.strip():
            raise ValueError(f"description for exchange {exchange} must be non-empty")
        trimmed = description.strip()
        conn.execute(
            """
            INSERT INTO exchanges (parent_session, exchange, description, description_updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(parent_session, exchange) DO UPDATE SET
                description = excluded.description,
                description_updated_at = CURRENT_TIMESTAMP
            """,
            (session, exchange, trimmed),
        )
        written[exchange] = trimmed
    conn.commit()
    return written


def clear_many(
    conn: sqlite3.Connection,
    session: str,
    exchanges: list[int],
) -> list[int]:
    """Batch clear descriptions for a session. Single transaction.

    Returns the list of exchange numbers that actually had a description
    cleared (subset of input — exchanges with no stored description are
    silently skipped).
    """
    if not exchanges:
        return []
    cleared: list[int] = []
    for exchange in exchanges:
        cursor = conn.execute(
            """
            UPDATE exchanges
            SET description = NULL, description_updated_at = NULL
            WHERE parent_session = ? AND exchange = ? AND description IS NOT NULL
            """,
            (session, exchange),
        )
        if cursor.rowcount > 0:
            cleared.append(exchange)
    conn.commit()
    return cleared


def list_for_session(conn: sqlite3.Connection, session: str) -> list[dict]:
    """Return all stored descriptions for a session, ordered by exchange."""
    rows = conn.execute(
        """
        SELECT exchange, description, description_updated_at FROM exchanges
        WHERE parent_session = ? AND description IS NOT NULL
        ORDER BY exchange
        """,
        (session,),
    ).fetchall()
    return [
        {"exchange": ex, "description": d, "updated_at": ut}
        for ex, d, ut in rows
    ]


def count_for_session(conn: sqlite3.Connection, session: str) -> int:
    """Return how many exchanges in this session have stored descriptions."""
    return conn.execute(
        """
        SELECT COUNT(*) FROM exchanges
        WHERE parent_session = ? AND description IS NOT NULL
        """,
        (session,),
    ).fetchone()[0]
