# Permissions

Auto-approve pattern management across Claude Code's project and user scopes. Reports coverage against plugin-recommended patterns, installs recommended patterns at a user-selected scope, analyzes cross-scope health, and cleans redundant entries.

## Files

- `settings.json` — recommended permission patterns grouped by category
- `_operations.py` — list, install, analyze, clean, and helper functions
- `_init.py` — subsystem `init()`/`status()` per the Init/Status Contract

## CLI

Invoked via the plugin CLI:

```
ocd-run subsystems.setup permissions status               # report both scopes' permission state
ocd-run subsystems.setup permissions install --scope <x>  # deploy recommended patterns to <x>
ocd-run subsystems.setup permissions analyze              # cross-scope health check
ocd-run subsystems.setup permissions clean --scope <x>    # remove recommendations redundant with other scope
```

`install` requires an explicit scope choice — the `/ocd:setup guided` skill drives the interactive flow that picks scope, deploys, and offers cross-scope cleanup.
