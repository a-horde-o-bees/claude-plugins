# OCD Architecture

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Three subsystems — hooks, rules, and skills — operate independently through the plugin lifecycle.

## Purpose

OCD shapes agent behavior at the project level. Hooks enforce permissions on every tool call without relying on prose instructions. Rules load into every conversation as always-on context. Skills provide agent-facing CLIs for project navigation and convention management. Each subsystem solves a distinct problem: hooks handle what the agent is *allowed* to do, rules handle *how* the agent should work, and skills handle *what infrastructure the agent can query*.

## Layers

```
Claude Code runtime
    ↓ hook events (SessionStart, PreToolUse)
Hook scripts (hooks/)
    ↓ JSON protocol (stdin/stdout)
Claude Code runtime
    ↓ rule loading
Rules (rules/)
    ↓ always-on context
Agent instructions (skills/*/SKILL.md)
    ↓ CLI invocation
Skill modules (skills/*/)
    ↓ SQL
SQLite databases (.claude/ocd/)
```

**Hooks** execute as subprocesses on Claude Code lifecycle events. They receive JSON on stdin and write JSON to stdout. No agent involvement — the runtime invokes them directly.

**Rules** are markdown files deployed to `.claude/rules/`. Claude Code loads them automatically every session. They shape agent behavior through always-on context, not enforcement.

**Skills** are agent-facing workflows (SKILL.md) backed by Python CLIs. The agent reads SKILL.md for instructions and invokes the CLI via Bash for data operations.

## Hooks

### PreToolUse: Permission Enforcement

`hooks/auto_approval/` — package that intercepts Bash, Edit, and Write tool calls. Two evaluation layers in fixed order:

**Layer 1: Hardcoded blocks** — structural constraints that do not stick as prose instructions. Blocks directory changes (`cd`, `pushd`, `popd`) and `cat` (use Read tool). Returns inline guidance so the agent self-corrects without user intervention.

**Layer 2: Dynamic settings enforcement** — reads and merges global (`~/.claude/settings.json`) and project (`.claude/settings.json`) allow/deny lists. Evaluates tool-specific patterns:

| Tool | Pattern format | Example |
|------|---------------|---------|
| Bash | `Bash(verb:*)`, `Bash(path/*)` | `Bash(git:*)` |
| Edit | Blanket `Edit` + directory check | `Edit` in allow list |
| Write | Blanket `Write` + directory check | `Write` in allow list |

Deny rules take precedence over allow rules. File paths resolve against allowed directories (project root + `additionalDirectories`). Compound commands (`&&`, `||`, `;`, `|`) split outside quotes and each part is evaluated independently — all parts must pass.

**Output protocol:**
- `approve()` — emit `permissionDecision: allow`
- `block(reason)` — emit `decision: block` with corrective guidance
- No output — fall through to Claude Code's default permission prompt

### PreToolUse: Convention Gate

`hooks/convention_gate.py` — intercepts Read, Edit, and Write tool calls. Calls `governance_match` from `lib/governance/` with the target file path and injects matched convention paths into `additionalContext`. Read invocations receive conventions as informational context; Edit and Write invocations receive a directive to conform and refactor immediately if non-conformant.

## Governance

Rules and conventions share a governance infrastructure implemented in `lib/governance/`. The library reads directly from disk on every call — no database, no caching. It scans `.claude/rules/` and `.claude/conventions/` directories, parses YAML frontmatter, and performs in-memory pattern matching.

**`governance_match`** takes file paths and returns applicable conventions. Rules are excluded by default (already in agent context); `include_rules=True` adds them for evaluation workflows.

**`governance_order`** computes level-grouped dependency ordering from `governed_by` frontmatter using Tarjan's SCC algorithm. Produces foundation-first levels for evaluation traversal. Detects dangling references and cycles.

**`governed_by`** frontmatter declares which governance entries a file builds on. Consumed at evaluation time by skills that walk the dependency chain — not consumed by runtime convention loading.

## Rules

Template files in `templates/rules/` deploy to `.claude/rules/` via `/init`. Users own the deployed copies — they can inspect, edit, or delete them.

| Rule | Scope |
|------|-------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Working directory, agents, testing — execution discipline for working in this project |
| `system-documentation.md` | README and architecture.md requirements per system, with nesting and currency rules |
| `process-flow-notation.md` | Structured programming notation for skill workflows |

Rules use the template-deployed model: templates in `templates/rules/` are the source of truth; deployed copies in `.claude/rules/ocd/` are derived. `scripts/sync-templates.py` syncs templates to deployed copies. A SessionEnd hook runs sync-templates automatically so the next session loads current rules.

## Skills

### Navigator

Project structure index in SQLite. Agents query by purpose ("what does this file do?") rather than by name or content.

**Modules:**

| Module | Responsibility |
|--------|---------------|
| `_db.py` | Schema, migrations, connection factory, seed rules from CSV |
| `_scanner.py` | Filesystem walking with rule-based pruning, git hash change detection |
| `_references.py` | File reference mapping — builds dependency DAG from skill, governance, and component references |
| `_skills.py` | Resolves skill names to SKILL.md paths across discovery locations |
| `__init__.py` | Business logic facade: paths, scan, scope analysis; re-exports from all modules |
| `__main__.py` | MCP server entry point with FastMCP tool registrations |
| `cli.py` | CLI entry point for operational commands (scan, describe) |
| `_init.py` | Initialize navigator database; report deployment states |

**Database schema:**

```
entries
├── path TEXT PK              — relative path from project root
├── parent_path TEXT          — parent directory path (indexed)
├── entry_type TEXT           — CHECK: file, directory
├── exclude INTEGER           — 1 = omit from scans and listings
├── traverse INTEGER          — 0 = list but don't descend (shallow)
├── description TEXT          — human-written purpose description
├── git_hash TEXT             — SHA-1 blob hash for change detection
└── stale INTEGER             — 1 = content changed since description written
```

**Rule-based pruning:** Pattern entries (paths containing `*`) control scanning behavior. Exclude patterns omit matching paths entirely. Shallow patterns (traverse=0) list directories without descending. Seed rules from `navigator_seed.csv` provide defaults for common excludes (`.git`, `node_modules`, `__pycache__`).

**Change detection:** Scanner computes git-compatible blob hashes (`blob {size}\0{content}`) and compares against stored hashes. Changed files are marked stale; stale propagates up to parent directories. Prescribed rules (patterns with descriptions) auto-apply descriptions to matching new files.

**Skill resolver** searches four discovery locations in Claude Code priority order: personal (`~/.claude/skills/`), project (`.claude/skills/`), plugin-dir (`$CLAUDE_PLUGIN_ROOT/skills/`), marketplace (from `installed_plugins.json`). First match by frontmatter `name` field wins.

### Other Skills

Workflow-only skills with no Python infrastructure (SKILL.md only):

| Skill | Purpose |
|-------|---------|
| `commit` | Topic-grouped commits with end-state descriptions |
| `push` | Push to remote with pre-push commit check |
| `init` | Deploy rules, conventions, and skill infrastructure |
| `status` | Report plugin version, rules state, skill status |
| `log` | Capture decisions, friction, problems, ideas as log entries |
| `pdf` | Export markdown to PDF with GitHub-style CSS |
| `evaluate-governance` | Evaluate governance chain conformity, followability, coherence |
| `evaluate-skill` | Evaluate a skill across conformity, efficacy, quality |
| `evaluate-documentation` | Evaluate README.md and architecture.md across systems |

## MCP Servers

Agent-facing tools exposed over the Model Context Protocol. Each server lives as a single file in `servers/` and is registered in `.mcp.json`. Claude Code starts the servers on session connect and routes tool calls by name.

| Server | Entry point | Role |
|--------|-------------|------|
| `navigator` | `servers/navigator/__main__.py` | Project structure index, governance discovery, reference mapping. Delegates to `servers/navigator` package for business logic. |
| `log` | `servers/log/__main__.py` | Unified project log across multiple types (decision, friction, problem, idea) with per-type tag management. |

## Libraries

Python packages consumed as imports — no MCP server, no subprocess. Located in `lib/`.

| Library | Package | Role |
|---------|---------|------|
| `governance` | `lib/governance/` | Convention and rule governance: matching files to applicable governance entries, listing entries, and computing the level-grouped dependency order. Reads directly from disk on every call — no database, no caching. Consumed by the convention gate hook, navigator's `scope_analyze`, the governance CLI, and evaluation skills. |

Server modules are thin presentation layers: tool handlers validate, delegate to a domain module, and serialize the result.

Server-level `instructions` fields publish when to reach for each server's tools; individual tool descriptions cover per-tool semantics.

`servers/_helpers.py` bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time when the variable is missing. Claude Code launches MCP subprocesses with cwd set to the project root but does not propagate the env var and does not expand variable references inside `.mcp.json` env block values. Every server module imports `_helpers` for `_ok`/`_err`, so the bootstrap fires at process start. This is the only cwd-derived project-directory source in the codebase; hooks, CLI, and tests must set `CLAUDE_PROJECT_DIR` explicitly. See `.claude/conventions/ocd/mcp-server.md` *MCP Subprocess Environment Bootstrap* for the full rationale.

## Plugin Framework

`plugin/` — generic deployment, formatting, skill discovery, and orchestration shared across plugins. Propagated identically to every plugin via pre-commit hook. Decomposed into 8 internal modules:

| Module | Responsibility |
|--------|---------------|
| `_environment.py` | Plugin path resolution (`get_project_dir`, `get_plugin_root`, `get_plugin_data_dir`) |
| `_metadata.py` | Plugin version, name, marketplace source discovery |
| `_deployment.py` | Template file deployment primitives (copy, stamp, compare, orphan clearing) |
| `_formatting.py` | Output column alignment and section rendering |
| `_content.py` | Deploy and state tracking for rules, conventions, patterns, logs |
| `_discovery.py` | System and workflow skill discovery |
| `_permissions.py` | Auto-approve pattern analysis, deployment, and cleanup |
| `_orchestration.py` | `run_init` and `run_status` entry points |

## Entry Points

All execution flows through `run.py`, which adds the plugin root to `sys.path` and runs the target module via `runpy.run_module`:

```
python3 run.py hooks.auto_approval          # Hook invocation
python3 run.py hooks.convention_gate        # Hook invocation
python3 run.py plugin init [--force]        # Init orchestration
python3 run.py plugin status                # Status reporting
python3 run.py servers.navigator.cli scan .     # Navigator CLI (operational)
```

Hooks are invoked by Claude Code via `hooks.json` configuration. Navigator agent-facing operations are exposed via MCP server (`servers/navigator.py`); CLI retained for operational commands (init, scan, governance-load). No shebangs or execute permissions — all scripts run via `python3` interpreter prefix.

## Concurrency

Navigator database uses WAL mode with 5-second busy timeout for concurrent access. Multiple agents can read simultaneously; writes queue behind the busy timeout.

## File Organization

```
plugins/ocd/
├── .claude-plugin/plugin.json   — plugin manifest (name, version, license)
├── hooks/
│   ├── hooks.json               — hook registration (SessionStart, SessionEnd, PreToolUse)
│   ├── install_deps.sh          — install/refresh plugin venv dependencies
│   ├── auto_approval/           — permission enforcement package (hardcoded + dynamic)
│   └── convention_gate.py       — surface applicable conventions on Read/Edit/Write
├── templates/
│   ├── rules/                   — rule templates (deployed to .claude/rules/ocd/)
│   ├── conventions/             — convention templates (deployed to .claude/conventions/ocd/)
│   ├── patterns/                — pattern templates (deployed to .claude/patterns/ocd/)
│   ├── logs/                    — log type templates (deployed to .claude/logs/)
│   └── settings.json            — recommended auto-approve patterns
├── lib/
│   └── governance/              — governance library (disk-only matching, listing, ordering)
├── servers/
│   └── navigator/               — MCP server package (project structure index)
├── skills/
│   ├── navigator/               — navigator maintenance workflow
│   ├── commit/                  — topic-grouped commits
│   ├── push/                    — push with pre-push checks
│   ├── init/                    — deployment orchestration
│   ├── status/                  — plugin status reporting
│   ├── log/                     — log entry capture
│   ├── pdf/                     — markdown-to-PDF export
│   ├── evaluate-governance/     — governance chain evaluation
│   ├── evaluate-skill/          — skill quality evaluation
│   └── evaluate-documentation/  — system documentation evaluation
├── plugin/                      — generic plugin framework (8 modules, shared across plugins)
├── run.py                       — module launcher with package context
└── tests/                       — hook and invocation tests
```
