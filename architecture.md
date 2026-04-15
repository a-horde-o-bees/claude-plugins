# Marketplace Architecture

Claude Code plugin marketplace that packages the `ocd` plugin. This document covers how the plugin is packaged, delivered, and composed into consumer projects.

## Layers

```
Claude Code plugin runtime
    ↓ marketplace resolution
Marketplace manifest (.claude-plugin/marketplace.json)
    ↓ plugin source path
Plugin (plugins/ocd/)
    ↓ own entry points, hooks, servers, skills
Plugin internals (see plugins/ocd/architecture.md)
```

## Plugins

| Plugin | Purpose | Architecture |
|--------|---------|-------------|
| [ocd](plugins/ocd/) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation | [architecture.md](plugins/ocd/architecture.md) |

Future plugins will live in sibling directories under `plugins/` and register themselves in `.claude-plugin/marketplace.json`.

Each plugin may register Claude Code hooks (PreToolUse, PostToolUse, SessionStart), MCP servers for persistent tooling, and skills (slash commands). The specific hooks, servers, and skills this plugin provides are documented in `plugins/ocd/architecture.md`.

## Marketplace

The marketplace manifest at `.claude-plugin/marketplace.json` registers each plugin with a source path relative to the repository root. Claude Code resolves these paths when users install from the marketplace.

Distribution: users add the GitHub repository (pinned to a release branch or tag) as a marketplace source, then install individual plugins. Each plugin installs to `~/.claude/plugins/` with its own lifecycle (init, status, update).

## Three-Document Model

Every system boundary in this project — the repository root, each plugin, each skill that carries agent procedures — maintains a consistent set of documents, each targeting one consumer perspective:

- **`README.md`** — user-facing. What the system does, how to install and use it. At plugin and subsystem boundaries, the README targets the end users of that component.
- **`architecture.md`** — developer-facing. Layers, components, relationships, and key implementation details. A parent `architecture.md` describes each subsystem's role in the overall composition and links to the subsystem's own `architecture.md` for internals, rather than re-explaining what belongs to the subsystem.
- **`SKILL.md`** — agent-facing. Present inside skill packages. Contains procedures, workflow rules, and tool invocation patterns for the named operation.

Readers navigate from general to specific through the nesting chain. A parent document answers "how do these pieces fit together"; each subsystem's documents answer "how does this piece work internally." Neither layer re-explains content that belongs to the other.

## Governance Delivery

The ocd plugin delivers three kinds of agent guidance to consumer projects, each loaded through a mechanism suited to its scope.

**Rules** deploy to `.claude/rules/` and load into every session automatically via Claude Code's built-in rule auto-loading. Rules encode project-wide behavioral guidance — the agent follows them regardless of which file it is touching. A rule file contains the guidance the agent should consult at every step.

**Conventions** deploy to `.claude/conventions/` and load on demand. A PreToolUse hook on Read, Edit, and Write calls the navigator's `governance_match` with the target file path and surfaces matching convention files as additional tool-call context. This keeps session context focused — an agent editing a Python file sees the Python convention, an agent editing a markdown file sees the markdown convention, and neither sees the other. A convention file contains the content standards its target file type must meet.

**Operational documents** — `SKILL.md` inside skill packages — load when Claude Code discovers them. They carry the procedures the agent follows when performing work within the system they describe.

Rules govern how the agent behaves. Conventions govern what a file contains. Operational documents govern how operations are performed. Guidance that applies regardless of which file is touched belongs in a rule; guidance that applies only to a specific file type belongs in a convention; step-by-step procedures for a named operation belong in an operational document.

## Plugin Framework

The generic framework (`plugin/` under each plugin) is shared deployment, formatting, discovery, and init/status orchestration. A plugin's `plugin/` package has no plugin-specific logic; each lib subsystem's `_init.py` module provides its own infrastructure bootstrap.

## Template-Deployed Model

Templates live in plugin source (`plugins/<plugin>/templates/rules/`, `plugins/<plugin>/templates/conventions/`, `plugins/<plugin>/templates/patterns/`, `plugins/<plugin>/templates/logs/`). Init deploys copies to the consumer project's `.claude/` directory. Governance metadata (`includes`, `governed_by`) lives in each file's YAML frontmatter; the navigator reconciles rules and conventions against disk state on every governance query, so entries stay current without an explicit registration step.

## File Organization

```
claude-plugins/
├── .claude-plugin/
│   └── marketplace.json         — marketplace manifest registering plugins
├── plugins/
│   └── ocd/                     — ocd plugin (see plugins/ocd/architecture.md)
├── README.md                    — consumer-facing overview
├── architecture.md              — this file
└── LICENSE
```
