# Project data-format standardization

Implement the verified project-actionable recommendations from data-formats research — concrete items that codify how this project handles JSON, YAML, CSV, and SQL across MCP tools, plugin code, and agent allowlists. Detail and rationale in `logs/research/data-formats/consolidated.md` Verified Project Recommendations section.

## Items

- **Adopt `strict: true` on existing MCP tool definitions** (transcripts, navigator). Verified GA on Claude Opus/Sonnet/Haiku 4.5/4.6/4.7. Schema constraints apply (no recursive types, no external `$ref`, etc.).
- **Codify `ruamel.yaml` round-trip mode as project Python YAML default**; forbid `PyYAML.dump` in mutating code paths via convention or code-review rule. Verified: PyYAML default sorts keys and discards comments; ruamel.yaml round-trip preserves both.
- **Allowlist `mdq`, `jq`, `yq` as bash CLIs for read-path slicing**. All three verified to exist; single-binary installs.
- **Three `sql_query` / `schema_describe` enhancements**:
    - `format=compact` (two-array `{columns, rows}` result shape)
    - `format=summary` (shape-of-result-set queries — types, counts, sample values)
    - M-Schema-style tuple-per-column on `schema_describe` when schema grows
- **Codify "CSV is wire format, not working format" as a project rule**. When CSV appears as ingest, load to SQLite (`sqlite-utils insert --csv`) or DuckDB (`read_csv_auto`) before answering structural questions. Generate CSV from structured source only at the export boundary.

## Pointers

- Full rationale, sources, and trade-offs: `logs/research/data-formats/consolidated.md`
- Per-format detail: `logs/research/data-formats/samples/<format>.md`
