# Template edit paths

Where to edit when changing rules, conventions, log-type templates, or shared canonicals. Deployed copies under `.claude/` and propagated copies under `plugins/<x>/skills/<y>/` are derived; the `.claude/hooks/guard_derived.py` hook blocks direct edits to them.

| Content | Edit path |
|---------|-----------|
| All rule canonicals | `shared/_dependencies/<name>.md` |
| Shared cross-skill scripts (`_environment.py`, `_deps.py`) | `shared/scripts/<name>.py` |
| Log-type templates (legacy) | `plugins/ocd-old/systems/log/templates/<type>/_template.md` |
| Conventions templates (source-only; deployment dormant) | `plugins/ocd-old/systems/conventions/templates/<convention>.md` |

## Deployment

Rules deploy via `/ocd:rules install <name> --scope <user|project>` — copies from the rules skill's bundled seed at `<skill>/_dependencies/<name>.md` to the scope's always-on path `<scope>/rules/dependencies/<name>.md`. The underscore-prefix bundled folder marks install-source-only storage; the discovery `find` filter excludes it from runtime resolution per markdown-dependency-resolution.

Pre-commit globs `shared/scripts/*.py` and `shared/_dependencies/*.md`, propagating each staged canonical into every `plugins/<x>/skills/<y>/<dir>/<file>` that already exists (file-existence opt-in). See `.githooks/pre-commit`.

## Never edit

- Deployed copies in `.claude/rules/` — guard hook blocks the write
- Propagated copies in `plugins/<x>/skills/<y>/scripts/` and `plugins/<x>/skills/<y>/_dependencies/` for files that exist as canonicals under `shared/` — guard blocks
- Deployed log templates at `logs/<type>/_template.md` — guard blocks

If you find yourself wanting to edit a deployed or propagated file, edit the source at the path above and let pre-commit re-propagate (or re-run `/ocd:rules install <name> --scope <scope> --force` for deployed rules).
