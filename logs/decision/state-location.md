---
log-role: reference
---

# Plugin State Location Convention

Where plugin-managed working files (DBs, indices, caches) live, keyed on whether the agent or Claude Code reads them directly versus only through bin tools.

## Context

Two recurring frictions surface when the agent operates on plugin-managed state:

- **Approval friction in `.claude/`** — agent Read/Edit/Write tools that touch paths under any `.claude/` directory trigger permission prompts. Systems that make many small writes (sync operations, log entries, working DB updates) accumulate prompt overhead
- **Where to put per-project state that isn't user-facing** — the navigator DB at `<project>/.navigator.db` works but pollutes the project root with a binary file. The transcripts DB lives at a Claude Code-managed path. Other future systems with similar needs lack a canonical home

The `bin/` indirection pattern (e.g., `ocd-run navigator scan`) bypasses approval friction because Python inside the subprocess writes wherever it wants — the user approves the `ocd-run` command once, and all internal writes go through.

## Options Considered

**Everything in scope tree (`<scope>/.claude/<system>/state/`)** — keep state visible at the user's chosen scope. Rejected: hits approval friction for every write; pollutes `.claude/` with binary state; couples plugin-internal state to scope decisions

**Everything in plugin data dir (`~/.claude/plugins/data/<plugin>-<author>/`)** — move all plugin-managed state to data dir. Rejected: user-meaningful artifacts (logs, configs) need to stay with the project tree to version-control with the user's work

**Categorize by access pattern** — bin-mediated state in plugin data dir; user-edited artifacts in project tree; Claude Code-read files at scope. Adopted.

## Decision

State location is determined by who reads or writes the file directly via tools that hit the permission system.

| Category | Reader/writer | Location | Examples |
|---|---|---|---|
| Bin-mediated | `<plugin>-run` subprocesses only — agent never touches via Read/Write/Edit | `~/.claude/plugins/data/<plugin>-<author>/` | Navigator DB, transcripts DB, dep manifest cache, venv, internal indices |
| User-edited | User and agent edit/read directly | Project tree, outside `.claude/` | Logs, plans, sandbox tasks, project configs |
| Scope-required | Claude Code parses directly | `<scope>/.claude/...` | Settings, rules, skill shims, discovery substrate stubs |

The principle: **path location is a function of access pattern, not data ownership.** A file the agent never touches through agent tools can live anywhere `ocd-run` can reach; a file the agent does touch must follow location-determined approval rules.

For per-project state in plugin data dir, key on a project hash:

```
~/.claude/plugins/data/<plugin>-<author>/projects/<sha-of-canonical-project-path>/<state-file>
```

This isolates per-project state from cross-project state without polluting any project tree.

## Consequences

- **Enables:** approval-free plugin-internal writes (no permission prompts on navigator scans, transcript ingests, etc.); cleaner project trees (plugin-managed binary state gone from project root); single mechanism for cross-project plugin state
- **Constrains:** state living in plugin data dir is harder for the user to inspect (they have to know to look there); plugins must rebuild state on data-dir loss (treat data dir as cache-grade, not authoritative)
- **Migration candidates** — the obvious near-term moves:
  - `<project>/.navigator.db` → `~/.claude/plugins/data/ocd-a-horde-o-bees/projects/<hash>/navigator.db`
  - transcripts DB → `~/.claude/plugins/data/ocd-a-horde-o-bees/projects/<hash>/transcripts.db`
- **Stays put:** logs (user-edited), sandbox state (user-edited), discovery substrate content (Claude Code-read)
- **Bin-discipline reinforced:** writing systems should funnel writes through `ocd-run <system> <verb>` rather than agent-direct writes whenever the data is plugin-internal. This is already the navigator pattern; codify it as a system-design rule
