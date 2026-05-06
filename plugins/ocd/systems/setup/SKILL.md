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

Single entry point for plugin infrastructure. Setup itself is informational; per-system verbs (install, uninstall, status) are dispatched to each system's `setup/` handlers.

## Process Model

- **Meta verbs** — `purposes` (lettered list of systems), `statuses` (aggregated state), `permissions` (auto-approve patterns) report across the plugin.
- **System fallthrough** — any other first argument is treated as a system name. Unknown systems error with the available list.
- **Per-system verb** — `<system> <verb>` dispatches to that system's `setup/<verb>.md` workflow. Install and uninstall require `--scope user` or `--scope project`.

Systems are invisible to setup until they have a `setup/__init__.py` exposing the per-system shape — see `plugins/ocd/systems/conventions/templates/plugin-system.md`.

## Workflow

1. If not $ARGUMENTS: bash: `ocd-run setup` — surfaces meta verbs and migrated systems
2. {first} = first token of $ARGUMENTS
3. {rest} = remainder of $ARGUMENTS after {first}

> Meta-verb match — purposes / statuses / permissions are handled by the CLI directly; no markdown component to load. Surface the CLI output verbatim.

4. If {first} is `purposes`: bash: `ocd-run setup purposes`; present output; Return to caller
5. If {first} is `statuses`: bash: `ocd-run setup statuses`; present output; Return to caller
6. If {first} is `permissions`: bash: `ocd-run setup permissions {rest}`; present output; Return to caller

> System fallthrough — load the system's verb component when a verb is named, otherwise show usage.

7. {system} = {first}
8. {verb} = first token of {rest}; null if {rest} is empty
9. {verb-args} = remainder of {rest} after {verb}

10. If not {verb}: bash: `ocd-run setup {system}`; present output; Return to caller

> Verb dispatch — install and uninstall use the system's interactive markdown workflow; status runs read-only via the CLI directly.

11. If {verb} is `status`:
    1. bash: `ocd-run setup {system} status {verb-args}`
    2. Present output
    3. Return to caller
12. If {verb} is `install`:
    1. Read: `${CLAUDE_PLUGIN_ROOT}/systems/{system}/setup/install.md`
    2. Follow that workflow with {verb-args} as its arguments
    3. Return to caller
13. If {verb} is `uninstall`:
    1. Read: `${CLAUDE_PLUGIN_ROOT}/systems/{system}/setup/uninstall.md`
    2. Follow that workflow with {verb-args} as its arguments
    3. Return to caller
14. Else: Exit to user: unknown verb `{verb}` for system `{system}` — expected install, uninstall, or status

### Report

Each delegated path returns its own report; surface the called CLI's or the called workflow's output verbatim.
