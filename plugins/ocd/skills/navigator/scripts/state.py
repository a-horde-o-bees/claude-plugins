"""Navigator state check.

Verifies navigator infrastructure by inspecting database state.
"""

import sqlite3
from pathlib import Path


def check_state(project_dir: str) -> dict:
    """Check navigator infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted" | "error"
    - details: list of human-readable status lines
    - actions: list of actionable commands (empty if operational with no maintenance)
    """
    db_path = Path(project_dir) / ".claude" / "ocd" / "navigator" / "navigator.db"

    if not db_path.exists():
        return {
            "state": "adopted",
            "details": ["Database: not found"],
            "actions": ["Run /ocd-init to create navigator database"],
        }

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

        # Verify schema
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='entries'",
        ).fetchone()
        if not tables:
            conn.close()
            return {
                "state": "error",
                "details": ["Database: missing entries table"],
                "actions": ["Run /ocd-init to reinitialize navigator database"],
            }

        # Count concrete entries (not glob patterns)
        total = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE path NOT LIKE '%*%'",
        ).fetchone()["c"]

        if total == 0:
            conn.close()
            return {
                "state": "adopted",
                "details": ["Database: ready", "Entries: none (scan needed)"],
                "actions": ["Run /ocd-navigator to scan and describe project"],
            }

        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND description IS NULL",
        ).fetchone()["c"]

        stale = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND stale = 1",
        ).fetchone()["c"]

        conn.close()

        details = [f"Entries: {total} total, {undescribed} undescribed, {stale} stale"]
        actions = []

        if undescribed > 0 or stale > 0:
            parts = []
            if undescribed > 0:
                parts.append(f"describe {undescribed} entries")
            if stale > 0:
                parts.append(f"review {stale} stale entries")
            actions.append(f"Run /ocd-navigator to {' and '.join(parts)}")

        return {
            "state": "operational",
            "details": details,
            "actions": actions,
        }

    except sqlite3.Error as e:
        return {
            "state": "error",
            "details": [f"Database: {e}"],
            "actions": ["Run /ocd-init to reinitialize navigator database"],
        }
