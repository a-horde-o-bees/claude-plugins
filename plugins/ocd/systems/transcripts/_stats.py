"""Derived statistics computed on demand from current data.

Not stored in the DB — recomputed each call. Exposed as callable utilities
so agents/skills can use them as fill values when assembling aggregates that
include exchanges with NULL `user_time_s` slots.
"""

import sqlite3


AVG_USER_TIME_DESCRIPTION = (
    "Mean of observable compose pauses (gap_s on user_msg events ≤ threshold). "
    "Use as fill value when computing aggregates that include exchanges with "
    "NULL user_time_s. Recomputed on every call from current event data — no "
    "caching, since every new exchange would invalidate it."
)


def avg_user_time(conn: sqlite3.Connection, threshold_s: float) -> float:
    """Mean of observable compose pauses across the entire DB.

    Definition: gap_s on user_msg events (parent_message IS NULL) where
    0 < gap_s ≤ threshold_s. Returns 0.0 when no observable pauses exist.
    """
    row = conn.execute(
        """
        SELECT AVG(gap_s) FROM events_with_gaps
        WHERE label = 'user_msg' AND parent_message IS NULL
          AND gap_s > 0
          AND gap_s <= ?
        """,
        (threshold_s,),
    ).fetchone()
    return float(row[0] or 0.0)
