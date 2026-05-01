# Prior art — embedded-editor-for-claude-code

Browser-served editor with embedded panels (Excalidraw, tldraw, Markdown w/ wikilinks, DuckDB tables, PDF/CSV viewers); MCP tools for read/write panel state; SSE-synced bidirectional state; Claude Code-specific via slash commands. **Closest browser-served + MCP-native + Claude-Code-specific match.**

## Identity

- **URL:** [github.com/1vav/embedded-editor-for-claude-code](https://github.com/1vav/embedded-editor-for-claude-code)
- **License:** MIT (research-stated; verify on direct read)
- **Stack:** Local Node HTTP server + browser viewer + MCP stdio (for Claude Code integration)
- **Status:** v1.2.1 dated April 29 2026, 9 releases, actively maintained — verified via research
- **Adoption signal:** 1 GitHub star at time of research — small project, key-person risk

## Fit to our goal

**~70% — leading fork candidate** for an MCP-native, browser-served, Claude-Code-specific starting point.

**Matches:**
- Browser-served on a port (✓ matches goal)
- Multi-panel layout with mixed content types
- MCP tools per panel (introspection + mutation, e.g. `read_diagram`, `write_diagram`, `query_table`, `read_note`, `append_elements`)
- Claude Code-specific via slash commands (`/editor-start`, `/editor-stop`)
- Panel content as files (matches our file-primary disposition)
- Live-synced via SSE between server and viewer

**Differs:**
- SSE + file-watcher syncing rather than CRDT — lower ceiling for true bidirectional concurrent editing
- No terminal panel yet
- No layout persistence schema verified
- Small project, single-maintainer risk
- AGPL-vs-MIT license needs explicit verification

## What to take, what to skip

**Take:** the MCP-tools-per-panel-type pattern; SSE-as-sync-fallback approach; slash-command lifecycle (`/editor-start` / `/editor-stop`); per-panel-type read/write tool surface design.

**Replace:** SSE + file-watcher (replace with Yjs CRDT for true bidirectional live state); add a terminal panel; add layout-persistence; add CRDT-peer agent pattern per the Electric reference.

## Open questions for deep-dive

- Layout-persistence schema (was the open question from the existing-implementations research wave)
- Panel-type extensibility model — how easy to add new panel types?
- License confirmation (MIT? AGPL? other?)
- Auth / permission model for the local server
- File-watcher robustness — race conditions, large-file behavior
- How the MCP stdio process and the HTTP server share state
- Whether the project has roadmap intent to add terminal panel / Yjs / etc.

## Sources

- [github.com/1vav/embedded-editor-for-claude-code](https://github.com/1vav/embedded-editor-for-claude-code) — verified active v1.2.1 April 2026
