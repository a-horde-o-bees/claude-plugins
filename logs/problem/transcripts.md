# Transcripts skill — friction log

Accumulated friction observed while exercising the transcripts skill. One file per system rather than one file per problem — these items share an audit/refactor scope and benefit from being read together.

## Principle

The transcripts skill should let an ad-hoc consumer (agent or human writing SQL via `sql_query`, or reading via the curated tools) interact with the corpus without trial-and-error discovery of vocabulary, encoding, or behavior. `schema_describe` is the natural place to surface most of this; tool descriptions cover the rest.

---

## schema_describe omits live vocabulary

### Tool name vocabulary not enumerated

`tool_use_label` values (`Agent`, `Bash`, `Edit`, `Read`, `WebFetch`, etc.) are runtime-determined and not surfaced in `schema_describe`. A consumer searching for agent-spawning events first guessed `Task` (the visible Anthropic-API tool name) and got zero rows; actual tool name in the DB is `Agent` (the harness-side name). Discovery required `SELECT DISTINCT tool_use_label`.

**Fix shape:** include the active tool vocabulary (`SELECT DISTINCT tool_use_label FROM events WHERE tool_use_label IS NOT NULL`) in `schema_describe` output, or document the harness-vs-API tool naming convention explicitly in the semantics block.

### Event label vocabulary not enumerated

Labels are colon-namespaced (`tool_use:Agent`, `tool_use:Bash`, `assistant[text]`, `assistant[thinking]`, `attachment:command_permissions`, etc.) and `events.label` has 30+ distinct values. `schema_describe` shows the column type but not the value vocabulary. A consumer assumed `label = 'tool_use'` and got nothing.

**Fix shape:** include `SELECT DISTINCT label FROM events` enumeration in `schema_describe`, or document the label-naming pattern (`{event_type}` for non-tool events; `{event_type}:{tool_name}` for tool-use rows; `assistant[{block_kind}]` for assistant content blocks; `attachment:{kind}` for attachments) in the semantics block.

---

## Data-model asymmetries

### `text` is NULL for `tool_use:*` rows with structured input

The Agent tool's `prompt` parameter is a high-value input (it's the entire delegated workflow) but lives only in the original JSONL `input` dict — not extracted into `events.text`. Recovery during the 2026-05-01 prompt-recovery exercise required reading the JSONL by file/line pointers stored on the row. Same likely applies to Edit/Write tool inputs (which include file content) and any other tool whose primary input is the load-bearing content rather than a flag-style argument.

**Fix shape:** decide whether tool input parameters should be ingested into `events.text` for tools where the input IS the load-bearing content (Agent, Edit, Write). If yes, ingest. If no, document the omission explicitly in semantics so the consumer knows the JSONL-fallback path via `file`/`line` pointers.

### `tool_use_label` populated asymmetrically across tool_use and tool_result rows

For `tool_use:Agent` rows: `label = "tool_use:Agent"` and `tool_use_label IS NULL`.
For corresponding `tool_result` rows: `label = "tool_result"` and `tool_use_label = "Agent"`.

The asymmetry surprised the consumer — `tool_use_label` reads like the canonical place for the tool name, but it's only populated on result rows. The information is duplicated on tool_use rows (encoded in `label`) but split into two columns on result rows.

**Fix shape:** populate `tool_use_label` consistently on both tool_use and tool_result rows so a single column gives the tool name regardless of label, OR document the asymmetry explicitly in semantics so consumers know to check `label` for tool_use rows and `tool_use_label` for tool_result rows.

---

## MCP-tool behavior

### `exchanges_query` response-size cap truncates whole-session reads

A single 60-exchange session dumped through `mcp__plugin_ocd_transcripts__exchanges_query` with `show=["messages"]` produced ~280KB and exceeded the response-size cap. The agent fell back to Python `sqlite3` against the `chat_messages` view, which had no cap and was faster.

The MCP tool DOES support paging via `range_from`/`range_to`, but the natural use case (consumer wanting the chat content of a whole session) hits the cap and either truncates or dumps to a file. Direct sqlite3 has no such cap.

**Fix shape:** consider either (a) raising the cap for `exchanges_query` specifically (other MCP tools may not need such large responses), (b) auto-paging in the tool with explicit continuation tokens, or (c) documenting in the tool description that whole-session reads should use `sql_query` with the `chat_messages` view, NOT `exchanges_query`. The third is cheapest; the first or second is more user-friendly.

### `ocd-run transcripts` CLI reported as dormant in a spawned agent's context

During the 2026-05-01 refresh, a spawned agent reported the `ocd-run transcripts` CLI as "dormant" despite the parent session having just run `/ocd:setup init --all --force` successfully. Cause unverified — possibly:

- The spawned agent's cwd wasn't the project root, so the dormancy check evaluated a different `.claude/` state
- A state-tracking issue between init completion and CLI invocation in a separate process
- Path resolution differing between `/ocd:setup` and `ocd-run transcripts` invocation

**Fix shape:** investigate the dormancy check's cwd handling. Document the expected invocation path in the skill description if cwd matters. Direct sqlite3 path bypasses this entirely; the bug is in the CLI fallback path, not the data layer.

---

## Consumer-side stripping

### Skill-template injections inflate session text by 30-50%

Not strictly a transcripts-skill bug — these are part of the Claude Code transcript content. But every consumer reading sessions for analysis must strip them, and the transcripts skill is the natural place to either (a) document the regex for consumers, or (b) offer a flag/view that filters them.

The injection text starts with `Base directory for this skill:` and continues with the full skill markdown — repeated each time a skill is invoked.

**Fix shape:** add an optional `--no-skill-templates` flag to `exchanges_query` (and the equivalent CLI verb), or expose a `chat_messages_clean` view that filters. The regex is simple: drop messages whose text starts with `Base directory for this skill:`.

---

## Origin

All findings surfaced 2026-05-01 during the consolidated-profile refresh exercise (job-search project). The schema_describe items appeared during prompt recovery from a 2026-04-15 session; the MCP cap appeared during the smoke-test agent run; the dormancy report came from the smoke-test agent's fallback discovery; the skill-template observation came from the smoke-test agent's analysis of the chat_messages view content.

Workflow ultimately succeeded — direct sqlite3 against `chat_messages` is the reliable path. But each item above cost discovery time and would recur for the next ad-hoc consumer.

## Audit scope

- `schema_describe()` implementation in the transcripts MCP server
- `events` table label and tool_use_label vocabularies — enumerate live values to embed in semantics or as separate response fields
- Decide consistent population strategy for `tool_use_label` across tool_use and tool_result rows
- Decide ingestion strategy for tool input parameters (Agent.prompt, Edit/Write content) — populate `events.text` or document the JSONL-fallback path
- `exchanges_query` response-size cap — raise, page, or document the alternative
- `ocd-run transcripts` CLI dormancy detection — investigate why a freshly-init'd skill reads as dormant in a sibling process
- Consider exposing a skill-template-stripped view (`chat_messages_clean`) for analytical consumers
