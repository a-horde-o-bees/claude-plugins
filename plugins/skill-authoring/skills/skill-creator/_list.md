# List

> Workflow component for the `list` verb of skill-creator. State report on in-progress skills across destinations.

## Variables

- {destination} — optional; defaults to all three: `user` (~/.claude/skills/), `project` (.claude/skills/), and `plugins/skill-authoring/skills/` (composition-adjacent skills)

## Process

1. {destinations}: passed {destination} as a single-item list, else `[user, project, plugins/skill-authoring/skills]`
2. For each {dest} in {destinations}:
    1. {candidates}: child folders containing a `SKILL.md`
    2. For each {name} in {candidates}:
        1. {state}:
            - `new` if no `evals/evals.json` and no `evals-workspace/` exist
            - `refining` if either is present
            - `ready` if a `.skill` file exists in the folder
        2. {iterations}: highest numbered `evals-workspace/iteration-N/` directory, or `0` if none
        3. Emit: `{dest} > {name}: {state} (iterations: {iterations})`

3. If nothing emitted across all destinations: Emit: `no in-progress skills`

## Report

```
{destination} > {name}: {state} (iterations: {iterations})
```

One line per in-progress skill. Empty output when nothing is in flight.
