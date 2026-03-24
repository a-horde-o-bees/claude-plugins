# Project Instructions

## Versioning

Plugin versions follow `x.y.z` format in each plugin's `.claude-plugin/plugin.json`:

- `x` — major version; starts at `0` until a change breaks previous setups
- `y` — increments on public release; cohesive set of changes ready for consumers; resets `z` to `0`
- `z` — increments on every commit during development; required for local plugin reload to detect changes

## Commit Workflow

Use `/ocd-commit` to commit changes. Skill analyzes working tree, groups changes by topic, and executes commits sequentially with version bumps.

Core rules (enforced by skill):

- Every commit bumps `z` version in `.claude-plugin/plugin.json` for each plugin with changes
- Always surface untracked files for user review — never skip or ignore
- Group changes by topic when multiple coherent topics exist in working tree
- Commit messages describe end-state results, not change history

## Architectural Enforcement

ocd plugin rules (installed via `/ocd-init`) enforce architectural principles (script naming, deterministic/non-deterministic split, CLI design). CLAUDE.md covers only project-specific procedures not addressed by those rules.

## Project File Deployment

Plugin-generated files deployed to user projects follow this structure:

- Rule files → `.claude/rules/<plugin>-<name>.md` (prefix for namespace isolation)
- Supporting files → `.claude/<plugin>/` (directory nesting for isolation, no prefix)
- Skill-specific files → `.claude/<plugin>/<skill>/`

Never place plugin data in the user's project tree outside `.claude/`.

## README Scopes

- **Project root `README.md`** — developer and contributor facing: marketplace info, installation for users and local dev, architecture, design principles, naming conventions, versioning
- **Plugin `README.md`** (e.g., `plugins/ocd/README.md`) — user facing: what the plugin does, how to install, configure, use, and override it; no internal architecture or contributor details

## Testing

- Run tests via `.venv/bin/python3 -m pytest -v`
- Run only tests affected by current changes, scoped to narrowest relevant test file
- All test paths configured in `pyproject.toml`
