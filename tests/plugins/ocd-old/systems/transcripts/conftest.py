"""Fixtures for transcripts tests.

Per-test isolation: CLAUDE_PROJECT_DIR points at a tmp project root, and
CLAUDE_HOME redirects ~/.claude/projects/ access into a tmp directory so
sync() never reads the developer's real Claude Code transcripts.

Provides DB/connection fixtures plus a synthetic-JSONL helper so tests can
seed transcripts without depending on real session files.
"""

import json
from pathlib import Path

import pytest

from systems.transcripts import _db


@pytest.fixture(autouse=True)
def project_dir(tmp_path, monkeypatch) -> Path:
    """Project root with CLAUDE_PROJECT_DIR set; isolates per-test."""
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(project))
    return project


@pytest.fixture(autouse=True)
def claude_home(tmp_path, monkeypatch) -> Path:
    """Redirect ~/.claude to tmp_path/.claude/ so sync stays out of real data."""
    home = tmp_path / ".claude"
    (home / "projects").mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CLAUDE_HOME", str(home))
    return home


@pytest.fixture
def db_path(tmp_path) -> str:
    """Path to a freshly-initialized DB outside the project root."""
    path = str(tmp_path / "test.db")
    _db.init_db(path)
    return path


@pytest.fixture
def conn(db_path):
    """Open SQLite connection against the initialized schema."""
    connection = _db.get_connection(db_path)
    try:
        yield connection
    finally:
        connection.close()


def write_jsonl(path: Path, events: list[dict]) -> None:
    """Write a list of event dicts as JSONL at the given path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")


def make_event(
    type_: str,
    ts: str,
    *,
    uuid: str = "",
    label_extras: dict | None = None,
) -> dict:
    """Build a minimal event dict for synthetic JSONL.

    Caller passes additional fields (message, toolUseResult, subtype, etc.)
    via label_extras to drive the desired event_label() output.
    """
    e: dict = {
        "type": type_,
        "timestamp": ts,
        "uuid": uuid or f"u-{ts}",
    }
    if label_extras:
        e.update(label_extras)
    return e


def make_user_msg(ts: str, text: str = "hi", *, uuid: str = "") -> dict:
    """Synthesize a top-level user_msg event."""
    return make_event(
        "user", ts, uuid=uuid,
        label_extras={"message": {"role": "user", "content": text}},
    )


def make_assistant_text(ts: str, text: str = "ok", *, uuid: str = "") -> dict:
    """Synthesize an assistant text-content event."""
    return make_event(
        "assistant", ts, uuid=uuid,
        label_extras={
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": text}],
            },
        },
    )


@pytest.fixture
def seeded_project(claude_home):
    """Factory that seeds a project's JSONL transcripts under claude_home.

    Returns a callable: seeded_project(name, sessions) writes
    `claude_home/projects/<name>/<session>.jsonl` for each (session, events)
    in sessions.
    """
    def _seed(project_name: str, sessions: dict[str, list[dict]]) -> Path:
        project_path = claude_home / "projects" / project_name
        project_path.mkdir(parents=True, exist_ok=True)
        for session_id, events in sessions.items():
            write_jsonl(project_path / f"{session_id}.jsonl", events)
        return project_path
    return _seed
