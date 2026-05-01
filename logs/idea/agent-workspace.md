# Agent workspace — tiled browser interface with shared state

Locally-served workspace platform that extends Claude Code's CLI chat with dynamically arrangeable panels carrying other interaction modes (canvases, editors, viewers, terminals), where the agent and human share live state across all panels — so the agent can see and act on what the human is currently working on, without giving up the existing CLI workflow.

## Purpose

> A locally-served browser interface that extends agent-human chat communication with a fully configurable layout of panels — an optional terminal panel mirroring the live CLI, bidirectional collaboration surfaces (canvases, editors, structured documents both modify), and read-only viewers (PDFs, rendered output, images) — orchestrated by the Claude Code session: the agent opens panels at conversation-driven invocations, the user controls the layout, and the workspace shares the session's working directory and lifetime. Panel content persists as files; users can save layouts for reopening in future sessions.

## Why this matters

Current Claude Code workflow is terminal-only — no inline visualization. The user has been forced to switch between Claude Code (terminal, WSL multi-repo) and Claude Desktop / claude.ai (artifacts, mermaid, interactive HTML) when visualization is needed. This loses the WSL multi-repo benefit and severs the agent's awareness of what the user is looking at.

The integrated solution: human and agent share live workspace state via a panel-based interface, so the agent can see what the user has selected, read panel state (canvas contents, document slices, table cells), and write to panels (place a diagram, update a table, render a PDF for view) — all without leaving the Claude Code CLI workflow.

## Recommended architecture

Four-layer composition, all backed by research at `logs/research/agent-workspace/`:

1. **Sync mechanism**: Yjs + Hocuspocus (self-hosted Node) + SQLite + server-side Yjs peer per the ElectricSQL pattern, MCP-exposed. Layout state as one Y.Map.
2. **Data model**: file-primary + panel-type-as-interpreter + per-type MCP agent surface (Apache Zeppelin's interpreter dispatch pattern at the workspace level).
3. **Information architecture**: SQLite reference table mirroring the navigator MCP pattern; agent surface like LSP `textDocument/references` + Unison `ucm` + Roam Datalog. Single canonical source + live propagation.
4. **Interface**: browser, served from WSL on a port. Tauri as upgrade path.

## Genuinely novel piece

**Panel-as-queryable-citizen of the reference graph** — `panels_showing(id)`. Stable IDs, backlinks, transclusion, and renames are all heavily prior-art-covered (Roam, Logseq, Notion, Anytype, Unison, Obsidian). The layout as a graph node — "what panels are showing this content right now," "if I edit this content, which panels need updating" — was not surfaced in any tool examined. That's the contribution; everything else is borrowable.

## Pointers

**Research:**

- Synthesis: `logs/research/agent-workspace/consolidated.md`
- Layer-by-layer landscape:
    - `logs/research/agent-workspace/sync-mechanism-layer.md`
    - `logs/research/agent-workspace/data-model-layer.md`
    - `logs/research/agent-workspace/information-architecture-layer.md`
    - `logs/research/agent-workspace/existing-implementations.md`
    - `logs/research/agent-workspace/interface-mechanisms.md`

**Prior-art per-project starter packs** at `logs/research/agent-workspace/samples/prior-art/*.md` — twelve projects, each with identity / fit / what-to-take / open questions, ready for deep-dive when revisited.

**Highest-fidelity prior art (study these first):**

- `samples/prior-art/opencove.md` — ~85% fit, single highest-fidelity match (spatial canvas + Claude Code + Codex + headless browser mode)
- `samples/prior-art/embedded-editor-for-claude-code.md` — closest browser-served + MCP-native + Claude-Code-specific match (leading fork candidate)
- `samples/prior-art/electric-sql-collaborative-ai-editor.md` — canonical sync architecture reference (working demo + open-source repo from April 2026)

## Recommended next steps

1. Hands-on trial of OpenCove (1-2 hours) — closest existing approximation
2. Hands-on trial of `embedded-editor-for-claude-code` (1-2 hours) — leading fork candidate
3. Run the ElectricSQL collaborative-ai-editor demo and read the source
4. Decide tile-vs-canvas (default tiles per user preference for primarily-2-panel left/right)
5. Build a /sandbox prototype: one terminal panel + one markdown panel + one diagram panel, MCP introspection, Yjs sync, layout persistence

## Aggregated pitfalls (from research)

- **Figma is not a CRDT** despite marketing — they use centralized OT-style with multiplayer broadcast. Don't model on Figma.
- **Google Docs has not migrated to CRDT** — still OT.
- **Jupyter RTC's content-triplication problem** — when CRDTs layer on top of existing stores (filesystem + memory + CRDT), state diverges. Pick one source of truth and project to others.
- **CRDT metadata bloat at scale** — Y.Doc grows monotonically with edit history; periodic snapshots and history pruning are operational requirements, not optional polish.
- **Orchestration-layer churn is real**: Crystal renamed to Nimbalyst, Roo Code reportedly shutting down May 2026, Goose moved orgs (Block → AAIF), Vibe Kanban (~25.7k stars!) sunsetting. Don't depend on small projects without due diligence.
- **Liveblocks AI Copilots is not Yjs-based** — chat + register-knowledge/register-tool React components, separate product from Liveblocks Yjs storage. Don't confuse.
- **LSP-style symbol-table-backed renames, not regex sweeps.** A 2026 multi-agent rename-refactoring paper and Kiro both argue LLMs alone can't reliably rename — they need a precise reference graph to call into.

## Open questions

- OpenCove's actual layout configurability (tile vs canvas)
- embedded-editor-for-claude-code's layout-persistence schema
- Claude-Code-as-CRDT-peer wiring — no verified implementation yet; the Electric pattern shows server-side Y.Doc + agent loop, but the agent loop in their demo is direct Anthropic API, not Claude Code itself
- MCP Apps + Yjs coexistence — both post-2025 protocols, no public precedent for using them together
- Layout-as-Y.Map vs layout-as-file — saved layouts imply file-based; treating layout as a Y.Map gives live-collab on layout itself but adds complexity
- Rename of file-primary content — who cascades references? Agent? File-watcher daemon? LSP-style server?
- BlockSuite's standalone-adoption signal beyond AFFiNE
- Marimo stable cell IDs (issue #3177) status
- AGPL implications of forking claudecodeui (if that becomes the chosen base)

## Lifecycle

Active investigation. Convert to a project, sandbox, or archive into a decision log when the path commits. Research artifacts at `logs/research/agent-workspace/` should remain as reference even after the path commits — they are evergreen prior-art mappings.
