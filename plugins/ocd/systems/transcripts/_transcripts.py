"""Transcript operations for Claude Code session management.

Extracts user/assistant chat from top-level ~/.claude/projects/<project>/*.jsonl
transcripts, filtering out tool results, tool-use blocks, thinking, and empty
messages. Spawned-agent transcripts in subdirectories are not touched.

Extract is written beside each source as `<stem>_chat.json`:

    {
      "githash": "<git-compatible blob sha1 of source>",
      "messages": [
        {"type": "user", "timestamp": "...", "message": "..."},
        {"type": "assistant", "timestamp": "...", "message": "..."},
        ...
      ]
    }

Re-run behavior: if the sibling `_chat.json` already has a githash matching
the current source, the file is skipped (idempotent).
"""

import hashlib
import json
from pathlib import Path

from tools import environment


def _user_dir() -> Path:
    """Return the Claude Code user transcripts root (~/.claude/projects/)."""
    return environment.get_claude_home() / "projects"


def _path_encode(project_dir: Path) -> str:
    """Encode a project directory the way Claude Code does for ~/.claude/projects/."""
    path_str = str(project_dir.resolve())
    return path_str.replace(":", "-").replace("\\", "-").replace("/", "-").replace(" ", "-")


def _project_path(name: str) -> Path | None:
    """Resolve a project folder name to its absolute path.

    Returns None if the named project directory does not exist.
    """
    project_dir = _user_dir() / name
    return project_dir if project_dir.is_dir() else None


def _git_blob_hash(path: Path) -> str:
    """Compute git-compatible blob SHA1 for a file's content.

    Matches `git hash-object <file>` output, enabling interop with git tooling
    and portable change detection without requiring a git repo.
    """
    content = path.read_bytes()
    header = f"blob {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def _extract_message_text(content) -> str:
    """Extract display text from a message content value (string or list of parts)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_parts.append(part.get("text", ""))
            elif isinstance(part, str):
                text_parts.append(part)
        return "\n".join(text_parts)
    return ""


def _chat_extract(transcript_path: Path) -> list[dict]:
    """Extract chat messages from a transcript .jsonl file.

    Keeps user prompts and assistant responses. Skips tool results
    (user type with toolUseResult key), tool-use blocks, thinking,
    and empty messages.

    Returns a list of {type, timestamp, message} dicts in file order.
    """
    messages = []
    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("type") == "user" and "toolUseResult" in entry:
                continue

            if entry.get("type") not in ("user", "assistant") or "uuid" not in entry:
                continue

            message_text = _extract_message_text(
                entry.get("message", {}).get("content", "")
            )
            if not message_text.strip():
                continue

            messages.append({
                "type": entry["type"],
                "timestamp": entry.get("timestamp", ""),
                "message": message_text,
            })

    return messages


def _existing_githash(json_path: Path) -> str | None:
    """Return the `githash` field from an existing extracted JSON file, if readable."""
    if not json_path.exists():
        return None
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if isinstance(data, dict):
        return data.get("githash")
    return None


def _transcript_export(src: Path) -> bool:
    """Extract one transcript .jsonl and write `<stem>_chat.json` beside it.

    Returns True if written, False if skipped as unchanged.
    """
    dest = src.with_name(f"{src.stem}_chat.json")
    current_hash = _git_blob_hash(src)
    if _existing_githash(dest) == current_hash:
        return False

    envelope = {
        "githash": current_hash,
        "messages": _chat_extract(src),
    }
    dest.write_text(json.dumps(envelope, indent=2), encoding="utf-8")
    return True


def project_list() -> list[str]:
    """Return encoded folder names of all projects in ~/.claude/projects/.

    Names are Claude Code's path-encoding of project directories (e.g.,
    '-home-dev-projects-job-search'). Use names as arguments to
    `chat_export()`.
    """
    user_dir = _user_dir()
    if not user_dir.exists():
        return []
    return sorted(p.name for p in user_dir.iterdir() if p.is_dir())


def project_path() -> Path | None:
    """Return the absolute path to the current project's transcripts directory.

    Resolves the current project via `tools.environment.get_project_dir()`
    and looks up the matching directory under ~/.claude/projects/. Returns
    None if no transcripts exist for the current project.

    Directory names under ~/.claude/projects/ are Claude Code's path-encoded
    form of the project root, so the encoded name is always `result.name`
    when a directory is returned.
    """
    encoded = _path_encode(environment.get_project_dir())
    return _project_path(encoded)


def chat_export(projects: list[str]) -> dict:
    """Export top-level chat for each named project in place.

    For each project in `projects`:
      - Looks up its directory under ~/.claude/projects/<name>/
      - Extracts every top-level .jsonl transcript (no subdirectory descent)
      - Writes `<stem>_chat.json` beside each source
      - Skips files whose source githash matches the existing output

    Returns dict with counts: {"written": int, "skipped": int, "missing": int}.
    `missing` counts names in `projects` that do not resolve to a real
    project directory.
    """
    counts = {"written": 0, "skipped": 0, "missing": 0}
    for name in projects:
        project_dir = _project_path(name)
        if project_dir is None:
            counts["missing"] += 1
            continue

        for transcript_path in sorted(project_dir.glob("*.jsonl")):
            if not transcript_path.is_file():
                continue
            if _transcript_export(transcript_path):
                counts["written"] += 1
            else:
                counts["skipped"] += 1

    return counts


def chat_clean(projects: list[str]) -> dict:
    """Remove `<stem>_chat.json` extracts for each named project.

    Inverse of `chat_export`. Deletes every top-level `*_chat.json` file
    under ~/.claude/projects/<name>/ (no subdirectory descent). Source
    `.jsonl` transcripts are untouched.

    Returns dict with counts: {"removed": int, "missing": int}.
    `missing` counts names in `projects` that do not resolve to a real
    project directory.
    """
    counts = {"removed": 0, "missing": 0}
    for name in projects:
        project_dir = _project_path(name)
        if project_dir is None:
            counts["missing"] += 1
            continue

        for chat_path in project_dir.glob("*_chat.json"):
            if chat_path.is_file():
                chat_path.unlink()
                counts["removed"] += 1

    return counts
