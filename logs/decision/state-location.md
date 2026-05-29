---
log-role: reference
---

# Plugin State Location Convention

Where plugin-managed working files (DBs, indices, caches) live, keyed on whether the agent or Claude Code reads them directly versus only through bin tools.

> **Status (2026-05-13)** — Four-category matrix (bin-mediated, user-edited, scope-required, plugin-namespaced user-edited) remains the framework. The `skill-authoring` plugin (formerly `progressive-skill-composer`) embeds `composition.md` inside each skill's folder rather than using plugin-namespaced storage — the recipe travels with the skill. The plugin-namespaced extension stays valid for plugins that need plugin-managed user-edited content not tied to any specific skill.
>
> **Status (2026-05-21)** — Migration candidates listed under §Consequences below are still pending. Transcripts modernization (`plans/transcripts.md` Workstream A) is routing the transcripts DB to `~/.claude/transcripts/transcripts.db` rather than the plugins-data-dir path prescribed on line 54 below — a deliberate deviation under that plan's Open Question 4. Reconciling the framework (allow simpler top-level paths for single-DB plugins, vs. conform new migrations to the prescribed namespacing) is open. Navigator's state-location migration is also pending and will be guided by whatever shape transcripts lands.

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

## Plugin-namespaced user-edited content

### Context

The original three categories (bin-mediated, user-edited, scope-required) were drafted assuming user-edited content is *project content* — logs, plans, sandbox tasks. The "outside `.claude/`" rule for user-edited targets that case: project content belongs at the project tree's top level, not buried in a config directory.

Plugin-managed user-edited content is a different case the original framing did not cover. progressive-skill-composer's compose flow needs a per-composition spec file the user reads and edits between sessions to articulate design intent. This file is:

- **User-edited** (read/edit by both user and agent during dialogue refinement)
- **Plugin-owned** (created by progressive-skill-composer; format is its contract)
- **Cross-project for user-scope, project-bound for project-scope** (compositions can be either)

Putting plugin-owned user-edited content in the project root tree (per the original user-edited rule) would mix it with project-not-plugin artifacts and create naming collisions when multiple plugins want similar content kinds. Putting it in plugin data dir (per the bin-mediated rule) puts the agent through Read/Write hops via subprocess scripts every time the user wants to refine the spec, which defeats the dialogue UX.

### Decision

A fourth category extends the matrix:

| Category | Reader/writer | Location | Examples |
|---|---|---|---|
| Plugin-namespaced user-edited | User and agent edit/read directly; plugin owns the format and content shape | `<scope>/.claude/<plugin-name>-<author>/<concern>/` | A plugin maintaining user-editable config or templates separate from any specific skill |

The `<plugin-name>-<author>` segment matches Claude Code's plugin data dir convention so two plugins from different authors with the same name never collide. The `<concern>/` segment groups related artifacts within a single plugin (e.g. `templates/`, `configs/`).

This category sits under `.claude/` rather than at the project tree's top level because the content is plugin-owned (its format is the plugin's contract), not project content the user authored from scratch. The `.claude/` namespace already signals "tooling-related" to the user; namespacing under `.claude/<plugin>-<author>/` is a coherent extension.

### Consequences

- **Enables:** plugin-managed user-editable content with a stable filesystem home; multiple plugins coexist without colliding on `<scope>/.claude/<concern>/` paths; user-readable artifacts that survive between sessions and are version-controllable when scoped to a project
- **Constrains:** the agent's Read/Edit/Write tools hit the standard `.claude/` permission gate — first-touch per session prompts; subsequent edits typically pre-approved. Heavy-dialogue artifacts can allowlist their specific path (`<scope>/.claude/<plugin>-<author>/<concern>/**`) when friction surfaces. The original user-edited rule's "outside `.claude/`" guidance still applies to project-not-plugin content (logs, plans) — those don't move
- **Naming discipline:** the plugin-name + author segment matches the plugin's `name` and `author.name` fields in `plugin.json` (same convention Claude Code uses for `~/.claude/plugins/data/<plugin>-<author>/`); the concern segment uses a noun describing the content kind; content files at the leaf use the artifact's natural name. Avoid generic names like `data/` or `state/` — a future reader should infer the content kind from the directory name without reading inside

### Note on progressive-skill-composer (now `skill-authoring`)

progressive-skill-composer (renamed to `skill-authoring` 2026-05-12) initially exemplified this pattern (composition specs at `<scope>/.claude/progressive-skill-composer-a-horde-o-bees/compositions/<output>.md`) but moved away from it during Phase B redesign. Its compositions are now embedded inside the per-skill folder at `<scope>/.claude/skills/<name>/composition.md` because the recipe naturally travels with the skill. The plugin-namespaced extension remains valid for plugins that need plugin-managed user-edited content not tied to any specific skill.
