"""Governance operations.

Governance matching and listing. Reads rules and conventions directly
from disk — no database, no caching. Convention files in
.claude/conventions/ carry frontmatter with include/exclude patterns;
rule files in .claude/rules/ are always-on context with no pattern
matching.

All functions resolve project directory internally via the environment
helpers. All functions return structured data (dicts/lists). Formatting
for CLI display belongs in cli.py.
"""

from __future__ import annotations

from pathlib import Path

from tools import environment

from ._frontmatter import matches_pattern, normalize_patterns, parse_governance


def _scan_governance_files() -> tuple[list[Path], list[Path]]:
    """Scan governance directories and return (rule_files, convention_files)."""
    project_dir = environment.get_project_dir()
    rules_dir = project_dir / ".claude" / "rules"
    conv_dir = project_dir / ".claude" / "conventions"

    rule_files = sorted(rules_dir.rglob("*.md")) if rules_dir.is_dir() else []
    conv_files = sorted(conv_dir.rglob("*.md")) if conv_dir.is_dir() else []

    return (
        [f for f in rule_files if f.is_file()],
        [f for f in conv_files if f.is_file()],
    )


def governance_match(file_paths: list[str], include_rules: bool = False) -> dict:
    """Match files against governance patterns.

    By default returns only conventions (on-demand) since rules are always
    loaded into agent context. Set include_rules=True for governance
    evaluation where rules themselves are the evaluation target.

    Scans convention files from disk on every call — no caching.
    """
    project_dir = environment.get_project_dir()
    rule_files, conv_files = _scan_governance_files()

    result_matches: dict[str, list[str]] = {}

    for conv_path in conv_files:
        entry = parse_governance(conv_path)
        if not entry:
            continue
        entry_rel = str(conv_path.relative_to(project_dir))
        includes = normalize_patterns(entry["includes"])
        excludes = (
            normalize_patterns(entry["excludes"]) if entry.get("excludes") else []
        )

        for fp in file_paths:
            matched = any(matches_pattern(fp, p) for p in includes)
            excluded = any(matches_pattern(fp, p) for p in excludes)
            if matched and not excluded:
                result_matches.setdefault(fp, []).append(entry_rel)

    if include_rules:
        rule_paths = [str(f.relative_to(project_dir)) for f in rule_files]
        for fp in file_paths:
            for rp in rule_paths:
                result_matches.setdefault(fp, []).append(rp)

    conventions = sorted({c for cs in result_matches.values() for c in cs})

    return {
        "matches": result_matches,
        "conventions": conventions,
    }


def governance_list() -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    project_dir = environment.get_project_dir()
    rule_files, conv_files = _scan_governance_files()

    result = []

    for rule_path in rule_files:
        result.append({
            "path": str(rule_path.relative_to(project_dir)),
            "includes": "*",
            "mode": "rule",
        })

    for conv_path in conv_files:
        entry = parse_governance(conv_path)
        if not entry:
            continue
        item: dict = {
            "path": str(conv_path.relative_to(project_dir)),
            "includes": entry["includes"],
            "mode": "convention",
        }
        if entry.get("excludes"):
            item["excludes"] = entry["excludes"]
        result.append(item)

    return sorted(result, key=lambda e: e["path"])
