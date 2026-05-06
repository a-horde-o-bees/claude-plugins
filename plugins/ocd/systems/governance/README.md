# governance

Convention and rule governance library: match files to applicable governance entries and list entries by kind. Reads directly from disk on every call — no database, no caching.

## Setup

Imported by the ocd plugin. Not a user-facing library; consumed by:

- The `convention_gate` PreToolUse hook — surfaces matching conventions on Read/Edit/Write
- The navigator MCP server's `scope_analyze` tool — attaches governance metadata to scanned files
- The governance CLI (`ocd-run governance ...`) — operational queries

No installation step beyond `/ocd:setup init` in the consuming project.

## Usage

### As a Python import

```python
import systems.governance

matches = systems.governance.governance_match(["plugins/ocd/skills/status/SKILL.md"])
entries = systems.governance.governance_list()
```

Functions return structured data (dicts, lists). Formatting for display is the caller's responsibility.

### As a CLI

```
ocd-run governance for <path> [<path> ...]
ocd-run governance list
```

`for` returns applicable conventions for the given paths. `list` enumerates rules and conventions with their include/exclude fields.

## Dependencies

Standard-library only — no PyYAML or other third-party packages. Governance frontmatter is parsed by a purpose-built mini-parser that reads the specific structure used by rules and conventions (`includes:`, `excludes:`).

## License

MIT
