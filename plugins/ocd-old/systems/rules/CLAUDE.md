# Rules

Always-on agent guidance — rule templates that auto-load into every Claude Code session when deployed at user or project scope.

## Paths

| Path | Purpose |
|---|---|
| `README.md` | User-facing overview |
| `ARCHITECTURE.md` | Internals and deployment paths per scope |
| `__init__.py` | Python facade exposing purpose, status, list_items, show, install, uninstall per the plugin-system convention |
| `workflows/` | Setup workflows |
| `workflows/install.md` | Interactive install workflow (scope + target selection, deploys templates) |
| `workflows/uninstall.md` | Interactive uninstall workflow (removes deployed rule files at the chosen scope) |
| `templates/` | Source-of-truth rule templates that deploy as `.claude/rules/<plugin>/<rule>.md` |

## Cold-pickup

No persistent in-flight work surface; entry is per-verb. Read `workflows/<verb>.md` when invoked via `/ocd:setup rules <verb>`.
