# Agent Authoring

Conventions for content consumed by agents: skills, conventions, plans, actions, CLAUDE.md files, and CLI tools.

## Writing Style

### Grammar

- Prioritize completeness over brevity — missing information causes incorrect assumptions
- Every word must earn its place — if removing a word or phrase does not change meaning, remove it; complete does not mean verbose
- Include examples only when a rule is ambiguous without one

### Naming

- Use verbose names that convey purpose; capture full meaning in descriptions
- Do not truncate for visual format
- Script names match the domain concept — `navigator_cli.py` not `cli.py` or `pt.py`
- Skill frontmatter `name` field uses plugin-name prefix — `ocd-navigator` not `navigator`; surfaces plugin name during search

### Content Rules

- Describe current reality; do not reference previous states, removed features, or change history
- Examples must be generic — use `module`, `client`, `library` not project-specific names

## Skill Architecture

- Deterministic operations belong in CLI scripts; non-deterministic steps stay in SKILL.md as agent-executed workflow instructions
- When continuing a session that was mid-skill, re-read SKILL.md from disk before resuming — carried-over context may be stale

## Conventions

Before creating or modifying files, check for applicable conventions:

```
python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.conventions list-matching <file> [<file> ...]
```

Pass all target file paths in a single call. Output groups each target file with its matching convention paths. If output is non-empty, read and follow returned convention files before proceeding.

## Structural Principles

- Structural decisions must be deterministic — divide, group, and organize based on functional principles that produce the same result regardless of who evaluates them or when; do not use subjective thresholds ("too big", "complex enough", "feels painful") as triggers for structural action
- Every change must be followed through as if the old way never existed; no compatibility shims, no split conventions; if refactor touches function, variable, path, or pattern, update every reference to match

## CLI Design

### Agent-facing vs internal scripts

Agent-facing CLIs are executables that agents call directly during tasks. Internal scripts are implementation details called by plugin infrastructure (hooks, commands) — agents never invoke them.

Naming convention:
- `<name>_cli.py` (or `<name>_cli.sh`, etc.) — agent-facing entry point; agents call it directly, read its `--help`, and parse its output
- `<name>.py` (or `<name>.sh`, etc.) — internal library or internal script; called by plugin hooks, commands, or other scripts

Absence of a `_cli` file for a domain concept indicates missing CLI capabilities — deterministic operations should have an agent-facing entry point.

### Interpreter

- `python3` not `python` — explicit interpreter version
- No shebangs, no execute permissions — scripts are invoked via interpreter prefix
