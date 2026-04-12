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

`hooks/auto_approval.py` — intercepts Bash, Edit, and Write tool calls. Two evaluation layers in fixed order:

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

## Rules

Template files in `rules/` deploy to `.claude/rules/` via `/init`. Users own the deployed copies — they can inspect, edit, or delete them.

| Rule | Scope |
|------|-------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Working directory, agents, testing — execution discipline for working in this project |
| `system-documentation.md` | README and architecture.md requirements per system, with nesting and currency rules |
| `process-flow-notation.md` | Structured programming notation for skill workflows |

Rules use the template-deployed model: templates in `rules/` are the source during plugin development; deployed copies in `.claude/rules/` are the product. `scripts/sync-templates.py` syncs deployed back to templates before commits.

## Skills

### Navigator

Project structure index in SQLite. Agents query by purpose ("what does this file do?") rather than by name or content.

**Modules:**

| Module | Responsibility |
|--------|---------------|
| `_db.py` | Schema, migrations, connection factory, seed rules from CSV |
| `_scanner.py` | Filesystem walking with rule-based pruning, git hash change detection |
| `_frontmatter.py` | Governance frontmatter parsing: pattern and depends from files |
| `_governance.py` | Governance loading, matching, ordering, and analysis |
| `__init__.py` | Business logic facade: describe, list, search, set, remove; re-exports from all modules |
| `__main__.py` | CLI entry point with argparse |
| `_init.py` | Deploy conventions, manifest, and database; report deployment states |
| `_skills.py` | Resolves skill names to SKILL.md paths across discovery locations |

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
| `commit` | Structured commit workflow with topic grouping |
| `push` | Push to remote with pre-push commit check |
| `init` | Deploy rules, conventions, and skill infrastructure |
| `status` | Report plugin version, rules state, skill status |
| `pdf` | Export markdown to PDF with GitHub-style CSS |

## MCP Servers

Agent-facing tools exposed over the Model Context Protocol. Each server lives as a single file in `servers/` and is registered in `.mcp.json`. Claude Code starts the servers on session connect and routes tool calls by name.

| Server | Entry point | Role |
|--------|-------------|------|
| `navigator` | `servers/navigator/__main__.py` | Project structure index, governance discovery, reference mapping. Delegates to `servers/navigator` package for business logic. |
| `governance` | `servers/governance/__main__.py` | Convention and rule governance: loading, matching, ordering, and dependency analysis. |
| `log` | `servers/log/__main__.py` | Unified project log across multiple types (decision, friction, problem, idea) with per-type tag management. |

Server modules are thin presentation layers: tool handlers validate, delegate to a domain module, and serialize the result.

Server-level `instructions` fields publish when to reach for each server's tools; individual tool descriptions cover per-tool semantics.

`servers/_helpers.py` bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time when the variable is missing. Claude Code launches MCP subprocesses with cwd set to the project root but does not propagate the env var and does not expand variable references inside `.mcp.json` env block values. Every server module imports `_helpers` for `_ok`/`_err`, so the bootstrap fires at process start. This is the only cwd-derived project-directory source in the codebase; hooks, CLI, and tests must set `CLAUDE_PROJECT_DIR` explicitly. See `.claude/conventions/ocd/mcp-server.md` *MCP Subprocess Environment Bootstrap* for the full rationale.

## Plugin Framework

`plugin/__init__.py` — generic deployment, formatting, skill discovery, and orchestration shared across plugins. Propagated identically to every plugin via pre-commit hook.

Key operations:

- **Deploy** — copy template files to target directory, stamp `type: template` → `type: deployed` in frontmatter, detect absent/current/divergent states
- **Skill discovery** — scan `skills/*/SKILL.md`, distinguish infrastructure skills (have `_init.py`) from bare skills (SKILL.md only)
- **Permissions** — compare recommended auto-approve patterns against project and user settings, merge additively
- **Marketplace** — resolve source version from local-directory marketplaces for update detection

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
│   ├── hooks.json               — hook registration (SessionStart install_deps, PreToolUse)
│   ├── install_deps.sh          — install/refresh plugin venv dependencies
│   ├── auto_approval.py         — permission enforcement (hardcoded + dynamic)
│   └── convention_gate.py       — surface applicable conventions on Read/Edit/Write
├── rules/                       — rule templates (source of truth during development)
├── conventions/                 — convention templates (deployed to .claude/conventions/)
├── templates/
│   └── settings.json            — recommended auto-approve patterns
├── skills/
│   ├── navigator/               — project structure index, convention deployment (SQLite + CLI)
│   ├── commit/                  — structured commit workflow
│   ├── push/                    — push with pre-push checks
│   ├── init/                    — deployment orchestration
│   ├── status/                  — plugin status reporting
│   └── pdf/                     — markdown-to-PDF export
├── servers/                     — MCP servers (navigator, governance, log)
├── plugin/                      — generic plugin framework (shared across plugins)
├── patterns/                    — reusable agent workflow patterns
├── run.py                       — module launcher with package context
└── tests/                       — hook and invocation tests
```
