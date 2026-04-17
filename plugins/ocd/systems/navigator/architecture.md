# Navigator Library Architecture

Project structure index in SQLite with human-written descriptions, filesystem change detection via git-compatible blob hashes, reference graph over files that link to other files, and skill resolution across Claude Code's discovery locations. This document covers the library's internals.

## Purpose

Agents need to answer "should I open this file?" without reading every file in a project. Navigator maintains a queryable index where each entry carries:

- Its filesystem type (file or directory) and structural role (excluded, shallow, normal)
- A human-written description conveying scope and role
- A git-compatible blob hash to detect when content has changed since description was written
- Links into and out of the entry via reference parsing (for cross-file navigation)

The library owns the database, the scan loop, the reference graph, and the skill resolver — four related but separable capabilities sharing one SQLite store.

## Layers

```
Consumer (MCP server, CLI, other library)
    ↓ import systems.navigator
Facade (__init__.py — re-exports paths_*, scope_analyze, skills_*, references_*)
    ↓ delegates to
Internals: _db, _scanner, _references, _skills, _init
    ↓ SQL / filesystem / file reads
SQLite database (.claude/ocd/navigator/navigator.db) + filesystem

CLI (__main__.py)
    ↓ thin argparse dispatch
Facade (above)
```

## Modules

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Facade — re-exports the public API from all internals |
| `__main__.py` | CLI entry point (scan, describe, list, search, set, remove, resolve-skill, list-skills, get-undescribed, init) |
| `_db.py` | Schema, migrations, connection factory, seed-rule loading from `navigator_seed.csv` |
| `_scanner.py` | Filesystem walking with rule-based pruning, git-hash change detection, stale-cascade to parent directories |
| `_references.py` | File reference mapping — builds a dependency DAG from parseable file references (SKILL.md component calls, governance `governed_by`, etc.) |
| `_skills.py` | Resolves skill names to SKILL.md paths across discovery locations. Accepts bare, slash-prefixed, plugin-qualified, or fully-qualified forms |
| `_init.py` | Initialize database and report status; called by plugin orchestration during `/ocd:setup init` and `/ocd:setup status` |

## Database Schema

```
entries
├── path TEXT PK              — relative path from project root
├── parent_path TEXT          — parent directory path (indexed)
├── entry_type TEXT           — CHECK: file, directory
├── exclude INTEGER           — 1 = omit from scans and listings
├── traverse INTEGER          — 0 = list but don't descend (shallow directory)
├── description TEXT          — human-written purpose description (NULL = not yet reviewed)
├── git_hash TEXT             — SHA-1 blob hash for change detection
└── stale INTEGER             — 1 = content changed since description was written
```

Pattern entries (paths containing `*`) control scanning behavior rather than representing a specific file:

- Exclude patterns omit matching paths entirely from scans and listings
- Shallow patterns (`traverse=0`) list directories without descending into them
- Seed patterns (loaded from `navigator_seed.csv` at init) provide defaults for `.git`, `node_modules`, `__pycache__`, and similar directories

## Change Detection

Scanner computes git-compatible blob hashes — `blob {size}\0{content}` hashed with SHA-1 — for every non-excluded file and compares against the stored hash.

- New files: added with `description=NULL`
- Removed files: deleted from entries
- Changed files: `stale=1`
- Seed patterns with prescribed descriptions auto-apply their description to new matching files (and clear stale when re-matched)

Staleness cascades: when any child entry is marked stale, its parent directory is marked stale too. Directory descriptions summarize their children, so a child change invalidates the parent description by implication.

## Skill Resolver

`skills_resolve(name)` searches four discovery locations in Claude Code priority order — personal, project, plugin-dir, marketplace — and returns the path of the first `SKILL.md` whose frontmatter `name` matches. Input is normalized before matching:

- Leading `/` is stripped
- Any `plugin:` prefix is stripped

So `audit-static`, `/audit-static`, `ocd:audit-static`, and `/ocd:audit-static` all resolve the same way. This lets callers pass the canonical qualified form (`/plugin:skill`) without a separate normalization step.

## Concurrency

SQLite database is opened in WAL mode with a 5-second busy timeout. Multiple agents can read simultaneously; writes queue behind the busy timeout. The MCP server and CLI share the same database file; connection lifetimes are per-call (open, operate, close).

## Design Decisions

- **Facade re-exports, not subclassing or injection.** Internals are private to the library and re-exported from `__init__.py` by name. Consumers import `systems.navigator` and get the public surface. Internal modules can be restructured without breaking consumers.
- **No ORM.** Direct SQL against the entries table. Schema is small, queries are simple, and avoiding an ORM keeps the dependency footprint small and the code debuggable.
- **Path-string primary key.** Paths (relative to project root) are the canonical identity. No synthetic integer IDs. Makes joins to other tables unnecessary (there are no other tables) and keeps schema migrations simple.
- **Stale-cascade to parents.** When a child changes, its parent's description is now out-of-date by implication. Marking stale eagerly means description-writing workflows naturally re-examine parents.

## Integration

- **Navigator MCP server** (`plugins/ocd/systems/navigator/server.py`) — thin FastMCP adapter. Every tool delegates to a facade function, serializes the result, and returns.
- **`/ocd:navigator` skill** — drives description writing for undescribed and stale entries, using `paths_undescribed` and `paths_upsert` via the MCP server.
- **Convention gate hook** — the related `systems/governance` library reads from disk directly, not through navigator. Navigator's `scope_analyze` calls `governance_match` to attach governance data to scanned files.
