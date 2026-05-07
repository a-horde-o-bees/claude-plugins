---
name: setup
description: Manage ocd plugin infrastructure — discover systems, inspect their status, and run install/uninstall verbs at user or project scope.
argument-hint: "[purposes | statuses | <system> [<verb> [args]]]"
allowed-tools:
  - AskUserQuestion
  - Bash(ocd-run:*)
  - Bash(plugins/ocd/bin/ocd-run:*)
  - Read
---

# /setup

Single entry point for plugin infrastructure. Setup itself is informational; per-system verbs (install, uninstall, status) are dispatched to each system's `__init__.py` facade and `workflows/` markdown.

## Process Model

- **Meta verbs** — `list` (lettered system list with purposes), `status` (aggregated state across systems) report across the plugin.
- **System fallthrough** — any other first argument is treated as a system name. Unknown systems error with the available list.
- **Per-system verb** — `<system> <verb>` dispatches to the system. Standard verbs (status, list, install, uninstall) route through setup's common handlers; systems with custom verbs (e.g., permissions) declare them via their own `dispatch()` and the setup CLI routes accordingly.

Systems are invisible to setup until their package `__init__.py` exposes `purpose()` per `plugins/ocd/systems/conventions/templates/plugin-system.md`. Beyond purpose, each system declares its own verb shape — standard handlers, custom dispatch, or both.

## Workflow

1. If not $ARGUMENTS: bash: `ocd-run setup` — surfaces meta verbs and migrated systems
2. {first} = first token of $ARGUMENTS
3. {rest} = remainder of $ARGUMENTS after {first}

> Meta-verb match — list / status are handled by the CLI directly; no markdown component to load. Surface the CLI output verbatim.

4. If {first} is `list`: bash: `ocd-run setup list`; present output; Return to caller
5. If {first} is `status`: bash: `ocd-run setup status`; present output; Return to caller

> System fallthrough — load the system's verb component when a verb is named, otherwise show usage.

6. {system} = {first}
7. {verb} = first token of {rest}; null if {rest} is empty
8. {verb-args} = remainder of {rest} after {verb}

9. If not {verb}: bash: `ocd-run setup {system}`; present output; Return to caller

> Verb dispatch — read-only verbs (status, list) run via the CLI directly; install and uninstall use the system's interactive markdown workflow when present. Systems with custom verbs route through their own `dispatch()` via the CLI — pass through verbatim.

10. If {verb} is `status`:
    1. bash: `ocd-run setup {system} status {verb-args}`
    2. Present output
    3. Return to caller
11. If {verb} is `list`:
    1. bash: `ocd-run setup {system} list {verb-args}`
    2. Present output
    3. Return to caller
12. If {verb} is `install`:
    1. Read: `${CLAUDE_PLUGIN_ROOT}/systems/{system}/workflows/install.md`
    2. Follow that workflow with {verb-args} as its arguments
    3. Return to caller
13. If {verb} is `uninstall`:
    1. Read: `${CLAUDE_PLUGIN_ROOT}/systems/{system}/workflows/uninstall.md`
    2. Follow that workflow with {verb-args} as its arguments
    3. Return to caller
14. Else: bash: `ocd-run setup {system} {verb} {verb-args}` — custom verb; the system's dispatch handles it. Present output; Return to caller

### Report

Each delegated path returns its own report; surface the called CLI's or the called workflow's output verbatim.
