"""Per-exchange purpose summaries.

Stores Purpose Statement-style summaries (scope + role; no mechanics, no
history) for individual exchanges in the `exchanges` annotations table.
Persists across ingest runs — sync only adds events, never touches stored
purposes. Wiped only by `reset`.

Once an agent reads an exchange's content and generates a purpose summary,
it calls `set_purpose` to persist. Subsequent reads via `sessions` and
`exchanges` surface the purpose for fast at-a-glance navigation.

The `exchanges` table holds annotations only — view-derived metrics (like
exchange numbering and gap_s) come from `events_with_gaps`. Each annotation
column has its own setter module; `purpose` is the first.
"""

import sqlite3


def get(conn: sqlite3.Connection, session: str, exchange: int) -> str | None:
    """Return the stored purpose for an exchange, or None when unset."""
    row = conn.execute(
        "SELECT purpose FROM exchanges "
        "WHERE parent_session = ? AND exchange = ?",
        (session, exchange),
    ).fetchone()
    return row[0] if row else None


def set_purpose(
    conn: sqlite3.Connection, session: str, exchange: int, purpose: str,
) -> None:
    """Upsert the purpose for an exchange. Updates `purpose_updated_at` on overwrite."""
    if not purpose or not purpose.strip():
        raise ValueError("purpose text must be non-empty")
    conn.execute(
        """
        INSERT INTO exchanges (parent_session, exchange, purpose, purpose_updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(parent_session, exchange) DO UPDATE SET
            purpose = excluded.purpose,
            purpose_updated_at = CURRENT_TIMESTAMP
        """,
        (session, exchange, purpose.strip()),
    )
    conn.commit()


def clear(conn: sqlite3.Connection, session: str, exchange: int) -> bool:
    """Clear the stored purpose. Returns True when a purpose was actually cleared.

    Sets `purpose` and `purpose_updated_at` to NULL while preserving the row
    so that other annotation columns (when added) survive the clear.
    """
    cursor = conn.execute(
        """
        UPDATE exchanges
        SET purpose = NULL, purpose_updated_at = NULL
        WHERE parent_session = ? AND exchange = ? AND purpose IS NOT NULL
        """,
        (session, exchange),
    )
    conn.commit()
    return cursor.rowcount > 0


def set_many(
    conn: sqlite3.Connection,
    session: str,
    purposes: dict[int, str],
) -> dict[int, str]:
    """Batch upsert purposes for a session. Single transaction.

    Keys are exchange numbers, values are purpose text. Each text is validated
    (non-empty after strip) and trimmed before storage. Returns the dict of
    {exchange: trimmed_purpose} actually written.
    """
    if not purposes:
        return {}
    written: dict[int, str] = {}
    for exchange, purpose in purposes.items():
        if not purpose or not purpose.strip():
            raise ValueError(f"purpose for exchange {exchange} must be non-empty")
        trimmed = purpose.strip()
        conn.execute(
            """
            INSERT INTO exchanges (parent_session, exchange, purpose, purpose_updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(parent_session, exchange) DO UPDATE SET
                purpose = excluded.purpose,
                purpose_updated_at = CURRENT_TIMESTAMP
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
    """Batch clear purposes for a session. Single transaction.

    Returns the list of exchange numbers that actually had a purpose cleared
    (subset of input — exchanges with no stored purpose are silently skipped).
    """
    if not exchanges:
        return []
    cleared: list[int] = []
    for exchange in exchanges:
        cursor = conn.execute(
            """
            UPDATE exchanges
            SET purpose = NULL, purpose_updated_at = NULL
            WHERE parent_session = ? AND exchange = ? AND purpose IS NOT NULL
            """,
            (session, exchange),
        )
        if cursor.rowcount > 0:
            cleared.append(exchange)
    conn.commit()
    return cleared


def list_for_session(conn: sqlite3.Connection, session: str) -> list[dict]:
    """Return all stored purposes for a session, ordered by exchange."""
    rows = conn.execute(
        """
        SELECT exchange, purpose, purpose_updated_at FROM exchanges
        WHERE parent_session = ? AND purpose IS NOT NULL
        ORDER BY exchange
        """,
        (session,),
    ).fetchall()
    return [
        {"exchange": ex, "purpose": p, "updated_at": ut}
        for ex, p, ut in rows
    ]


def count_for_session(conn: sqlite3.Connection, session: str) -> int:
    """Return how many exchanges in this session have stored purposes."""
    return conn.execute(
        """
        SELECT COUNT(*) FROM exchanges
        WHERE parent_session = ? AND purpose IS NOT NULL
        """,
        (session,),
    ).fetchone()[0]
