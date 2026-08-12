"""Resolve the skill's two path anchors: the working-data directory it writes, and
the transcripts root it reads. Both are user-chosen and stored by `raw_db.py init`.

The **working dir** holds every artifact the skill produces — the DBs, plus `logs/`,
`diagrams/`, and `scratch/` beneath it. Precedence: `ENGAGED_TIME_WORK`, then the
stored value, then `~/.claude/engaged-time`.

The **transcripts root** — the directory of raw Claude Code session JSONL — has NO
default: every reading verb blocks without it. A wrong-but-plausible default would
silently produce an empty or partial timeline, which reads as "no work happened"
rather than as an error.

The config lives OUTSIDE the working dir (`~/.config/engaged-time/config.json`,
honoring `XDG_CONFIG_HOME`), because a file inside the working dir cannot record
where the working dir is.

Stdlib-only and dependency-free so EVERY module — including the otherwise
import-free `raw_db.py` — can share one source of truth for paths instead of hardcoding
a cwd-relative `build/` (which broke depending on where a verb was run from)."""
import json
import os
import pathlib

CONFIG_FILE = (pathlib.Path(os.environ.get("XDG_CONFIG_HOME")
                            or pathlib.Path.home() / ".config")
               / "engaged-time" / "config.json")

#: Used when nothing is stored and no env override is set.
DEFAULT_WORK = pathlib.Path.home() / ".claude/engaged-time"

#: Where Claude Code writes session transcripts under a standard install — offered by
#: `init` as the suggested root, never applied as a silent fallback.
CONVENTIONAL_ROOT = pathlib.Path.home() / ".claude/projects"


def _read_config() -> dict:
    """The stored config, or an empty dict when absent or unreadable."""
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (OSError, ValueError):
        return {}


def _write_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")


def resolve_work_dir() -> pathlib.Path:
    """The working dir — env override, then stored, then the default."""
    env = os.environ.get("ENGAGED_TIME_WORK")
    if env:
        return pathlib.Path(env).expanduser()
    stored = _read_config().get("work_dir")
    return pathlib.Path(stored) if stored else DEFAULT_WORK


#: Resolved once at import so argparse defaults across the package agree within a run.
WORK_DIR = resolve_work_dir()


def db(name: str = "raw.db") -> str:
    """Absolute path to a DB in the working dir (raw.db, annotations.db)."""
    return str(WORK_DIR / name)


def diagram(name: str) -> str:
    """Absolute path to a generated artifact under the working dir's diagrams/."""
    return str(WORK_DIR / "diagrams" / name)


def log(name: str = "serve.log") -> str:
    """Absolute path to a log file under the working dir's logs/."""
    return str(WORK_DIR / "logs" / name)


def ensure_work_dirs() -> None:
    """Create the working-dir skeleton.

    `serve` redirects its output into `logs/` from the shell, which fails before
    Python can create anything — so the subdirectories must exist ahead of any verb.
    """
    for sub in ("logs", "diagrams", "scratch"):
        (WORK_DIR / sub).mkdir(parents=True, exist_ok=True)


def stored_root() -> pathlib.Path | None:
    """The transcripts root as configured — env override, then stored. None if unset."""
    env = os.environ.get("ENGAGED_TIME_ROOT")
    if env:
        return pathlib.Path(env).expanduser()
    value = _read_config().get("transcripts_root")
    return pathlib.Path(value) if value else None


def transcripts_root() -> pathlib.Path:
    """The transcripts root, guaranteed to exist. Exits with guidance when it does not.

    Blocks rather than falling back: an unset root means the skill was never
    initialized, and a set-but-absent root usually means retention deleted the
    corpus the analysis depends on. Both are user decisions, not defaults to guess.
    """
    root = stored_root()
    if root is None:
        raise SystemExit(
            "transcripts root is not set — no transcripts to read.\n"
            f"  Set it:  uv run {pathlib.Path(__file__).parent}/raw_db.py init --root PATH\n"
            f"  Omit --root to accept the conventional location ({CONVENTIONAL_ROOT}).\n"
            "  Or set ENGAGED_TIME_ROOT for a one-off override.")
    if not root.is_dir():
        raise SystemExit(
            f"transcripts root does not exist: {root}\n"
            "  Claude Code deletes transcripts older than `cleanupPeriodDays`\n"
            "  (settings.json) — if the corpus was pruned, the history is gone and\n"
            "  cannot be rebuilt. Re-point the root with `raw_db.py init --root PATH`.")
    return root


def set_transcripts_root(path) -> pathlib.Path:
    """Validate and persist the transcripts root. Exits when the path is unusable."""
    root = pathlib.Path(path).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    config = _read_config()
    config["transcripts_root"] = str(root)
    _write_config(config)
    return root


def set_work_dir(path) -> pathlib.Path:
    """Persist the working dir and create its skeleton. Returns the resolved path."""
    work = pathlib.Path(path).expanduser().resolve()
    work.mkdir(parents=True, exist_ok=True)
    config = _read_config()
    config["work_dir"] = str(work)
    _write_config(config)
    for sub in ("logs", "diagrams", "scratch"):
        (work / sub).mkdir(parents=True, exist_ok=True)
    return work


def retention_note() -> str:
    """A warning about Claude Code's transcript retention, read from live settings.

    The corpus is this skill's only source and Claude Code prunes it on a timer, so
    every rollup silently loses its oldest history unless retention is raised.
    """
    settings = pathlib.Path.home() / ".claude/settings.json"
    try:
        days = json.loads(settings.read_text()).get("cleanupPeriodDays")
    except (OSError, ValueError):
        days = None
    if days is None:
        return ("RETENTION: `cleanupPeriodDays` is unset in ~/.claude/settings.json, so\n"
                "  Claude Code prunes transcripts at its default age. This skill reads\n"
                "  those files as its ONLY source — pruned sessions are unrecoverable and\n"
                "  drop out of every rollup. Raise it to cover your analysis window.")
    return (f"RETENTION: `cleanupPeriodDays` is {days:,} — transcripts older than that are\n"
            "  deleted by Claude Code and cannot be recovered. This skill reads those\n"
            "  files as its ONLY source; keep the value at or above your analysis window.")
