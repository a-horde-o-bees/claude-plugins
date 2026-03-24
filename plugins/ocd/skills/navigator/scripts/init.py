"""Navigator skill init and status.

Initializes navigator database and reports infrastructure state.
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def get_project_dir() -> Path:
    import os
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_db_path(project_dir: Path) -> Path:
    return project_dir / ".claude" / "ocd" / "navigator" / "navigator.db"


def init(project_dir: Path) -> list[str]:
    """Initialize navigator database. Returns status lines."""
    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))
    try:
        import navigator
        db_path = get_db_path(project_dir)
        result = navigator.init_db(str(db_path))
        return [result]
    except Exception as e:
        return [f"Error: {e}"]
    finally:
        sys.path.pop(0)


def status(project_dir: Path) -> dict:
    """Check navigator infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted" | "error"
    - details: list of human-readable status lines
    - actions: list of actionable commands
    """
    db_path = get_db_path(project_dir)

    if not db_path.exists():
        return {
            "state": "adopted",
            "details": ["Database: not found"],
            "actions": ["Run /ocd-init to create navigator database"],
        }

    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Navigator skill init and status.")
    parser.add_argument("--status", action="store_true", help="Report infrastructure state")
    parser.add_argument("--force", action="store_true", help="Accepted for interface consistency")
    args = parser.parse_args()

    project_dir = get_project_dir()

    if args.status:
        result = status(project_dir)
        print(f"navigator: {result['state']}")
        for detail in result.get("details", []):
            print(f"  {detail}")
        for action in result.get("actions", []):
            print(f"  Action: {action}")
    else:
        lines = init(project_dir)
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
