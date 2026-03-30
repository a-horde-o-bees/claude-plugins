# Project Instructions

## Versioning

`x.y.z` in each plugin's `.claude-plugin/plugin.json`:

- `x` — major; starts at `0` until a change breaks previous setups
- `y` — public release; cohesive set of changes ready for consumers; resets `z`
- `z` — every commit; required for plugin reload to detect changes

## Development Workflow

When user asks to "checkpoint" progress:

1. Commit (skill): `/ocd-commit`
2. Push (skill): `/ocd-push --branch main`
3. Marketplace refresh (bash): `claude plugins marketplace update a-horde-o-bees`
4. Suggest session restart (`/exit` then `claude --continue`) only when `.claude/rules/` files changed; skill and convention changes take effect after marketplace update

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

Templates in `plugins/<plugin>/rules/` and `plugins/<plugin>/templates/conventions/`. Deployed copies in `.claude/rules/` and `.claude/<plugin>/conventions/`. Init copies templates to deployed locations.

Edit deployed copies in `.claude/`, never templates in `plugins/`. `/ocd-commit` runs `scripts/sync-templates.py` to sync deployed→templates before committing. Guard hook blocks direct template edits.

## README Scopes

- **Root `README.md`** — developer and contributor facing
- **Plugin `README.md`** — user facing; what it does, how to install, configure, use, and override

## Testing

- All tests: `bash scripts/test.sh`
- Project tests in `tests/`, per-plugin tests isolated by `pythonpath`
- Plugin configs: `plugins/<plugin>/pytest.ini`; project config: `pyproject.toml`
