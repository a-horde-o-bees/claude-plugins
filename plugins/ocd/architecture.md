# OCD Architecture

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. This document covers the plugin's internal layers, components, and relationships.

## Purpose

OCD shapes agent behavior at the project level. Hooks enforce permissions on every tool call without relying on prose instructions. Rules load into every conversation as always-on context. Skills provide agent-facing workflows for project navigation, committing, pushing, logging, and documentation export. Each subsystem solves a distinct problem: hooks handle what the agent is *allowed* to do, rules handle *how* the agent should work, skills handle *what workflows the agent can invoke*, and MCP servers + libraries handle *what infrastructure the agent can query*.

## Layers

```
Claude Code runtime
    ↓ hook events (SessionStart, PreToolUse)
Hook scripts (hooks/)
    ↓ JSON protocol (stdin/stdout)
Claude Code runtime
    ↓ rule loading
Rules (.claude/rules/ocd/ after deployment)
    ↓ always-on context
Agent instructions (skills/*/SKILL.md)
    ↓ CLI / MCP tool invocation
Domain libraries (lib/)
    ↓ SQL / filesystem
SQLite database + .claude/ governance directories
```

**Hooks** execute as subprocesses on Claude Code lifecycle events. They receive JSON on stdin and write JSON to stdout. No agent involvement — the runtime invokes them directly.

**Rules** are markdown files deployed to `.claude/rules/`. Claude Code loads them automatically every session. They shape agent behavior through always-on context, not enforcement.

**Skills** are agent-facing workflows (`SKILL.md`) optionally backed by Python CLIs. The agent reads SKILL.md for instructions and invokes CLIs via Bash or MCP tools for data operations.

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

### SessionStart: Dependency Install

`hooks/install_deps.sh` — creates a plugin-local virtual environment under `${CLAUDE_PLUGIN_DATA}/venv/` and installs `requirements.txt`. Idempotent — detects whether the venv exists and whether requirements have changed before reinstalling.

## Governance

Rules and conventions share a governance infrastructure implemented in `lib/governance/`. The library reads directly from disk on every call — no database, no caching. It scans `.claude/rules/` and `.claude/conventions/` directories, parses YAML frontmatter, and performs in-memory pattern matching.

**`governance_match`** takes file paths and returns applicable conventions. Rules are excluded by default (already in agent context); `include_rules=True` adds them for evaluation workflows.

**`governance_order`** computes level-grouped dependency ordering from `governed_by` frontmatter using Tarjan's SCC algorithm. Produces foundation-first levels for evaluation traversal. Detects dangling references and cycles.

**`governed_by`** frontmatter declares which governance entries a file builds on. Consumed at evaluation time by downstream tooling that walks the dependency chain — not consumed by runtime convention loading.

## Rules

Template files in `templates/rules/` deploy to `.claude/rules/ocd/` via `/ocd:init`. Users own the deployed copies — they can inspect, edit, or delete them.

| Rule | Scope |
|------|-------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Working directory, agents, testing — execution discipline |
| `system-documentation.md` | README and architecture.md requirements per system, with nesting and currency rules |
| `process-flow-notation.md` | Structured programming notation for skill workflows |
| `log-routing.md` | When and how to capture decisions, friction, problems, and ideas as log entries |
| `markdown.md` | Base content standards for markdown files |

## Skills

Skill packages live under `skills/`. Each contains at minimum a `SKILL.md` describing the workflow. Some include extracted component files (`_*.md`) for subflows that only run on optional execution paths. Per the Subsystem Doc Consolidation rule in `system-documentation.md`, skills' operational reference IS `SKILL.md` — no separate README or architecture is required; purpose statements below are propagated from each skill's frontmatter `description` field.

| Skill | Purpose (from SKILL.md frontmatter) |
|-------|-------------------------------------|
| `init` | Initialize ocd conventions and skill infrastructure in current project |
| `status` | Report plugin infrastructure state |
| `navigator` | Sync navigator database with filesystem and describe entries that need descriptions |
| `commit` | Commit working tree changes grouped by topic for readable git history |
| `push` | Push local commits to a named branch on the remote |
| `log` | Capture or manage project log entries — decisions, friction, problems, ideas |
| `md-to-pdf` | Export markdown files to PDF styled with GitHub-flavored CSS |

## MCP Servers

Agent-facing tools exposed over the Model Context Protocol. The plugin registers servers in `.mcp.json`; Claude Code starts them on session connect and routes tool calls by name. Per the Subsystem Doc Consolidation rule, thin MCP adapters that delegate business logic to a domain library do not require their own README or architecture — their purpose statement lives in the server module's docstring.

| Server | Entry point | Purpose (from module docstring) |
|--------|-------------|----------------------------------|
| `navigator` | `servers/navigator.py` | Agent-facing tools for project structure navigation, governance discovery, reference mapping, and scope analysis. Thin presentation layer over `lib/navigator/`. |

`servers/_helpers.py` bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time when the variable is missing. Claude Code launches MCP subprocesses with cwd set to the project root but does not propagate the env var and does not expand variable references inside `.mcp.json` env block values. The server module imports `_helpers` for `_ok`/`_err` response envelopes, so the bootstrap fires at process start. This is the only cwd-derived project-directory source in the plugin; hooks and CLI must set `CLAUDE_PROJECT_DIR` explicitly.

## Libraries

Python packages consumed as imports. Each is a subsystem with its own README.md and architecture.md; this section is the plugin-level overview.

| Library | Package | Purpose | Docs |
|---------|---------|---------|------|
| `governance` | `lib/governance/` | Convention and rule governance library: match files to applicable governance entries, list entries by kind, and compute the dependency-ordered level grouping. Reads directly from disk on every call — no database, no caching. | [README](lib/governance/README.md) · [architecture.md](lib/governance/architecture.md) |
| `navigator` | `lib/navigator/` | Project structure index backed by SQLite. Maintains a queryable directory of project files and directories with human-written descriptions agents use to decide whether to open a file. | [README](lib/navigator/README.md) · [architecture.md](lib/navigator/architecture.md) |

Consumers within this plugin: the `convention_gate` hook imports `lib.governance`; the navigator MCP server imports `lib.navigator`; plugin orchestration (`run_init` / `run_status`) imports `lib/*/_init.py` for per-library bootstrap and reporting.

## Plugin Framework

`plugin/` — generic deployment, formatting, discovery, and orchestration shared across plugins. Contains no plugin-specific logic; `lib/*/_init.py` modules in each domain library provide subsystem-specific bootstrap.

| Module | Responsibility |
|--------|---------------|
| `_environment.py` | Plugin path resolution (`get_project_dir`, `get_plugin_root`, `get_plugin_data_dir`) |
| `_metadata.py` | Plugin version, name, marketplace source discovery |
| `_deployment.py` | Template file deployment primitives (copy, stamp, compare, orphan clearing) |
| `_formatting.py` | Output column alignment and section rendering |
| `_content.py` | Deploy and state tracking for rules, conventions, patterns, logs |
| `_discovery.py` | Library subsystem and workflow skill discovery (glob `lib/*/_init.py` for MCP Servers grouping) |
| `_permissions.py` | Auto-approve pattern analysis, deployment, and cleanup |
| `_orchestration.py` | `run_init` and `run_status` entry points; wraps discovered subsystems under an "MCP Servers" output heading |

## Entry Points

All execution flows through `run.py`, which adds the plugin root to `sys.path` and runs the target module via `runpy.run_module`:

```
python3 run.py hooks.auto_approval          # Hook invocation
python3 run.py hooks.convention_gate        # Hook invocation
python3 run.py plugin init [--force]        # Init orchestration
python3 run.py plugin status                # Status reporting
python3 run.py lib.navigator scan .         # Navigator CLI (operational)
python3 run.py lib.governance order --json  # Governance CLI (operational)
python3 run.py servers.navigator            # MCP server (launched by Claude Code)
```

Hooks are invoked by Claude Code via `hooks.json` configuration. Navigator agent-facing operations are exposed via the MCP server (`servers/navigator.py`); CLI is retained for operational commands (init, scan, describe, etc.). No shebangs or execute permissions — all scripts run via `python3` interpreter prefix.

## Concurrency

Navigator database uses WAL mode with a 5-second busy timeout for concurrent access. Multiple agents can read simultaneously; writes queue behind the busy timeout.

## File Organization

```
plugins/ocd/
├── .claude-plugin/plugin.json   — plugin manifest (name, version, license)
├── .mcp.json                    — MCP server registration
├── hooks/
│   ├── hooks.json               — hook registration (SessionStart, PreToolUse)
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
│   ├── governance/              — governance library (disk-only matching, listing, ordering)
│   └── navigator/               — navigator library (SQLite-backed project index)
├── servers/
│   └── navigator.py             — MCP server (thin adapter over lib/navigator)
├── skills/
│   ├── init/                    — deployment orchestration
│   ├── status/                  — plugin status reporting
│   ├── navigator/               — navigator maintenance workflow
│   ├── commit/                  — topic-grouped commits
│   ├── push/                    — push with pre-push checks and first-push handling
│   ├── log/                     — log entry capture (add/list/remove as component subflows)
│   └── md-to-pdf/               — markdown-to-PDF export (uses global `md-to-pdf` CLI)
├── plugin/                      — generic plugin framework (8 modules)
├── requirements.txt             — Python dependencies installed into plugin venv
├── run.py                       — module launcher with package context
└── README.md                    — consumer-facing overview
```
