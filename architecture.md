# Marketplace Architecture

Claude Code plugin marketplace packaging one released plugin and one in-development plugin with shared development infrastructure. Each plugin is an independent system with its own architecture; this document covers how they are packaged, developed, and delivered.

## Layers

```
Claude Code plugin runtime
    ↓ marketplace resolution
Marketplace manifest (.claude-plugin/marketplace.json)
    ↓ plugin source paths
Plugins (plugins/ocd/, plugins/blueprint/)
    ↓ own entry points, hooks, skills
Plugin internals (see per-plugin architecture.md)
```

## Plugins

| Plugin | Status | Purpose | Architecture |
|--------|--------|---------|-------------|
| [ocd](plugins/ocd/) | Active (v0.1.0 released) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation | [architecture.md](plugins/ocd/architecture.md) |
| [blueprint](plugins/blueprint/) | In development | Structured solution research and implementation planning through entity-based analysis | [architecture.md](plugins/blueprint/architecture.md) |

Plugins are independent systems — each has its own manifest, hooks, skills, rules, and tests. Blueprint depends on ocd at the skill level (uses ocd's navigator and conventions infrastructure) but operates independently at the plugin level. The released version of ocd lives on the `v0.1.0` release branch; blueprint is still under main-branch development and not yet released.

Each plugin may register Claude Code hooks (PreToolUse, PostToolUse, SessionStart), MCP servers for persistent tooling (SQLite-backed, launched as subprocesses with per-server data directories under `.claude/<plugin>/`), and skills (discoverable by Claude Code at configured skill paths). The specific hooks, servers, and skills each plugin provides are documented in that plugin's own `architecture.md`.

## Marketplace

The marketplace manifest at `.claude-plugin/marketplace.json` registers both plugins with source paths relative to the repository root. Claude Code resolves these paths when users install from the marketplace.

Distribution: users add the GitHub repository as a marketplace source, then install individual plugins. Each plugin installs to `~/.claude/plugins/` with its own lifecycle (init, status, update).

## Three-Document Model

Every system boundary in this project — the repository root, each plugin, each skill that carries agent procedures — maintains a consistent set of documents, each targeting one consumer perspective:

- **`README.md`** — user-facing. What the system does, how to install and use it. At the repository root, the README targets developers and contributors working on the marketplace; at plugin and subsystem boundaries, the README targets the end users of that component.
- **`architecture.md`** — developer-facing. Layers, components, relationships, and key implementation details. A parent `architecture.md` describes each subsystem's role in the overall composition and links to the subsystem's own `architecture.md` for internals, rather than re-explaining what belongs to the subsystem.
- **`CLAUDE.md`** or **`SKILL.md`** — agent-facing. Present only when the system has agent-facing procedures. Opens by directing the agent to read the sibling `architecture.md` before acting. Contains procedures, workflow rules, and tool invocation patterns; structural context is read from `architecture.md` rather than embedded inline.

Readers navigate from general to specific through the nesting chain. A parent document answers "how do these pieces fit together"; each subsystem's documents answer "how does this piece work internally." Neither layer re-explains content that belongs to the other.

## Governance Delivery

The project delivers three kinds of agent guidance, each loaded through a mechanism suited to its scope.

**Rules** live in `.claude/rules/` and load into every session automatically via Claude Code's built-in rule auto-loading. Rules encode project-wide behavioral guidance — the agent follows them regardless of which file it is touching. A rule file contains the guidance the agent should consult at every step.

**Conventions** live in `.claude/conventions/` and load on demand. A PreToolUse hook on Read, Edit, and Write calls the navigator's `governance_match` with the target file path and surfaces matching convention files as additional tool-call context. This keeps session context focused — an agent editing a Python file sees the Python convention, an agent editing a markdown file sees the markdown convention, and neither sees the other. A convention file contains the content standards its target file type must meet.

**Operational documents** — `CLAUDE.md` at system boundaries, `SKILL.md` inside skill packages — load when Claude Code discovers them. They carry the procedures the agent follows when performing work within the system they describe.

Rules govern how the agent behaves. Conventions govern what a file contains. Operational documents govern how operations are performed. Guidance that applies regardless of which file is touched belongs in a rule; guidance that applies only to a specific file type belongs in a convention; step-by-step procedures for a named operation belong in an operational document.

## Shared Infrastructure

### Plugin Framework

`plugin/__init__.py` in each plugin is identical — a generic framework for deployment, formatting, skill discovery, and init/status orchestration. Propagated across plugins by a pre-commit hook. Contains no plugin-specific logic; each plugin's skill `_init.py` modules provide their own infrastructure.

### Template-Deployed Model

Templates live in plugin source (`plugins/<plugin>/templates/rules/`, `plugins/<plugin>/templates/conventions/`, `plugins/<plugin>/templates/patterns/`, `plugins/<plugin>/templates/logs/`). Init deploys copies to the consumer's project (`.claude/rules/`, `.claude/conventions/`, `.claude/patterns/`, `.claude/logs/`). Users edit deployed copies; `scripts/sync-templates.py` syncs deployed content back to templates before commits (main branch only — release branches don't carry the sync script). Governance metadata (`includes`, `excludes`, `governed_by`) lives in each file's YAML frontmatter; the governance library reconciles rules and conventions against disk state on every query, so entries stay current without an explicit registration step.

### Development Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sync-templates.py` | Sync deployed copies back to template files; called by pre-commit hook |
| `scripts/run-plugin.sh` | Run plugin CLI with correct environment variables for local development |
| `scripts/test.sh` | Run full test suite across project and all plugins |
| `scripts/pyextract.py` | Utility for extracting Python code blocks from markdown |

These are dev-only — stripped from release branches.

### Testing

Project-level tests in `tests/`, per-plugin tests isolated by `pytest.ini` with independent `pythonpath` settings. Each plugin's tests run in isolation matching production import paths. `scripts/test.sh` runs all suites sequentially. Tests are dev-only and stripped from release branches.

## File Organization

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         — marketplace manifest registering plugins
├── .claude/
│   ├── rules/                   — deployed rule files (gitignored; regenerated by /ocd:setup init)
│   ├── conventions/             — deployed convention files (gitignored; regenerated by /ocd:setup init)
│   ├── patterns/                — deployed pattern files (gitignored)
│   ├── logs/                    — dev-only log entries (decisions, friction, problems, ideas)
│   ├── skills/                  — project-local dev skills (checkpoint, sync-templates)
│   ├── hooks/                   — project-level pre-commit guards
│   ├── ocd/                     — ocd plugin project data (navigator db)
│   ├── blueprint/               — blueprint plugin project data (research db)
│   └── settings.json            — project-level permission patterns
├── plugins/
│   ├── ocd/                     — ocd plugin (own system, see plugins/ocd/architecture.md)
│   └── blueprint/               — blueprint plugin (own system, see plugins/blueprint/architecture.md)
├── scripts/                     — shared development scripts (dev-only)
├── tests/                       — project-level integration tests (dev-only)
└── purpose-map/                 — methodology tooling for live-invention audits (dev-only)
```
