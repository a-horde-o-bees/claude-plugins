# Show

> Workflow component for the `show` verb of /ocd:rules. Prints the full body of one rule from the catalog.

### Variables

- {name} — rule basename without `.md` (e.g. `honesty`)

### Process

1. If {name} is empty: Exit to user: `show` requires a rule name — run `list` for the catalog
2. {body}: bash: `uv run -m scripts.rules show {name}`
3. Surface {body} to the user.

### Error Handling

1. If the script exits nonzero (unknown rule): surface stderr verbatim — it includes the available-rules list for the user's next attempt.
