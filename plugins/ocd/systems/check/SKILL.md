---
name: check
description: Run universal discipline checks (dormancy today) against plugin systems. Verifies System Dormancy contract conformance per the marketplace architecture.
argument-hint: "<dormancy | all> [<system-name>] [--plugin <path>]"
allowed-tools:
  - Bash(ocd-run:*)
---

# /check

Run universal discipline checks against plugin systems. Dimensions today: `dormancy`. More dimensions slot in as separate check modules without changing this skill's shape.

## Process Model

Each check dimension verifies one universal discipline that applies to every system across every plugin. The checker scans the target system's folder, detects which dormancy-relevant surfaces it exposes (init contract, readiness interface, MCP server, rule contribution), and runs the applicable assertions. Real systems drift — the checker is tested against synthetic fixtures, not against any particular plugin's live systems.

Dormancy dimension verifies:

- Systems with an init contract (`init()` + `status()`) transition correctly between absent and operational states.
- Systems with runtime operations (MCP server) expose the readiness interface (`ready()` + `ensure_ready()`) and guard their surface internally.
- Deploy-only systems (init/status without runtime operations) are accepted without a readiness requirement.
- Rule contributions deploy to the plugin's expected rule corpus location after init.
- MCP servers gate tool registration on a readiness predicate and emit a dormant-state instruction.

## Rules

- `dormancy` runs against the invoking plugin's systems by default; `--plugin <path>` targets a different plugin
- `all` runs every implemented dimension
- Exit code reflects overall pass/fail — 0 when every check passes, 1 otherwise
- Output is structured per system — pass lines prefixed `+`, fail lines `-`, skip lines `~`

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {dimension} = first token of $ARGUMENTS
3. {remainder} = $ARGUMENTS after {dimension}
4. If {dimension} is `dormancy`: bash: `ocd-run check dormancy {remainder}`
5. Else if {dimension} is `all`: bash: `ocd-run check dormancy {remainder}` — extend when additional dimensions are implemented
6. Else: Exit to user: unrecognized dimension {dimension} — expected dormancy or all
7. Present CLI output to user — no summarization or reformatting
8. Return to caller

### Report

- Per-system pass/fail/skip with evidence lines from the CLI output
- Exit code from the CLI — 0 on full pass, 1 on any failure
