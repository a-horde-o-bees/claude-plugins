# Status

> Workflow component for the `status` verb of /ocd:rules. Reports which rules are deployed at each scope.

### Variables

- {args} — remaining CLI args (e.g. `--scope user`); empty for all scopes

### Process

1. Invoke — bash: `uv run -m scripts.rules status {args}`
2. Surface the status table to the user.

### Report

Per-rule × per-scope grid:

```
name           user       project
<rule-1>       current    absent
<rule-2>       absent     current
<rule-3>       divergent  absent
```

States:

- `absent` — not deployed at this scope
- `current` — deployed and matches the canonical
- `divergent` — deployed but content differs from canonical (likely user-edited; re-install with `--force` to overwrite)
