# Show

> Workflow component for the `show` verb of /ocd:rules. Prints the full body of one rule from the catalog.

### Variables

- {name} — rule basename without `.md` (e.g. `honesty`)

### Process

1. If {name} is empty: Exit to user: `show` requires a rule name — run `list` for the catalog
2. Invoke — bash: `uv run -m scripts.rules show {name}`
3. Surface the rule body to the user.

### Error Handling

1. If the script exits nonzero (unknown rule): surface the error message and the list of available rules from the script's stderr.
