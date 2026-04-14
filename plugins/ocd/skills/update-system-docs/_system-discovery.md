# System Discovery

Deterministic heuristics for identifying system boundaries during traversal. A system is a structural unit with its own entry point or public interface; the project root is always a system. Skills are systems too (SKILL.md is their agent-facing doc; architecture.md appears only when the Document Separation rule would otherwise be violated).

## System Boundary Heuristics

Applied in order. First match wins.

### 1. Project Root

The repository root. Always a system. Recognized by presence of `.git/` directory.

### 2. Plugin

Directory containing `.claude-plugin/plugin.json`.

### 3. MCP Server

Single module under `*/servers/` (`*/servers/<name>.py`, not underscore-prefixed) with FastMCP usage (either `from mcp.server.fastmcp import FastMCP` import or `FastMCP(` construction). The module is a thin adapter over a domain library under `lib/`.

### 4. Hook System

Directory under `*/hooks/*/` with package structure (`__init__.py` + `__main__.py`).

Single-file hooks (`*/hooks/*.py` with no wrapping directory) are not systems. They are non-obvious surfaces within the parent hooks directory's scope.

### 5. Library Package

Directory under `*/lib/*/` with `__init__.py` establishing a public facade.

### 6. Framework Package

Directory under a plugin root with `__init__.py` providing a facade, not fitting the above categories.

### 7. Skill

Directory under `*/skills/*/` with a `SKILL.md` file.

### 8. Exclusions

- Test directories (`*/tests/`, `conftest.py`) — scaffolding, not systems.
- Data directories (`.claude/`, `.venv/`, `node_modules/`, `__pycache__/`) — per navigator's standard exclusion rules.

## DAG Construction

After discovery, build parent-child relationships from path containment. System A is a parent of B if B's path is a strict prefix descendant of A's path and no other discovered system lies between them.

DAG for this project:

```
/ (project root)
└── plugins/ocd/ (plugin)
    ├── plugins/ocd/servers/navigator.py (mcp-server)
    ├── plugins/ocd/lib/navigator/ (library)
    ├── plugins/ocd/lib/governance/ (library)
    ├── plugins/ocd/hooks/auto_approval/ (hook-system)
    ├── plugins/ocd/plugin/ (framework)
    └── plugins/ocd/skills/{commit,init,log,...}/ (skills)
```

Wave assignment by DFS depth from leaves:

- Wave 0: navigator, governance, auto_approval, plugin framework, each skill (~13 leaves, parallel)
- Wave 1: ocd plugin (consumes ~13 child summaries)
- Wave 2: project root (consumes ocd summary)

## Required Documents Per Kind

Per `system-documentation.md` Document Separation and Nesting Discipline:

| Kind | README.md | architecture.md | CLAUDE.md / SKILL.md |
|------|-----------|-----------------|----------------------|
| project-root | required | required | CLAUDE.md if agent procedures |
| plugin | required | required | CLAUDE.md if agent procedures |
| mcp-server | required | required | n/a |
| library | required | required | n/a |
| framework | required | required | n/a |
| hook-system | required | required | n/a |
| skill | required | required when SKILL.md would otherwise violate Document Separation | SKILL.md (always) |

**README for internal systems is minimal** — a purpose statement and nothing more when no installation/usage/configuration applies. The purpose statement is SSoT with the architecture.md H1 paragraph; the README serves as the directory-landing doc.

**Architecture.md Contents table** — every architecture.md includes a `## Contents` section after its purpose statement, listing each `##`-level section with its purpose statement copied from the section's first paragraph. The table is a derived projection; the skill regenerates it from section scan on every run.

**CLAUDE.md trigger**: a system has agent-facing procedures if it contains skills, agent-invocable slash commands, operational procedures for agents, or files whose purpose statement declares agent operation scope. Default: no CLAUDE.md unless triggered.

**Skill architecture.md trigger** (per Document Separation): SKILL.md excludes architectural descriptions. If SKILL.md content starts explaining layers, components, relationships, or design patterns, split them out into architecture.md.

## CLI Entry Point Resolution

The skill extracts CLI commands for the fact bundle from `__main__.py` in the system root — the single source of truth per Python package convention. MCP server modules (`servers/<name>.py`) have no CLI surface; their CLI lives in the paired library under `lib/<name>/__main__.py`.

## Implementation

Discovery is a CLI subcommand at `${CLAUDE_PLUGIN_ROOT}/run.py update_system_docs.cli discover --json` that returns:

```json
{
  "systems": [
    {"path": "plugins/ocd/servers/navigator.py", "kind": "mcp-server", "parent": "plugins/ocd"},
    {"path": "plugins/ocd/lib/navigator", "kind": "library", "parent": "plugins/ocd"},
    {"path": "plugins/ocd/lib/governance", "kind": "library", "parent": "plugins/ocd"},
    ...
  ],
  "waves": [
    ["plugins/ocd/servers/navigator.py", "plugins/ocd/lib/navigator", "plugins/ocd/lib/governance", ...],
    ["plugins/ocd"],
    ["."]
  ]
}
```

Deterministic; no agent judgment.
