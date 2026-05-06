# Governance Library Architecture

Match files to applicable conventions and list governance entries. This document covers the library's internals.

## Purpose

Consumers need answers to two questions:

1. Which conventions apply to this file?
2. What rules and conventions exist, and what do their frontmatter declarations say?

Answer (1) is the PreToolUse convention_gate's entire job. Answer (2) supports CLI listing and health checks.

All answers read directly from disk on every call. No database, no caching, no registration step. Governance files are the source of truth; their frontmatter and filesystem presence fully describe the state.

## Layers

```
Consumer (hook, MCP tool, CLI, other library)
    ↓ import systems.governance
Facade and operations (__init__.py)
    ↓ reads files, parses frontmatter via
Frontmatter parser (_frontmatter.py)
    ↓ returns
Dict / list structures to consumer

CLI (__main__.py)
    ↓ thin argparse dispatch
Facade (above)
```

## Components

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Facade — public interface re-exports from internal modules |
| `_governance.py` | Core operations — file-to-convention matching, entry listing |
| `_frontmatter.py` | Purpose-built YAML frontmatter parser for the governance field set (no PyYAML dependency) |
| `__main__.py` | CLI — argument parsing and dispatch wrappers around the facade |

## Public Interface

- **`governance_match(paths)`** — returns a mapping of each input path to the list of convention files whose `includes` pattern matches it, excluding any whose `excludes` pattern also matches. Rules are excluded from match results by default (already in agent context). `include_rules=True` adds them for evaluation walks.
- **`governance_list()`** — enumerates governance entries (rules and conventions) with their parsed frontmatter (`includes`, `excludes`).

## Frontmatter Schema

Each governance file opens with YAML frontmatter:

```yaml
---
includes: "pattern" | ["pattern", ...]
excludes: "pattern" | ["pattern", ...]     # optional
---
```

`includes` and `excludes` are glob patterns matched against file paths relative to the project root.

## Design Decisions

- **Disk-first reads on every call.** Governance entries change rarely during a session, but the cost of stale data (applying removed conventions, missing new ones) is higher than the cost of re-reading. Reading is cheap — a few dozen small files — so caching adds complexity without justified benefit.
- **No PyYAML dependency.** Governance frontmatter uses a fixed small schema; a purpose-built parser (~150 lines) handles it without pulling a dependency. Keeps the plugin's installed footprint small and avoids a YAML-version mismatch risk.
- **Structured return types.** Every public function returns dicts or lists, not formatted strings. Consumers format for display as needed. Allows the CLI to render JSON or tables from the same data as the hook's internal consumption.

## Integration

- **convention_gate hook** calls `governance_match` on every Read/Edit/Write tool call; output paths join `additionalContext` for the invoking tool.
- **Navigator's `scope_analyze`** calls `governance_match` for each scanned file and attaches the match list to its scope entry.
- **Governance CLI** exposes `for` and `list` subcommands for operational queries.
