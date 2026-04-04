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

### SessionStart: Plugin Root Persistence

`hooks/session_start.py` — writes `CLAUDE_PLUGIN_ROOT` to `.claude/ocd/.plugin_root` so agent Bash commands can resolve the plugin directory. Hook execution context provides the environment variable; agent Bash commands do not.

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

Template files in `rules/` deploy to `.claude/rules/` via `/ocd-init`. Users own the deployed copies — they can inspect, edit, or delete them.

| Rule | Scope |
|------|-------|
| `ocd-design-principles.md` | Foundational principles governing all artifacts |
| `ocd-communication.md` | Agent-user interaction triggers and alignment gates |
| `ocd-workflow.md` | Working directory discipline, testing, system documentation |
| `ocd-process-flow-notation.md` | Structured programming notation for skill workflows |
| `ocd-navigator.md` | Navigator CLI usage guide loaded as always-on context |

Rules use the template-deployed model: templates in `rules/` are the source during plugin development; deployed copies in `.claude/rules/` are the product. `scripts/sync-templates.py` syncs deployed back to templates before commits.

## Skills

### Navigator

Project structure index in SQLite. Agents query by purpose ("what does this file do?") rather than by name or content.

**Modules:**

| Module | Responsibility |
|--------|---------------|
| `_db.py` | Schema, migrations, connection factory, seed rules from CSV |
| `_scanner.py` | Filesystem walking with rule-based pruning, git hash change detection |
| `_manifest.py` | Manifest parsing: governance entries and settings |
| `__init__.py` | Business logic facade: describe, list, search, scan, set, remove |
| `__main__.py` | CLI entry point with argparse |
| `_init.py` | Deploy conventions, manifest, and database; report deployment states |
| `skill_resolver.py` | Resolves skill names to SKILL.md paths across discovery locations |

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
python3 run.py hooks.session_start          # Hook invocation
python3 run.py hooks.auto_approval          # Hook invocation
python3 run.py plugin init [--force]        # Init orchestration
python3 run.py plugin status                # Status reporting
python3 run.py skills.navigator describe .  # Navigator CLI
```

Hooks are invoked by Claude Code via `hooks.json` configuration. Agent-facing CLIs are invoked by agents via Bash during skill execution. No shebangs or execute permissions — all scripts run via `python3` interpreter prefix.

## Concurrency

Navigator database uses WAL mode with 5-second busy timeout for concurrent access. Multiple agents can read simultaneously; writes queue behind the busy timeout.

## File Organization

```
plugins/ocd/
├── .claude-plugin/plugin.json   — plugin manifest (name, version, license)
├── hooks/
│   ├── hooks.json               — hook registration (SessionStart, PreToolUse)
│   ├── session_start.py         — persist plugin root for agent access
│   └── auto_approval.py         — permission enforcement (hardcoded + dynamic)
├── rules/                       — rule templates (source of truth during development)
├── conventions/                 — convention templates (deployed to .claude/ocd/conventions/)
├── manifest.yaml                — governance manifest (rules + conventions ownership)
├── templates/
│   └── settings.json            — recommended auto-approve patterns
├── skills/
│   ├── navigator/               — project structure index, convention deployment (SQLite + CLI)
│   ├── commit/                  — structured commit workflow
│   ├── push/                    — push with pre-push checks
│   ├── init/                    — deployment orchestration
│   ├── status/                  — plugin status reporting
│   └── pdf/                     — markdown-to-PDF export
├── plugin/                      — generic plugin framework (shared across plugins)
├── patterns/                    — reusable agent workflow patterns
├── run.py                       — module launcher with package context
└── tests/                       — hook and invocation tests
```
