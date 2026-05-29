# /skill-architecture reassert — verb stub (W5 of plans/skill-architecture.md)

Status: **not yet implemented.** See [`plans/skill-architecture.md`](../../../../plans/skill-architecture.md) Workstream W5 for the implementation plan, including the parseable test-design format (Open Question S3), the scratch-directory destination for ephemeral fixtures (S2), and the detection-method automation approach (S4).

## Intended surface

```
/skill-architecture reassert [<topic> | <assertion-path>]
```

| Argument shape | Behavior |
|---|---|
| No argument | Re-run every assertion across every topic |
| `<topic>` (e.g. `skill-runtime`, `platform-discovery`) | Re-run all assertions in that topic |
| `<assertion-path>` (e.g. `platform-discovery/project-dir-resolution`) | Re-run the single named assertion |

## Planned mechanic

1. Parse the target's `Test design` section into structured fixture-skill bodies, run procedure, and detection method (format TBD per S3)
2. Materialize ephemeral fixture skills to a scratch location (destination TBD per S2)
3. Spawn the appropriate driver — `claude -p` headless, sub-agent via Task, or in-process orchestration — per the run procedure
4. Apply the detection method to outputs; produce pass / fail / needs-investigation
5. Append a row to the assertion's `Historical results` section with date, result, and platform version (read from `CLAUDE_CODE_EXECPATH` package version or `claude --version`)
6. Clean up scratch fixtures unless `--keep-fixtures` is passed

## Workflow

1. Exit to user: the `reassert` verb is not yet implemented. To re-verify an assertion manually for now, open `assertions/<topic>/<assertion>.md` and follow its `Test design` section directly. The implementation plan is at `plans/skill-architecture.md` Workstream W5.
