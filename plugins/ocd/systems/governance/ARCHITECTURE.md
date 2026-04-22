# Governance Library Architecture

Match files to applicable conventions, list governance entries, and compute the dependency-ordered level grouping. This document covers the library's internals.

## Purpose

Consumers need answers to three questions:

1. Which conventions apply to this file?
2. What rules and conventions exist, and what do their frontmatter declarations say?
3. In what order should governance be evaluated when one entry governs another?

Answer (1) is the PreToolUse convention_gate's entire job. Answer (2) supports CLI listing and health checks. Answer (3) supports audit-style walks through the governance chain.

All answers read directly from disk on every call. No database, no caching, no registration step. Governance files are the source of truth; their frontmatter and filesystem presence fully describe the state.

## Layers

```
Consumer (hook, MCP tool, CLI, other library)
    ↓ import systems.governance
Facade (__init__.py — re-exports governance_match, list_rules, list_conventions, governance_order)
    ↓ calls
Operations (_governance.py)
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
| `__init__.py` | Facade — re-exports the public interface |
| `_governance.py` | Core operations: file-to-convention matching, entry listing, dependency-level grouping |
| `_frontmatter.py` | Purpose-built YAML frontmatter parser for the governance field set (no PyYAML dependency) |
| `__main__.py` | CLI — argument parsing and dispatch wrappers around the facade |

## Public Interface

- **`governance_match(paths)`** — returns a mapping of each input path to the list of convention files whose `includes` pattern matches it, excluding any whose `excludes` pattern also matches. Rules are excluded from match results by default (already in agent context). `include_rules=True` adds them for evaluation walks.
- **`list_rules()`** / **`list_conventions()`** — enumerate governance entries with their parsed frontmatter (`includes`, `excludes`, `governed_by`).
- **`governance_order()`** — computes the level-grouped topological order of all governance entries based on `governed_by` declarations. Uses Tarjan's SCC algorithm, which detects cycles; dangling references (entries pointing at non-existent governors) are reported separately.

## Frontmatter Schema

Each governance file opens with YAML frontmatter:

```yaml
---
includes: "pattern" | ["pattern", ...]
excludes: "pattern" | ["pattern", ...]     # optional
governed_by:                                 # optional
  - .claude/rules/ocd/design-principles.md
---
```

`includes` and `excludes` are glob patterns matched against file paths relative to the project root. `governed_by` names governance entries this one builds on, defining evaluation ordering for audit workflows (not runtime matching).

## Design Decisions

- **Disk-first reads on every call.** Governance entries change rarely during a session, but the cost of stale data (applying removed conventions, missing new ones) is higher than the cost of re-reading. Reading is cheap — a few dozen small files — so caching adds complexity without justified benefit.
- **No PyYAML dependency.** Governance frontmatter uses a fixed small schema; a purpose-built parser (~150 lines) handles it without pulling a dependency. Keeps the plugin's installed footprint small and avoids a YAML-version mismatch risk.
- **Structured return types.** Every public function returns dicts or lists, not formatted strings. Consumers format for display as needed. Allows the CLI to render JSON or tables from the same data as the hook's internal consumption.

## Integration

- **convention_gate hook** calls `governance_match` on every Read/Edit/Write tool call; output paths join `additionalContext` for the invoking tool.
- **Navigator's `scope_analyze`** calls `governance_match` for each scanned file and attaches the match list to its scope entry.
- **Governance CLI** exposes `match`, `list`, and `order` subcommands for operational queries.
