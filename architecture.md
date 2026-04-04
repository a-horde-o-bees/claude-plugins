# Marketplace Architecture

Claude Code plugin marketplace packaging two plugins with shared development infrastructure. Each plugin is an independent system with its own architecture; this document covers how they are packaged, developed, and delivered.

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

| Plugin | Purpose | Architecture |
|--------|---------|-------------|
| [ocd](plugins/ocd/) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation | [architecture.md](plugins/ocd/architecture.md) |
| [blueprint](plugins/blueprint/) | Structured solution research and implementation planning through entity-based analysis | [architecture.md](plugins/blueprint/architecture.md) |

Plugins are independent systems — each has its own manifest, hooks, skills, rules, and tests. Blueprint depends on ocd at the skill level (uses ocd's navigator and conventions infrastructure) but operates independently at the plugin level.

## Marketplace

The marketplace manifest at `.claude-plugin/marketplace.json` registers both plugins with source paths relative to the repository root. Claude Code resolves these paths when users install from the marketplace.

Distribution: users add the GitHub repository as a marketplace source, then install individual plugins. Each plugin installs to `~/.claude/plugins/` with its own lifecycle (init, status, update).

## Shared Infrastructure

### Plugin Framework

`plugin/__init__.py` in each plugin is identical — a generic framework for deployment, formatting, skill discovery, and init/status orchestration. Propagated across plugins by a pre-commit hook. Contains no plugin-specific logic; each plugin's skill `_init.py` modules provide their own infrastructure.

### Template-Deployed Model

Templates live in plugin source (`plugins/<plugin>/rules/`, `plugins/<plugin>/conventions/`). Init deploys copies to the user's project (`.claude/rules/`, `.claude/conventions/`). Users edit deployed copies; `scripts/sync-templates.py` syncs deployed content back to templates before commits. Governance metadata (pattern, depends) lives in each file's YAML frontmatter — navigator scans for it automatically.

### Development Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sync-templates.py` | Sync deployed copies back to template files; called by pre-commit hook |
| `scripts/run-plugin.sh` | Run plugin CLI with correct environment variables for local development |
| `scripts/test.sh` | Run full test suite across project and all plugins |
| `scripts/pyextract.py` | Utility for extracting Python code blocks |

### Testing

Project-level tests in `tests/`, per-plugin tests isolated by `pytest.ini` with independent `pythonpath` settings. Each plugin's tests run in isolation matching production import paths. `scripts/test.sh` runs all suites sequentially.

## File Organization

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         — marketplace manifest registering both plugins
├── .claude/
│   ├── rules/                   — deployed rule files (edited here, synced to templates)
│   ├── conventions/             — deployed convention files (edited here, synced to templates)
│   ├── ocd/                     — ocd plugin project data (navigator db)
│   ├── blueprint/               — blueprint plugin project data (research db)
│   ├── hooks/                   — project-level git hooks
│   └── settings.json            — project-level permission patterns
├── plugins/
│   ├── ocd/                     — ocd plugin (own system, see plugins/ocd/architecture.md)
│   └── blueprint/               — blueprint plugin (own system, see plugins/blueprint/architecture.md)
├── decisions/                   — architectural decision records
├── scripts/                     — shared development scripts
├── tests/                       — project-level integration tests
└── research/                    — reference materials from research activities
```
