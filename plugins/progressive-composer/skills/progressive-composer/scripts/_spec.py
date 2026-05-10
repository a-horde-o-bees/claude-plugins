"""composition.md schema — parse, serialize, scaffold.

Each composed skill carries a composition.md sibling at
`<scope>/.claude/skills/<name>/composition.md` recording the recipe
(sources, pinned commits, goal articulation) and provenance.

Python reads frontmatter for build / refine / drift logic. Both Python
and the agent (via Edit tool) write the file — the agent's edits
target the body; Python's edits target frontmatter fields like
last_build and build_status, plus the sources list (via add-source /
remove-source / update-sources sub-ops).

Stdlib-only YAML subset (rolled inline) — keeps the script runnable
under uniform `uv run -m scripts.<verb>` module-mode invocation without
`--with pyyaml` ceremony.

There is no `type` discriminator. Every composition.md describes a
composition. For users wanting to install an unmodified upstream skill,
Vercel's `npx skills add <repo> --skill <name>` is the recommended
path; this plugin focuses on composition.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


CURRENT_SPEC_VERSION = 1

BUILD_STATUS_DRAFT = "draft"
BUILD_STATUS_BUILT = "built"
VALID_BUILD_STATUSES = (BUILD_STATUS_DRAFT, BUILD_STATUS_BUILT)

VALID_SCOPES = ("user", "project")


@dataclass
class Source:
    url: str
    skill: str
    ref: str
    commit: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "skill": self.skill,
            "ref": self.ref,
            "commit": self.commit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Source:
        return cls(
            url=data["url"],
            skill=data["skill"],
            ref=data["ref"],
            commit=data.get("commit", ""),
        )


@dataclass
class Spec:
    name: str
    scope: str
    sources: list[Source] = field(default_factory=list)
    description: str = ""
    goal_summary: str = ""
    last_build: str | None = None
    build_status: str = BUILD_STATUS_DRAFT
    spec_version: int = CURRENT_SPEC_VERSION
    body: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_version": self.spec_version,
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "sources": [s.to_dict() for s in self.sources],
            "goal_summary": self.goal_summary,
            "last_build": self.last_build,
            "build_status": self.build_status,
        }

    @classmethod
    def from_dict(cls, frontmatter: dict[str, Any], body: str) -> Spec:
        return cls(
            spec_version=frontmatter.get("spec_version", CURRENT_SPEC_VERSION),
            name=frontmatter["name"],
            scope=frontmatter["scope"],
            description=frontmatter.get("description", ""),
            sources=[Source.from_dict(s) for s in frontmatter.get("sources", [])],
            goal_summary=frontmatter.get("goal_summary", ""),
            last_build=frontmatter.get("last_build"),
            build_status=frontmatter.get("build_status", BUILD_STATUS_DRAFT),
            body=body,
        )


COMPOSED_SCAFFOLD_BODY = """\

# Goal

<articulate what this composed skill enables Claude to do, when it should fire, and what the expected output format is — refined through `compose new` and subsequent `compose refine` dialogue>

## Source mapping

<one subsection per `compose add-source` invocation; agent fills as sources are added>

## Design refinements

<accumulated decisions from `compose refine` sessions — appended over time, previous entries preserved unless explicitly superseded>
"""


def make_composed_scaffold(
    name: str,
    scope: str,
    description: str = "",
) -> Spec:
    """Build a draft composed-skill spec with empty sources list and stub body.

    Sources are added incrementally via `compose add-source` after this
    initial scaffold is written.
    """
    if scope not in VALID_SCOPES:
        raise ValueError(f"unknown scope: {scope!r} — expected one of {VALID_SCOPES}")
    return Spec(
        name=name,
        scope=scope,
        description=description,
        body=COMPOSED_SCAFFOLD_BODY,
    )


_QUOTE_TRIGGERS = (":", "#", "\"", "'", "[", "]", "{", "}", ",", "&", "*", "!", "|", ">", "%", "@", "`")


def _yaml_quote(value: str) -> str:
    """Quote a string for safe YAML emission. Empty strings become `""`."""
    if value == "":
        return '""'
    if any(c in value for c in _QUOTE_TRIGGERS) or value != value.strip():
        escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
        return f'"{escaped}"'
    if value in ("null", "true", "false", "yes", "no", "on", "off", "~"):
        return f'"{value}"'
    return value


def _emit_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    return _yaml_quote(str(value))


_SOURCE_FIELD_ORDER = ("url", "skill", "ref", "commit")


def _emit_frontmatter(data: dict[str, Any]) -> str:
    """Serialize the spec dict to a YAML subset preserving insertion order."""
    lines: list[str] = []
    for key, value in data.items():
        if key == "sources":
            sources = value or []
            if not sources:
                lines.append("sources: []")
                continue
            lines.append("sources:")
            for entry in sources:
                first = True
                for field_name in _SOURCE_FIELD_ORDER:
                    if field_name not in entry:
                        continue
                    prefix = "- " if first else "  "
                    lines.append(
                        f"{prefix}{field_name}: {_emit_scalar(entry.get(field_name, ''))}"
                    )
                    first = False
        else:
            lines.append(f"{key}: {_emit_scalar(value)}")
    return "\n".join(lines) + "\n"


def serialize(spec: Spec) -> str:
    """Render a Spec to the markdown + YAML-frontmatter file form."""
    return f"---\n{_emit_frontmatter(spec.to_dict())}---\n{spec.body}"


def _parse_scalar(text: str) -> Any:
    text = text.strip()
    if text == "" or text == "null" or text == "~":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    if (text.startswith('"') and text.endswith('"')) or (
        text.startswith("'") and text.endswith("'")
    ):
        inner = text[1:-1]
        if text[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    try:
        return int(text)
    except ValueError:
        return text


def _parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse the bounded YAML subset our serializer emits."""
    result: dict[str, Any] = {}
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line == "" or line.lstrip().startswith("#"):
            i += 1
            continue

        if line.startswith(" ") or line.startswith("-") or line.startswith("\t"):
            raise ValueError(f"unexpected indented top-level line at {i}: {line!r}")

        if ":" not in line:
            raise ValueError(f"expected 'key: value' or 'key:' at line {i}: {line!r}")

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key == "sources":
            entries: list[dict[str, str]] = []
            if value and value != "[]":
                raise ValueError(
                    f"sources value must be empty (block list to follow) or '[]' at line {i}"
                )
            i += 1
            while i < len(lines):
                inner = lines[i]
                if inner == "":
                    i += 1
                    continue
                if not inner.startswith("- ") and not inner.startswith("  "):
                    break
                if inner.startswith("- "):
                    entry: dict[str, str] = {}
                    sub_key, _, sub_value = inner[2:].partition(":")
                    entry[sub_key.strip()] = _parse_scalar(sub_value)
                    i += 1
                    while i < len(lines) and lines[i].startswith("  ") and not lines[i].startswith("- "):
                        cont = lines[i][2:]
                        if cont.startswith("- "):
                            break
                        c_key, _, c_value = cont.partition(":")
                        entry[c_key.strip()] = _parse_scalar(c_value)
                        i += 1
                    entries.append(entry)
                else:
                    raise ValueError(
                        f"unexpected indented line under sources at line {i}: {inner!r}"
                    )
            result[key] = entries
        else:
            result[key] = _parse_scalar(value)
            i += 1

    return result


def parse(text: str) -> Spec:
    """Parse a composition.md file's text into a Spec."""
    if not text.startswith("---\n"):
        raise ValueError("composition.md must begin with '---' frontmatter delimiter")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("composition.md frontmatter is unterminated (missing closing '---')")

    frontmatter_text = text[4:end]
    body = text[end + 5 :]
    frontmatter = _parse_frontmatter(frontmatter_text)

    if "name" not in frontmatter or "scope" not in frontmatter:
        raise ValueError(
            "composition.md frontmatter must include 'name' and 'scope' fields"
        )

    return Spec.from_dict(frontmatter, body)


def write(path: Path, spec: Spec) -> None:
    """Atomic write — temp sibling then rename. Creates parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(serialize(spec))
    os.replace(tmp, path)


def read(path: Path) -> Spec:
    """Read a composition.md file from disk into a Spec."""
    return parse(path.read_text())


def add_source_to_spec(spec: Spec, source: Source) -> Spec:
    """Append a source to the spec, replacing any prior entry with the same URL+skill."""
    existing_index = None
    for i, s in enumerate(spec.sources):
        if s.url == source.url and s.skill == source.skill:
            existing_index = i
            break
    if existing_index is not None:
        spec.sources[existing_index] = source
    else:
        spec.sources.append(source)
    return spec


def remove_source_from_spec(spec: Spec, url: str, skill: str) -> Spec:
    """Remove the source matching url+skill, if present."""
    spec.sources = [s for s in spec.sources if not (s.url == url and s.skill == skill)]
    return spec
