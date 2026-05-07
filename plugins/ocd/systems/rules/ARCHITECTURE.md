# Rules Architecture

Always-on agent guidance — rule templates that auto-load into every Claude Code session. This document covers the system's internal layers and how install/uninstall map to deployed file paths.

## Purpose

Rules answer one question: what guidance should every agent see in every session?

Each rule template is a self-contained markdown file with a `tagline:` frontmatter line for catalog display. Claude Code auto-loads any markdown file under `.claude/rules/` (and `~/.claude/rules/`) at session start, so deploying a template at a scope is the entire installation mechanism.

## Layers

```
Setup CLI (ocd-run setup rules <verb>)
    ↓ dispatches to
Rules facade (__init__.py)
    ↓ purpose / status / list_items / show / install / uninstall
Setup library helpers (deploy_files, compare_deployed)
    ↓ filesystem reads/writes
Deployed copies (~/.claude/rules/ocd/  OR  <project>/.claude/rules/ocd/)
```

## Components

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Facade — purpose, status, list_items, show, install, uninstall. Resolves scope to deploy path; delegates file ops to `setup.deploy_files` / `compare_deployed`. |
| `workflows/install.md` | Interactive install workflow — asks scope, presents lettered template selection per `confirm-shared-intent`, dispatches to CLI |
| `workflows/uninstall.md` | Interactive uninstall workflow — mirror of install |
| `templates/` | Source-of-truth rule templates. Each file is a deployable rule with `tagline:` frontmatter for catalog display. |

## Scope Resolution

Both scopes supported:

| Scope | Deploy path | Auto-load |
|-------|-------------|-----------|
| `user` | `~/.claude/rules/ocd/<rule>.md` | Every project the user works in |
| `project` | `<project-root>/.claude/rules/ocd/<rule>.md` | The project that owns this clone |

`SUPPORTED_SCOPES = ("user", "project")` declared in `__init__.py`. Calling install/uninstall with any other scope returns an error in the result's `extra` field per the plugin-system convention.

## Target Resolution

`install` and `uninstall` accept an optional `target`:

- `target=None` or `target="all"` — operate on every `templates/*.md` file
- `target="<basename>"` or `target="<basename>.md"` — operate on one specific rule

Unknown target names return an error in `extra` listing the available rules.

## State Model

Install state derives from disk presence — `.claude/rules/ocd/<rule>.md` (or its user-scope equivalent) either exists with content matching the template (`current`), exists with diverged content (`divergent`), or is absent (`absent`).

`status(scope=None)` reports per-template state for both scopes. `status(scope="user")` or `status(scope="project")` narrows.

`install(force=False)` deploys absent files; existing files only overwrite when `force=True`.

## Design Decisions

- **Per-rule install rather than all-or-nothing.** Each rule is an independent template; users opt in selectively. Lets contributors evaluate one principle at a time without committing to the full set.
- **No state file beyond filesystem.** Install state is the deployed copy's existence and content. No JSON sidecar to drift.
- **Same templates, two scopes.** `templates/` is the single source of truth; user-scope and project-scope deploys read from the same source.
