---
name: setup
description: Manage ocd plugin infrastructure — pick which systems deploy, enable or disable individual systems, report current state, or walk through guided setup.
argument-hint: "<status | init [--all | --systems <csv> | --force] | enable <system> | disable <system> | guided>"
allowed-tools:
  - AskUserQuestion
  - Bash(ocd-run:*)
---

# /setup

Manage ocd plugin infrastructure. Every deployable system (rules, conventions, patterns, log, navigator, permissions, refactor) is opt-in — the user chooses which ones belong in their project. The enabled selection persists in `.claude/ocd/enabled-systems.json` so subsequent inits and checkpoints honor the choice without re-prompting.

## Rules

- Systems not in the enabled list are not deployed and their artifacts are cleaned on `disable`
- Permissions deploy to exactly one scope — deploying to both is not an option
- Non-recommended patterns (user's custom additions) are never modified by deploy or clean
- User scope cleanup warns about cross-project impact before proceeding
- Clean only removes patterns that exist in both the template and the other scope

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-arg} = remainder of $ARGUMENTS after {verb}

> Verb dispatch — status reports, init deploys/cherry-picks, enable/disable toggle one system, guided walks through interactively.

4. If {verb} is `status`: Call: Status
5. Else if {verb} is `init`: Call: Init
6. Else if {verb} is `enable`: Call: Enable
7. Else if {verb} is `disable`: Call: Disable
8. Else if {verb} is `guided`: Call: Guided
9. Else: Exit to user: unrecognized verb {verb} — expected status, init, enable, disable, or guided

## Status

> Report current infrastructure state — which systems are enabled, deployment status per system, plugin version. Changes nothing.

1. bash: `ocd-run setup status`
2. Present output to user — no summarization or reformatting
3. Return to caller

### Report

- Plugin version
- Per-system opt-in state (`[enabled]` / `[disabled]`) and deployment status
- Skills list

## Init

> Deploy enabled systems. First-time runs with no flags default to enabling every system so the plugin works out of the box. Subsequent runs honor the persisted selection unless `--all` or `--systems` is passed to change it.

1. If --all: bash: `ocd-run setup init --all [--force if --force]`
2. Else if --systems: bash: `ocd-run setup init --systems {systems} [--force if --force]`
3. Else if --system: bash: `ocd-run setup init --system {system} [--force if --force]`
4. Else: bash: `ocd-run setup init [--force if --force]`
5. Present init output to user
6. Return to caller

### Flag semantics

- `--all` — enable every discovered system, persist the selection
- `--systems <csv>` — enable exactly this comma-separated list, persist the selection
- `--system <name>` — narrow one run to a single system; does not persist anything
- `--force` — overwrite divergent files with plugin defaults
- No flags — use the existing persisted selection; on first install default to everything

## Enable

> Add one system to the enabled list and init it in place.

1. If no {verb-arg}: Exit to user: enable requires a system name
2. bash: `ocd-run setup enable {verb-arg}`
3. Present output to user
4. Return to caller

## Disable

> Remove one system from the enabled list and clean its deployed artifacts.

1. If no {verb-arg}: Exit to user: disable requires a system name
2. bash: `ocd-run setup disable {verb-arg}`
3. Present output to user
4. Return to caller

## Guided

> Interactive walkthrough — show current state, let user cherry-pick systems, confirm, deploy. Offers permissions setup as an optional final step.

1. bash: `ocd-run setup status`
2. Present current state to user — explain opt-in, deployment status, and what init will do
3. AskUserQuestion — which systems to enable, options combine individual systems plus `All` and `Keep current selection`
4. If `Keep current selection`: {selection} = persisted enabled list; proceed with no config change
5. Else if `All`: {selection} = every available system
6. Else: {selection} = the chosen subset
7. If any currently-deployed files would be removed by narrowing the selection: present the list and confirm with user
8. If --force and any files show `divergent`: explain that force mode will overwrite divergent files with plugin defaults
9. Ask user to confirm — AskUserQuestion with options: `["Proceed", "Cancel"]`
10. If cancel: Exit to user: setup cancelled
11. If `All` or `Keep current selection` was chosen:
    1. bash: `ocd-run setup init --all [--force if --force]`
12. Else: bash: `ocd-run setup init --systems {selection-csv} [--force if --force]`
13. Ask user about permissions — AskUserQuestion with options: `["Configure permissions", "Skip"]`
14. If configure: Call: `_permissions-setup.md`
15. Return to caller
