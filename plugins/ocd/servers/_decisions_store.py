"""Business logic for the decisions MCP server.

Reads and writes the project-root decisions.md index and decisions/*.md
detail files in their existing markdown format. The server module
(decisions.py) is a thin presentation layer that dispatches to functions
here.

File layout this module maintains:

    <project_root>/decisions.md           — index, one entry per line
    <project_root>/decisions/<slug>.md    — optional detail files

Index entry forms:

    - **[Title]** — summary
    - **[Title]** — summary → [detail](decisions/<slug>.md)

Detail files use the Context/Options Considered/Decision/Consequences
section structure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# --- Constants ---

INDEX_HEADER = "# Decisions\n"
DEFAULT_PREAMBLE = (
    "\n"
    "Non-obvious choices with alternatives considered. Prevents backtracking. "
    "Record when the reasoning is not derivable from code or conventions — "
    "if an agent arriving fresh would need to re-evaluate from scratch, "
    "record it. Detail files in `decisions/` hold full context; entries here "
    "are the scannable index.\n"
    "\n"
)

# Two accepted index entry forms:
#
#   1. "- **[Title](decisions/slug.md)** — summary"   (bracketed-link form)
#   2. "- **[Title]** — summary"                      (plain form)
#   3. "- **[Title]** — summary → [detail](decisions/slug.md)"  (trailing-link form)
#
# Form 1 is the real format used in this repository; forms 2 and 3 are the
# forms named in the original rule file. Parser accepts all three and the
# renderer emits form 1 when a detail path exists, form 2 otherwise — this
# keeps round-tripping stable for existing entries.
_ENTRY_RE = re.compile(
    r"^-\s+\*\*\["
    r"(?P<title>[^\]]+)"
    r"\](?:\((?P<detail_inline>[^)]+)\))?"
    r"\*\*\s+—\s+"
    r"(?P<summary>.+?)"
    r"(?:\s+→\s+\[detail\]\((?P<detail_trailing>[^)]+)\))?"
    r"\s*$"
)


# --- Data classes ---


@dataclass
class DecisionEntry:
    """One line in the decisions.md index."""

    title: str
    summary: str
    detail_path: str | None  # relative to project root (e.g. "decisions/foo.md")

    def to_line(self) -> str:
        if self.detail_path:
            return f"- **[{self.title}]({self.detail_path})** — {self.summary}"
        return f"- **[{self.title}]** — {self.summary}"


@dataclass
class DecisionDetail:
    """Contents of a detail file."""

    context: str | None
    options: str | None
    decision: str | None
    consequences: str | None

    def is_empty(self) -> bool:
        return not any([self.context, self.options, self.decision, self.consequences])


# --- Helpers ---


def _index_path(project_root: Path) -> Path:
    return project_root / "decisions.md"


def _detail_dir(project_root: Path) -> Path:
    return project_root / "decisions"


def slugify(title: str) -> str:
    """Convert a title to a filesystem-safe slug.

    Lowercase, alphanumeric and hyphens only; collapses runs of non-word chars
    into single hyphens.
    """
    slug = title.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug or "decision"


def _unique_detail_path(project_root: Path, title: str) -> str:
    """Generate a non-colliding detail file path relative to project root."""
    base = slugify(title)
    detail_dir = _detail_dir(project_root)
    candidate = f"decisions/{base}.md"
    n = 2
    while (project_root / candidate).exists():
        candidate = f"decisions/{base}-{n}.md"
        n += 1
    return candidate


def _parse_index(text: str) -> tuple[list[str], list[DecisionEntry]]:
    """Split index text into (preamble_lines, entries).

    Preamble is everything up to the first bullet entry, including the header
    and blank lines. Entries preserve insertion order.
    """
    lines = text.splitlines()
    preamble: list[str] = []
    entries: list[DecisionEntry] = []
    entry_started = False

    for line in lines:
        if not entry_started and not line.lstrip().startswith("- **["):
            preamble.append(line)
            continue
        entry_started = True
        match = _ENTRY_RE.match(line)
        if match:
            detail = match.group("detail_inline") or match.group("detail_trailing")
            entries.append(
                DecisionEntry(
                    title=match.group("title").strip(),
                    summary=match.group("summary").strip(),
                    detail_path=(detail or None),
                )
            )
        # Unparseable lines inside the entry region are dropped — they do not
        # fit the known format and re-serialization would silently change them.

    return preamble, entries


def _render_index(preamble: list[str], entries: list[DecisionEntry]) -> str:
    parts: list[str] = []
    if preamble:
        parts.append("\n".join(preamble))
        # Ensure a blank line separates preamble from entries
        if parts[-1] and not parts[-1].endswith("\n"):
            parts.append("")
    else:
        parts.append(INDEX_HEADER.rstrip())
        parts.append(DEFAULT_PREAMBLE.rstrip())
        parts.append("")

    for entry in entries:
        parts.append(entry.to_line())

    text = "\n".join(parts).rstrip() + "\n"
    return text


def _read_index(project_root: Path) -> tuple[list[str], list[DecisionEntry]]:
    path = _index_path(project_root)
    if not path.exists():
        return [], []
    return _parse_index(path.read_text())


def _write_index(
    project_root: Path, preamble: list[str], entries: list[DecisionEntry]
) -> None:
    path = _index_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_index(preamble, entries))


def _render_detail(title: str, detail: DecisionDetail) -> str:
    parts: list[str] = [f"# {title}", ""]
    if detail.context:
        parts.extend(["## Context", "", detail.context.strip(), ""])
    if detail.options:
        parts.extend(["## Options Considered", "", detail.options.strip(), ""])
    if detail.decision:
        parts.extend(["## Decision", "", detail.decision.strip(), ""])
    if detail.consequences:
        parts.extend(["## Consequences", "", detail.consequences.strip(), ""])
    return "\n".join(parts).rstrip() + "\n"


def _parse_detail(text: str) -> DecisionDetail:
    """Parse a detail file into its four canonical sections.

    Sections outside the canonical four are preserved only insofar as they
    fall inside one of the recognized headings; unrecognized headings are
    ignored by the parser but remain in the file on read-only operations.
    """
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip().lower()
            if heading == "context":
                current = "context"
            elif heading in ("options considered", "options"):
                current = "options"
            elif heading == "decision":
                current = "decision"
            elif heading == "consequences":
                current = "consequences"
            else:
                current = None
            if current:
                sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)

    def _joined(key: str) -> str | None:
        if key not in sections:
            return None
        value = "\n".join(sections[key]).strip()
        return value or None

    return DecisionDetail(
        context=_joined("context"),
        options=_joined("options"),
        decision=_joined("decision"),
        consequences=_joined("consequences"),
    )


def _read_detail(project_root: Path, detail_path: str) -> tuple[str, DecisionDetail] | None:
    """Read a detail file. Returns (raw_text, parsed) or None if missing."""
    full = project_root / detail_path
    if not full.exists():
        return None
    raw = full.read_text()
    return raw, _parse_detail(raw)


# --- Resolution ---


def _resolve(entries: list[DecisionEntry], identifier: str | int) -> int | None:
    """Resolve title-or-index to a list index. Returns None if not found.

    Integer identifier: 1-based index. String identifier: case-insensitive
    title match.
    """
    if isinstance(identifier, int):
        if 1 <= identifier <= len(entries):
            return identifier - 1
        return None
    # String — try as int first (agents may pass stringy numbers)
    try:
        as_int = int(identifier)
        if 1 <= as_int <= len(entries):
            return as_int - 1
    except (TypeError, ValueError):
        pass
    lowered = identifier.strip().lower()
    for i, entry in enumerate(entries):
        if entry.title.lower() == lowered:
            return i
    return None


# --- Public operations ---


def record(
    project_root: Path,
    title: str,
    summary: str,
    context: str | None = None,
    options: str | None = None,
    decision: str | None = None,
    consequences: str | None = None,
) -> dict:
    """Record a new decision. Creates a detail file when any detail field is set."""
    title = title.strip()
    summary = summary.strip()
    if not title:
        raise ValueError("title is required")
    if not summary:
        raise ValueError("summary is required")

    preamble, entries = _read_index(project_root)

    # Duplicate title check (case-insensitive)
    for existing in entries:
        if existing.title.lower() == title.lower():
            raise ValueError(
                f"Decision with title '{existing.title}' already exists; "
                f"use decisions_update to revise or choose a distinct title"
            )

    detail = DecisionDetail(
        context=context, options=options, decision=decision, consequences=consequences
    )
    detail_path: str | None = None
    if not detail.is_empty():
        detail_path = _unique_detail_path(project_root, title)
        full = project_root / detail_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(_render_detail(title, detail))

    new_entry = DecisionEntry(title=title, summary=summary, detail_path=detail_path)
    entries.append(new_entry)
    _write_index(project_root, preamble, entries)

    return {
        "action": "recorded",
        "index": len(entries),
        "title": title,
        "summary": summary,
        "detail_path": detail_path,
    }


def list_decisions(project_root: Path) -> dict:
    """Return decisions in insertion order."""
    _, entries = _read_index(project_root)
    return {
        "count": len(entries),
        "decisions": [
            {
                "index": i + 1,
                "title": e.title,
                "summary": e.summary,
                "detail_path": e.detail_path,
            }
            for i, e in enumerate(entries)
        ],
    }


def get(project_root: Path, identifier: str | int) -> dict:
    """Return full decision content for one entry, including detail file if present."""
    _, entries = _read_index(project_root)
    idx = _resolve(entries, identifier)
    if idx is None:
        raise ValueError(
            f"No decision matches '{identifier}'; call decisions_list to see available entries"
        )
    entry = entries[idx]
    result: dict = {
        "index": idx + 1,
        "title": entry.title,
        "summary": entry.summary,
        "detail_path": entry.detail_path,
        "detail": None,
    }
    if entry.detail_path:
        read = _read_detail(project_root, entry.detail_path)
        if read is None:
            result["detail_missing"] = True
        else:
            raw, parsed = read
            result["detail"] = {
                "context": parsed.context,
                "options": parsed.options,
                "decision": parsed.decision,
                "consequences": parsed.consequences,
                "raw": raw,
            }
    return result


def update(
    project_root: Path,
    identifier: str | int,
    title: str | None = None,
    summary: str | None = None,
    context: str | None = None,
    options: str | None = None,
    decision: str | None = None,
    consequences: str | None = None,
) -> dict:
    """Update an existing decision. Any supplied field replaces the prior value.

    If detail fields are supplied and no detail file exists, one is created.
    Unspecified fields are left unchanged.
    """
    preamble, entries = _read_index(project_root)
    idx = _resolve(entries, identifier)
    if idx is None:
        raise ValueError(
            f"No decision matches '{identifier}'; call decisions_list to see available entries"
        )
    entry = entries[idx]

    old_detail_path = entry.detail_path
    new_title = (title.strip() if title else entry.title)
    new_summary = (summary.strip() if summary else entry.summary)

    if title and new_title.lower() != entry.title.lower():
        for i, other in enumerate(entries):
            if i != idx and other.title.lower() == new_title.lower():
                raise ValueError(
                    f"Decision with title '{other.title}' already exists"
                )

    # Load existing detail, if any, so partial updates merge into it
    existing_detail = DecisionDetail(None, None, None, None)
    if old_detail_path:
        read = _read_detail(project_root, old_detail_path)
        if read is not None:
            _, existing_detail = read

    merged_detail = DecisionDetail(
        context=context if context is not None else existing_detail.context,
        options=options if options is not None else existing_detail.options,
        decision=decision if decision is not None else existing_detail.decision,
        consequences=(
            consequences if consequences is not None else existing_detail.consequences
        ),
    )

    new_detail_path = old_detail_path

    # Handle title rename: move the detail file to match the new slug if the
    # old slug was derived from the old title.
    if old_detail_path and title and new_title != entry.title:
        old_slug = Path(old_detail_path).stem
        if old_slug == slugify(entry.title):
            proposed = _unique_detail_path(project_root, new_title)
            (project_root / old_detail_path).rename(project_root / proposed)
            new_detail_path = proposed

    if not merged_detail.is_empty():
        if new_detail_path is None:
            new_detail_path = _unique_detail_path(project_root, new_title)
        full = project_root / new_detail_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(_render_detail(new_title, merged_detail))

    entries[idx] = DecisionEntry(
        title=new_title, summary=new_summary, detail_path=new_detail_path
    )
    _write_index(project_root, preamble, entries)

    return {
        "action": "updated",
        "index": idx + 1,
        "title": new_title,
        "summary": new_summary,
        "detail_path": new_detail_path,
    }


def remove(project_root: Path, identifier: str | int) -> dict:
    """Remove a decision entry and its detail file, if present."""
    preamble, entries = _read_index(project_root)
    idx = _resolve(entries, identifier)
    if idx is None:
        raise ValueError(
            f"No decision matches '{identifier}'; call decisions_list to see available entries"
        )
    removed = entries.pop(idx)
    detail_removed = False
    if removed.detail_path:
        full = project_root / removed.detail_path
        if full.exists():
            full.unlink()
            detail_removed = True
    _write_index(project_root, preamble, entries)
    return {
        "action": "removed",
        "title": removed.title,
        "detail_removed": detail_removed,
    }
