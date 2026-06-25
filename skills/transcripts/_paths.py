"""Resolve the skill's working-data directory (DBs, generated diagrams, logs, scratch).

Default `~/.claude/a-horde-o-bees/transcripts/`; override with the `TRANSCRIPTS_WORK`
env var. Stdlib-only and dependency-free so EVERY module — including the otherwise
import-free `raw_db.py` — can share one source of truth for paths instead of hardcoding
a cwd-relative `build/` (which broke depending on where a verb was run from)."""
import os
import pathlib

WORK_DIR = pathlib.Path(os.environ.get("TRANSCRIPTS_WORK")
                        or pathlib.Path.home() / ".claude/a-horde-o-bees/transcripts")


def db(name: str = "raw.db") -> str:
    """Absolute path to a DB in the working dir (raw.db, annotations.db)."""
    return str(WORK_DIR / name)


def diagram(name: str) -> str:
    """Absolute path to a generated artifact under the working dir's diagrams/."""
    return str(WORK_DIR / "diagrams" / name)
