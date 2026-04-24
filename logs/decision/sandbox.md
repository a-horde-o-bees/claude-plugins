---
log-role: reference
---

# Sandbox

Decisions governing the sandbox system — worktree-based isolation for durable feature work and ephemeral testing.

## Sandbox consolidates worktree lifecycle

### Context

Two concerns meet at "isolated workspace for some concern":

- Durable feature work — a feature shelved off main for independent development
- Ephemeral testing — an isolated environment for validating changes or running the test suite

Both need filesystem isolation, a git branch, and lifecycle management. The prior design split them across `/ocd:git` and `/ocd:sandbox`. The split caused two problems:

1. Durable verbs (`box`, `open`, `close`, `unbox`) checked out dev branches in the main working tree. Parallel sessions could not coexist — one session's checkout clobbered another's state.
2. Ephemeral substrate at `.claude/worktrees/<topic>/` nested worktrees inside the main project. Identical relative paths existed in both trees; main-session tool calls silently leaked edits to main (relative paths resolve against `CLAUDE_PROJECT_DIR`; bash without `env -C` ran against main's cwd; MCP servers stayed bound to main's project dir; spawned subagents inherited main's context).

### Options Considered

**Keep separate skills, add `new` verb to `/ocd:git`** — minimal surface change. Rejected: leaves both parallelism and substrate-leakage problems unsolved.

**Standalone `plugins/ocd/systems/worktree/` subsystem consumed by both skills** — clean primitives/policy separation. Rejected: only sandbox consumes the primitives; single-consumer abstraction is YAGNI. Primitives stay in `plugins/ocd/systems/sandbox/_worktree.py`.

**Expose `/ocd:git worktree <add|remove|list|status>` as user-facing verbs** — raw primitives surface. Rejected: bypasses sandbox's opinionated conventions (sibling paths, branch namespacing, permission rules). Users wanting raw worktree operations can invoke native `git worktree` directly.

**Mixed substrate — nested ephemeral + sibling durable** — retains current ephemeral location. Rejected: two location conventions mean two permission rules, two cleanup patterns; prevents a single `<project>--*` glob.

**Branch namespace under `feature/<feature>` + `sandbox/<topic>`** — standard git-flow convention. Rejected in favor of `sandbox/<feature>` + `sandbox/tmp/<topic>` — single `sandbox/*` root lists everything; matches the skill's umbrella concept.

**Gitignore `.claude/settings.json`** — per-user settings only. Rejected: hooks and baseline permissions stop propagating on clone. Keep it tracked; extend existing `/ocd:setup guided` permissions subflow for the `additionalDirectories` rule instead.

### Decision

- Single skill `/ocd:sandbox` owns durable + ephemeral verbs. `/ocd:git` slims to `commit` + `push`.
- Durable verbs: `new`, `pack`, `open`, `close`, `unpack`, `list` (`box`/`unbox` renamed to `pack`/`unpack`).
- Ephemeral verbs: `tests`, `exercise`, `cleanup`. Previous `project`/`worktree` verbs fold into `exercise`'s internal classifier.
- All worktrees live at `<parent>/<project>--<name>/`. Single permission glob `<project>--*`.
- Branch namespace: `sandbox/<feature>` durable, `sandbox/tmp/<topic>` ephemeral. Name `tmp` reserved.
- Python primitives extend `plugins/ocd/systems/sandbox/_worktree.py`. No standalone subsystem.
- Permissions subflow in `/ocd:setup guided` extended to offer the `additionalDirectories` rule via the existing project/user scope selection.

### Consequences

- **Enables:** parallel sessions — each sibling worktree starts its own Claude session with `CLAUDE_PROJECT_DIR` bound correctly; no tool/state leakage between sessions
- **Enables:** main tree stays on `main` through the entire box-family lifecycle — no checkouts disrupt a running session
- **Enables:** one substrate, one permission rule, one cleanup sweep, one inventory view
- **Constrains:** existing `dev/<feature>` branches need one-time rename to `sandbox/<feature>`
- **Constrains:** users re-learning the verb surface find feature-lifecycle operations under `/ocd:sandbox`, not `/ocd:git`
- **Constrains:** sibling paths require explicit `additionalDirectories` permission per project (or user-scope default) — subflow handles this, but it is a one-time gesture per setup
- **Constrains:** nested `.claude/worktrees/` location is retired; any leftover artifacts there need migration or cleanup
