# Template edit paths

Where to edit when changing rules, conventions, log-type templates, or shared canonicals. Deployed copies under `.claude/` and propagated copies under `plugins/<x>/skills/<y>/` are derived; the `.claude/hooks/guard_derived.py` hook blocks direct edits to them.

| Content | Edit path |
|---------|-----------|
| Project-wide rules (legacy templates) | `plugins/ocd-old/systems/rules/templates/<rule>.md` |
| System-scoped rules (legacy) | `plugins/ocd-old/systems/<system>/rules/<rule>.md` |
| Conventions (source-only; deployment dormant) | `plugins/ocd-old/systems/conventions/templates/<convention>.md` |
| Log-type templates | `plugins/ocd-old/systems/log/templates/<type>/_template.md` |
| Shared cross-skill rules (PFN, file-decomposition, dependency-resolution, trigger-specificity) | `shared/dependencies/<name>.md` |
| Shared cross-skill scripts (`_environment.py`, `_deps.py`) | `shared/scripts/<name>.py` |

## Deployment

Currently manual — sync from canonicals into `.claude/rules/ocd/` when content changes substantively. The legacy per-system setup handler (`/ocd:setup <system> install`) is dormant during the architecture refactor; conventions and system rules are not deployed at all (see `plans/architecture-refactor.md` *Stopgap: manual rules deployment* section for the always-on set criterion).

Pre-commit propagates `shared/<dir>/<file>` copies into every `plugins/<x>/skills/<y>/<dir>/<file>` that already exists (file-existence opt-in). See `.githooks/pre-commit` `CANONICALS` array.

## Never edit

- Deployed copies in `.claude/rules/` — guard hook blocks the write
- Propagated copies in `plugins/<x>/skills/<y>/scripts/` and `plugins/<x>/skills/<y>/dependencies/` for files that exist as canonicals under `shared/` — guard blocks
- Deployed log templates at `logs/<type>/_template.md` — guard blocks

If you find yourself wanting to edit a deployed or propagated file, edit the source at the path above and re-deploy / let pre-commit re-propagate.
