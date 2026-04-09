"""Business logic for the stash MCP server.

Reads and writes markdown-backed stash files that hold ideas, future
work, and unaddressed observations. The server module (``stash.py``)
is a thin presentation layer that dispatches to functions here.

Two storage locations:

- Project stash — ``<project_root>/.claude/stash/stash.md`` for
  entries belonging to the current project
- User stash — ``~/.claude/stash/stash.md`` for cross-project ideas
  and observations not tied to a particular codebase; entries live
  under the ``## Unattached`` heading

Entry formats:

    - **[Title]** — summary
    - **[Title]** — summary → [detail](filename.md)

Companion detail files sit alongside the stash.md file that references
them and are named ``{slug}.md`` where slug is a kebab-case derivation
of the entry title.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

# --- Constants ---

STASH_FILENAME = "stash.md"
PROJECT_STASH_RELATIVE = Path(".claude") / "stash"


def _user_stash_dir() -> Path:
    """Return the user-level stash directory.

    Honors the ``OCD_STASH_USER_DIR`` environment variable so tests
    (and alternate installations) can redirect user-level writes away
    from the real ``~/.claude/stash`` location.
    """
    override = os.environ.get("OCD_STASH_USER_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".claude" / "stash"

UNATTACHED_HEADING = "## Unattached"

PROJECT_HEADER = "# Stash\n"
PROJECT_PREAMBLE = (
    "\n"
    "Ideas, future work, and unaddressed observations for this project. "
    "A holding area between noticing and doing — entries come in fast, "
    "move out when addressed. Managed by the stash MCP server.\n"
    "\n"
)

USER_HEADER = "# Stash\n"
USER_PREAMBLE = (
    "\n"
    "Ideas, future work, and unaddressed observations not tied to a "
    "specific project. Cross-project items live here under the "
    "`## Unattached` heading. Managed by the stash MCP server.\n"
    "\n"
)

_ENTRY_RE = re.compile(
    r"^-\s+\*\*\[(?P<title>[^\]]+)\]\*\*\s+—\s+(?P<summary>.+?)"
    r"(?:\s+→\s+\[detail\]\((?P<detail>[^)]+)\))?\s*$"
)

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


# --- Data classes ---


@dataclass
class StashEntry:
    """One entry in a stash file."""

    title: str
    summary: str
    detail_file: str | None = None  # filename only, sibling of stash.md

    def to_line(self) -> str:
        if self.detail_file:
            return (
                f"- **[{self.title}]** — {self.summary} → "
                f"[detail]({self.detail_file})"
            )
        return f"- **[{self.title}]** — {self.summary}"


@dataclass
class StashSection:
    """A ``## `` heading and its entries.

    A section with an empty ``heading`` represents entries that sit
    directly under the file's top-level title with no sub-heading.
    """

    heading: str
    entries: list[StashEntry] = field(default_factory=list)


# --- Path resolution ---


def project_stash_path(project_root: Path) -> Path:
    return project_root / PROJECT_STASH_RELATIVE / STASH_FILENAME


def user_stash_path() -> Path:
    return _user_stash_dir() / STASH_FILENAME


# --- Slug ---


def slugify(title: str) -> str:
    slug = _SLUG_STRIP.sub("-", title.lower()).strip("-")
    return slug or "entry"


# --- Parsing ---


def _parse(text: str) -> tuple[list[str], list[StashSection]]:
    """Split stash text into (preamble_lines, sections).

    Preamble is everything up to the first ``## `` heading or first
    entry bullet — the top-level title and its descriptive paragraph.
    Sections follow, each with their heading and zero or more entries.
    Unparseable lines inside sections are dropped so re-serialization
    is deterministic.
    """
    lines = text.splitlines()
    preamble: list[str] = []
    sections: list[StashSection] = []
    current = StashSection(heading="")
    seen_content = False

    for line in lines:
        stripped = line.rstrip()
        is_heading = stripped.startswith("## ")
        is_entry = stripped.startswith("- **[")

        if not seen_content and not is_heading and not is_entry:
            preamble.append(line)
            continue

        seen_content = True

        if is_heading:
            # Start a new section. Attach the current section only if
            # it has content or is the top implicit section with entries.
            if current.heading or current.entries:
                sections.append(current)
            current = StashSection(heading=stripped)
            continue

        if is_entry:
            match = _ENTRY_RE.match(stripped)
            if match:
                current.entries.append(
                    StashEntry(
                        title=match.group("title").strip(),
                        summary=match.group("summary").strip(),
                        detail_file=(match.group("detail") or None),
                    )
                )
            continue
        # Other lines within the section body are dropped intentionally.

    # Flush the final section.
    if current.heading or current.entries:
        sections.append(current)

    return preamble, sections


def _render(
    preamble: list[str],
    sections: list[StashSection],
    default_header: str,
    default_preamble: str,
) -> str:
    parts: list[str] = []
    if preamble:
        parts.append("\n".join(preamble).rstrip())
    else:
        parts.append(default_header.rstrip())
        parts.append(default_preamble.rstrip())
    parts.append("")

    for i, section in enumerate(sections):
        if section.heading:
            parts.append(section.heading)
            parts.append("")
        for entry in section.entries:
            parts.append(entry.to_line())
        if i < len(sections) - 1:
            parts.append("")

    text = "\n".join(parts).rstrip() + "\n"
    return text


def _read(path: Path) -> tuple[list[str], list[StashSection]]:
    if not path.exists():
        return [], []
    return _parse(path.read_text(encoding="utf-8"))


def _write(
    path: Path,
    preamble: list[str],
    sections: list[StashSection],
    default_header: str,
    default_preamble: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _render(preamble, sections, default_header, default_preamble),
        encoding="utf-8",
    )


# --- Section helpers ---


def _find_section(sections: list[StashSection], heading: str) -> StashSection | None:
    for section in sections:
        if section.heading == heading:
            return section
    return None


def _ensure_section(
    sections: list[StashSection],
    heading: str,
    *,
    append: bool = True,
) -> StashSection:
    section = _find_section(sections, heading)
    if section is None:
        section = StashSection(heading=heading)
        if append:
            sections.append(section)
        else:
            sections.insert(0, section)
    return section


# --- Detail file helpers ---


def _unique_detail_file(base_dir: Path, title: str) -> str:
    """Filename for a new detail file that does not collide."""
    base = slugify(title)
    candidate = f"{base}.md"
    n = 2
    while (base_dir / candidate).exists():
        candidate = f"{base}-{n}.md"
        n += 1
    return candidate


def _normalize_detail_body(title: str, body: str) -> str:
    body = body.strip()
    if body.startswith("# "):
        return body + "\n"
    return f"# {title}\n\n{body}\n"


# --- Public operations ---


def add(
    project_root: Path,
    *,
    title: str,
    summary: str,
    detail: str | None = None,
    unattached: bool = False,
) -> dict:
    """Add an entry to the project stash or user stash."""
    title = title.strip()
    summary = summary.strip()
    if not title:
        raise ValueError("title is required")
    if not summary:
        raise ValueError("summary is required")

    if unattached:
        path = user_stash_path()
        header, file_preamble = USER_HEADER, USER_PREAMBLE
        target_heading = UNATTACHED_HEADING
    else:
        path = project_stash_path(project_root)
        header, file_preamble = PROJECT_HEADER, PROJECT_PREAMBLE
        target_heading = ""

    preamble, sections = _read(path)
    section = _ensure_section(sections, target_heading)

    for existing in section.entries:
        if existing.title == title:
            raise ValueError(
                f"entry already exists in {path}: {title}. "
                "Remove the existing entry first or choose a different title."
            )

    detail_file: str | None = None
    detail_path: Path | None = None
    if detail and detail.strip():
        detail_file = _unique_detail_file(path.parent, title)
        detail_path = path.parent / detail_file
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        detail_path.write_text(
            _normalize_detail_body(title, detail), encoding="utf-8"
        )

    entry = StashEntry(title=title, summary=summary, detail_file=detail_file)
    section.entries.append(entry)

    _write(path, preamble, sections, header, file_preamble)

    return {
        "action": "added",
        "scope": "user" if unattached else "project",
        "section": target_heading or "(top)",
        "stash_file": str(path),
        "detail_file": str(detail_path) if detail_path else None,
        "entry": {
            "title": title,
            "summary": summary,
            "detail_file": detail_file,
        },
    }


def _section_to_dict(section: StashSection, base_dir: Path) -> dict:
    out = {"heading": section.heading or None, "entries": []}
    for entry in section.entries:
        item: dict = {"title": entry.title, "summary": entry.summary}
        if entry.detail_file:
            item["detail_file"] = entry.detail_file
            detail_path = base_dir / entry.detail_file
            if detail_path.exists():
                item["detail_content"] = detail_path.read_text(encoding="utf-8")
            else:
                item["detail_missing"] = True
        out["entries"].append(item)
    return out


def _review_one(path: Path, scope_label: str) -> dict:
    if not path.exists():
        return {
            "scope": scope_label,
            "stash_file": str(path),
            "exists": False,
            "sections": [],
            "total": 0,
        }
    _, sections = _read(path)
    sections = [s for s in sections if s.heading or s.entries]
    total = sum(len(s.entries) for s in sections)
    return {
        "scope": scope_label,
        "stash_file": str(path),
        "exists": True,
        "sections": [_section_to_dict(s, path.parent) for s in sections],
        "total": total,
    }


def review(project_root: Path, *, scope: str = "project") -> dict:
    scope = (scope or "project").lower()
    if scope not in {"project", "user", "all"}:
        raise ValueError(
            f"invalid scope: {scope}. Use one of: project, user, all."
        )

    results: list[dict] = []
    if scope in {"project", "all"}:
        results.append(_review_one(project_stash_path(project_root), "project"))
    if scope in {"user", "all"}:
        results.append(_review_one(user_stash_path(), "user"))

    return {"scope": scope, "results": results}


def _remove_from(
    path: Path,
    title: str,
    scope_label: str,
    header: str,
    preamble_default: str,
) -> dict | None:
    if not path.exists():
        return None
    preamble, sections = _read(path)
    for section in sections:
        for i, entry in enumerate(section.entries):
            if entry.title == title:
                removed = section.entries.pop(i)
                detail_deleted: str | None = None
                if removed.detail_file:
                    detail_path = path.parent / removed.detail_file
                    if detail_path.exists():
                        detail_path.unlink()
                        detail_deleted = str(detail_path)
                _write(path, preamble, sections, header, preamble_default)
                return {
                    "action": "removed",
                    "scope": scope_label,
                    "stash_file": str(path),
                    "detail_deleted": detail_deleted,
                    "entry": {
                        "title": removed.title,
                        "summary": removed.summary,
                    },
                }
    return None


def remove(
    project_root: Path, *, title: str, scope: str = "project"
) -> dict:
    title = title.strip()
    if not title:
        raise ValueError("title is required")
    scope = (scope or "project").lower()
    if scope not in {"project", "user", "all"}:
        raise ValueError(
            f"invalid scope: {scope}. Use one of: project, user, all."
        )

    if scope in {"project", "all"}:
        result = _remove_from(
            project_stash_path(project_root),
            title,
            "project",
            PROJECT_HEADER,
            PROJECT_PREAMBLE,
        )
        if result is not None:
            return result
    if scope in {"user", "all"}:
        result = _remove_from(
            user_stash_path(),
            title,
            "user",
            USER_HEADER,
            USER_PREAMBLE,
        )
        if result is not None:
            return result

    return {"action": "not_found", "scope": scope, "title": title}


def promote(project_root: Path, *, title: str) -> dict:
    """Move an entry from the user stash into the current project stash."""
    title = title.strip()
    if not title:
        raise ValueError("title is required")

    user_path = user_stash_path()
    if not user_path.exists():
        return {"action": "not_found", "scope": "user", "title": title}

    user_preamble, user_sections = _read(user_path)
    found: tuple[StashSection, int, StashEntry] | None = None
    for section in user_sections:
        for i, entry in enumerate(section.entries):
            if entry.title == title:
                found = (section, i, entry)
                break
        if found:
            break
    if not found:
        return {"action": "not_found", "scope": "user", "title": title}

    section, idx, entry = found

    project_path = project_stash_path(project_root)
    project_preamble, project_sections = _read(project_path)
    top = _ensure_section(project_sections, "", append=False)

    for existing in top.entries:
        if existing.title == title:
            raise ValueError(
                f"entry already exists in project stash: {title}. "
                "Remove the project-side entry first."
            )

    # Move companion detail file if present.
    if entry.detail_file:
        src = user_path.parent / entry.detail_file
        dst_dir = project_path.parent
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst_name = entry.detail_file
        # Avoid collision on the project side.
        if (dst_dir / dst_name).exists():
            dst_name = _unique_detail_file(dst_dir, entry.title)
            entry.detail_file = dst_name
        if src.exists():
            (dst_dir / dst_name).write_text(
                src.read_text(encoding="utf-8"), encoding="utf-8"
            )
            src.unlink()

    section.entries.pop(idx)
    top.entries.append(entry)

    _write(user_path, user_preamble, user_sections, USER_HEADER, USER_PREAMBLE)
    _write(
        project_path,
        project_preamble,
        project_sections,
        PROJECT_HEADER,
        PROJECT_PREAMBLE,
    )

    return {
        "action": "promoted",
        "from_stash_file": str(user_path),
        "to_stash_file": str(project_path),
        "entry": {
            "title": entry.title,
            "summary": entry.summary,
            "detail_file": entry.detail_file,
        },
    }
