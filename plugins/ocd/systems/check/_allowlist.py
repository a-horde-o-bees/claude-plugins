"""Per-rule path allowlist for the check system.

Reads `allowlist.csv` from the system folder and provides a predicate
for filtering violations by `(rule, path)`. Row schema:

    rule     — exact-match against `Violation.rule` / `PyViolation.rule`,
               or `*` to match any rule (cross-dimension suppression)
    pattern  — fnmatch glob matched against the path's posix string
    reason   — prose explanation surfaced in `--verbose` output

Patterns match the path's full posix form (typically project-
relative when the scanner is invoked from the project root). fnmatch
`*` matches any character including `/`, so `*conftest.py` matches any
conftest file anywhere in the tree. Users wanting tighter matches can
anchor patterns to earlier path segments (e.g. `plugins/*/run.py`).

The `*` rule is for files whose content is inherently exempt across
every check dimension — scanner test fixtures (`fixture_*.*`) are the
canonical example: they exist to contain the anti-patterns the checks
detect, so flagging them would mean the check works against its own
tests.

This loader is intentionally I/O-only — it does not look up its own
CSV path via `__file__`. The caller supplies the path; that keeps
this module non-self-anchoring and reusable.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path


@dataclass(frozen=True)
class AllowlistEntry:
    rule: str
    pattern: str
    reason: str


def load_allowlist(csv_path: Path) -> list[AllowlistEntry]:
    """Parse the allowlist CSV into entries.

    Missing file returns an empty list — no allowlist, no suppression.
    Rows missing `rule` or `pattern` are skipped; `reason` is optional
    but encouraged.
    """
    if not csv_path.is_file():
        return []
    entries: list[AllowlistEntry] = []
    with csv_path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule = (row.get("rule") or "").strip()
            pattern = (row.get("pattern") or "").strip()
            reason = (row.get("reason") or "").strip()
            if not rule or not pattern:
                continue
            entries.append(
                AllowlistEntry(rule=rule, pattern=pattern, reason=reason)
            )
    return entries


def is_allowed(
    entries: list[AllowlistEntry],
    rule: str,
    path: Path,
    project_root: Path | None = None,
) -> bool:
    """Return True when (rule, path) matches any entry in the allowlist.

    `path` is rendered as a posix string relative to `project_root`
    when supplied and the path lies under it; otherwise matched as
    absolute posix. Patterns typically assume project-relative form.
    """
    if not entries:
        return False
    rel: str
    if project_root is not None:
        try:
            rel = path.resolve().relative_to(project_root.resolve()).as_posix()
        except ValueError:
            rel = path.as_posix()
    else:
        rel = path.as_posix()
    for entry in entries:
        if entry.rule != "*" and entry.rule != rule:
            continue
        if fnmatch(rel, entry.pattern):
            return True
    return False


def filter_allowed(
    violations: list,
    entries: list[AllowlistEntry],
    project_root: Path | None = None,
) -> tuple[list, list]:
    """Partition violations into (kept, suppressed) using the allowlist.

    Works with any violation object exposing `rule` and `path` attributes.
    """
    kept: list = []
    suppressed: list = []
    for v in violations:
        if is_allowed(entries, v.rule, v.path, project_root):
            suppressed.append(v)
        else:
            kept.append(v)
    return kept, suppressed
