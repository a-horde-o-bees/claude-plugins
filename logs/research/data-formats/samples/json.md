# JSON

Strict-syntax structured data format using nested objects and arrays. Primary interchange format for web APIs, configuration files consumed by tools, and Claude's tool-use protocol.

## Metadata

- **File extensions:** `.json`
- **MIME type:** `application/json`
- **Spec:** RFC 8259 (2017), ECMA-404 (2013)
- **Primary use cases:** Web API request/response bodies, schema-validated configuration (`plugin.json`, `settings.json`, `package.json`, `tsconfig.json`), Claude tool-use input/output, anywhere a JSON Schema validator is the source of truth

## Disposition

**Endorsed** — for strict-schema configs read by tools and for Claude tool-use definitions. Pair with `strict: true` on tool definitions to eliminate malformed-output retry loops. Avoid for prose-heavy content (use markdown) and for arrays of records that grow unbounded (use JSONL).

## Token efficiency

Among the worst structured formats for token cost — every key is repeated for every record, every string is double-quoted, every nested object adds braces, no comments to amortize. Per the 2025 third-party nested-data benchmark, Markdown was 34-38% cheaper than JSON in tokens on the tested non-Claude workloads.

### Read-path inefficiency

- **Whole-document loads.** Default agent move when a JSON file is referenced is `Read` on the whole file. For `package.json` or `settings.json`, every key-value pair the agent did not need still enters context.
- **Repeated keys in arrays of objects.** A list of N records repeats every key N times. JSONL avoids this at the record level.
- **Tool responses that ship full objects when one field was needed.** An agent calls a tool returning `{user: {profile: {name, email, ...50 other fields}}}` and only `name` is consumed.
- **Pretty-printing tax.** Whitespace-formatted JSON carries indentation tokens minified JSON does not.

The read-path remedy is selective access — name the path or query, get only that, never touch the rest.

### Write-path inefficiency

- **Whole-object rewrites for leaf edits.** Changing `version` in a 200-line `plugin.json` requires the model to emit the whole file in conventional `Write` flow.
- **Re-emitting nested context.** Anchor-based edits (`str_replace`-style) require enough surrounding context to make the anchor unique, scaling with depth.
- **Array index drift.** Inserting one element into an array of objects shifts every subsequent index — a known LLM weakness ([JSON Whisperer paper](https://arxiv.org/abs/2510.04717)).
- **Round-trip parse-and-reserialize.** Tools that "edit" by deserializing, mutating in memory, and reserializing destroy formatting and re-emit the whole document.

The write-path remedy is partial-mutation protocols — express only the change, not the post-change state.

## LLM parse reliability

Excellent. JSON's strict syntax means unambiguous structure extraction once the input is well-formed.

## LLM generation reliability

Acceptable but error-prone in free generation — common failure modes are unclosed strings, trailing commas, unescaped newlines inside string values, dropped closing braces in deeply nested output. Anthropic's `strict: true` on tool definitions constrains generation to a JSON Schema and largely closes this gap when the JSON is a defined-schema output. Verified: `strict: true` is GA on Claude Opus 4.5/4.6/4.7, Sonnet 4.5/4.6, and Haiku 4.5 per Anthropic docs.

## Modification ergonomics

Weak for partial edits. Changing a leaf value usually requires re-emitting at least the enclosing object. `jq` and JSON Patch (RFC 6902) provide partial-edit primitives but few MCP servers expose them as agent affordances today.

## Diff and human readability

Acceptable but noisy. Trailing-comma rules force unrelated lines to change when array items are added or removed. Most reviewers can read JSON, but YAML/TOML/markdown read more naturally.

## Tooling and ecosystem

### Tool catalog

| Name | URL | Type | Maturity | Primary capability | Token reducer |
|---|---|---|---|---|---|
| `jq` | [jqlang.org](https://jqlang.org) | CLI | Reference implementation; widely packaged | Filter, project, transform JSON via expression language | Selective read — emit only matched paths/fields; minified output |
| RFC 6901 JSON Pointer | [rfc-editor.org/rfc/rfc6901](https://www.rfc-editor.org/rfc/rfc6901) | IETF spec | Published 2013 | Single-value path notation (`/foo/bar/0`) | Point at one location instead of describing structure |
| RFC 6902 JSON Patch | [datatracker.ietf.org/doc/html/rfc6902](https://datatracker.ietf.org/doc/html/rfc6902) | IETF spec | Published 2013; libraries in every major language | Array-of-operations partial mutation | Express only the delta; don't re-emit document |
| RFC 7396 JSON Merge Patch | [datatracker.ietf.org/doc/html/rfc7396](https://datatracker.ietf.org/doc/html/rfc7396) | IETF spec | Published 2014 | Partial-document merge (only the changed subtree) | Simpler than 6902 for tree-shaped edits; no array element addressing |
| RFC 9535 JSONPath | [rfc-editor.org/rfc/rfc9535.html](https://www.rfc-editor.org/rfc/rfc9535.html) | IETF spec | Published Feb 2024 | Multi-value path query language | Selective read for queries returning multiple matches |
| Anthropic strict tool use (`strict: true`) | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) | Pattern (API feature) | GA on Claude 4.5/4.6/4.7 (verified) | Schema-constrained generation; grammar-restricted tokens | Eliminates retry loops on malformed JSON |
| JSON Schema | [json-schema.org](https://json-schema.org) | Spec | De facto standard | Validate and constrain JSON shape | Rejects bad input early; pairs with codegen (Pydantic, AJV) |
| python-json-patch (`jsonpatch`) | [pypi.org/project/jsonpatch/](https://pypi.org/project/jsonpatch/) | Library | Mature on PyPI | RFC 6902 apply + diff generation in Python | `make_patch(src, dst)` produces minimal patch |
| fast-json-patch | [npmjs.com/package/fast-json-patch](https://www.npmjs.com/package/fast-json-patch) | Library | Mature, widely used | RFC 6902 apply + compare in JavaScript | Same role for JS-based MCP servers |
| json-repair (Python) | [pypi.org/project/json-repair/](https://pypi.org/project/json-repair/) | Library | Active; v0.59.5 (April 2026) | Repair malformed LLM JSON output | Avoids regeneration round-trips when single-character defects would force retry |
| ijson | [github.com/ICRAR/ijson](https://github.com/ICRAR/ijson) | Library | Niche but documented | Incremental parse of streaming JSON | Lets a consumer act on partial output before full doc arrives |
| mcp-jq | [github.com/247arjun/mcp-jq](https://github.com/247arjun/mcp-jq) | MCP server | Small (4 stars at fetch); proof-of-concept | Exposes jq query/filter/format/validate as MCP tools | Selective read against JSON file via jq filter |
| ciresnave/json-mcp-server | [mcpservers.org/servers/ciresnave/json-mcp-server](https://mcpservers.org/servers/ciresnave/json-mcp-server) | MCP server | Listed in MCP server registries | Read, write, query, validate large JSON files | Streaming + path-based access |
| DuckDB (`read_json`) | [duckdb.org/docs/current/data/json/loading_json](https://duckdb.org/docs/current/data/json/loading_json) | CLI/Library | Mature; widely deployed | Query JSON with SQL | SQL projection + filter pushdown |
| Anthropic `str_replace_based_edit_tool` | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) | First-party tool | `text_editor_20250728` | Anchor-based file edit | Avoids whole-file rewrites |

### Capability matrix

Rows are tools/patterns. Columns are operations a JSON-aware agent stack needs.

| | Load whole | Project / select | Multi-match query | Validate schema | Patch leaf | Patch tree | Schema-constrained gen | Summarize |
|---|---|---|---|---|---|---|---|---|
| jq | ✓ | ✓ | ✓ | ~ via expr | ~ via assign | ~ | ✗ | ✓ keys/types |
| JSON Pointer | ✗ | ✓ single | ✗ | ✗ | ~ as ID in 6902 | ✗ | ✗ | ✗ |
| JSON Patch (6902) | ✗ | ✗ | ✗ | ✗ | ✓ | ~ via replace+remove | ✗ | ✗ |
| Merge Patch (7396) | ✗ | ✗ | ✗ | ✗ | ~ via subtree | ✓ | ✗ | ✗ |
| JSONPath (9535) | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| python-json-patch | ✗ | ✗ | ✗ | ✗ | ✓ apply+diff | ~ | ✗ | ✗ |
| Anthropic strict | ✗ | ✗ | ✗ | ✓ on output | ✗ | ✗ | ✓ | ✗ |
| JSON Schema | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ via codegen | ~ via schema docs |
| mcp-jq | ✓ load file | ✓ | ✓ | ~ via jq | ~ | ✗ | ✗ | ✓ |
| ciresnave/json-mcp-server | ✓ | ✓ | ✓ | ✓ | ✓ | ~ | ✗ | ✓ |
| DuckDB read_json | ✓ | ✓ | ✓ | ~ via cast | ~ via UPDATE | ✗ | ✗ | ✓ types/cols |
| str_replace_based_edit_tool | ~ via view | ~ via view_range | ✗ | ✗ | ✓ anchor | ~ | ✗ | ✓ via view |

### Recommended starter set

1. **Adopt `strict: true` on existing MCP tool definitions** (transcripts, navigator, future plugins). Highest leverage because it's free of new dependencies and removes the entire class of "Claude generated invalid JSON, retry" loops. Trade-off: schema must avoid recursive types, external `$ref`, numerical/string-length constraints, and `additionalProperties: true`. One-line change with measurable reliability gain. Tied to write-path pain.
2. **`jq` invoked through the existing Bash tool, allow-listed once.** Already the de facto tool for selective JSON read; agent can ask `jq -c '.mcpServers["foo"]' settings.json` instead of `Read settings.json`. Pair with a convention bullet pointing the agent at jq when only one path matters. Trade-off: requires `jq` on the user's machine — falls under the project's existing system-tool dependency pattern. Tied to read-path pain.
3. **Adopt RFC 6902 JSON Patch as the convention for any future "modify a structured config" tool** the project builds — but do not retrofit onto small files like `plugin.json` (200 lines) where `str_replace_based_edit_tool` already pays its way. JSON Whisperer reports a 31% **output-token** reduction with EASE-encoded arrays vs full regeneration on synthetic data tested on GPT-4o-mini and Claude Sonnet — directional, not Claude-Opus-measured. Trade-off: agents handle patch generation imperfectly when arrays are involved.

These three fit the existing stack: strict tool use lives at the Messages API layer; `jq` is shell-level; JSON Patch is opt-in per future tool.

### Gaps

- **No widely-adopted MCP server for RFC 6902 patch application against a project file.** Query-leaning servers (mcp-jq, ciresnave) exist; "apply this patch document to that file" MCP shape does not appear in this search.
- **No JSON Pointer / jq filter on Anthropic's text-editor `view`.** The tool accepts `view_range` (line numbers) but not `--json-pointer /mcpServers/foo`. A view variant would close this gap inside first-party tooling.
- **No first-party Anthropic guidance on freehand vs strict-mode token economics.** Strict mode injects an additional system prompt and invalidates prompt caches when `output_config.format` changes — but Anthropic doesn't quantify the trade-off vs retry tokens saved.
- **Patch correctness on arrays remains LLM-hard** even with EASE; the technique trades intuitive array indices for stable two-character keys plus a `display_order` field, a non-standard schema convention.
- **MergePatch's `null`-means-delete is a footgun** for any schema where `null` is a valid value.

## Random access and queryability

Weak without a separate index. Looking up a specific key requires parsing the whole document. `jq` enables ad-hoc query but does not make the file itself indexed.

## Scale ceiling

Single-file JSON degrades past the megabyte scale because parsers load the whole document into memory. Streaming JSON parsers exist but are uncommon. For large datasets, JSONL or SQLite is the canonical escape.

## Failure mode

Loud and immediate. Malformed JSON fails at the parser with a line/column error. Strength for configuration — invalid state cannot be silently consumed.

## Claude-specific notes

- Claude's tool-use API uses JSON throughout. Tool definitions carry JSON Schema; tool calls return `tool_use` blocks with a JSON `input` object.
- `strict: true` on a tool definition constrains Claude's output to schema-conformant JSON — verified GA on Claude 4.5/4.6/4.7. See [Anthropic — strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use).
- Anthropic's Messages API request/response format is JSON.
- The 2025 SQLi vulnerability in Anthropic's archived Postgres MCP server ([Datadog Security Labs](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/)) was JSON adjacent — JSON tool inputs were composed unsafely into SQL strings. Not an indictment of JSON; relevant when JSON values flow into other contexts.

## Pitfalls and anomalies

- No comments — workarounds (`"_comment": "..."` keys, JSONC) are non-standard
- No trailing commas
- No native date type — dates serialize as strings with no enforced format
- Numeric precision varies between parsers (JS treats all numbers as float64; Python and Go parse integers losslessly)
- Duplicate keys are technically allowed but parsers vary in which value wins

## Open questions

- What's Claude's actual error rate on freehand JSON generation versus `strict: true`-constrained generation, on real workloads? Not published by Anthropic.
- For JSON configs read into Claude's context, are there token-cost differences between minified and pretty-printed forms that affect cache hit rates?
- Does the JSON Whisperer 31% output-token reduction generalize beyond the synthetic film-production-scenes dataset to typical agent JSON workloads?
- Is there a path to a project-friendly "apply this RFC 6902 patch" MCP tool — or is `str_replace_based_edit_tool` sufficient at this project's scale?

## Sources

- [Anthropic — Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Anthropic — Strict tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use) — verified GA on 4.5/4.6/4.7
- [Anthropic — Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Anthropic — Text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) — `text_editor_20250728`
- [JSON Whisperer paper (arXiv 2510.04717)](https://arxiv.org/abs/2510.04717) — verified: 31% output-token reduction, GPT-4o-mini + Claude Sonnet, ~400 synthetic examples
- [RFC 6901 JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901)
- [RFC 6902 JSON Patch](https://datatracker.ietf.org/doc/html/rfc6902)
- [RFC 7396 JSON Merge Patch](https://datatracker.ietf.org/doc/html/rfc7396)
- [RFC 9535 JSONPath](https://www.rfc-editor.org/rfc/rfc9535.html)
- [jq](https://jqlang.org)
- [Datadog Security Labs — Postgres MCP SQLi case study](https://securitylabs.datadoghq.com/articles/mcp-vulnerability-case-study-SQL-injection-in-the-postgresql-mcp-server/) — Anthropic reference Postgres MCP affected; no CVE assigned
- [improvingagents.com — nested data format benchmark](https://www.improvingagents.com/blog/best-nested-data-format/) — markdown 34-38% cheaper than JSON (non-Claude models)
