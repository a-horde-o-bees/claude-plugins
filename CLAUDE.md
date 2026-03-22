# Project Instructions

## Versioning

Plugin versions follow `x.y.z` format in each plugin's `.claude-plugin/plugin.json`:

- `x` — major version; starts at `0` until a change breaks previous setups
- `y` — increments on public release; cohesive set of changes ready for consumers; resets `z` to `0`
- `z` — increments on every commit during development; required for local plugin reload to detect changes

## Commit Workflow

Every commit must bump the `z` version in `.claude-plugin/plugin.json` for each plugin that has changes. This enables the local plugin reload cycle:

1. Bump `z` in affected plugin's `.claude-plugin/plugin.json`
2. Commit changes
3. Developer runs `/plugin marketplace update a-horde-o-bees` then `/reload-plugins` to test

## Architectural Enforcement

ocd plugin rules (installed via `/ocd-init`) enforce architectural principles (script naming, deterministic/non-deterministic split, CLI design). CLAUDE.md covers only project-specific procedures not addressed by those rules.

## README Scopes

- **Project root `README.md`** — developer and contributor facing: marketplace info, installation for users and local dev, architecture, design principles, naming conventions, versioning
- **Plugin `README.md`** (e.g., `plugins/ocd/README.md`) — user facing: what the plugin does, how to install, configure, use, and override it; no internal architecture or contributor details

## Testing

- Run tests via `.venv/bin/python3 -m pytest -v`
- Run only tests affected by current changes, scoped to narrowest relevant test file
- All test paths configured in `pyproject.toml`
