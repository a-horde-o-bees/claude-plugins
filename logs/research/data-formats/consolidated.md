# Data formats for LLM-read storage

Synthesized findings on choosing a data format for storing information that LLMs (especially Claude) read, write, and modify. Subject covers formats commonly used in Claude Code / agent-tooling projects: markdown, markdown with YAML frontmatter, JSON, JSONL, YAML, TOML, CSV/TSV, XML, SQLite, plain text, HTML. Each format has its own sample file under `samples/` carrying per-purpose evidence, agent-tooling catalog, capability matrix, and recommended starter set; this doc is the cross-format synthesis with explicit dispositions.

## Decision Table

Compact ratings for fast scanning. Cell notes explain non-obvious entries. Full per-format detail in each sample.

| Format | Token efficiency | LLM parse | LLM gen | Modify ergonomics | Diff/human readability | Tooling | Random access | Scale ceiling | Failure mode |
|---|---|---|---|---|---|---|---|---|---|
| **Markdown** | ✓ | ✓ | ✓ | ✓ line-oriented | ✓ | ~ no schema | ✗ | ~ ~10K lines | ✓ silent, prose-tolerant |
| **Markdown + YAML frontmatter** | ✓ | ✓ | ~ frontmatter indent errors | ✓ split header/body | ✓ | ✓ frontmatter parsers ubiquitous | ~ via index | ~ same as md | ~ frontmatter loud, body silent |
| **JSON** | ✗ repeated keys, brace tax | ✓ | ~ unclosed strings, trailing commas | ✗ whole-object rewrite | ~ noisy diffs on nested edits | ✓✓ schema, jq, JSON Schema | ✗ without index | ~ depth + size | ✓ loud — invalid JSON fails at line N |
| **JSONL / NDJSON** | ✓ vs JSON for arrays | ✓ | ✓ each line independent | ✓ append-only friendly | ✓ one record per line | ✓ jq, streaming parsers | ✓ line-seek + grep | ✓ millions of rows | ✓ bad lines isolated |
| **YAML** | ✓ best of structured per benchmarks | ✓ | ✗ indentation, type coercion (`no` → false), tab/space mixing | ~ indent-sensitive partial edits | ✓ | ✓ but ambiguous spec | ✗ | ~ depth painful past ~3 | ✗ silent type coercion; loud syntax |
| **TOML** | ~ | ✓ | ~ section-header errors | ~ section-grain edits | ✓ | ✓ pyproject standard | ~ via section | ✗ not for big data | ✓ loud parse errors |
| **CSV / TSV** | ✓ very dense | ~ ~16-pt accuracy gap behind markdown KV (non-Claude) | ~ quoting/escaping bugs | ~ row append easy, column edit hard | ~ wide rows wrap badly | ✓✓ pandas, sqlite import | ~ row-seek | ✓ millions of rows | ✗ silent (wrong column count parses as data) |
| **XML** | ✗ closing-tag tax | ✓✓ Anthropic-recommended for prompt structure | ✓ tag-symmetry forced | ~ nested edits painful | ~ verbose | ✓ schemas, XPath | ~ via XPath | ~ depth | ✓ loud on unclosed tags |
| **SQLite** | n/a (binary) | n/a (queried, not read raw) | n/a (model emits SQL, not file) | ✓✓ row/column granularity | ✗ binary, opaque diffs | ✓✓ SQL, indexes, constraints | ✓✓ true random access | ✓✓ GB scale | ✓ constraints reject invalid writes |
| **Plain text** | ✓ no overhead | ✓ for prose | ✓ | ✓ | ✓ | ✗ no schema | ✗ | ~ size only | ✗ silent — no validation |
| **HTML** | ✗ | ~ tag noise distracts | ~ similar to XML | ~ | ✗ verbose | ✓ DOM parsers | ~ via selectors | ~ | ~ tolerant — silent |

## Format Dispositions

Explicit go/avoid stance per format. Each disposition cites the dominant reason and names the alternative when warned.

### Endorsed

- **Markdown** — default for prose-first content (skills, rules, conventions, log entries, READMEs, ARCHITECTURE docs). Pair with `str_replace_based_edit_tool` discipline (Claude Code `Edit` mirrors the Anthropic spec) and `mdq` as a bash CLI for read-slicing.
- **Markdown + YAML frontmatter** — for content-with-metadata. Keep frontmatter flat; nest only when unavoidable. Read frontmatter via `python-frontmatter` to skip the body.
- **JSON** — for strict-schema configs (`plugin.json`, `settings.json`, `hooks.json`) and Claude tool-use definitions. Always pair with `strict: true` on tool definitions where the schema fits the supported feature set.
- **JSONL / NDJSON** — for append-only logs, transcripts, streaming events. Cheap appends preserve cache prefixes; bad lines isolate; line-seek + grep approximates random access.
- **SQLite** — for indexed structured data with relationships, constraints, or scale beyond a single file. Open with `file:...?mode=ro` URI for engine-level read-only safety; pair with schema-introspection tooling.
- **TOML** — only where the language ecosystem dictates (`pyproject.toml`). Don't introduce TOML for new niches.

### Acceptable with discipline

- **YAML — frontmatter only.** Project's heaviest YAML use is markdown frontmatter; that's fine. **Require `ruamel.yaml` round-trip mode for any code path that mutates YAML and writes it back. Forbid `PyYAML.dump` in plugin code.** Verified: PyYAML default sorts keys alphabetically and discards comments; ruamel.yaml round-trip preserves both. Silent comment loss is a real ongoing hazard.
- **Plain text** — only for genuinely unstructured single-purpose payloads (a UUID, a path, a status flag). If you reach for delimiters, switch to markdown.

### Warned — prefer alternative

- **CSV / TSV** — **wire format only, not working format.** Use only at ingest/export boundaries where another tool produced or will consume it.
    - **Why warned:** silent failure (wrong-column-count rows parse as data; quoting bugs corrupt silently); cell/column mutation is structurally always full-rewrite; LLM cell-lookup accuracy materially worse than markdown KV (non-Claude benchmark, ~16-pt gap, directionally consistent).
    - **Use instead:** SQLite (read/write workloads — `sqlite-utils insert ... --csv` ingest path) or DuckDB / Parquet (read-mostly analytical workloads — `duckdb -c "SELECT ... FROM read_csv_auto('file.csv')"`).
    - **Discipline rule:** on first contact with CSV ingest, the agent's first move is to load it into SQLite or run a DuckDB query before answering structural questions. Generate CSV from structured source only at the export boundary.
- **YAML — full-file as primary storage.** Beyond frontmatter, the silent-coercion + comment-loss hazards stack against full-file YAML.
    - **Use instead:** TOML (where the ecosystem permits — explicit typing, no Norway problem) or JSON with `strict: true` validation (loud failure, no silent coercion).

### Discouraged

- **XML — for storage.** XML earns its place at the prompt-assembly boundary (Anthropic recommends XML tags inside prompts to delimit `<instructions>`, `<context>`, `<input>`, etc. — see `samples/xml.md`). For file storage, JSON or markdown wins on every dimension.
- **HTML — for storage.** Browser-tolerance of malformed input + verbosity = worst failure mode + worst token efficiency. Convert to markdown for any agent-consumed content.

## Per-Purpose Cross-Format Synthesis

Each subsection is the one-paragraph cross-format read on a single dimension. Per-format detail and citations live in `samples/<format>.md` under the matching section heading.

### Token efficiency

Markdown and plain text carry near-zero delimiter tax; JSON pays the highest brace/quote/repeated-key tax among structured formats; YAML's indent-and-colon syntax wins among nested structured formats per third-party 2025 benchmarks (markdown 34-38% cheaper in tokens than JSON on the tested workloads). Token-count claims come from non-Claude benchmarks; directional, not measured for Claude.

### LLM parse reliability

All text formats parse reliably enough when well-formed; differences show up under malformation. Markdown and plain text degrade gracefully; JSON and XML fail loudly at a specific line; YAML's silent type coercion (`no` → `False`, `2:00` → time) is the one parse-time hazard the format introduces by syntax rather than malformation.

### LLM generation reliability

JSONL and markdown are most reliably generated by current LLMs (one-record-per-line and prose-with-headings respectively). JSON generation is acceptable but error-prone (unclosed strings, trailing commas) — Claude's `strict: true` tool-use mode largely closes this gap when the JSON is a defined-schema output. YAML is the riskiest to generate freehand.

### Modification ergonomics

JSONL and SQLite lead — append a line or `UPDATE` a row without touching anything else. Line-oriented markdown is close behind. Nested formats (JSON, XML, deeply-indented YAML) require re-emitting the enclosing object even for leaf-level changes.

### Diff and human readability

Markdown wins for prose; JSONL wins for structured records (one logical unit per line); YAML and TOML are readable but more brittle in code review. JSON arrays of objects produce noisy diffs because trailing-comma rules force unrelated lines to change. SQLite is opaque in git — `sqldiff` exists but is rarely set up.

### Tooling and ecosystem

JSON has the deepest ecosystem (JSON Schema, jq, every language's stdlib parser, partial-update RFCs 6901/6902/7396, JSONPath 9535). SQLite is unmatched for query, index, and constraint tooling within a single file. YAML and TOML have ubiquitous parsers but YAML's spec ambiguity (1.1 vs 1.2) creates parser-to-parser drift. CSV's strength is the pipeline ecosystem; markdown has weaker schema tooling but `mdq`/`mq` close the read-slice gap recently. See per-sample tool catalogs for the deeper map.

### Random access and queryability

SQLite is the only format with true indexed random access. JSONL approximates it via line-seek + grep — adequate for log scans, inadequate for joins. Every other text format requires full-file parse; path-language CLIs (`jq`, `yq`, `mdq`, `dasel`) approximate selective access by doing the parse for you.

### Scale ceiling

SQLite scales to GBs comfortably. JSONL scales to millions of rows. CSV scales similarly when the consumer streams. Single-file JSON, YAML, TOML degrade at the megabyte scale. Markdown's ceiling is the LLM's context window divided by retention needs.

### Failure mode

Loud-failing formats (JSON, XML, TOML, SQLite constraints) push errors to the moment of write. Silent-failing formats (CSV with bad column count, YAML with type coercion, plain text with no validation) push errors to whoever consumes the data later.

## Cross-Format Patterns

Patterns that surfaced across multiple format-specific deep-research passes and apply project-wide.

- **Pointer/path notation as a first-class read primitive.** JSON Pointer (RFC 6901) for JSON, jq filters for JSON, yq for YAML/JSON/TOML, JSONPath (RFC 9535) for JSON, dasel for unified cross-format, `mdq`/`mq` for markdown, SQL for SQLite. Every nested format benefits from a path language; the format choice should be paired with which path tool the agent uses to slice it.
- **Patch protocols over rewritten files.** RFC 6902 JSON Patch and Kubernetes strategic merge encode "what to change" rather than "what the file should look like after." For agents, emitting a small patch is structurally smaller than emitting a rewritten file. SQLite's `UPDATE ... SET col = ?` is the same pattern at the relational layer; `str_replace` is the same at the byte/string layer.
- **Tree-only views as a universal read mode.** Markdown's heading-tree, JSON's `jq 'paths'`, SQLite's `.schema`/PRAGMA, YAML's structure walking. "Describe shape, not content" is a cheap orientation primitive; surfacing it as a first-class read mode saves a probing read across every format.
- **Schema-as-context as first-class affordance.** Spider 2.0 results (verified ~27.6% of failures attributed to schema linking) confirm schema-introspection is the single highest-leverage read-path intervention for SQL. The lesson generalizes: JSON Schema, JSONL inferred schemas, frontmatter schemas, navigator's purpose-indexing for filesystem layout — all serve the same role of letting the agent learn structure once instead of re-deriving from data.
- **Header/body split for queryability.** Markdown+frontmatter's win — small structured header, large prose body, separated by a stable delimiter — is reusable. Any format that pairs structured metadata with bulk content benefits from a parser that returns the two separately.
- **Round-trip preservation as library default.** YAML's ruamel.yaml-vs-PyYAML lesson — that comment/key-order loss is silent damage that outlives the edit — applies to any format with comments or formatting humans care about. Pick the round-trip-preserving library at project setup; forbid the lossy default in code review.
- **Append-only as cheap-write disposition.** CSV row-append, JSONL line-append, markdown log entries, SQLite `INSERT` to append-only tables. When the working pattern is "add events, never edit," append-only is the cheapest representation across formats.
- **Auto-detection at the read boundary.** DuckDB CSV sniffer, CleverCSV dialect detection, JSON Schema inference, YAML-version auto-detect. Letting the read tool answer "what shape is this?" beats forcing the agent to ask via a probe-read first.
- **Loud-failure write paths and constraint feedback.** SQLite NOT NULL/CHECK/FOREIGN KEY error messages give the agent corrective signals; JSON Schema validators give the same shape for JSON. Where the format permits, surfacing structured-validation errors at write time generalizes.
- **Engine-boundary safety beats parser-boundary safety.** SQLite's `mode=ro` URI is structurally safer than parsing SQL to detect writes (the Anthropic Postgres MCP CVE bypassed parser-based read-only by using `COMMIT;DROP SCHEMA;`). Filesystem-level read-only mounts, GET-only HTTP servers, and JSONL append-only file modes all generalize the principle.
- **Deferred tool loading via search-index.** qsv MCP exposes 10 core tools and surfaces 40+ via `qsv_search_tools`, claiming ~80% token reduction. Pattern applies to any large-tool-surface MCP server.
- **Compact serialization with column-extraction.** Two-array `{columns, rows}` layouts beat per-row dict layouts when the result is wide and the agent will scan or aggregate. Tools that offer both shapes let the agent pick.

## Verified Project Recommendations

Project-actionable shortlist drawn from the agent-tools research wave, with each recommendation traced to a verified source. Ordered by leverage.

1. **Adopt `strict: true` on existing MCP tool definitions** (transcripts, navigator, future plugin servers). Verified GA on Claude Opus/Sonnet/Haiku 4.5/4.6/4.7 per [Anthropic strict tool use docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use). Zero new dependencies; eliminates malformed-output retry loops. Trade-off: tool input schemas must avoid recursive types, external `$ref`, numerical/string-length constraints, and `additionalProperties: true`.
2. **Codify `ruamel.yaml` round-trip mode as the project YAML default.** Verified: PyYAML default `sort_keys=True` and discards comments; ruamel.yaml `YAML(typ='rt')` preserves comments, key order, quote style, block style. Worth a Python-convention update under `.claude/conventions/ocd/python.md` plus a code-review rule forbidding `PyYAML.dump` in mutating code paths.
3. **Allowlist `mdq`, `jq`, `yq` as bash CLIs for read-path slicing.** All three verified to exist and address the read-path token-waste pattern. `mdq` v0.10.0 (Mar 2026), `yq` v4.53.2 (Apr 2026), `jq` reference implementation. Pair with a convention bullet pointing the agent at the right tool when only one path matters from a structured file.
4. **Three concrete enhancements to the existing `sql_query`/`schema_describe` MCP surface:**
    - `format=compact` — two-array `{columns, rows}` shape instead of dict-per-row, eliminates per-row column-name repetition.
    - `format=summary` — per-column type, distinct count, NULL count, min/max, sample values; replaces `SELECT * LIMIT 5` orientation pattern.
    - M-Schema-style tuple-per-column on `schema_describe` if the schema grows large enough that introspection cost dominates. M-Schema verified at [github.com/XGenerationLab/M-Schema](https://github.com/XGenerationLab/M-Schema), 217 stars, Apache-2.0.
5. **Project's existing SQL discipline is verified safe — no audit needed.** The `sql_query` engine-level read-only via `file:...?mode=ro` URI is structurally stronger than parser-based read-only (which the 2025 Anthropic Postgres MCP vulnerability bypassed via `COMMIT;DROP SCHEMA;` per [Datadog Security Labs](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/)). Project f-string SQL composition uses allowlisted column names + `?` parameter binding for values — verified safe at `transcripts/_settings.py` and `navigator/__init__.py`.
6. **Write the CSV "wire format, not working format" discipline as a project rule.** When CSV appears as ingest, first move is to load into SQLite (`sqlite-utils insert --csv`) or run a DuckDB query (`read_csv_auto`). Generate CSV from structured source only at the export boundary.

## Claude-Specific Considerations

**XML tags inside prompts.** Anthropic's prompt-engineering guidance recommends XML tags to delimit content sections inside a prompt — wrapping `<instructions>`, `<context>`, `<input>`, etc. reduces misinterpretation. For multi-document inputs the docs prescribe a `<documents><document index="n"><source>...</source><document_content>...</document_content></document></documents>` shape. This is guidance about prompt structure, not file storage. See [Anthropic — XML tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags) and `samples/xml.md`.

**Tool definitions and tool calls.** Claude's tool-use API is JSON-based. Tool definitions carry JSON Schema; tool calls return `tool_use` blocks with a JSON `input` object. With `strict: true`, Claude is constrained to schema-conformant outputs — verified GA across current models.

**Prompt caching and format choice.** Cache hit rates depend on stable prefixes, not on which format the prefix is in. The format implication is indirect but real: append-only formats (JSONL, markdown logs) preserve stable prefixes by construction; formats requiring rewrite of a containing object on every change (JSON arrays, deeply nested YAML) invalidate caches more often. No Anthropic guidance directly comparing formats by cache impact was found — mechanism-based inference, not documented claim.

**Format-vs-accuracy benchmarks.** Recent (2025) third-party benchmarks suggest YAML edges JSON/XML for nested data on smaller models, and Markdown-KV beats CSV/JSONL by ~16 points on tabular cell-lookup. These were tested on GPT-5 Nano, Gemini 2.5 Flash Lite, Llama 3.2 3B, and GPT-4.1-nano — **not Claude**. No Claude-specific format-accuracy benchmarks from Anthropic were found. Llama 3.2 showed no strong preference in the same study, so model-specific variance is real.

**JSON Whisperer paper** (verified: arxiv 2510.04717, "JSON Whisperer: Efficient JSON Editing with LLMs") reports a 31% **output-token** reduction with EASE array encoding on a synthetic ~400-example dataset, tested on GPT-4o-mini and Claude Sonnet. Directional for Claude generally; not measured at Opus tier.

**Spider 2.0 schema-linking findings.** Verified: schema linking dominates text-to-SQL failures on real enterprise schemas — "Wrong schema linking 33.0%" overall, "column linking errors 16.6%" specifically, "schema linking at scale with 700+ columns 27.6%" of SQL errors. Source: [Spider 2.0 paper](https://arxiv.org/abs/2411.07763). Confirms schema-introspection tooling (the project's `schema_describe`) is well-positioned.

**MCP SQLi disclosure wave (2025).** Multiple SQL injection vulnerabilities disclosed in MCP servers from f-string interpolation: Anthropic's archived reference Postgres MCP server (no CVE assigned per Datadog article); Apache Doris MCP CVE-2025-66335 (verified at NVD, fixed in 0.6.1); SQLite MCP `describe_table` table-name concatenation. Engine-boundary read-only enforcement (`file:...?mode=ro`) is the structural fix; parser-based read-only was bypassed in the Anthropic case via `COMMIT;DROP SCHEMA;`.

## Caveats

- Token-cost ratios cited (e.g., 34-38% markdown-vs-JSON, 2.7× markdown-KV-vs-CSV, 31% JSON Whisperer EASE) come from third-party benchmarks on non-Claude models or synthetic datasets. Treat as directional, not authoritative for Claude.
- "JSON tends to need post-processing" is conventional wisdom; with Claude's `strict: true` tool use, the gap largely closes for schema-defined outputs.
- The append-only-vs-rewrite cache-hit claim is mechanism-based inference, not measured.
- The decision table emphasizes single-document tradeoffs. When a need spans multiple documents (e.g., a corpus of related records), JSONL and SQLite move up regardless of any single-document score.
- Tool-catalog entries reflect what searches surfaced in April 2026. MCP server registries evolve week-to-week; "not yet found" applies, not "does not exist."

## Sources

- [Anthropic — Prompting best practices (use-xml-tags)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/use-xml-tags)
- [Anthropic — Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) — verified GA on Claude 4.5/4.6/4.7
- [Anthropic — Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Anthropic — Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) — `text_editor_20250728`
- [Anthropic — Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic — Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [JSON Whisperer (arXiv 2510.04717)](https://arxiv.org/abs/2510.04717) — verified: 31% output-token reduction, GPT-4o-mini + Claude Sonnet
- [Spider 2.0 (arXiv 2411.07763)](https://arxiv.org/abs/2411.07763) — verified: schema linking 33% / column linking 16.6% / scale 27.6% of failures
- [Datadog Security Labs — Postgres MCP SQLi](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/) — Anthropic reference Postgres MCP affected; no CVE assigned
- [CVE-2025-66335 (Apache Doris MCP)](https://nvd.nist.gov/vuln/detail/CVE-2025-66335) — verified
- [github.com/yshavit/mdq](https://github.com/yshavit/mdq) — verified v0.10.0 (Mar 2026)
- [github.com/mikefarah/yq](https://github.com/mikefarah/yq) — verified 15.3k stars, v4.53.2 (Apr 2026)
- [github.com/XGenerationLab/M-Schema](https://github.com/XGenerationLab/M-Schema) — verified 217 stars
- [improvingagents.com — nested data format benchmark](https://www.improvingagents.com/blog/best-nested-data-format/) — non-Claude
- [improvingagents.com — table format benchmark](https://www.improvingagents.com/blog/best-input-data-format-for-llms/) — non-Claude
