#!/usr/bin/env python3
"""Skill-linter check: cross-plugin `/skill-name` invocations must have declared deps.

Walks `plugins/*/.claude-plugin/plugin.json` to inventory declared deps. Walks
`plugins/*/skills/*/SKILL.md` to build a `skill-name → owning-plugin` index.
Scans each plugin's body files for `/<known-skill>` invocations and verifies
that any cross-plugin invocation has its target plugin listed in dependencies.

`/skill-name` resolution is global at runtime — the matcher could find a
skill in any installed plugin. The dep declaration is the plugin author's
intent that the target lives in a specific plugin and must be installed
alongside this one. Static analysis can't infer the intent from the
invocation alone, so the author maintains the contract via plugin.json
and this check enforces it.

Invocations that don't resolve to any skill in this repo (e.g., Anthropic
upstream `/skill-creator`, `/pdf`, `/loop`) are ignored — out of scope.

Usage:
    check_plugin_deps.py [<plugin> ...]

With no args, checks every plugin under plugins/ except SKIP_PLUGINS.
With args, checks only the named plugins.

Exit 0 if clean; exit 1 with a violation report if any invocation lacks
its dep declaration.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLUGINS_DIR = Path("plugins")
SKIP_PLUGINS = {"ocd-old"}  # Legacy backlog under Phase E migration; not currently consistent

NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)
INVOCATION_RE = re.compile(r"/([a-z][a-z0-9-]*)\b")


def build_skill_index() -> dict[str, str]:
    """skill-name → owning plugin name, derived from each SKILL.md's frontmatter."""
    index: dict[str, str] = {}
    for skill_md in PLUGINS_DIR.glob("*/skills/*/SKILL.md"):
        plugin_name = skill_md.parts[1]
        if plugin_name in SKIP_PLUGINS:
            continue
        m = NAME_RE.search(skill_md.read_text())
        if m:
            index[m.group(1)] = plugin_name
    return index


def load_declared_deps(plugin: str) -> set[str]:
    path = PLUGINS_DIR / plugin / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    deps = data.get("dependencies", [])
    # Dep entries are either bare strings or {name, version, marketplace} objects
    return {d if isinstance(d, str) else d["name"] for d in deps}


def find_cross_plugin_invocations(
    plugin: str, skill_index: dict[str, str]
) -> dict[str, str]:
    """Map skill-name → target-plugin for every cross-plugin invocation in this plugin's bodies.

    Skips vendored upstream content under any `sources/` subdirectory and a skill's
    `tests/` subdirectory — third-party files (e.g., embedded Anthropic skills
    referenced by skill-composer) and test fixtures/docs don't represent this plugin's
    invocation surface.
    """
    invocations: dict[str, str] = {}
    for md_file in (PLUGINS_DIR / plugin).rglob("*.md"):
        if "sources" in md_file.parts or "tests" in md_file.parts:
            continue
        for match in INVOCATION_RE.finditer(md_file.read_text()):
            skill = match.group(1)
            target = skill_index.get(skill)
            if target and target != plugin:
                invocations[skill] = target
    return invocations


def check(plugins_to_check: list[str]) -> int:
    skill_index = build_skill_index()
    violations: list[tuple[str, str, str]] = []

    for plugin in plugins_to_check:
        if plugin in SKIP_PLUGINS:
            continue
        if not (PLUGINS_DIR / plugin / ".claude-plugin" / "plugin.json").exists():
            continue
        invocations = find_cross_plugin_invocations(plugin, skill_index)
        if not invocations:
            continue
        declared = load_declared_deps(plugin)
        for skill, target in sorted(invocations.items()):
            if target not in declared:
                violations.append((plugin, skill, target))

    if not violations:
        return 0

    print(
        "Plugin dependency violations — body invokes /skill from a plugin not in dependencies:",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    by_plugin: dict[str, list[tuple[str, str]]] = {}
    for plugin, skill, target in violations:
        by_plugin.setdefault(plugin, []).append((skill, target))
    for plugin, entries in by_plugin.items():
        targets = sorted({t for _, t in entries})
        print(f"  plugins/{plugin}:", file=sys.stderr)
        for skill, target in entries:
            print(f"    invokes /{skill}  (from plugin: {target})", file=sys.stderr)
        print(
            f"    → add {targets} to plugins/{plugin}/.claude-plugin/plugin.json dependencies",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
    print(
        f"{len(violations)} violation(s) across {len(by_plugin)} plugin(s). "
        "Reconcile plugin.json dependencies.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    if len(sys.argv) > 1:
        plugins_to_check = sys.argv[1:]
    else:
        plugins_to_check = sorted(
            p.name
            for p in PLUGINS_DIR.iterdir()
            if p.is_dir()
            and (p / ".claude-plugin" / "plugin.json").exists()
            and p.name not in SKIP_PLUGINS
        )
    return check(plugins_to_check)


if __name__ == "__main__":
    sys.exit(main())
