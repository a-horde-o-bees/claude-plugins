"""Environment resolution for the transcripts skill.

Resolves Claude home (where session JSONL transcripts live at
`~/.claude/projects/`, and where the transcripts DB lives at
`~/.claude/transcripts.db`). The `CLAUDE_HOME` env var overrides the
default so callers running against a non-default Claude home can still
drive the skill.

There is no project-directory resolution here — the skill no longer
derives "the current project" from cwd/env/git. All per-project verbs
take an explicit `--project` argument; the `projects` verb lists
available names.
"""

import os
from pathlib import Path


def get_claude_home() -> Path:
    """Resolve ~/.claude (override via CLAUDE_HOME env var)."""
    env = os.environ.get("CLAUDE_HOME")
    if env:
        return Path(env).resolve()
    return (Path.home() / ".claude").resolve()
