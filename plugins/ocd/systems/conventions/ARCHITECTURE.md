# Conventions Library Architecture

Deploy convention templates and match files to applicable conventions. This document covers the library's internals.

## Purpose

The conventions system answers three questions:

1. Which conventions apply to this file?
2. What rules and conventions exist, and what do their frontmatter declarations say?
3. How are convention templates deployed and removed at the chosen scope?

Answer (1) is the PreToolUse `convention_gate` hook's entire job. Answer (2) supports CLI listing and health checks. Answer (3) is the deployment side that mirrors every other plugin system's setup contract.

All matching reads directly from disk on every call. No database, no caching, no registration step. Convention files are the source of truth; their frontmatter and filesystem presence fully describe the state.

## Layers

```
Consumer (hook, MCP tool, CLI, other library)
    ↓ import systems.conventions
Facade (__init__.py) — re-exports matching, frontmatter, deployment
    ↓
Internal modules:
    _matching.py     — file-to-convention matching, entry listing
    _frontmatter.py  — YAML frontmatter parser (no PyYAML)
    _init.py         — template deployment (init/status/clean)
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
| `_matching.py` | Core matching — file-to-convention matching, entry listing |
| `_frontmatter.py` | Purpose-built YAML frontmatter parser for the conventions field set (no PyYAML dependency) |
| `_init.py` | Template deployment — init/status/clean for `.claude/conventions/<plugin>/` |
| `__main__.py` | CLI — argument parsing and dispatch wrappers around the facade |
| `templates/` | Source-of-truth convention templates that deploy via `_init.py` |

## Public Interface

- **`governance_match(paths)`** — returns a mapping of each input path to the list of convention files whose `includes` pattern matches it, excluding any whose `excludes` pattern also matches. Rules are excluded from match results by default (already in agent context). `include_rules=True` adds them for evaluation walks.
- **`governance_list()`** — enumerates governance entries (rules and conventions) with their parsed frontmatter (`includes`, `excludes`).
- **`init(force=False)` / `status()` / `clean()`** — template deployment per the legacy Init/Status Contract. (Migrating to the per-system setup/ shape is a follow-on task.)

## Frontmatter Schema

Each convention file opens with YAML frontmatter:

```yaml
---
includes: "pattern" | ["pattern", ...]
excludes: "pattern" | ["pattern", ...]     # optional
---
```

`includes` and `excludes` are glob patterns matched against file paths relative to the project root.

## Design Decisions

- **Disk-first reads on every match call.** Convention entries change rarely during a session, but the cost of stale data (applying removed conventions, missing new ones) is higher than the cost of re-reading. Reading is cheap — a few dozen small files — so caching adds complexity without justified benefit.
- **No PyYAML dependency.** Convention frontmatter uses a fixed small schema; a purpose-built parser handles it without pulling a dependency. Keeps the plugin's installed footprint small and avoids a YAML-version mismatch risk.
- **Structured return types.** Every public function returns dicts or lists, not formatted strings. Consumers format for display as needed. Allows the CLI to render JSON or tables from the same data as the hook's internal consumption.
- **Matching and deployment colocated.** Both responsibilities operate on the same files (convention templates and their deployed copies). Splitting them across two systems forced consumers to import from two places for one concept. Folded together, the system is the single backbone for conventions end to end.

## Integration

- **convention_gate hook** calls `governance_match` on every Read/Edit/Write tool call; output paths join `additionalContext` for the invoking tool.
- **Navigator's `scope_analyze`** calls `governance_match` for each scanned file and attaches the match list to its scope entry.
- **Conventions CLI** exposes `for` and `list` subcommands for operational queries.
- **Setup orchestration** calls `init(force=...)` to deploy templates and `clean()` to remove them.
