# List

> Workflow component for the `list` verb of skill-creator. State report on in-progress skills across destinations.

### Variables

- {destination} — optional; defaults to both `user` (~/.claude/skills/) and `project` (.claude/skills/), plus `plugins/skill-authoring/skills/` for composition-adjacent skills

### Process

1. For each destination ∈ {`user`, `project`, `plugins/skill-authoring/skills`} (or just the one passed):
    1. List child folders containing a `SKILL.md`.
    2. For each candidate `{name}`:
        1. {state}: `new` if no `evals/evals.json` and no `evals-workspace/` exist; `refining` if either is present; `ready` if a `.skill` file exists in the folder.
        2. {iterations}: highest numbered `evals-workspace/iteration-N/` if present, else `0`.
        3. Emit: `<destination> > <name>: <state> (iterations: <count>)`.
2. If nothing found across all destinations: Emit: `no in-progress skills`.

### Report

```
{destination} > {name}: {state} (iterations: {iterations})
```

One line per in-progress skill. Empty output when nothing is in flight.
