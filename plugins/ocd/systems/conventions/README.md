# conventions

File-content governance for ocd: deploys convention templates to `.claude/conventions/<plugin>/` and matches files to applicable conventions via frontmatter `includes`/`excludes` patterns. Reads directly from disk on every matching call — no database, no caching.

## Setup

Imported by the ocd plugin. Consumed by:

- The `convention_gate` PreToolUse hook — surfaces matching conventions on Read/Edit/Write
- The navigator MCP server's `scope_analyze` tool — attaches governance metadata to scanned files
- The conventions CLI (`ocd-run conventions ...`) — operational queries
- Setup orchestration — deploys convention templates as part of project install

No installation step beyond `/ocd:setup` in the consuming project.

## Usage

### As a Python import

```python
import systems.conventions

matches = systems.conventions.governance_match(["plugins/ocd/skills/status/SKILL.md"])
entries = systems.conventions.governance_list()
```

Functions return structured data (dicts, lists). Formatting for display is the caller's responsibility.

### As a CLI

```
ocd-run conventions for <path> [<path> ...]
ocd-run conventions list
```

`for` returns applicable conventions for the given paths. `list` enumerates rules and conventions with their include/exclude fields.

## Dependencies

Standard-library only — no PyYAML or other third-party packages. Governance frontmatter is parsed by a purpose-built mini-parser that reads the specific structure used by rules and conventions (`includes:`, `excludes:`).

## License

MIT
