"""Generic JSON file helpers — kept for any future per-skill or per-plugin
state outside of composition.md.

Under the redesigned model, no top-level registries (sources.json,
installed.json) exist. composition.md is the per-skill provenance
record; walking `<scope>/.claude/skills/*/composition.md` enumerates
everything the plugin owns.

These helpers stay because they're tiny and may be needed by future
verbs that want a small JSON state file (e.g., in plugin data dir).
"""

import json
import os
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    """Read a JSON file; return empty dict when the file is absent."""
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save(path: Path, data: dict[str, Any]) -> None:
    """Atomic write — temp sibling then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)
