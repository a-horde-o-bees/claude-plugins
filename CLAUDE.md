# Project Instructions

## Versioning

`x.y.z` in each plugin's `.claude-plugin/plugin.json`:

- `x` — major; starts at `0` until a change breaks previous setups
- `y` — public release; cohesive set of changes ready for consumers; resets `z`
- `z` — every commit; required for plugin reload to detect changes

## Development Workflow

When user asks to "checkpoint" progress: skill: `/checkpoint`

## Plugin Reference

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), check the official Claude Code plugin docs first: https://code.claude.com/docs/en/plugins-reference

This is the primary source for patterns, supported fields, and examples. Fetch the page and review relevant sections before designing new plugin features.

## Python Dependencies in Plugins

Plugins requiring Python packages beyond the standard library use a `SessionStart` hook to install into a persistent venv at `${CLAUDE_PLUGIN_DATA}/venv/`. This is the plugin-native pattern from the official docs.

Required files:

- `requirements.txt` — declares pip dependencies
- `hooks/hooks.json` — `SessionStart` hook that diffs `requirements.txt` against a cached copy in `${CLAUDE_PLUGIN_DATA}`, creates a venv via `uv venv --seed`, installs via pip, and copies the manifest; skips when unchanged
- `.mcp.json` — MCP server command points to `${CLAUDE_PLUGIN_DATA}/venv/bin/python3`

Adding a dependency: add the package to `requirements.txt`. The diff detects the change on next session start and reinstalls automatically.

Prerequisite: `uv` must be installed on the user's system.

### System and Global Tool Dependencies

Tools installed globally on the user's system (npm globals, system packages, standalone binaries) cannot be auto-installed by plugins — they require user action. Skills that depend on these tools check availability at runtime in their Route and provide corrective install guidance:

```
1. Verify tool available — bash: `command -v <tool>`
    1. If not found: Exit to user — `<tool>` is required; install with `<install command>`
```

Use `SessionStart` hooks for Python packages (isolated in plugin venv). Use runtime checks in skills for everything else.

## Content Boundaries

- **CLAUDE.md** — project-specific procedures for this repository
- **Rules** — always-on agent behavior; loaded every conversation regardless of file being edited
- **Conventions** — file-type-specific content standards; matched by pattern, applied when creating or modifying matching files

Rules govern agent behavior. Conventions govern file content. If guidance applies regardless of which file is being edited, it belongs in a rule. If it applies only when working with a specific file type, it belongs in a convention.

## Project File Deployment

Files deployed to user projects:

- Rule files → `.claude/rules/<plugin>-<name>.md`
- Supporting files → `.claude/<plugin>/`
- Skill-specific files → `.claude/<plugin>/<skill>/`

No plugin data outside `.claude/`.

## Template vs Deployed Files

Templates in `plugins/<plugin>/rules/` and `plugins/<plugin>/conventions/`. Deployed copies in `.claude/rules/` and `.claude/conventions/`. Governance metadata (pattern, depends) lives in each file's YAML frontmatter — no external manifest. Init copies templates to deployed locations.

Edit deployed copies in `.claude/`, never templates in `plugins/`. `/ocd-commit` runs `scripts/sync-templates.py` to sync deployed→templates before committing. Guard hook blocks direct template edits.

## README Scopes

- **Root `README.md`** — developer and contributor facing
- **Plugin `README.md`** — user facing; what it does, how to install, configure, use, and override

## Testing

- All tests: `bash scripts/test.sh`
- Project tests in `tests/`, per-plugin tests isolated by `pythonpath`
- Plugin configs: `plugins/<plugin>/pytest.ini`; project config: `pyproject.toml`
