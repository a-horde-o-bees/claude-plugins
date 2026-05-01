# CSV / TSV

Plain-text tabular format with comma- or tab-separated values, one record per line. Industry-standard interchange format for tabular data between spreadsheets, databases, and analytics pipelines.

## Metadata

- **File extensions:** `.csv`, `.tsv`
- **MIME type:** `text/csv` (RFC 4180, 2005), `text/tab-separated-values`
- **Spec:** RFC 4180 standardizes CSV but predates many real-world dialects (Excel CSV, MySQL CSV, etc.). TSV has no formal spec
- **Primary use cases:** Data export/import between Excel, databases, and pandas; bulk load into SQLite/Postgres; wire format for tabular dumps; legacy systems

## Disposition

**WARN — wire format only, not working format.** CSV is appropriate at ingest/export boundaries where another tool produced or will consume it. **Do not use CSV as primary LLM-read storage** for data the agent will repeatedly query or mutate. Reasons:

1. **Silent failure profile** — wrong-column-count rows, dialect ambiguity, and quoting bugs all parse as valid data, producing silently wrong results.
2. **Cell-level mutations are structurally impossible to make cheap** on row-major flat text — adding a column or updating a cell forces full-file rewrite.
3. **LLM cell-lookup accuracy is materially worse on CSV** than markdown KV-list per a 2025 third-party benchmark on GPT-4.1-nano (44.3% vs 60.7%, ~16-point gap; not Claude-specific but directionally consistent).

**The right answer for CSV-as-LLM-storage is to convert it to format X.** When CSV appears as ingest, the agent's first move is to load it into SQLite (read/write workloads) or DuckDB / Parquet (read-mostly analytical workloads) before answering structural questions. Sustained agent work against a raw CSV file is the anti-pattern this disposition prevents.

## Token efficiency

Very dense — no per-cell delimiters beyond the column separator, no repeated keys, no quoting unless required. For pure tabular data, CSV is the most token-efficient text format. The cost is paid in interpretability — without column headers in context, the LLM sees a wall of comma-separated values.

### Read-path inefficiency

- **Whole-file reads for cell-level needs.** A row-major text format is opaque to byte-offset access — finding "the value of column `email` in the row where `id = 7`" requires a parser to walk every prior row, and the cheapest agent-side approach is `Read` the whole file. The "very dense" property applies only when the whole file is needed; once the agent only needs one cell, every other cell is wasted context.
- **Wide-row context bleeding.** A CSV with 30 columns and 200 rows produces 6,000 cells with no structural cue grouping cells under their column. The agent must hold the header in working context to interpret any later row. The third-party 2025 benchmark measured a ~16-point accuracy gap between CSV (44.3%) and Markdown-KV (60.7%) on cell-lookup specifically because the agent loses cells when rows are wide ([ImprovingAgents](https://www.improvingagents.com/blog/best-input-data-format-for-llms/)).
- **No projection.** Column-grain selectivity ("show me only `id`, `name`, `email` from this 30-column file") is not native; agents either read the whole file and project mentally, or invoke a tool.
- **No predicate pushdown.** Row-grain selectivity ("rows where `status = 'failed'`") similarly requires a tool. Naive `grep` works only when the predicate happens to be a substring of the line.
- **Header repetition in serialized output.** Tools that re-emit each row in expanded form (dictionary-per-line JSON) duplicate column-name strings on every row.
- **Dialect ambiguity.** Real CSV is a family of dialects. An agent that picks the wrong dialect parses garbage and either retries or proceeds on wrong data. Auto-detection (DuckDB, qsv, CleverCSV) short-circuits this.

### Write-path inefficiency

Sharper structural problem: row-major flat text doesn't admit partial mutations cleanly except at the row-append boundary.

- **Column-add forces full rewrite.** Every existing row must gain a new field at a positional index. There is no in-place mechanism that avoids this: "If you want to extend existing rows by adding more columns, you will have to rewrite the whole file from beginning to end" ([sqlpey.com](https://www.sqlpey.com/python/top-6-ways-to-append-to-csv/)).
- **Cell update forces row rewrite at minimum.** Read-modify-write the whole file is the common path; one cell changed → full file in the diff.
- **Reordering or renaming columns is a full rewrite.** The header is one line, but every row encodes column position.
- **Append is the one cheap operation.** Adding a new row is `>>` to the file. This is the only path where CSV's flat-text shape is a write-side virtue.
- **Atomic safety.** Even row-append carries a corruption risk if interrupted mid-write — Python's `csv.writer` doesn't fsync by default; partial line is silent CSV corruption.

The structural conclusion: cell-level and column-level mutations on CSV cannot be made cheap on the write side. Mitigation: push mutation off the CSV — load into SQLite or DataFrame, mutate, write CSV out only at the export boundary.

## LLM parse reliability

Mixed. The 2025 benchmark on GPT-4.1-nano showed CSV at 44.3% accuracy versus Markdown-KV's 60.7% on cell-lookup tasks. The model can read CSV but loses cells when rows are wide or many. Not Claude-specific.

## LLM generation reliability

Acceptable for simple tables. Risks: quoting bugs (commas inside values without surrounding quotes) and escape-character handling (RFC 4180 specifies doubled quotes; many models default to backslash escaping, which is wrong).

## Modification ergonomics

Row-grain operations are easy: appending and replacing rows are line-level. Column-grain operations are hard: adding a column requires touching every row; reordering columns requires rewriting every row.

## Diff and human readability

Wide rows wrap awkwardly in editors and PR diffs. Column-aligned viewing requires a tool (`column -t`, `csvlook`, `visidata`). Diffs of cell-level changes are hard to scan.

## Tooling and ecosystem

### Tool catalog

| Name | URL | Type | Maturity | Primary capability | Token reducer |
|---|---|---|---|---|---|
| qsv MCP server | [github.com/dathere/qsv](https://github.com/dathere/qsv) | MCP | 3.6k stars; deferred-load model | 50+ commands wrapping qsv's CSV/Excel/JSONL toolkit | Deferred tool loading — 10 core tools at session start, others via `qsv_search_tools` (project claims ~80%); TSV output reduces emission ~30% vs CSV-quoted |
| MotherDuck/DuckDB MCP | [github.com/motherduckdb/mcp-server-motherduck](https://github.com/motherduckdb/mcp-server-motherduck) | MCP | Official MotherDuck-maintained | `execute_query` over DuckDB | Default 1024-row / 50K-char result cap; CSV via `read_csv_auto('file.csv')` with projection + predicate pushdown |
| sqlite-utils | [github.com/simonw/sqlite-utils](https://github.com/simonw/sqlite-utils) | CLI + library | v3.39 (Nov 2025) | `insert ... --csv` builds typed schema from CSV; `memory` runs SQL against CSV without persisting | `sqlite-utils memory data.csv "select id, email from t where status='failed'"` projects + filters in one command |
| DuckDB (CLI/library) | [duckdb.org](https://duckdb.org/) | library + CLI | Mature | `read_csv_auto`/`read_csv` exposes CSV as a queryable relation in-process | Projection + predicate pushdown at scan |
| Polars `scan_csv` | [docs.pola.rs](https://docs.pola.rs/py-polars/html/reference/api/polars.scan_csv.html) | library | Mature Rust+Python | Lazy CSV scan with query optimizer | Same projection/predicate pushdown story |
| pandas `read_csv` | [pandas.pydata.org](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) | library | Industry default | `usecols=`, `nrows=`, `chunksize=`, `dtype=` | Reduces reads to requested slice; chunksize streams |
| csvkit | [csvkit.readthedocs.io](https://csvkit.readthedocs.io/en/latest/cli.html) | CLI | v2.2 | `csvcut`, `csvgrep`, `csvsql`, `csvstat`, `csvjson`, `csvlook` | Each command is column-aware; projection/filter happen tool-side |
| xsv | [github.com/BurntSushi/xsv](https://github.com/BurntSushi/xsv) | CLI | Maintenance mode (use `qsv` as fork) | Slice/select/search/index/stats over CSV | `xsv index` enables O(1) row-seek |
| miller (`mlr`) | [github.com/johnkerl/miller](https://github.com/johnkerl/miller) | CLI | Active multi-format | awk-like pipelines across CSV/TSV/JSON/JSONL with field-name DSL | Verb chain projects + filters in one streaming pass |
| qsv (CLI) | [qsv.dathere.com](https://qsv.dathere.com/) | CLI | 3.6k stars; active xsv fork | 50+ commands incl. `select`, `search`, `sqlp` (Polars SQL), `sniff`, `validate`, `index`, `stats` | True random access via index; in-process Polars SQL |
| CleverCSV | [github.com/alan-turing-institute/CleverCSV](https://github.com/alan-turing-institute/CleverCSV) | library | Alan Turing Institute project | Drop-in `csv` replacement with high-accuracy dialect sniffer (~97% per project README) | One correct read instead of two wrong ones |
| RFC 4180 | [rfc-editor.org/rfc/rfc4180](https://www.rfc-editor.org/rfc/rfc4180.html) | spec | Stable since 2005 | Canonical comma-delimited dialect | Eliminates dialect ambiguity on write |
| CSV on the Web (csvw) | [w3c.github.io/csvw](https://w3c.github.io/csvw/primer/) | spec | W3C recommendation | JSON sidecar describing schema, types, primary key | Schema sidecar lets agent learn structure once |
| Frictionless Data / Table Schema | [datapackage.org](https://datapackage.org/) | spec + library | Open Knowledge Foundation | Data Package container, Table Schema descriptor | Same schema-sidecar story with broader ecosystem |
| Apache Parquet | [parquet.apache.org](https://parquet.apache.org/) | format | Industry standard for analytical columnar | Columnar binary with embedded schema | True column-projection from disk; ~5× smaller than CSV per DuckDB TPC-H benchmark |

### Capability matrix

`Y` = first-class, `~` = possible but indirect, `N` = absent/impractical.

| Tool / pattern | Project | Filter | Aggregate | Sniff dialect | Mutate row | Mutate column | Append row | Validate schema | Ingest to DB |
|---|---|---|---|---|---|---|---|---|---|
| qsv MCP | Y | Y | Y | Y | ~ via SQL+rewrite | ~ via rewrite | Y | Y | Y |
| DuckDB MCP | Y (SQL) | Y (SQL) | Y | Y (`read_csv_auto`) | ~ load → UPDATE → COPY | ~ | Y | ~ via constraints | Y native |
| sqlite-utils | Y (`memory ... select`) | Y | Y | ~ stdlib sniffer | ~ via SQL | ~ via `transform` | Y (`insert --csv`) | Y (`schema`) | Y |
| DuckDB CLI | Y | Y | Y | Y | ~ same load-mutate-export | ~ | Y | ~ | Y |
| Polars (`scan_csv`) | Y | Y | Y | ~ | ~ DataFrame ops | ~ | Y | ~ via `Schema` | ~ |
| pandas | Y (`usecols`) | Y | Y | ~ | ~ | ~ | Y (`mode='a'`) | ~ | Y (`to_sql`) |
| csvkit | Y (`csvcut`) | Y (`csvgrep`) | Y (`csvstat`) | ~ stdlib | N | N | Y (`csvstack`) | ~ (`csvclean`) | Y (`csvsql --insert`) |
| miller | Y (`cut`) | Y (`filter`) | Y (`stats1`) | ~ | Y (`put`) | Y (`reorder`/`rename`) | Y | N | ~ |
| qsv (CLI) | Y | Y (`search`, `sqlp`) | Y (`stats`) | Y (`sniff`) | ~ | ~ | Y (`cat`) | Y (`validate`, `schema`) | Y (`to`, sqlite) |
| CleverCSV | N | N | N | Y (97% accuracy) | N | N | N | ~ | N |
| csvw / Table Schema | N | N | N | Y (declared) | N | N | N | Y (descriptor) | N |

Many cells are `~` because cell-grain or column-grain mutation on CSV is structurally always full-rewrite. The mitigation is the *Ingest to DB* column.

### Recommended starter set

For this project (Claude Code plugins, SQLite is primary structured-data substrate, CSV is rare and lives at ingest/export):

1. **DuckDB CLI / `read_csv_auto`** as the in-process query engine. `duckdb -c "SELECT id, email FROM read_csv_auto('users.csv') WHERE status = 'failed' LIMIT 50"` projects, filters, sniffs, and limits in one shell command. Stateless; no persisted database.
2. **`sqlite-utils insert ... --csv`** as the ingest-to-database path when CSV needs to become persistent structured storage. Lands data in SQLite where the project's other structured data already lives; CSV becomes archival.
3. **Discipline rule: CSV is wire format, not working format.** Codify this so that on first contact with CSV ingest, the agent's first move is to load it into SQLite (or run a DuckDB query) before answering structural questions. Generate CSV from the structured source via `COPY ... TO 'file.csv'` (DuckDB) or `sqlite-utils ... --csv` only at the export boundary.

The qsv MCP server is the strongest *general-purpose CSV-first* MCP option, fine for projects where CSV is genuinely primary; not the recommendation here because the project's CSV exposure is small and SQLite-centric.

### Gaps

- **In-place cell update without full rewrite.** Structurally impossible on row-major flat text; no tool surfaced fixes this. Mitigation is "load into a DB, mutate, export."
- **Column-add without full rewrite.** Same impossibility; same mitigation.
- **Token-budgeted query result emission.** No CSV tool found exposes a "return at most N tokens of result" knob.
- **Streaming partial-read with seek by primary key.** `xsv index` and `qsv index` give row-number access; key-based seek requires SQL ingest.
- **Agent-aware schema inference output.** Tools produce JSON Schema or CREATE TABLE, both verbose. A token-compact "header + types + key + cardinality" tuned for prompt embedding wasn't surfaced.
- **MCP servers that consume csvw/Frictionless schema sidecars** to plan tool calls — not surfaced in this search.
- **Concurrent-write safety on append.** No tool surfaced offers row-append with locking; concurrent appends can interleave bytes mid-line.

## Random access and queryability

Row-seek via line index is feasible. Column lookup requires header parsing. True query needs ingest into SQLite/DuckDB or pandas/Polars.

## Scale ceiling

Scales to millions of rows when consumed by streaming readers. The bottleneck is the consumer, not the format.

## Failure mode

**Worst failure-mode profile of any format here.** Silent and dangerous for wrong-column-count rows — many parsers treat them as valid data, shifting all subsequent values. Quoting bugs likewise produce silently wrong parses.

## Claude-specific notes

- No Anthropic guidance specific to CSV; no first-party Anthropic CSV MCP tooling found in this search.
- The third-party benchmark (44.3% CSV vs 60.7% Markdown-KV cell-lookup on GPT-4.1-nano) is directionally relevant but not Claude-measured. Treat as a reason to avoid CSV as primary LLM-read storage; not a quantitative claim about Claude's accuracy.

## Pitfalls and anomalies

- Multiple incompatible dialects: Excel CSV (comma + double-quote escape), MySQL CSV (comma + backslash escape), European Excel CSV (semicolon as separator)
- BOM at file start trips some parsers (Excel writes UTF-8 BOM by default)
- Cells containing commas, newlines, or quotes require quoting; failing to quote produces silent corruption
- TSV has no formal escaping spec — embedded tabs in cells break the format
- Trailing newlines and blank lines are ambiguously handled
- Large numbers (16+ digit identifiers) lose precision when Excel auto-imports as numbers

## Open questions

- Does Claude perform better on CSV than the GPT-4.1-nano benchmark suggests? Not measured in publicly available studies.
- For tabular data the LLM must read directly, is the recommended pattern to convert to markdown KV-list / markdown table for retrieval, then store as CSV for ingest pipelines?
- Are there established conventions for embedding schema/dtype information in a CSV header beyond column names? csvw and Frictionless are the candidates; adoption signals weren't measured here.

## Sources

- [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180.html) — canonical CSV dialect
- [csvw primer (W3C)](https://w3c.github.io/csvw/primer/) — schema sidecar pattern
- [Frictionless Data / datapackage.org](https://datapackage.org/)
- [github.com/dathere/qsv](https://github.com/dathere/qsv) — qsv + qsv MCP
- [github.com/motherduckdb/mcp-server-motherduck](https://github.com/motherduckdb/mcp-server-motherduck) — DuckDB MCP
- [github.com/simonw/sqlite-utils](https://github.com/simonw/sqlite-utils) — `insert --csv`, `memory`
- [duckdb.org/docs/current/data/csv/auto_detection](https://duckdb.org/docs/current/data/csv/auto_detection)
- [docs.pola.rs — Polars scan_csv](https://docs.pola.rs/py-polars/html/reference/api/polars.scan_csv.html)
- [pandas.pydata.org — read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [csvkit.readthedocs.io](https://csvkit.readthedocs.io/en/latest/cli.html)
- [github.com/BurntSushi/xsv](https://github.com/BurntSushi/xsv) — maintenance mode
- [github.com/johnkerl/miller](https://github.com/johnkerl/miller)
- [github.com/alan-turing-institute/CleverCSV](https://github.com/alan-turing-institute/CleverCSV)
- [parquet.apache.org](https://parquet.apache.org/)
- [last9.io — Parquet vs CSV](https://last9.io/blog/parquet-vs-csv/) — directional benchmark recap
- [improvingagents.com — table format benchmark](https://www.improvingagents.com/blog/best-input-data-format-for-llms/) — non-Claude
- [sqlpey.com — appending to CSV](https://www.sqlpey.com/python/top-6-ways-to-append-to-csv/) — column-add forces full rewrite
