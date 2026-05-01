# SQLite

Embedded relational database stored as a single file. The only format in this comparison that is queried rather than read raw — the LLM emits SQL, not the file's bytes. Standard for indexed structured data with relationships, constraints, and significant scale.

## Metadata

- **File extensions:** `.db`, `.sqlite`, `.sqlite3` (no enforced convention)
- **MIME type:** `application/vnd.sqlite3`
- **Spec:** SQLite file format fully documented at sqlite.org; SQL dialect is a subset of SQL-92 plus extensions (UPSERT, JSON1, FTS5, STRICT tables since 3.37)
- **Primary use cases:** Local application databases, indexed transcripts/logs (`/ocd:transcripts`), navigator file-purpose index, any structured data with relationships or query needs that exceed flat files

## Disposition

**Endorsed** — for indexed, queryable structured data with relationships or scale. The canonical structured-data substrate in this project. Pair with schema-introspection tooling (project's `schema_describe`), engine-level read-only enforcement (`file:...?mode=ro`), and parameterized queries (`?` placeholders) to address the agent token-waste and security pain points.

## Token efficiency

Not directly comparable — the LLM never reads SQLite bytes. The tokens that matter are SQL queries and result sets. Result-set token cost depends on query design (`SELECT id, name FROM users WHERE ...` is cheap; `SELECT * FROM users` is unbounded).

### Read-path inefficiency

- **Schema-blind queries.** An agent issuing a query before reading schema either guesses at table/column names (wrong-name retries amplify cost) or asks for everything via `SELECT *`. The Spider 2.0 benchmark — 632 enterprise text-to-SQL workflows over real databases with 700-3000+ columns — shows even state-of-the-art systems fail roughly two thirds of the time on real schemas. ReFoRCE, the leaderboard top, scores ~36% execution accuracy. The paper attributes ~16.6% of failures to column-linking specifically and 27.6% of SQL errors to schema linking at scale ([Spider 2.0 paper](https://arxiv.org/abs/2411.07763), verified). Schema linking — narrowing the schema surface fed into the prompt — is the single highest-leverage intervention.
- **`SELECT *` and unbounded result sets.** When the agent doesn't know which columns matter, the cheap path is to take all of them. Wide tables with text columns inflate the result by orders of magnitude over what was needed.
- **Verbose result formatting.** Returning rows as a list of full JSON objects re-ships every column name on every row. Two-array `{columns: [...], rows: [[...], [...]]}` avoids the per-row repetition.
- **Re-issued queries from missing context.** Without introspection affordance, an unexpected result drives a `SELECT * LIMIT 5` orientation query, then a real query. Surfacing column types, FK relationships, sample values, and *semantics the schema can't express* eliminates the loop. The project's `schema_describe` returns a `semantics` block doing exactly this.
- **Pagination affordances missing.** A naive tool returning "everything that matched" forces the agent to add `LIMIT/OFFSET` itself. The `transcripts.sql_query` tool defends with a 1000-row cap and a `truncated: bool` flag.

### Write-path inefficiency

Less studied than read paths because most agent-facing SQL tooling deliberately exposes only read access.

- **No parameterization affordance.** When a tool accepts only a SQL string, the agent constructs `UPDATE users SET name = 'O''Brien' WHERE id = 42` — escaping is the agent's problem and a high-incident one. The 2025 SQLi disclosure wave specifically caused by f-string interpolation: Anthropic's reference Postgres MCP (no CVE assigned, [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/)); Apache Doris MCP ([CVE-2025-66335](https://nvd.nist.gov/vuln/detail/CVE-2025-66335), verified); SQLite MCP `describe_table` table-name concatenation. Parameterized queries are the structural fix. The project's `sql_query` accepts `params: list[Any]` for `?` placeholders.
- **Whole-row rewrites.** When an agent reads a row, modifies one field, then issues `UPDATE table SET col1=..., col2=..., col3=...`, it has paid to read all columns and write all columns. SQL natively supports partial updates (`UPDATE ... SET col_changed = ? WHERE id = ?`); schema introspection that surfaces NOT NULL/CHECK constraints lets the agent narrow safely.
- **Missing `RETURNING`.** SQLite (since 3.35) and Postgres support `INSERT/UPDATE/DELETE ... RETURNING <cols>` so a write returns the post-write row in the same round trip. Without it, agents issue separate `SELECT` to confirm the write — doubling round-trip cost. Search did not surface a write tool that defaults to `RETURNING`.
- **Constraint feedback.** SQLite's error string identifies the constraint (`NOT NULL constraint failed: users.email`). A tool that surfaces the raw error gives a tight self-correction loop. STRICT tables (3.37+) extend this to type validation.
- **Transactions without explicit handles.** Multi-statement workflows (insert parent then children) need transaction boundaries. Tools that don't expose them either run each call in its own implicit commit or wrap a SQL string in a single execute (which `sqlite3.execute` rejects, since it takes one statement).

## LLM parse reliability

Not applicable — the model doesn't parse SQLite files. SQL result sets (when returned through an MCP tool) are typically formatted as JSON, markdown tables, or text and parse per their format.

## LLM generation reliability

Good for standard SELECT/UPDATE/DELETE; degrades for complex joins, window functions, dialect-specific features. Schema introspection (the project's `schema_describe`) substantially improves accuracy.

## Modification ergonomics

The strongest of any format — `UPDATE table SET field = value WHERE id = ?` is row-and-column granularity by design. Constraints and triggers enforce invariants the application would otherwise have to check.

## Diff and human readability

Worst of any format in git — the file is binary, diffs are opaque. Tools like `sqldiff` produce SQL-statement diffs but require manual setup. Schema migrations partially address this by tracking schema changes as text files.

## Tooling and ecosystem

### Tool catalog

| Name | URL | Type | Maturity | Primary capability | Token reducer |
|---|---|---|---|---|---|
| Anthropic SQLite MCP server (archived) | [github.com/modelcontextprotocol/servers-archived](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite) | MCP | archived; forked 5000+ times before archival | basic SQLite read/write via MCP | reference only — known SQLi via f-string |
| DBHub | [github.com/bytebase/dbhub](https://github.com/bytebase/dbhub) | MCP | 2.7k stars, MIT, TypeScript | unified read/write across Postgres, MySQL, MariaDB, SQL Server, SQLite | "two MCP tools" minimalism — `execute_sql` + `search_objects`; read-only mode flag, row limit, query timeout |
| Postgres MCP Pro | [github.com/crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp) | MCP | 2.7k stars, v0.3.0 May 2025 | Postgres-specific read/write + index/health analysis | restricted mode parses SQL to reject COMMIT/ROLLBACK; layered tools (`list_schemas` → `list_objects` → `get_object_details`) |
| MotherDuck/DuckDB MCP server | [github.com/motherduckdb/mcp-server-motherduck](https://github.com/motherduckdb/mcp-server-motherduck) | MCP | official MotherDuck | DuckDB analytical SQL over local files, S3, MotherDuck | catalog browse + `execute_sql`; switches DBs on the fly |
| Datasette MCP | [github.com/mhalle/datasette-mcp](https://github.com/mhalle/datasette-mcp) | MCP | first-pass | read-only over Datasette HTTP API | "complete database schema in one efficient call"; HTTP transport |
| sqlite-utils + `sqlite-utils-ask` | [simonwillison.net 2024](https://simonwillison.net/2024/Nov/25/ask-questions-of-sqlite/) | CLI / library | mature ecosystem | natural-language → SQL via local `llm` integration, three-strikes self-correction | extracts schema once; retries on execution error |
| Datasette | [datasette.io](https://datasette.io) | CLI / web | mature, 9k+ stars | publish SQLite as queryable HTTP+SQL+JSON API | layered URLs are RESTful schema introspection by structure |
| Python `sqlite3` stdlib + URI mode | [docs.python.org/3/library/sqlite3](https://docs.python.org/3/library/sqlite3.html) | library | universal stdlib | `sqlite3.connect("file:db?mode=ro", uri=True)` opens read-only at engine level | engine-level read-only enforcement — no SQL parsing, no authorizer, no bypass. The project's transcripts `_connect_readonly` uses exactly this (verified at `plugins/ocd/systems/transcripts/server.py:81`) |
| sqlglot | [github.com/tobymao/sqlglot](https://github.com/tobymao/sqlglot) | library | mature, 7k+ stars, no deps | parse, transpile, optimize SQL across 20+ dialects via AST | parse before execute to detect malformed SQL without DB round-trip |
| sqlean / sqlean.py | [github.com/nalgeon/sqlean](https://github.com/nalgeon/sqlean) | library | active, ~2k stars | bundle of SQLite extensions (uuid, regexp, fileio, percentile, define) | drop-in replacement with extensions; reduces application-layer post-processing |
| SQLAlchemy Core/ORM | [docs.sqlalchemy.org](https://docs.sqlalchemy.org) | library | mature, decades of use | Python query API + raw SQL execution + introspection | `inspect()` for live schema; query API gives the *application code path* an agent can invoke deterministically |
| AutoLink | [arxiv.org/abs/2511.17190](https://arxiv.org/html/2511.17190) | research pattern | published Nov 2025 | autonomous schema exploration for large schemas | <50% the tokens of competing schema-linking methods at competitive accuracy |
| M-Schema | [github.com/XGenerationLab/M-Schema](https://github.com/XGenerationLab/M-Schema) | pattern | active, 217 stars verified | compact semi-structured schema representation | tuple-per-column with type+description+example, fewer tokens than DDL or verbose JSON Schema |
| ReFoRCE | [arxiv.org/abs/2502.00675](https://arxiv.org/pdf/2502.00675) | research / pattern | Spider 2.0 leaderboard top | self-refinement + column-exploration text-to-SQL agent | column-by-column schema exploration; 35.83 / 36.56 EX on Spider 2.0 Snow / Lite |
| MCP `structuredContent` (spec 2025-06-18) | [modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-06-18/schema) | spec | shipped in protocol | tools return structured + unstructured fields | structured payloads parse mechanically (no model-side string parsing) |
| Read-only DB role pattern | [SQLAlchemy text-to-SQL guidance](https://myengineeringpath.dev/programming/python/llm-database-integration/) | pattern | conventional best practice | grant agent connection a role with no INSERT/UPDATE/DELETE/DDL | engine-level rejection regardless of generated SQL |

### Capability matrix

`✓` = supported, `~` = partial/conditional, `✗` = absent. Maintainer-stated; not all verified hands-on.

| Tool/pattern | schema-introspect | query-read | query-write | param-bind | sandbox-exec | paginate / row-cap | summarize-result | read-only-enforce | partial-update | constraint feedback |
|---|---|---|---|---|---|---|---|---|---|---|
| Project `sql_query` + `schema_describe` | ✓ live + semantics | ✓ | ✗ | ✓ `?` placeholders | ✓ engine RO | ✓ 1000-row cap + `truncated` | ✗ raw rows | ✓ engine RO | n/a (read-only) | n/a |
| DBHub | ✓ `search_objects` | ✓ | ✓ | ~ via custom tools | ~ flag | ✓ row limit | ✗ | ✓ flag | ~ | passes through DB error |
| Postgres MCP Pro | ✓ layered | ✓ | ✓ | ~ | ✓ restricted mode | ✓ + query budget | ✗ | ✓ restricted mode | ~ | ~ |
| MotherDuck MCP | ✓ catalog | ✓ | ✓ | ~ | ✗ | ~ | ✗ | ✗ | ~ | ~ |
| Datasette MCP | ✓ "schema in one call" | ✓ | ✗ | ~ | ✓ HTTP RO | ✓ Datasette `_size` | ✗ | ✓ | n/a | ~ |
| Anthropic archived SQLite MCP | ~ | ✓ | ✓ | ✗ f-string | ✗ | ✗ | ✗ | ✗ | ~ | ~ |
| sqlite-utils-ask | ✓ extracts on each run | ✓ | ✗ (read-tilted) | ~ | ~ | ~ | ✗ | ✓ | n/a | ✓ feeds error back |
| sqlglot | ~ AST surfaces refs | n/a (parser only) | n/a | n/a | ✗ | n/a | n/a | n/a | n/a | n/a |
| Python `sqlite3` URI ro | ✗ (lib-level) | ✓ | ✗ | ✓ stdlib | ✓ engine | n/a | n/a | ✓ engine | n/a | ✓ raises with reason |
| AutoLink (pattern) | ✓ (the point) | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| M-Schema (pattern) | ✓ token-efficient | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| Read-only role pattern | ~ | ✓ | ✗ | ~ | ✓ DB-engine | ~ | ~ | ✓ | n/a | ✓ |

### Recommended starter set

Three additions that fit this stack and address gaps the existing `sql_query`/`schema_describe` pair leaves open. Each addresses token-pain explicitly relative to current behavior.

1. **Compact result format option (`format=compact`).** Current `sql_query` returns `{columns: [...], rows: [{col: val, ...}, ...]}` — column names re-shipped per row. Adding a `format` parameter that swaps to `{columns: [...], rows: [[v, v, v], ...]}` (two-array shape) preserves all information at the token cost of names-once. *Beats current pattern* on token cost when the agent will scan or aggregate; agent already has columns from the `columns` array.
2. **Result-set summary mode (`format=summary`).** For exploratory queries, return per-column type, distinct-value count, NULL count, min/max for numeric/date columns, and a few example values for text columns — not the rows themselves. Replaces the `SELECT * LIMIT 5` orientation pattern. *Adjacent to* schema introspection but for dynamic result sets — `schema_describe` can't summarize a join's output. Implementation is sqlite3 wrapped with stdlib aggregation; no new dependency.
3. **Schema linking on the input side.** If `schema_describe` becomes large enough that introspection cost dominates (current size is small enough that this isn't yet the issue), adopt M-Schema's tuple-per-column layout in place of dict-of-dicts. Compactness is from format, not omission. *Beats current pattern* purely on output tokens for large schemas.

What this stack does not need: a multi-database gateway (only SQLite is in play); a schema-recommendation tool (Postgres MCP Pro's index-analysis operates at a scale this project doesn't reach); a parsing layer between agent and engine (sqlglot's value is for cross-dialect transpile and AST-driven schema linking, neither of which applies when there's one DB and `schema_describe` already serves intent).

### Gaps

- **Standardized partial-update tool shape for SQLite MCP servers.** Most write-capable MCP servers expose a single `execute_sql` taking the full UPDATE. A first-class `update_row(table, pk, {col: value})` shape would be parameterized by construction, surface NOT NULL/CHECK violations cleanly, and close the partial-update gap without exposing arbitrary DDL. Not found in surveyed servers.
- **`RETURNING` as a tool-default for write tools.** No surveyed write tool surfaced `RETURNING <cols>` as default behavior; convention is "execute, return rowcount, agent re-queries if needed."
- **Result-set summarization protocol.** Outside of `EXPLAIN`/`ANALYZE` (plans, not result content), no surveyed tool returned shape-of-result-set summaries.
- **Token-budget feedback in tool responses.** Some tools cap rows; none surveyed return "this query would have produced N rows; I returned M" so the agent can reason about widening the cap.
- **Schema versioning surfaced to the agent.** When schema changes between sessions, an agent's cached query patterns break silently. No surveyed tool exposes a schema fingerprint.
- **STRICT-table coverage.** SQLite STRICT tables are the loud-failure mechanism aligned with agent-write paths, but the ecosystem hasn't standardized around them — many tools and library examples still produce non-strict tables, leaving silent type coercion as the default.

## Random access and queryability

True indexed random access — the entire reason to use SQLite. Joins, aggregations, and constraints are first-class.

## Scale ceiling

Comfortably handles GB-scale databases. SQLite officially supports databases up to 281 TB. Constraint is single-writer concurrency (only one writer at a time); for multi-writer workloads, Postgres or MySQL is appropriate.

## Failure mode

Loud and constraint-driven. Invalid writes (NOT NULL violations, FK failures, type mismatches in STRICT tables) are rejected at write time. The strongest failure-mode profile of any format here.

## Claude-specific notes

- No Anthropic guidance specific to SQLite. The format is a standard tool any LLM can drive via a SQL-emitting MCP tool.
- The `/ocd:transcripts` skill in this project ingests JSONL transcripts into SQLite for query — `sql_query` exposes read-only `SELECT` to Claude (verified: `file:...?mode=ro` URI mode).
- For Claude to query SQLite effectively, schema introspection should be available — the project provides `schema_describe`.
- Result-set size matters for context cost — design tools to support `LIMIT`/`OFFSET` and column projection, not always returning all columns.
- The Anthropic-archived SQLite MCP server had f-string interpolation issues. **The project's own SQL composition is verified safe** — f-strings are used only for column-name composition with allowlist gates (`SETTINGS_SCHEMA` keys) or hardcoded sources; values flow through `?` parameter binding.

## Pitfalls and anomalies

- Default schema is non-strict — columns accept any type unless declared `STRICT`. Type mismatches succeed silently
- Single-writer constraint surprises authors expecting concurrent-write behavior
- The default journaling mode (`DELETE`) creates a `.db-journal` sidecar; WAL mode (`PRAGMA journal_mode=WAL`) creates `.db-wal` and `.db-shm` sidecars — `.gitignore` should exclude all
- Backup-during-write requires the backup API or VACUUM INTO; copying the file directly during a write produces a corrupted backup
- Indexes are not automatic — query performance falls off a cliff when the schema lacks indexes for actual query patterns

## Open questions

- Is there published guidance on optimal schema patterns for LLM-driven SQL query (flatter tables vs more joins, name conventions that aid query generation)?
- For Claude specifically, what's the result-set-format preference — JSON dict-per-row, two-array compact, markdown table — at typical query result sizes?
- Would adopting STRICT tables in the project's schemas (transcripts, navigator) reduce silent-coercion bugs enough to justify the migration cost?
- Is `format=compact` worth the API surface expansion vs document an "always ask for explicit columns" agent discipline rule?

## Sources

- [Spider 2.0 paper](https://arxiv.org/abs/2411.07763) — verified: 27.6% schema-linking failure attribution at scale, 16.6% column-linking specifically
- [AutoLink (arXiv 2511.17190)](https://arxiv.org/html/2511.17190) — autonomous schema exploration
- [M-Schema](https://github.com/XGenerationLab/M-Schema) — verified: 217 stars, semi-structured schema representation
- [ReFoRCE (arXiv 2502.00675)](https://arxiv.org/pdf/2502.00675) — Spider 2.0 leaderboard top
- [Datadog Security Labs — Postgres MCP SQLi case study](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/) — Anthropic reference Postgres MCP affected; no CVE assigned
- [CVE-2025-66335 (Apache Doris MCP)](https://nvd.nist.gov/vuln/detail/CVE-2025-66335) — verified
- [Anthropic archived MCP servers](https://github.com/modelcontextprotocol/servers-archived)
- [DBHub](https://github.com/bytebase/dbhub)
- [Postgres MCP Pro](https://github.com/crystaldba/postgres-mcp)
- [MotherDuck MCP](https://github.com/motherduckdb/mcp-server-motherduck)
- [Datasette MCP](https://github.com/mhalle/datasette-mcp)
- [sqlglot](https://github.com/tobymao/sqlglot)
- [sqlean](https://github.com/nalgeon/sqlean)
- [Simon Willison — sqlite-utils-ask](https://simonwillison.net/2024/Nov/25/ask-questions-of-sqlite/)
- [Python sqlite3 stdlib](https://docs.python.org/3/library/sqlite3.html)
- [MCP 2025-06-18 spec](https://modelcontextprotocol.io/specification/2025-06-18/schema)
- [Trend Micro — MCP vulnerability writeup](https://www.trendmicro.com/en_us/research/25/f/why-a-classic-mcp-server-vulnerability-can-undermine-your-entire-ai-agent.html)
