# Rules

Always-on agent guidance — rule templates that auto-load into every Claude Code session when deployed at user or project scope.

## workflows/

- `install.md` — interactive install workflow (scope + target selection, deploys templates)
- `uninstall.md` — interactive uninstall workflow (removes deployed rule files at the chosen scope)

## Other

- `__init__.py` — Python facade exposing purpose, status, install, uninstall per the plugin-system convention
- `templates/` — source-of-truth rule templates that deploy as `.claude/rules/<plugin>/<rule>.md`

## Cold-pickup reading order

1. `README.md` — user-facing overview
2. `ARCHITECTURE.md` — internals and deployment paths per scope
3. `workflows/install.md` when invoked via `/ocd:setup rules install`
