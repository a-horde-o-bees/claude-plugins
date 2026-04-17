# governance

Convention and rule governance library: match files to applicable governance entries, list entries by kind, and compute the dependency-ordered level grouping. Reads directly from disk on every call — no database, no caching.

## Setup

Imported by the ocd plugin. Not a user-facing library; consumed by:

- The `convention_gate` PreToolUse hook — surfaces matching conventions on Read/Edit/Write
- The navigator MCP server's `scope_analyze` tool — attaches governance metadata to scanned files
- The governance CLI (`ocd subsystems.governance ...`) — operational queries

No installation step beyond `/ocd:plugin install` in the consuming project.

## Usage

### As a Python import

```python
import subsystems.governance

matches = subsystems.governance.governance_match(["plugins/ocd/skills/status/SKILL.md"])
rules = subsystems.governance.list_rules()
order = subsystems.governance.governance_order()
```

Functions return structured data (dicts, lists). Formatting for display is the caller's responsibility.

### As a CLI

```
ocd subsystems.governance match <path> [<path> ...]
ocd subsystems.governance list [--kind rules|conventions]
ocd subsystems.governance order [--json]
```

`match` returns applicable conventions for the given paths. `list` enumerates rules and/or conventions with their include/exclude/governed_by fields. `order` computes dependency-level grouping from `governed_by` declarations using Tarjan's SCC algorithm.

## Dependencies

Standard-library only — no PyYAML or other third-party packages. Governance frontmatter is parsed by a purpose-built mini-parser that reads the specific structure used by rules and conventions (`includes:`, `excludes:`, `governed_by:`).

## License

MIT
