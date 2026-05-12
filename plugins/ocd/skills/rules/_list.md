# List

> Workflow component for the `list` verb of /ocd:rules. Prints the catalog of available rules with one-line descriptions.

### Process

1. Invoke — bash: `uv run -m scripts.rules list`
2. Surface the catalog to the user.

### Report

```
<name>: <first-paragraph description>
```

One line per rule, sorted alphabetically.
