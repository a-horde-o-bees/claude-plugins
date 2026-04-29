---
includes: "**/systems/*/__main__.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/conventions/ocd/python.md
---

# CLI Conventions

Structural and naming conventions for argparse-based CLI dispatch in `__main__.py` modules. Each system's CLI is a thin wrapper that delegates to library functions. Verb structure mirrors the system's MCP tool surface so a reader who knows one knows the other.

## Noun-Verb Hierarchy

CLI verbs are organized as `<system> <noun> <verb> [args...]` via argparse subparser nesting. The top-level subparser dispatches by noun (the concept being acted on); each noun's subparser dispatches by verb (the operation).

```
transcripts sessions query [--project X] [--show ...]
transcripts exchanges query [--session Y]
transcripts purposes update [--set <json>] [--clear <list>]
navigator paths query [--text X]
navigator paths upsert <path> [--purpose ...]
navigator skills query [--name X]
```

This matches MCP tool naming: `<noun>_<verb>` in MCP is `<noun> <verb>` in CLI. A reader who knows `sessions_query` from MCP knows `sessions query` from CLI; the only difference is the separator.

## CLI ↔ MCP Naming Alignment

For every MCP tool exposed by the system's `server.py`, there is a corresponding CLI verb at `<noun> <verb>`. The names differ only in separator (underscore vs space). When the MCP tool surface changes, the CLI follows in the same change.

A reader migrating between surfaces (debugging via CLI then automating via MCP, or vice versa) does not encounter renamed operations.

## System-Level Verbs Stay Flat

Verbs that act on the whole system — not on any specific noun — dispatch from the top level without a noun layer:

```
transcripts reset
setup init
setup status
setup enable <system>
navigator scan
```

These verbs do not have meaningful noun anchors. `reset` resets the whole system, not a specific noun. Forcing them into a noun-verb shell (`system reset`, `state status`) adds ceremony without semantic value.

The boundary: if the operation's scope is the whole system, it stays flat. If the operation acts on a specific concept the system manages, it nests under that concept's noun.

## Single-Concept Systems

Systems with one concept may use flat verbs without an explicit noun layer — the system name *is* the noun. Multi-concept systems require the noun layer to disambiguate.

The judgment: if ambiguity exists between operations that target different concepts, nest. If every CLI verb operates on the same implicit concept, flat works.

## Argparse Subparser Pattern

```python
def main() -> None:
    ap = argparse.ArgumentParser(prog="<system>")
    top = ap.add_subparsers(dest="noun", required=True)

    # System-level verbs (flat)
    top.add_parser("reset", help="...").set_defaults(func=cmd_reset)

    # Noun: <concept_a>
    a_p = top.add_parser("<concept_a>", help="...")
    a_sub = a_p.add_subparsers(dest="verb", required=True)

    a_query = a_sub.add_parser("query", help="...")
    a_query.add_argument("--filter", default="")
    a_query.set_defaults(func=cmd_concept_a_query)

    a_update = a_sub.add_parser("update", help="...")
    a_update.add_argument("--set", default="")
    a_update.set_defaults(func=cmd_concept_a_update)

    # Noun: <concept_b> ...
```

Handler function names follow `cmd_<noun>_<verb>` so they are grep-aligned with the dispatch path. System-level verbs use `cmd_<verb>`.

## Verb Names

Verb names mirror the MCP tool's verb part exactly. The standard set:

| Verb | Use |
|------|-----|
| `query` | All retrieval — PK lookup, enumeration, structural filter, text search. Mode selected by parameters. |
| `upsert` | Create or update by primary key |
| `set` | Replace a value |
| `update` | Mutate fields on existing entry; supports multiple changes per call |
| `clear` | Null out a value while preserving the row |
| `remove` | Delete the entry |

Domain-specific verbs use descriptive names (e.g. `paths undescribed`, `references map`). The same verb names apply in MCP. See `mcp-server.md` *Standardized Verbs* for the canonical definitions.

## Adding a Verb vs Adding a Flag

When designing a new operation:

- **Add a new verb** when the operation has different semantics or a different transactional shape — `update` vs `remove`, `set` vs `clear`. The agent expects a different review/safety stance, so the tool surface mirrors that.
- **Add a new flag** when the operation is the same with a different input shape — `paths query --text X` vs `paths query --paths X` are both retrieval, parameterized by what to look up.

When in doubt: would a reader expect `--help` of one to mention the other? If yes, same verb with flags. If no, different verbs.

## Output

CLI output is JSON throughout — same shape as the MCP tool's response. Pretty-print at the CLI boundary (`json.dumps(..., indent=2)`); the underlying library returns plain Python data structures.

Errors emit `{"error": "..."}` on stderr with exit code 1. Expected exception classes (`LookupError`, `ValueError`, `KeyError`, framework error types) are caught at the CLI boundary; unhandled exceptions bubble up as Python tracebacks and are diagnostic.

## CLI as Agent-Debug Surface

The CLI mirrors the MCP tool surface 1:1. Its primary consumer is the agent debugging via shell, or the user driving from `/<plugin>:<system>` skill invocations — not human end-users authoring documents. CLI ergonomics that diverge from MCP (shorter aliases, abbreviated forms, interactive prompts) are not added.
