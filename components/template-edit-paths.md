# Template edit paths

Where to edit when changing rules, conventions, or log-type templates. The deployed copies under `.claude/` are derived; a guard hook blocks direct edits to them so changes only flow template → deployed.

| Content | Edit path |
|---------|-----------|
| Project-wide rules | `plugins/ocd/systems/rules/templates/<rule>.md` |
| System-scoped rules | `plugins/ocd/systems/<system>/rules/<rule>.md` |
| Conventions | `plugins/ocd/systems/conventions/templates/<convention>.md` |
| Log-type templates | `plugins/ocd/systems/log/templates/<type>/_template.md` |

Per-system setup handlers manage deploys to `.claude/` via `/ocd:setup <system> install`.

## Never edit

- Deployed copies in `.claude/rules/` or `.claude/conventions/` — guard hook blocks the write
- Deployed log templates at `logs/<type>/_template.md` — same guard

If you find yourself wanting to edit a deployed file, edit the source template at the path above and the next install reflects the change.
