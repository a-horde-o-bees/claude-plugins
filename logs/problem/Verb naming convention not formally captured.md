# Verb naming convention not formally captured

Read-side verbs across MCP tools and CLI subcommands are inconsistent (`_get`, `_list`, `_search`, `_find`, `_query`) and no convention document defines when each applies. `decision/mcp.md` commits blueprint research to `get_*` / `list_*` / `find_*` but does not define the input-shape distinction that determines which one to pick, and the rule has not propagated to other MCP servers.

## Proposed distinction

The verb is determined by what the *input* is, not the operation it performs:

| Input shape | Verb suffix | Example |
|---|---|---|
| Primary key — single resource lookup | `_get` | `paths_get(path)`, `purpose_get(session, exchange)` |
| No filter — full enumeration | `_list` | `projects_list()`, `skills_list()` |
| Named structural filters over typed fields (exact match) | `_query` | `sessions_query(project=..., from=...)`, `exchanges_query(session=..., range=...)` |
| Search term matched against text/descriptions, often ranked | `_search` | `paths_search("authentication")`, `chat_search("AskUserQuestion")` |

Rule of thumb: if you'd implement it with `WHERE col = ?` it's `_query`; if you'd implement it with `WHERE col LIKE '%x%'`, FTS, or relevance ranking, it's `_search`. Mixed cases (a query that accepts an optional substring filter) stay `_query` — primary intent wins.

`decision/mcp.md` uses `find_*` as the third read verb, which collides with both `_query` and `_search` depending on its actual input shape. Audit needs to determine whether existing `find_*` tools are structural filters (rename to `_query`) or text-matched (rename to `_search`).

## What's wrong

- No convention doc defines `_query` vs `_search` vs `_find` selection criteria — every author picks based on intuition
- `paths_search` in navigator filters by directory prefix (structural) but uses `_search` — by the proposed rule it should be `_query`
- `find_*` in `decision/mcp.md` is undefined as to input shape — it could mean either category
- `decision/mcp.md` enumerates write verbs (`set`/`add`/`remove`/`clear`) precisely but stops short of the same precision for reads
- Future MCP authors (the transcripts port being the immediate next case) have no anchor to follow, so the drift compounds

## Audit scope

- All MCP server tool registrations under `plugins/*/servers/`
- All `__main__.py` subcommand verbs under `plugins/*/systems/*/`
- All skill argument verbs in `SKILL.md` files

For each, classify the operation by input shape (PK lookup / no-filter list / structural filter / text search) and check the verb suffix matches.

## Suspected fix shapes

- Promote the input-shape distinction to a convention doc (`plugins/ocd/conventions/verb-naming.md` or similar) — single source of truth referenced by `decision/mcp.md`
- Audit existing tools and either rename for conformance or document deliberate exceptions
- Update `decision/mcp.md` to point at the new convention rather than re-state read-verb selection
- Decide whether `find_*` survives (as a third category) or is replaced by `_query`/`_search` based on its actual input shape

## Origin

Surfaced during transcripts → MCP port design discussion. The transcripts data layer needs `sessions_query`, `exchanges_query`, `purpose_get`, `projects_list`, plus a `sql_query` escape hatch. Settling on `_query` vs `_search` for the structural-filter case prompted the question of where the convention is documented — it isn't.
