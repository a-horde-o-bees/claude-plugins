---
name: rules
description: Use this skill to manage always-on agent guidance — deploy rule canonicals at user or project scope so Claude Code auto-loads them into every session, or remove deployed rules to take them out of always-on. Provides verbs to list available rules, read individual rule bodies, report deployment state per scope, install rules as always-on, and uninstall them. Each rule deploys to `<scope>/rules/dependencies/<name>.md` per the markdown-dependency-resolution convention. Trigger on phrases like "install rule X", "deploy rule Y always-on", "what rules are deployed", "show me the rule on honesty", "list available rules", "remove rule Z", or any context where the user wants to manage the always-on rule layer.
allowed-tools:
  - Read
  - Bash(uv run *)
  - Bash(ls *)
  - Bash(find *)
  - AskUserQuestion
---

# rules

Catalog management for always-on agent guidance. Deploys rule canonicals at user or project scope so Claude Code auto-loads them; uninstalls remove the always-on copy without affecting skill-bundled fallbacks. The catalog ships bundled with this skill at `dependencies/` and propagates from project-root `shared/dependencies/` via pre-commit.

## Dependencies

Read each if not already in context. Discover via `find ~/.claude <project>/.claude -path "*dependencies/<name>.md" -type f 2>/dev/null`. Selection: prefer user-scope; prefer `rules/dependencies/` over plain `dependencies/`; skill-bundled is last resort. User-scope skills skip project matches.

- [[process-flow-notation]]
- [[workflow-vs-script]]
- [[description-authoring]]
- [[markdown-dependency-resolution]]
- [[confirm-shared-intent]]

## Triggers

| Cognitive moment | Verb |
|---|---|
| User wants the available rules catalog | `list` |
| User wants the full body of one rule | `show <name>` |
| User wants to see what's deployed at each scope | `status [--scope <user\|project>]` |
| User wants to deploy rules as always-on | `install <name>... --scope <user\|project> [--force]` |
| User wants to remove always-on rules | `uninstall <name>... --scope <user\|project>` |

## Verbs

| Verb | Workflow file |
|---|---|
| `list` | [`_list.md`](_list.md) |
| `show <name>` | [`_show.md`](_show.md) |
| `status` | [`_status.md`](_status.md) |
| `install ...` | [`_install.md`](_install.md) |
| `uninstall ...` | [`_uninstall.md`](_uninstall.md) |

Mechanical work lives in `scripts/rules.py`; workflow files orchestrate user-facing surface (argument prompts, catalog browsing, confirmations).

## Scope and deployment paths

| Scope | Deploy path | Auto-load |
|-------|-------------|-----------|
| `user` | `~/.claude/rules/dependencies/<name>.md` | Every project the user works in |
| `project` | `<project>/.claude/rules/dependencies/<name>.md` | Only when working in that project |

Lazy deployment (`<scope>/dependencies/<name>.md`) is not managed by this skill — that path resolves through agent discovery, not Claude Code auto-load. Move a rule there manually if you want skills to find it via discovery but not have it always-on.

## Workflow

1. {verb} = first token of $ARGUMENTS
2. {verb-args} = remainder of $ARGUMENTS after {verb}
3. If {verb} is `list`: Call: `_list.md`
4. Else if {verb} is `show`: Call: `_show.md` ({name} = first token of {verb-args})
5. Else if {verb} is `status`: Call: `_status.md` ({args} = {verb-args})
6. Else if {verb} is `install`: Call: `_install.md` ({args} = {verb-args})
7. Else if {verb} is `uninstall`: Call: `_uninstall.md` ({args} = {verb-args})
8. Else: Exit to user: unrecognized verb {verb} — expected `list`, `show`, `status`, `install`, or `uninstall`
