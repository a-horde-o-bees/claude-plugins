# Agent-workspace architecture

Synthesized findings on architecting a locally-served, browser-accessed workspace that extends Claude Code chat with a fully configurable layout of panels — bidirectional collaboration surfaces and read-only viewers — orchestrated by the Claude Code session, with state shared between agent and human across panels. Five focused research waves at subject root (`sync-mechanism-layer.md`, `data-model-layer.md`, `information-architecture-layer.md`, `existing-implementations.md`, `interface-mechanisms.md`) cover sync mechanism, data model, information architecture, existing implementations, and interface mechanism; per-entity prior-art starter packs in `samples/prior-art/`. This doc is the cross-layer synthesis with explicit recommendations and the gap analysis.

## Goal recap

The workspace's purpose statement, settled in conversation:

> A locally-served browser interface that extends agent-human chat communication with a fully configurable layout of panels — an optional terminal panel mirroring the live CLI, bidirectional collaboration surfaces (canvases, editors, structured documents both modify), and read-only viewers (PDFs, rendered output, images) — orchestrated by the Claude Code session: the agent opens panels at conversation-driven invocations, the user controls the layout, and the workspace shares the session's working directory and lifetime. Panel content persists as files; users can save layouts for reopening in future sessions.

## Bottom line on "are we reinventing?"

**Almost every primitive exists; the integrated whole exists in two places that came within ~85% of our design in the last 6 months.** Two findings dominate:

1. **OpenCove** ([github.com/DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove), MIT, alpha but actively developed, v0.2.0 dated April 27 2026, 414 commits, 16 contributors) is explicit: "agents, terminals, tasks, notes on the same infinite 2D canvas," Electron + xyflow + xterm.js + node-pty, headless mode for browser access, "space archives" for layout persistence. Designed for Claude Code and Codex specifically, model-agnostic at the terminal layer. **The single highest-fidelity match found.**

2. **ElectricSQL's "AI agents as CRDT peers with Yjs"** ([electric.ax/blog/2026/04/08](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs), Sam Willis, April 8 2026) describes the sync architecture we'd want: server-side Yjs peer per agent, three streams (Yjs document, Yjs awareness, AI chat) over one HTTP protocol via Durable Streams, MCP-shaped tool surface (`get_document_snapshot`, `search_text`, `place_cursor`, `insert_text`, `start_streaming_edit`). Working demo at [collaborative-ai-editor.examples.electric-sql.com](https://collaborative-ai-editor.examples.electric-sql.com); source at [github.com/electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor).

The user mandate — "absolutely certain we're not inventing something that already exists" — is satisfied with high confidence: the design lives at the intersection of OpenCove's spatial-workspace-with-agent-as-peer and Electric's CRDT-peer sync architecture. We can fork or compose; we don't have to reinvent.

The single genuinely novel piece our design adds: **the panel itself as a queryable citizen of the reference graph.** Information-architecture research found stable IDs, backlinks, transclusion, and rename semantics all heavily prior-art-covered — but treating the rendering layout as a first-class graph node ("what panels are showing this content right now," "if I edit this content, which panels need updating") was not surfaced in any tool examined. That's the contribution; everything else is borrowable.

## The four-layer architecture, settled

### Layer 1 — Sync mechanism

**Recommended: Yjs + Hocuspocus (self-hosted Node) + SQLite extension + server-side Yjs peer per the Electric pattern, exposing tools to Claude Code via MCP.**

Per the sync-mechanism research wave:

- **Yjs over Automerge** for our case — Y.Text is the right primitive for prose editor panels; the editor-binding ecosystem (Tiptap, BlockNote, Lexical, ProseMirror, Monaco, CodeMirror, BlockSuite) is unmatched.
- **Hocuspocus over y-sweet** — multi-runtime, auth/persistence/Redis extensions, file-system-shaped persistence is closer to our "files are source of truth" disposition than y-sweet's S3 backend.
- **Layout state lives as one Y.Map** so the layout itself is collaborative (agent can move/resize/open panels by mutating the same data structure the human's UI binds to).
- **Sync engines (Zero, Triplit, ElectricSQL's row-based, PowerSync) are wrong shape** for prose-collab as primary — they target relational sync, not text-CRDT. Use Yjs as primary; consider sync engine for non-text panel state if it becomes the dominant surface.
- **OT (ShareDB) for greenfield: don't.**
- **Liveblocks: SaaS-only; AI Copilots isn't CRDT-peer-shaped (RegisterAiKnowledge / RegisterAiTool React-component pattern, separate product line from Liveblocks Yjs storage).**

**Pitfalls aggregated:**

- **Figma is not a CRDT** despite the marketing — they use centralized OT-style with multiplayer broadcast. Don't use Figma as the conceptual model.
- **Google Docs has not migrated to CRDT** — still OT.
- **Jupyter RTC's content-triplication problem** — when CRDTs are layered on top of an existing source of truth (filesystem + memory + CRDT), state diverges. Lesson: the CRDT must *be* the source of truth, or there must be a single canonical projection. Our design picks files as canonical, which means we must enforce one direction of authority (file-on-disk → Y.Doc, never the other way) or accept Y.Doc as primary with files as exports.
- **CRDT metadata bloat at scale** — a Y.Doc grows monotonically with edit history; periodic snapshots and history pruning are operational requirements, not optional polish.
- **Replicache → Zero migration** showed Rocicorp prunes aggressively (Reflect killed Nov 2024). Zero is alpha-to-early-beta as of April 2026, behind original timeline.
- **Triplit is AGPL-3.0** — a license consideration if we ever want to ship non-AGPL derivatives.

Detail: `sync-mechanism-layer.md`.

### Layer 2 — Data model

**Recommended: file-primary + panel-type-as-interpreter + per-type MCP agent surface.**

Per the data-model research wave, borrowing Apache Zeppelin's interpreter dispatch pattern at the workspace level. Each panel type is an interpreter that knows how to:

- Render its content type (markdown, table, canvas, diagram, terminal, viewer)
- Open the file as canonical source
- Bind to a Y.Doc for live state
- Expose its own MCP tool surface for agent introspection and mutation

The novel piece is the workspace-level dispatch — "open a panel for X" → file extension or content type chooses the interpreter → panel registers with the workspace + MCP layer.

**Borrowable models:**

- **Marimo** — reactive Python notebook with shipped agent-as-cell-participant via ACP. Closest cell-level precedent.
- **jupyter-ai** + **jupyter-collaboration** — Yjs-based collab + agent participant via built-in Jupyter MCP server, supports Claude. Mature, incubating.
- **BlockSuite** ([blocksuite.io](https://blocksuite.io/)) — most architecturally aligned editor framework for a Yjs-CRDT-native workspace; underlies AFFiNE. v0.22.4 July 2025 — slow cadence and unclear standalone adoption beyond AFFiNE flagged as a risk. Watch but don't bet on as-yet.
- **Logseq mid-pivot to SQLite-backed DB version** — the pivot itself is a case study (in-memory rebuilds have a real ceiling); evaluate before any "build on Logseq" choice.

**Open questions flagged:**

- Marimo stable cell IDs (issue #3177 not yet shipped)
- ACP specification maturity
- BlockSuite standalone-adoption signal beyond AFFiNE

Detail: `data-model-layer.md`.

### Layer 3 — Information architecture

**Recommended: SQLite + thin schema mirroring the project's navigator MCP pattern; agent surface mirroring LSP `textDocument/references` + Unison `ucm` + Roam Datalog.**

Per the information-architecture research wave: nearly every primitive we'd want is already invented somewhere. Stable IDs (Roam, Logseq, Notion, Anytype, Unison), inverse-attribute backlink queries (DataScript `:block/_refs`, equivalent SQL indexes), live transclusion with single-canonical-source propagation (Obsidian embed, Notion synced block), metadata-only renames (Unison's content-hash extreme; Roam/Logseq's UUID architecture).

**Single canonical source + live propagation** is the validated pattern. When content is referenced from multiple panels, edits in any propagate; the panel renders the canonical content, doesn't own a copy. This matches Obsidian/Notion at scale.

**Don't reach for RDF or DataScript** — surveyed implementations that did (Logseq's older approach) eventually pivoted away. SQLite + indexed reference table is the boring-and-correct choice.

**LSP precedent for renames:** Kiro and a 2026 multi-agent rename-refactoring paper both argue LLMs alone can't reliably rename — they need a precise reference graph to call into. Direct mandate that "rename across all references" must be backed by a symbol-table-equivalent, not regex sweeps.

**The genuinely novel piece is `panels_showing(id)`:** the panel itself as a queryable citizen of the reference graph. Surveyed tools model the document graph but treat layout/rendering as opaque editor state. Adding the panel layer to the reference graph is our contribution.

Detail: `information-architecture-layer.md`.

### Layer 4 — Interface mechanism

**Recommended: browser (local server + browser client) as primary; Tauri as upgrade path if OS integration ever matters.**

Per the interface-mechanism research wave: browser is the only mechanism clearing every workspace requirement (canvas, PDF, viewer, terminal embed, freeform tiling, cross-platform reach to WSL) without caveats. Tauri's web-stack code is reusable, so the upgrade path is non-destructive.

**Disqualified mechanisms** for the canvas/PDF/viewer requirement:

- All TUI frameworks (Textual, Bubble Tea, ratatui, Ink) — content ceiling is text grids
- All terminal multiplexers (tmux, Zellij, Wave, Ghostty, WezTerm) — same ceiling
- VS Code extension — webviews don't allow freeform tiling; VS Code controls tile arrangement
- Zed extensions — cannot create custom UI panels today (docs say roadmap)

**Contingent path:** if our panel set later narrows to text-shaped surfaces only (no canvas / no PDF), the recommendation flips entirely to **tmux + MCP** with multiple production-tier precedents (NTM, tmux-agents, Tmux Automation MCP). Our stated requirements rule this out, but worth knowing the alternative exists.

**Notable corrections from prior verbal claims:**

- **Wave Terminal's "AI-native" claim is unverified** — docs page 404s; the homepage uses "AI-native" without describing integration mechanics.
- **VS Code webviews appear "as distinct editors"** — VS Code, not the extension, controls tile arrangement.
- **Tauri 2 multi-webview is real but unstable** (`add_child(webview_builder, position, size)` API; example exists at `tauri/examples/multiwebview`).

Detail: `interface-mechanisms.md`.

## Closest existing implementations

Three projects deserve direct study before committing to any architecture:

### OpenCove ([DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove))

**~85% fit, the highest-fidelity match found.** MIT, alpha, actively developed. Spatial 2D canvas (xyflow) hosting agent terminals + tasks + notes; explicit Claude Code + Codex integration; xterm.js + node-pty for terminal panels; "space archives" for layout persistence; headless mode for browser access. Electron-based but the core panel logic is web-stack and would lift to a pure browser deployment.

**Differs from our design:**

- Infinite 2D canvas vs tiled layout — design vocabulary difference; less of an issue if our user-controlled layout supports either tiling or canvas-positioning
- No documented CRDT-peer agent pattern — the agent runs in terminals, not as a Yjs peer with shared cursor + edit operations
- No surfaced panels-as-queryable-graph — the spatial layout is stored but not surfaced as introspectable state
- Alpha quality means risk; v0.2.0 with active churn

**Take:** worth a hands-on trial as the closest existing approximation. If the spatial-canvas vocabulary aligns with the user's model, fork direction is plausible. Otherwise, study the terminal-as-panel + space-archive patterns and borrow them.

### embedded-editor-for-claude-code ([1vav/embedded-editor-for-claude-code](https://github.com/1vav/embedded-editor-for-claude-code))

**Closest browser-served + MCP-native + Claude-Code-specific match.** v1.2.1 dated April 29 2026, 9 releases, actively maintained, MIT (verified). Per-panel MCP tools for introspection and mutation (read_diagram, write_diagram, query_table, read_note, append_elements). SSE-synced bidirectional state. Slash commands `/editor-start` and `/editor-stop`.

**Differs from our design:**

- Panel set is Excalidraw + tldraw + Markdown + DuckDB tables + PDF/CSV viewers — no terminal panel yet, no generic editor panel
- SSE + file-watcher syncing rather than CRDT — the architectural ceiling is lower for true bidirectional concurrent editing
- 1 GitHub star — small project, key-person risk

**Take:** the leading candidate to fork or compose around. Add CRDT-peer pattern (Yjs + Hocuspocus) for live state; add terminal panel; add layout persistence; ship.

### ElectricSQL's collaborative-ai-editor ([electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor))

**Reference implementation of the agent-as-CRDT-peer sync architecture.** Working demo at [collaborative-ai-editor.examples.electric-sql.com](https://collaborative-ai-editor.examples.electric-sql.com). Per the April 8 2026 blog post: server-side Y.Doc per agent + three streams over one HTTP protocol + MCP-shaped tool surface for read/locate/edit. Streaming markdown parser converts Claude tokens into Y.Text in real time. Relative-position anchors so the agent reasons about user-intended positions across concurrent edits.

**Take:** clone, run the demo, study the code. This is the canonical sync-architecture precedent regardless of which workspace-shell choice we make. The tool surface design (`get_document_snapshot`, `search_text`, `place_cursor`, `insert_text`, `start_streaming_edit`) is a strong default to mirror.

## Aggregated pitfalls across layers

- **Layer your CRDTs and your filesystem carefully.** Jupyter RTC's content-triplication problem comes from layering CRDT on top of two pre-existing stores. Pick one source of truth and project to others, or accept Y.Doc as primary with files as exports.
- **Beware closed cloud "AI agent" products that look like our design.** Liveblocks AI Copilots, Notion AI, Coda AI — all use chat + register-knowledge/register-tool patterns, not CRDT-peer + shared-state. Different mental model; don't confuse marketing terms.
- **Watch the orchestration-layer churn.** Crystal renamed to Nimbalyst, Roo Code reportedly shutting down May 2026, Goose moved from Block to AAIF, Vibe Kanban (~25.7k stars!) sunsetting. Tooling in this space turns over fast — fork projects of meaningful size, don't depend on small projects without due diligence.
- **Rename and reference cascades are LLM-hard.** LSP-backed rename or symbol-table-backed rename — never freehand model rename. The 2026 multi-agent rename paper is the citation; Kiro's IDE design echoes this.
- **CRDT history grows monotonically.** Plan snapshot/prune as Day 1.
- **Sync engine alpha churn.** Zero is alpha-to-early-beta in April 2026; Triplit is AGPL-3.0; PowerSync is paid; ElectricSQL pivoted entirely in July 2024. If we use a sync engine for any panel, expect to migrate or get pinned to a license.

## Recommended path forward

Concrete, ordered.

**1. Hands-on trial of OpenCove (1-2 hours).** Run the headless server, open in browser, point Claude Code at it. The closest existing approximation — confirm or rule out before reinventing.

**2. Hands-on trial of embedded-editor-for-claude-code (1-2 hours).** Same drill. Different design vocabulary (tiles vs canvas), different sync mechanism (SSE vs CRDT), simpler codebase. The leading fork candidate.

**3. Run the ElectricSQL collaborative-ai-editor demo and read the source.** This is the canonical sync architecture; it informs whichever shell we pick.

**4. Decide tile-vs-canvas.** OpenCove gives the canvas vocabulary; embedded-editor gives tiles. The user said "primarily 2-panel, left and right" — that's tiles. Default to tile, add canvas later only if needed.

**5. If we build (or fork from embedded-editor):**
- **Sync:** Yjs + Hocuspocus self-hosted; layout as Y.Map; per-panel Y.Doc.
- **Data model:** file-primary; panel types as interpreters; MCP tool surface per type.
- **Information architecture:** SQLite reference table mirroring navigator MCP's pattern; agent tools mirror LSP `textDocument/references`. Add `panels_showing(id)` as the contribution.
- **Interface:** browser, served from WSL on a port. Reach via Windows browser as the user's normal pattern.
- **Persistence:** files for content (automatic, source-of-truth); Y.Map snapshot for layout (user-saved, opt-in).
- **Lifecycle:** session-bound; agent orchestrates panel opening; user controls layout; workspace inherits session cwd.

**6. Build a /sandbox-shaped prototype before committing.** A worktree-isolated trial of the simplest end-to-end loop: one terminal panel + one markdown panel + one diagram panel, agent introspection via MCP, Yjs sync, layout persistence. Validate the architecture in the small before scaling to all panel types.

## Open questions that survive the research

- **OpenCove's actual layout configurability** — verified it has space archives but didn't verify the configurability matches the user's "primarily 2-panel left/right" preference vs locked to canvas-spatial.
- **embedded-editor's layout-persistence schema** — flagged for follow-up by Agent 4; haven't checked.
- **Claude-Code-as-CRDT-peer wiring** — no verified implementation exists; the Electric pattern shows server-side Y.Doc + agent loop, but the agent loop in their demo is direct Anthropic API, not Claude Code itself. The integration gap is small but real.
- **MCP Apps + Yjs coexistence** — both are post-2025 protocols, no public precedent for using them together. We'd be a first.
- **Layout-as-Y.Map vs layout-as-file** — the user said "users can save layouts" implying file-based persistence; treating layout as a Y.Map gives us live-collab on layout itself but adds complexity. Worth deciding when prototyping.
- **Rename of file-primary content** — if files are canonical and reference-tracking is in SQLite, who is responsible for cascading renames? The agent? A file-watcher daemon? An LSP-style server?

## Sources

- [Anthropic — MCP overview](https://platform.claude.com/docs/en/agents-and-tools/mcp/overview)
- [MCP Apps blog (Jan 2026)](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)
- [Yjs](https://github.com/yjs/yjs) — verified MIT, v14.0.0-rc.7 March 2026
- [Automerge](https://github.com/automerge/automerge) — verified MIT, v3.2.6 April 2026
- [y-sweet](https://github.com/jamsocket/y-sweet)
- [Hocuspocus](https://tiptap.dev/docs/hocuspocus/introduction)
- [ElectricSQL — AI agents as CRDT peers with Yjs (April 8 2026)](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs) — verified, working demo + source repo
- [electric-sql/collaborative-ai-editor](https://github.com/electric-sql/collaborative-ai-editor)
- [DeadWaveWave/opencove](https://github.com/DeadWaveWave/opencove) — verified MIT, alpha, v0.2.0 April 27 2026
- [1vav/embedded-editor-for-claude-code](https://github.com/1vav/embedded-editor-for-claude-code) — verified active, v1.2.1 April 29 2026
- [yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw)
- [Marimo](https://marimo.io/)
- [jupyter-ai](https://github.com/jupyterlab/jupyter-ai) — verified 4.2k stars, v3.0.0
- [jupyter-collaboration](https://github.com/jupyterlab/jupyter-collaboration) — verified v4.3.0 March 2026
- [BlockSuite](https://blocksuite.io/) — v0.22.4 July 2025
- [Tauri](https://tauri.app/)
- Per-layer detail at subject root in `sync-mechanism-layer.md`, `data-model-layer.md`, `information-architecture-layer.md`, `existing-implementations.md`, `interface-mechanisms.md`
