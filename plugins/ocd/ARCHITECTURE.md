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
Rules (rules/)
    ↓ always-on context
Agent instructions (systems/*/SKILL.md)
    ↓ CLI invocation
Subsystem modules (systems/*/)
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

**Output protocol.** Both layers speak Claude Code's `hookSpecificOutput` schema:
- `approve()` — emit `permissionDecision: allow`
- `block(reason)` — emit `permissionDecision: deny` with `permissionDecisionReason` carrying corrective guidance; Claude Code relays the reason to the agent
- Unhandled exception — dispatch is wrapped in a fail-open try/except that writes one stderr line and exits 0, so a crash never blocks a tool call; Claude Code's default permission prompt takes over
- No output — fall through to Claude Code's default permission prompt

### PreToolUse: Convention Gate

`hooks/convention_gate.py` — intercepts Read, Edit, and Write tool calls. Calls `governance_match` from `systems/governance/` with the target file path and injects matched convention paths into `additionalContext`. Read invocations receive conventions as informational context; Edit and Write invocations receive a directive to conform and refactor immediately if non-conformant.

## Governance

Rules and conventions share a governance infrastructure implemented in `systems/governance/`. The library reads directly from disk on every call — no database, no caching. It scans `.claude/rules/` and `.claude/conventions/` directories, parses YAML frontmatter, and performs in-memory pattern matching.

**`governance_match`** takes file paths and returns applicable conventions. Rules are excluded by default (already in agent context); `include_rules=True` adds them for evaluation workflows.

**`governance_order`** computes level-grouped dependency ordering from `governed_by` frontmatter using Tarjan's SCC algorithm. Produces foundation-first levels for evaluation traversal. Detects dangling references and cycles.

**`governed_by`** frontmatter declares which governance entries a file builds on. Consumed at evaluation time by skills that walk the dependency chain — not consumed by runtime convention loading.

## Rules

Plugin-wide rule templates in `systems/rules/templates/` deploy to `.claude/rules/ocd/` via `/ocd:setup init`. Users own the deployed copies — they can inspect, edit, or delete them.

| Rule | Scope |
|------|-------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Working directory, agents, testing — execution discipline for working in this project |
| `system-docs.md` | README and ARCHITECTURE.md requirements per system, including the Subsystem Doc Consolidation rule and purpose-statement propagation |
| `process-flow-notation.md` | Structured programming notation for skill workflows |
| `markdown.md` | Base content standards for markdown files |

System-owned rules live alongside the system that prescribes them — `systems/<name>/rules/` — and deploy flat under `.claude/rules/ocd/systems/<name>.md` via the system's own init per System Dormancy (see marketplace-level `ARCHITECTURE.md`). Today navigator owns `navigator.md` (navigator usage guidance), log owns `log.md` (log type selection and routing), and refactor owns `refactor.md` (when to reach for `/ocd:refactor` over manual sed or Edit). The `systems/` subdir inside `.claude/rules/ocd/` namespaces system-scoped rules away from project-wide foundational rules, so filenames can match system names without colliding.

Rules use the template-deployed model: sources are authoritative; deployed copies in `.claude/rules/ocd/` are derived artifacts tracked in git so the rectified state travels with the repo. A guard hook blocks direct edits to deployed copies so changes only flow template → deployed. `/checkpoint` runs `scripts/auto_init.py` (the auto-init orchestrator) to rectify deployed state against current templates.

## Skills

Skill packages live under `systems/` (declared via `plugin.json`'s `skills` field). Each contains at minimum a `SKILL.md` describing the workflow. Some include extracted component files (`_*.md`) for subflows that only run on optional execution paths. Per the Subsystem Doc Consolidation rule in `system-docs.md`, skills' operational reference IS `SKILL.md` — no separate README or architecture is required; purpose statements below are propagated from each skill's frontmatter `description` field.

**Skills:**

| Skill | Purpose (from SKILL.md frontmatter) |
|-------|-------------------------------------|
| `init` | Initialize ocd conventions and skill infrastructure in current project |
| `status` | Report plugin infrastructure state |
| `navigator` | Sync navigator database with filesystem and describe entries that need descriptions |
| `git` | Manage local git history — record commits grouped by topic and push a branch to origin. Sandbox-based feature lifecycle (new, pack, open, close, unpack, list) lives under /ocd:sandbox. |
| `log` | Capture or manage project log entries — decisions, friction, problems, ideas |
| `pdf` | Export markdown files to PDF using WeasyPrint |
| `sandbox` | Work on an isolated sandbox of the project — durable feature boxes (new, pack, open, close, unpack, list) for in-flight development that parallel sessions can drive without clobbering each other, and ephemeral sandboxes (exercise, tests, cleanup) for fresh-install or interactive validation against the current tree. All substrates share one sibling-path convention, one permission rule, and one cleanup sweep. |

## MCP Servers

Agent-facing tools exposed over the Model Context Protocol. The plugin registers servers in `.mcp.json`; Claude Code starts them on session connect and routes tool calls by name. Per the Subsystem Doc Consolidation rule, thin MCP adapters that delegate business logic to a domain library do not require their own README or architecture — their purpose statement lives in the server module's docstring.

| Server | Entry point | Purpose (from module docstring) |
|--------|-------------|----------------------------------|
| `navigator` | `systems/navigator/server.py` | Agent-facing tools for project structure navigation, governance discovery, reference mapping, and scope analysis. Thin presentation layer over `systems/navigator/`. |

`systems/navigator/_server_helpers.py` bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time when the variable is missing. Claude Code launches MCP subprocesses with cwd set to the project root but does not propagate the env var and does not expand variable references inside `.mcp.json` env block values. The server module imports `_helpers` for `_ok`/`_err` response envelopes, so the bootstrap fires at process start. This is the only cwd-derived project-directory source in the plugin; hooks and CLI must set `CLAUDE_PROJECT_DIR` explicitly.

## Libraries

Python packages consumed as imports. Each is a subsystem under `systems/`; substantial ones document their architecture separately, while thin subsystems consolidate their purpose into a README. This section is the plugin-level overview.

| Library | Package | Purpose | Docs |
|---------|---------|---------|------|
| `rules` | `systems/rules/` | Rules subsystem — deploys markdown rule templates to `.claude/rules/<plugin>/` as always-on agent context. | [README](systems/rules/README.md) |
| `conventions` | `systems/conventions/` | Conventions subsystem — deploys convention templates to `.claude/conventions/<plugin>/` for file-governance via `governed_by` frontmatter. | [README](systems/conventions/README.md) |
| `logs` | `systems/log/` | Logs subsystem — deploys per-type templates to the shared `logs/<type>/` pool at project root (unnamespaced; contributes to project-level log types). | [README](systems/log/README.md) |
| `permissions` | `systems/permissions/` | Permissions subsystem — reports auto-approve coverage; specialized CLI ops (`status`, `install`, `analyze`, `clean`) manage recommended patterns across project and user scopes. | [README](systems/permissions/README.md) |
| `governance` | `systems/governance/` | Convention and rule governance library: match files to applicable governance entries, list entries by kind, and compute the dependency-ordered level grouping. Reads directly from disk on every call — no database, no caching. | [README](systems/governance/README.md) · [ARCHITECTURE.md](systems/governance/ARCHITECTURE.md) |
| `navigator` | `systems/navigator/` | Project structure index backed by SQLite. Maintains a queryable directory of project files and directories with human-written descriptions agents use to decide whether to open a file. | [README](systems/navigator/README.md) · [ARCHITECTURE.md](systems/navigator/ARCHITECTURE.md) |

Consumers within this plugin: the `convention_gate` hook imports `systems.governance`; the navigator MCP server imports `systems.navigator`; plugin orchestration (`run_init` / `run_status`) discovers and calls every `systems/*/_init.py` uniformly for per-subsystem deployment and reporting.

## Always-On Primitives

`tools/` — path and error primitives vendored into every plugin. Ships with the plugin and is importable before any system is activated, so hooks fired on the critical path (auto_approval PreToolUse, SessionStart) can resolve project and plugin directories and raise typed errors without depending on lifecycle state. Canonical sources live at project-root `tools/`; each plugin's own `plugins/<name>/tools/` holds propagated copies maintained by the pre-commit hook.

| Module | Responsibility |
|--------|---------------|
| `environment.py` | Path resolution (`get_project_dir`, `get_plugin_root`, `get_plugin_data_dir`, `get_claude_home`, `get_git_root_for`) |
| `errors.py` | Shared exception types (`NotReadyError`) |

## Setup Package

`systems/setup/` — install/init/status/enable/disable orchestration plus the `/ocd:setup` skill. Opt-in like every other system; activated via `/ocd:setup`. Propagated identically to every plugin via pre-commit hook so each plugin exposes the same administrative surface. Internal modules:

| Module | Responsibility |
|--------|---------------|
| `_metadata.py` | Plugin version, name, marketplace source discovery |
| `_deployment.py` | Template file deployment primitives (copy, compare, orphan clearing) |
| `_enabled.py` | Per-system opt-in state (`enabled-systems.json`) — read, toggle, persist |
| `_formatting.py` | Output column alignment and section rendering |
| `_system_discovery.py` | System and workflow skill discovery |
| `_orchestration.py` | `run_init`, `run_status`, `run_enable`, `run_disable` entry points — discover every enabled subsystem and dispatch uniformly |

## Entry Points

All execution flows through `run.py`, which adds the plugin root to `sys.path` and runs the target module via `runpy.run_module`:

```
ocd-run hooks.auto_approval          # Hook invocation
ocd-run hooks.convention_gate        # Hook invocation
ocd-run setup <verb>                 # Setup — init | status | enable | disable | guided
ocd-run navigator <verb>             # Navigator CLI — scan | describe | list | search | set | resolve-skill | init
ocd-run check <dimension>            # Discipline checks (dormancy today)
ocd-run governance <verb>            # Governance queries — match | list | order
ocd-run refactor <tool>              # Mass transformation primitives (rename-symbol)
ocd-run sandbox <verb>               # Sandbox substrate primitives (worktree-add, cleanup, ...)
ocd-run pdf --src ... --dest ...     # PDF export
```

Hooks are invoked by Claude Code via `hooks.json` configuration. Navigator agent-facing operations are exposed via MCP server (`systems/navigator/server.py`); CLI retained for operational commands (init, scan, governance-load). No shebangs or execute permissions — all scripts run via `python3` interpreter prefix.

## Concurrency

Navigator database uses WAL mode with 5-second busy timeout for concurrent access. Multiple agents can read simultaneously; writes queue behind the busy timeout.

## File Organization

```
plugins/ocd/
├── .claude-plugin/plugin.json   — plugin manifest (name, version, description, homepage)
├── .mcp.json                    — MCP server registration (navigator)
├── ARCHITECTURE.md              — this document
├── README.md                    — user-facing overview and setup
├── LICENSE                      — MIT
├── pyproject.toml               — Python runtime dependencies (installed into plugin venv by install_deps.sh)
├── run.py                       — module launcher with package context
├── bin/
│   └── ocd-run                  — plugin CLI — resolves venv and dispatches to systems
├── hooks/
│   ├── hooks.json               — hook registration (SessionStart, PreToolUse)
│   ├── install_deps.sh          — install/refresh plugin venv dependencies
│   ├── auto_approval/           — permission enforcement package (hardcoded + dynamic)
│   └── convention_gate.py       — surface applicable conventions on Read/Edit/Write
├── tools/                       — always-on primitives (environment, errors) vendored from project root
└── systems/                     — every cohesive unit lives here (domain Python + skill + templates colocated)
    ├── check/                   — discipline-check skill (dormancy today)
    ├── conventions/             — deployable convention templates
    ├── git/                     — git skill (commit, push)
    ├── governance/              — rules/conventions governance library (no SKILL.md; lib + CLI only)
    ├── log/                     — log entry capture skill and deployable log-type templates
    ├── navigator/               — project structure index (SKILL.md + CLI + MCP server + library)
    ├── pdf/                     — markdown-to-PDF skill via WeasyPrint
    ├── permissions/             — permission pattern management (settings.json asset)
    ├── refactor/                — mass source transformation skill
    ├── rules/                   — deployable rule templates
    ├── sandbox/                 — isolated sandbox skill (durable + ephemeral substrates)
    └── setup/                   — install/init/status orchestration (and `/ocd:setup` skill)
```
