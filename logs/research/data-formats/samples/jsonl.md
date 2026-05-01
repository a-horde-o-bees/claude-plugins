# JSONL / NDJSON

Line-delimited JSON — one valid JSON value per line, separated by `\n`. Designed for streaming, append-only logs, and large record sets where the whole-file JSON pattern breaks down.

## Metadata

- **File extensions:** `.jsonl`, `.ndjson`, `.json` (ambiguous when overlapping with single-document JSON)
- **MIME type:** `application/jsonl`, `application/x-ndjson` (both common; no formal RFC)
- **Spec:** jsonlines.org (de facto), ndjson.org. The two are functionally equivalent
- **Primary use cases:** Append-only logs (Claude Code transcripts are JSONL), streaming API responses, large record sets ingested by analytics pipelines, event/telemetry storage

## Token efficiency

Per-record overhead matches JSON, but the array-wrapping tax (outer `[...]` plus inter-record commas) is gone. For collections of records, JSONL is unambiguously cheaper than wrapping the records in a single JSON array.

## LLM parse reliability

Each line is independent JSON, parsed identically to single-document JSON. Reliability inherits from JSON.

## LLM generation reliability

Strong. Each line is its own JSON value, so the model never has to track state across line boundaries. A malformed line doesn't break parsing of others.

## Modification ergonomics

Excellent for the dominant operations: appending a new record is one line at end-of-file; replacing a record is a single-line edit; deleting a record is line removal. No re-emit of containing structure required.

## Diff and human readability

Strong — one record per line gives line-grain diffs. Long records can wrap awkwardly in editors, which is the main readability cost.

## Tooling and ecosystem

`jq` operates on JSONL natively (each line a separate input). Streaming parsers in every language. Pandas reads JSONL with `pd.read_json(lines=True)`. Log analytics tools (Vector, Fluentd, Loki) treat JSONL as a primary substrate.

## Random access and queryability

Stronger than JSON: line-seek and `grep` work because each line is self-contained. Not as strong as SQLite — there's no index, so cell lookup over millions of records still requires a scan, but the scan is line-incremental rather than full-document.

## Scale ceiling

Scales to millions of rows because parsing is line-incremental. Bound only by disk space and the consumer's processing speed. The Claude Code transcript ingest in this project routinely handles JSONL files in the tens-of-thousands-of-lines range.

## Failure mode

Loud at the line level, but isolated — one malformed line is one lost record, not one corrupted file. This is the single biggest operational advantage for telemetry and log workloads.

## Claude-specific notes

- Claude Code session transcripts are stored as JSONL under `~/.claude/projects/<project-slug>/` — one event per line. The `/ocd:transcripts` skill in this project ingests them into SQLite for query
- No Anthropic guidance specifically prescribes JSONL for any storage pattern
- The format works well with prompt caching when used as append-only context — appending lines preserves the prefix for cache hits

## Pitfalls and anomalies

- Tooling that expects `.json` may not recognize `.jsonl` — explicit extension matters
- Records spanning multiple lines (newlines inside JSON string values) break the format unless escaped — `\n` inside a string literal is correct; raw newlines are not
- No file-level metadata (header, footer, document-level keys) — every record carries its own context
- File is "valid" even when half-written (last line may be partial); robust readers tolerate this

## Open questions

- What's the practical performance ceiling for JSONL ingest into SQLite on the hardware profile the transcripts skill targets?
- Does Anthropic publish guidance on streaming context formats for very long conversations?
- Are there established conventions for embedding schema or version information in a JSONL stream's first line vs in a sidecar file?
