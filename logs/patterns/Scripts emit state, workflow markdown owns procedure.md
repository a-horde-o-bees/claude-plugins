---
log-role: reference
---

# Scripts emit state, workflow markdown owns procedure

Separation pattern for skills that pair Python (or similar) scripts with companion `_<verb>.md` workflow files: the script outputs only resolved state and machine-relevant data (paths, scope, drift facts, deployed status); the workflow markdown owns the procedure the agent follows. The script's `print()` calls never duplicate "Next steps for the agent" content that already lives in the markdown.

## When to use

- A skill ships both Python scripts and `_<verb>.md` workflow files.
- The script's output is being consumed by the agent driving the workflow.
- "Next steps for the agent" is starting to appear in both places, drifting between them.

## Pattern

For each verb that has both a script and a `_<verb>.md`:

- Script emits **state** — paths it resolved, status booleans, derived facts, counts.
- Markdown carries **procedure** — what the agent does with that state, in PFN, with `bash:`/`skill:`/`Call:` invocations.
- The agent reads the markdown to learn what to do; reads the script output to learn the current state of the world. Two roles, two homes.

## Pitfalls

- Drift between the two when both try to describe procedure. Markdown wins because it's the documented contract; scripts then start lying about what the agent will do next.
- Script output that explains procedure breaks `separation-of-concerns` and `single-source-of-truth` simultaneously.

## See also

- `_compose_<verb>.md` files in `progressive-skill-composer` — the worked example after refactoring out the duplicated print/procedure overlap.
- `single-source-of-truth` rule.
- `separation-of-concerns` rule.
