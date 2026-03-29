# Project Instructions

## Versioning

Plugin versions follow `x.y.z` format in each plugin's `.claude-plugin/plugin.json`:

- `x` — major version; starts at `0` until a change breaks previous setups
- `y` — increments on public release; cohesive set of changes ready for consumers; resets `z` to `0`
- `z` — increments on every commit during development; required for local plugin reload to detect changes

## Development Workflow

Use `/ocd-commit` to commit changes. Use `/ocd-push --branch main` to push.

After pushing, refresh the marketplace so the running Claude session picks up changes:

```
/plugin marketplace update a-horde-o-bees
```

Restart (`/exit` then `claude --continue`) only required when `.claude/rules/` files changed. Skill and convention changes take effect after the marketplace update.

## Content Boundaries

Three layers of documentation serve different purposes:

- **CLAUDE.md** — project-specific procedures; applies only to this repository (versioning, commit workflow, test commands, deployment structure)
- **Rules** — always-on agent behavior; loaded into every conversation, apply regardless of what file is being edited; shape how agent operates (writing style, communication, workflow discipline, notation systems)
- **Conventions** — file-type-specific content standards; matched to files by pattern, applied when creating or modifying matching files; shape what conforming files look like (Python style, CLI content, SKILL.md structure)

Rules govern agent behavior (always needed). Conventions govern file content (needed when touching matching files). If guidance applies regardless of which file is being edited, it belongs in a rule. If it applies only when working with a specific file type, it belongs in a convention.

## Project File Deployment

Plugin-generated files deployed to user projects follow this structure:

- Rule files → `.claude/rules/<plugin>-<name>.md` (prefix for namespace isolation)
- Supporting files → `.claude/<plugin>/` (directory nesting for isolation, no prefix)
- Skill-specific files → `.claude/<plugin>/<skill>/`

Never place plugin data in the user's project tree outside `.claude/`.

## Template vs Deployed Files

Rules and conventions use a template→deployed model for distribution. Templates live in `plugins/<plugin>/rules/` and `plugins/<plugin>/templates/conventions/`. Deployed copies live in `.claude/rules/` and `.claude/<plugin>/conventions/`. Init copies templates to deployed locations for bootstrapping new clones and user installations.

Edit deployed copies in `.claude/`, never templates in `plugins/`. Templates are distribution artifacts — the commit workflow runs `scripts/sync-templates.py` to sync deployed copies to templates before committing. Guard hook blocks direct template edits.

## README Scopes

- **Project root `README.md`** — developer and contributor facing: marketplace info, installation for users and local dev, architecture, design principles, naming conventions, versioning
- **Plugin `README.md`** (e.g., `plugins/ocd/README.md`) — user facing: what the plugin does, how to install, configure, use, and override it; no internal architecture or contributor details

## Testing

- Run all tests via `bash scripts/test.sh`
- Two layers: project tests (`tests/`) and per-plugin tests (isolated `pythonpath` per plugin)
- Plugin test configs in `plugins/<plugin>/pytest.ini`
- Project test config in `pyproject.toml`
