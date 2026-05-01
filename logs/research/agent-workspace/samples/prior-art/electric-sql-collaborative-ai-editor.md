# Prior art — ElectricSQL collaborative-ai-editor

Reference implementation of "AI agent as Yjs CRDT peer" — server-side Y.Doc per agent, three streams over one HTTP protocol (Durable Streams), MCP-shaped tool surface. Working demo + open source. **Canonical sync-architecture precedent for our design.**

## Identity

- **URL:** [github.com/electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor) + [blog post](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs)
- **Author:** Sam Willis (April 8 2026)
- **License:** Likely Apache-2.0 (Electric's standard) — verify on read
- **Stack:** Yjs + ElectricSQL Durable Streams + TanStack AI chat + MCP tool surface
- **Status:** Reference demo + blog post; recent (~3 weeks at time of research)
- **Live demo:** [collaborative-ai-editor.examples.electric-sql.com](https://collaborative-ai-editor.examples.electric-sql.com)

## Fit to our goal

**~50% — reference implementation of one critical layer** (sync architecture), not full workspace. But the layer it references is the most central architectural choice for our design.

**Matches:**
- Agent-as-CRDT-peer (server-side Y.Doc per agent, joins same room as humans)
- Three streams over one HTTP protocol — clean separation of doc updates / awareness / chat
- MCP-shaped tool surface (`get_document_snapshot`, `search_text`, `place_cursor`, `insert_text`, `start_streaming_edit`)
- Streaming markdown parser converts Claude tokens into Y.Text in real time
- Relative-position anchors so the agent reasons about user-intended positions across concurrent edits

**Differs:**
- Single-document focus, not multi-panel workspace
- Demo-quality, not production
- Agent loop uses direct Anthropic API, not Claude Code as the agent surface
- No layout-state-as-Y.Map analog

## What to take, what to skip

**Take:** the entire sync architecture is the recommended path. Specifically:
- Server-side Y.Doc instance per agent
- Three Durable Streams over one HTTP protocol (doc updates, awareness, chat)
- The tool surface design — read → locate → edit pattern
- The streaming markdown parser pattern for converting Claude output into Y.Text
- Relative-position anchors for the agent's cursor

**Adapt:** scale from single-doc to multi-panel (each panel may need its own Y.Doc, or the workspace may be one Y.Doc with panel-keyed sub-types); replace direct Anthropic API agent loop with Claude-Code-via-MCP integration.

## Open questions for deep-dive

- How does `start_streaming_edit` behave under concurrent human edits?
- What's the durable-stream persistence story — how is history pruned?
- How would this scale to multi-document / multi-panel workspace? One Y.Doc per panel? One Y.Doc with sub-types?
- How would Claude-Code-as-agent-loop wiring look (instead of direct Anthropic API)?
- What does the awareness stream actually carry beyond cursor position?
- Performance: concurrent edits, large documents, history compaction?

## Sources

- [github.com/electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor)
- [Blog post — AI agents as CRDT peers with Yjs](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs) — verified April 8 2026, Sam Willis
- [Live demo](https://collaborative-ai-editor.examples.electric-sql.com)
