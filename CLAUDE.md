# Project Instructions

Operational procedures for agents working in the claude-plugins marketplace repository. For system structure and design, read `architecture.md`.

## Development Workflow

When user asks to "checkpoint" progress: skill: `/checkpoint`

## Versioning

`x.y.z` in each plugin's `.claude-plugin/plugin.json`:

- `x` — major; starts at `0` until a change breaks previous setups
- `y` — public release; cohesive set of changes ready for consumers; resets `z`
- `z` — every commit; required for plugin reload to detect changes

## Plugin Reference

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), check the official Claude Code plugin docs first: https://code.claude.com/docs/en/plugins-reference

This is the primary source for patterns, supported fields, and examples. Fetch the page and review relevant sections before designing new plugin features.

## Editing Rules and Conventions

Edit deployed copies in `.claude/rules/` and `.claude/conventions/`, never templates in `plugins/`. `/ocd-commit` runs `scripts/sync-templates.py` to sync deployed content back to templates before committing. A guard hook blocks direct template edits.

For the template-deployed model and file layout, read `architecture.md`.

## Adding Python Dependencies

Add the package to the plugin's `requirements.txt`. The SessionStart hook detects the change on next session start and reinstalls automatically into the plugin venv.

Prerequisite: `uv` must be installed on the user's system.

For how the dependency system works (venv lifecycle, SessionStart hook mechanics, MCP server binding), read `architecture.md`.

## System and Global Tool Dependencies

Tools installed globally on the user's system (npm globals, system packages, standalone binaries) cannot be auto-installed by plugins — they require user action. Skills that depend on these tools check availability at runtime in their Route and provide corrective install guidance:

```
1. Verify tool available — bash: `command -v <tool>`
    1. If not found: Exit to user — `<tool>` is required; install with `<install command>`
```

Use `SessionStart` hooks for Python packages (isolated in plugin venv). Use runtime checks in skills for everything else.

## Content Routing

- **CLAUDE.md** — project-specific procedures for this repository
- **Rules** — always-on agent behavior; loaded every conversation regardless of file being edited
- **Conventions** — file-type-specific content standards; matched by pattern, applied when creating or modifying matching files

Rules govern agent behavior. Conventions govern file content. If guidance applies regardless of which file is being edited, it belongs in a rule. If it applies only when working with a specific file type, it belongs in a convention.

## README Scopes

- **Root `README.md`** — developer and contributor facing
- **Plugin `README.md`** — user facing; what it does, how to install, configure, use, and override

## Testing

- All tests: `bash scripts/test.sh`
- Project tests in `tests/`, per-plugin tests isolated by `pythonpath`
- Plugin configs: `plugins/<plugin>/pytest.ini`; project config: `pyproject.toml`
