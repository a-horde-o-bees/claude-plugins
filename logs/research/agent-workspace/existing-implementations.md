# Existing implementations of the agent-workspace model

Survey of projects that ship some or all of a configurable, agent-orchestrated workspace — locally-served browser interface, configurable panels, agent-driven panel openings, shared session/working directory, layout persistence — so the new design borrows everything available before inventing anything new. Scope intentionally narrow on the workspace model; interface-mechanism alternatives (native, CLI-extension, etc.) are a sibling research thread. All version, star, and date claims sourced from GitHub READMEs / project docs / vendor blogs as of April 2026; treat ecosystem-level rankings as "from training data plus search results, may be stale."

## Closest matches

These ship 70%+ of the model: configurable panels in a browser-served (or web-tech) shell, agent-as-active-participant with bidirectional state, shared filesystem, layout persistence.

### OpenCove — `DeadWaveWave/opencove`

Highest-fidelity match found. Spatial development workspace placing agents, terminals, tasks, and notes on a single infinite 2D canvas. Electron + React + TypeScript via electron-vite; canvas engine `@xyflow/react`; terminal panels via xterm.js + node-pty. Layouts persist across restarts via "space archives" — snapshot/recover prior workspace states. Headless worker mode hosts a browser-accessible Web UI (LAN-capable, password-protected). MIT, ~1.2k stars, v0.2.0 April 27 2026, alpha but active.

- **Panels** — agent sessions (Claude Code, Codex), terminal, task planning nodes, notes, image paste; global search across canvas + terminal output.
- **Agent integration** — Agent-as-shared-state-peer; agents execute in terminal panels with "side effects stay visible." Mutual-reading depth needs source inspection — README emphasises co-presence.
- **Closeness** — ~85%. Canvas-only layout (more spatial than tiled), but every other property — agent panels, shared state, terminal mirroring, persistence, browser delivery — is here.
- **Take** — space archives as persistence primitive; `@xyflow/react` for spatial layout (or `react-resizable-panels` if tiled); xterm.js + node-pty; the "side effects stay visible" framing.
- **Missing** — Bidirectional collaboration surfaces (peer-edited canvases / structured docs); PDF / read-only viewer panels not advertised; no explicit MCP-tool surface for agent-driven panel opening.
- **Pitfall** — Spatial canvas as default UI fatigues users at scale (Flowith / tldraw critique). A configurable layout that can be tiled *or* canvas hedges this.

### Embedded Editor for Claude Code — `1vav/embedded-editor-for-claude-code`

Already named; updated. Browser-served visual workspace mirroring a Claude Code session. MCP server exposes tools to create/modify diagrams, tables, notes; SSE drives bidirectional sync — Claude's edits appear in browser, browser edits flow back. Inline PNG previews keep Claude in-budget; user sees full fidelity. MIT, v1.2.1 April 29 2026, 9 releases, actively maintained.

- **Panels** — Excalidraw, tldraw, Markdown with wikilinks, DuckDB analytical tables with SQL pane, PDF viewer, CSV viewer.
- **Agent integration** — Agent-as-shared-state-peer. Per-editor type-specific MCP tools — not a generic "edit canvas," but `add_shape`, `add_row`, `set_text`.
- **Closeness** — ~80%. Best evidence the MCP + SSE pattern works for the bidirectional case.
- **Take** — MCP-tools-for-panel-creation contract; SSE for live edit propagation; per-editor typed tools; "inline PNG for the model, full editor for the user" split.
- **Missing** — Configurable layout (fixed editor type per file); terminal panel; PDF as a viewer for arbitrary docs (only embedded-diagram previews).
- **Lesson** — Sibling project to the design. Likely the cleanest reference implementation of bidirectional-MCP for non-text artefacts.

### Wave Terminal — `wavetermdev/waveterm`

Terminal-first, not browser-first, but the layout primitive is exactly what the design needs. Electron-based; every surface — shell, file preview, web browser, AI chat, code editor, custom widgets — is a uniform tile-able "block." ViewModel / ViewComponent / BlockFrame separation; Jotai atoms for state; Wave Object Store for persistence. `wsh` is the inter-block CLI — agents and users use the same surface to manipulate any block from any other. Apache-2.0, ~20k stars, v0.14.5 April 16 2026. Mature and active.

- **Panels** — Terminal, file preview, web browser, AI chat, code editor, sysinfo, custom widgets via `widgets.json`.
- **Agent integration** — Chat-with-tool-use; "Wave Agent Mode" on the roadmap (#2168) but not GA. Wave AI reads terminal output, widget state, files; inter-block via `wsh`.
- **Closeness** — ~70% on layout, ~50% on agent integration.
- **Take** — Block system as a layout primitive to mirror in browser; `wsh` as a single command surface used identically by user and agent; `widgets.json` as a precedent for user-extensible panel types.
- **Missing** — Browser delivery; agent-driven panel opening as a first-class verb; structured-doc collaboration surfaces.
- **Lesson** — Wave's AI is a side-pinned chat panel, not a peer block. Even teams with the right layout primitive struggle to make agent a peer; chat-on-the-side is the path of least resistance.

### Goose — `block/goose` (now AAIF)

Already named. Native desktop app (Tauri/Rust); extensions = MCP servers. Recently adopted MCP Apps for embedded UI rendering — extensions return interactive forms, visualisations, wizards that render in the right-side "sidecar." Apache-2.0, AAIF-hosted, active.

- **Panels** — Chat primary; sidecar renders MCP App UIs on agent demand.
- **Agent integration** — Chat + MCP-Apps render. Agent doesn't manage layout — it returns artifacts the harness renders into the sidecar slot.
- **Closeness** — ~55%. Single sidecar slot, not configurable multi-panel.
- **Take** — MCP Apps as the protocol for "agent emits a UI, harness renders it" — directly applicable.
- **Missing** — Configurable layout; concurrent panels of different types; user-driven panel creation alongside agent-driven.
- **Lesson** — Block → AAIF governance move is a future-direction signal, not an adoption blocker.

## Partial matches

Projects that ship one or more pieces of the model. None is an end-to-end fit; each carries a transferable lesson.

### Notebook + AI category

- **Jupyter AI + Jupyter Collaboration + jupyter-ai-agents (Datalayer)** — Cell-as-panel; agent-as-cell-participant via ACP+RTC. Yjs/CRDT-backed real-time collaboration. ACP means Claude Code, Codex, Goose, Kiro, OpenCode all attach through one protocol. **Take** — ACP integration; CRDT pattern for humans and agents editing concurrently. **Skip** — Notebook fixes layout to a linear cell sequence.
- **Marimo + marimo-agents** — Three permission tiers (Manual / Ask / Agent). Watch mode propagates agent-driven `.py` file changes to the browser in real time. **Take** — File-on-disk-as-source-of-truth + watch-mode is a clean SSE alternative; permission tiers are the right gating discipline. **Skip** — Notebook constraint.
- **Hex / Deepnote / Noteable** — Hosted notebooks with embedded AI agents. Hex's collaborative + agent loop is closest. **Take** — Multiplayer-cell pattern. **Skip** — Hosted only.

### Agent IDE category

- **Zed + Agent Panel + ACP** — Multiplayer-from-day-one editor; native + ACP agents. Threads / agent / project / git as docked surfaces. Per-call permission grants; hunk-level accept/reject. Parallel agents. **Take** — Per-call permission gating; change-review-as-first-class-UI; ACP. **Skip** — Native, not browser; canvas/structured-doc panels absent.
- **Cursor 3 + Canvases (3.1)** — Tiled agents window for parallel sessions; canvases as durable artefacts in side panels — agents emit dashboards, diffs, to-dos, charts via React-rendered components, persisted alongside terminal/browser/SCM. **Take** — Canvases-as-durable-artefacts (not transient chat output); first-party React component library as a typed render contract. **Skip** — Closed-source.
- **Replit Agent / Agent 4** — Server-rendered IDE; workspace as a tree of nodes (built-in tabs/splits + plugin instances). All layout state owned by the layout itself; plugins dispatch built-in actions. Infinite Canvas in Agent 4. **Take** — The layout-tree-of-plugin-instances model: any plugin dispatches layout actions without owning layout state. **Skip** — Cloud-only; closed.
- **Windsurf + Cascade** — Persistent ambient observation of edits, commands, clipboard, terminal as agent context. Spaces gate which projects feed Cascade. **Take** — Ambient-observation-with-explicit-consent pattern. **Skip** — Closed.
- **Intent (Augment, macOS, Feb 2026)** — Coordinator + Specialist + Verifier persona model; living spec auto-updated as agents work; per-workspace worktree; built-in Chrome browser preview; BYOA. **Take** — Living-spec-as-a-panel that agents and human edit collaboratively. **Skip** — Closed; macOS-only.
- **Google Antigravity** — Browser-first Agent Manager (mission control) + Editor view. Artifacts (plans, results, diffs, screenshots, browser recordings) as inspectable typed deliverables. **Take** — Artefact-as-output pattern; browser-recording artefact as evidence is novel. **Skip** — Closed; Google Cloud / Gemini-bound.
- **GitHub Copilot Workspace** — Artifact-oriented (spec → plan → diff). **Take** — Spec/plan/diff as inspectable, editable artefacts before code lands. **Skip** — Closed.
- **GitHub Next "Ace"** — Multiplayer chat + microVMs + shared agent + integrated terminal/preview/edit. Sessions = sandboxed microVMs on their own branches; teammates join instantly. **Take** — Sessions-as-microVMs decouples session lifetime from any one machine; "social information fabric" framing for multiplayer extension. **Skip** — Research preview only.

### Claude-Code-adjacent + agent-orchestration category

- **claudecodeui / CloudCLI — `siteboon/claudecodeui`** — React frontend over the same `~/.claude` directory Claude Code uses. Chat / file explorer / git / shell / MCP panels. AGPL-3, ~10.4k stars. **Take** — Read/write `~/.claude` directly as the bidirectional sync mechanism — no new daemon, just stable JSONL transcript files. **Skip** — Layout fixed; panels are CRUD-over-Claude-Code, not collab surfaces.
- **Happy — `slopus/happy`** — Mobile + web client; E2E-encrypted remote control of Claude Code / Codex. Live-preview-with-click-to-edit feature *requested* in #802 but not shipped. MIT, ~19.6k stars. **Take** — E2E remote-control transport pattern. The unshipped #802 confirms the gap. **Skip** — Mobile-first; doesn't add panel types.
- **OpenAgents Workspace — `openagents-org/openagents`** — Browser Workspace + CLI Launcher + Network SDK. Persistent shareable workspace URL. Shared browser (agents and humans see and click the same browser tabs); shared filesystem; `@mention` agent-to-agent delegation. Apache-2.0, ~3.4k stars. **Take** — Shared-browser as a first-class panel type; URL-as-workspace-handle for resumability. **Skip** — Multi-agent collab is a different problem; architecture is heavier than needed.
- **Conductor** — macOS app; multiple Claude Code agents in parallel, each in its own worktree. Single window: query box, terminal, diff area, workspace list. **Take** — Diff-area-as-first-class-panel separate from terminal — review and execution surfaces should not share. **Skip** — macOS-only; closed; orchestration angle.
- **Crystal / Nimbalyst — `stravu/crystal` → Nimbalyst** — Already named. Crystal deprecated Feb 2026; Nimbalyst is the successor. Same orchestration ≠ workspace lesson as Conductor.
- **Cline / Roo Code / Continue.dev** — VS Code extensions, sidebar chat + tool use. Roo Code reportedly shutting down May 2026 (per prompt; verify). Continue.dev pivoted to CI enforcement; Cline doubled down on autonomous coding. None ship configurable peer panels.
- **Aider, Plandex, Devika, OpenHands** — CLI / TUI / web-chat-only. Aider's `--browser` mode is a chat surface, not a workspace. None match the model.
- **Vibe Kanban — `BloopAI/vibe-kanban` (sunsetting)** — Kanban + worktree-per-agent + preview browser + terminal + diff. Rust + SQLite backend, React frontend. ~25.7k stars but sunsetting. **Take** — Split UI (kanban left, agent right) is a credible 2-panel layout; SQLite for workflow-state vs git for code-state — clean separation. **Skip** — Sunsetting (read the announcement before mining lessons).
- **Emdash — `generalaction/emdash`** — YC W26, Apache-2.0, ~4.2k stars, 24 CLI agents, parallel worktrees, ticket integrations, local-first SQLite. **Take** — Ticket-as-task-source as a credible "task panel" backing. **Skip** — Orchestration angle.
- **cmux — `manaflow-ai/cmux`** — Ghostty-based macOS terminal; vertical tabs; agent notifications via OSC sequences; scriptable embedded browser. ~15.9k stars, GPL-3. **Take** — Notification-by-OSC-sequence pattern (cheap, protocol-light); scriptable embedded browser as a panel type. **Skip** — macOS terminal-shell, not browser.

### Collaborative editor + canvas category

- **tldraw + Agent Starter Kit + tldraw MCP App** — Already named. Multiplayer canvas (`@tldraw/sync` + Cloudflare Durable Objects); WebSocket streaming with backpressure. **Take** — Working multiplayer pattern for agent-and-user-on-the-same-canvas. **Skip** — Single-canvas-as-app.
- **Pencil (`pencil.dev`, Tom Krcha, Jan 2026)** — Infinite WebGL design canvas for Claude Code / Codex / Cursor / VS Code. Up to 6 design agents in parallel. Open `.pen` JSON committed to git. **Take** — File-format-as-contract: JSON in git, agents and users both read/write the same file, no proprietary state store. Aligned with "panel content persists as files" directly. **Skip** — Design-canvas single-app.
- **Flowith** — SaaS, 1M+ users; Agent Neo + Knowledge Garden + Canvas Cowork accepts Claude Code / Codex / OpenClaw output. **Take** — Canvas-as-meta-coordinator across agents. **Skip** — SaaS; production-not-developer focus.
- **AFFiNE + BlockSuite** — BlockSuite is the open-source block-editor framework underneath AFFiNE — every paragraph/task/image is a database block. Edgeless (whiteboard) + Page (doc) modes. Self-hostable. **Take** — BlockSuite as a credible OSS library for the "structured-document panel where agent and user both edit blocks" need. **Skip** — AFFiNE itself is a Notion-equivalent; use BlockSuite as a library, not adopt the app.
- **OpenClaw — `openclaw/openclaw`** — Local-first personal AI assistant; Live Canvas with A2UI (declarative-JSON-as-UI rather than HTML). MIT. **Take** — A2UI declarative-JSON-from-agent contract — typed render boundary that doesn't trust agent-emitted HTML. **Skip** — Personal assistant focus, not workspace.
- **Anytype + Anytype MCP** — Local-first encrypted PKM; MCP server bridges AI to the local Anytype API. **Take** — MCP-server-as-bridge-to-local-app generalises: any local app with an API can expose itself to a workspace agent via MCP. **Skip** — Anytype itself is PKM.
- **Tana / Capacities / Reflect / Mem 2.0** — PKM + AI integrations. Tana's "Supertags + AI workflow engine" is closest to "agent participates in structured documents." None ship configurable panel layouts.

### Self-hosted chat + artifact category

- **Open WebUI / LibreChat** — Self-hosted multi-LLM chat with artifacts (HTML/JS via Sandpack, mermaid, code rendering). MIT each, large stars. **Take** — Sandpack as the secure HTML/JS render boundary if any panel runs untrusted code; Open WebUI's workspace concept (separate "rooms") aligns with layout-saving. **Skip** — Chat-first; artefact panels aren't peer surfaces.
- **Big-AGI / LobeHub / AnythingLLM** — Self-hosted multi-LLM chat. LobeHub's workspace concept (Pages, Projects, Agent panel) is closest to the model but still chat-with-side-panel.

## Inspirational but distant

Manifestos, design docs, and adjacent work that informs the *why* without implementing the *what*.

### "One Developer, Two Dozen Agents, Zero Alignment" — Maggie Appleton, GitHub Next

The closest design-doc match for *why* an agent workspace exists.

- Argues the bottleneck moved from implementation to alignment; current agent tools are "single-player interfaces"; planning must merge with building in one space.
- Design principles named: shared context, continuous alignment (planning and building as one cycle), accessible participation (designers, PMs without terminals), transparent progress (dashboard against information overload).
- Proposed Ace architecture: Slack-like multiplayer chat + cloud microVMs + shared agent + integrated terminal/preview/edit + native PR integration.
- **Borrow** — The design vocabulary ("social information fabric," "alignment bottleneck," "implementation cheap, planning expensive"). Frames *why* the workspace exists, even if multi-user is out of scope.

### "Anatomy of an Agent Harness" — LangChain blog + Addy Osmani's "Agent Harness Engineering"

Foundational vocabulary for the harness layer. Six primitives: durable storage, code execution, memory + context injection, orchestration, context management, hooks. Filesystem framed as "the shared workspace." **Borrow** — The decomposition. The workspace is one harness; panels are the visible surface of harness state.

### tldraw "Agents on the Canvas" — Steve Ruiz talk

Three-pattern taxonomy for AI on a canvas — output-display, visual-workflows, agent-as-canvas-participant. Useful for any canvas-shaped panel.

### Live Preview Panel feature request — `slopus/happy#802`

The exact missing piece many projects share: an open feature request, not yet implemented. Confirms the gap; useful as evidence the design is wanted but no one has shipped it cleanly.

### Lower-traffic exploratory projects

TigrimOS, OpenFang, Agent Zero (universal canvas), Space Agent (browser), Hermes Workspace (`outsourc-e/hermes-workspace`, `nesquena/hermes-webui`) — agent-OS / browser-workspace prospectors. None at the maturity or fit of the closer matches; bookmarked as evidence the design space is being explored from multiple directions.

## Comparison table

| Project | URL | Panels | Agent depth | Self-host | License | Stars | Fit |
|---|---|---|---|---|---|---|---|
| **OpenCove** | `github.com/DeadWaveWave/opencove` | Agent, terminal, task, note, image | Shared-state-peer | Local + headless web | MIT | ~1.2k | Closest |
| **Embedded Editor** | `github.com/1vav/embedded-editor-for-claude-code` | Excalidraw, tldraw, MD, DuckDB, PDF, CSV | Shared-state-peer (MCP+SSE) | Local | MIT | low | Closest |
| **Wave Terminal** | `github.com/wavetermdev/waveterm` | Terminal, file, web, AI chat, editor | Chat-with-tool-use | Local desktop | Apache-2.0 | ~20k | Close |
| **Goose** | `github.com/block/goose` | Chat + sidecar (MCP Apps) | Tool-use + MCP-App render | Local desktop | Apache-2.0 | ~15k+ | Partial |
| **Jupyter AI** | `github.com/jupyterlab/jupyter-ai` | Cells (notebook fixed) | Cell-participant (ACP+RTC) | Local/server | BSD | ~3k+ | Partial |
| **Marimo** | `github.com/marimo-team/marimo` | Cells (reactive) | Edits cells (Agent beta) | Local | Apache-2.0 | ~10k+ | Partial |
| **Zed** | `github.com/zed-industries/zed` | Editor + agent + thread + project + git | Shared-state-peer (ACP) | Local desktop | GPL-3 | ~50k+ | Partial |
| **Cursor** | `cursor.com` | Editor + tiled agents + canvas + terminal + browser + SCM | Shared-state-peer | Local desktop | Closed | n/a | Partial |
| **Replit Agent** | `replit.com/agent4` | Editor, agent, preview, canvas | Shared-state-peer | Cloud | Closed | n/a | Partial |
| **Ace (GitHub Next)** | `githubnext.com` | Chat, terminal, code, preview | Multiplayer peer | Cloud (microVMs) | Research preview | n/a | Partial |
| **Antigravity** | `antigravity.google` | Editor, manager, artifacts | Artefact-producer | Cloud | Closed | n/a | Partial |
| **Vibe Kanban** | `github.com/BloopAI/vibe-kanban` | Kanban + agent + preview + terminal + diff | Task-runner | Local | Apache-2.0 | ~25.7k (sunsetting) | Partial |
| **Emdash** | `github.com/generalaction/emdash` | Workspace list + agent + diff + preview | Task-runner | Local + SSH | Apache-2.0 | ~4.2k | Partial |
| **OpenAgents** | `github.com/openagents-org/openagents` | Chat + shared browser + shared files | Multi-agent peer | Local + browser | Apache-2.0 | ~3.4k | Partial |
| **Conductor** | `conductor.build` | Workspace list + query + terminal + diff | Task-runner | Local Mac | Closed | n/a | Partial |
| **claudecodeui** | `github.com/siteboon/claudecodeui` | Chat, files, git, shell, MCP | Reads/writes `~/.claude` | Local + LAN | AGPL-3 | ~10.4k | Partial |
| **Happy** | `github.com/slopus/happy` | Mobile + web client | E2E remote control | Local + remote | MIT | ~19.6k | Partial |
| **cmux** | `github.com/manaflow-ai/cmux` | Terminal panes + embedded browser | Notification + scripting | Local Mac | GPL-3 | ~15.9k | Partial |
| **Pencil** | `pencil.dev` | WebGL design canvas | Multi-agent on `.pen` | Local | Closed | n/a | Partial |
| **tldraw** | `tldraw.dev` | Single canvas | Reads/writes canvas | Local + multiplayer | Custom (free OSS) | ~38k+ | Partial |
| **AFFiNE / BlockSuite** | `github.com/toeverything/affine` | Pages + Edgeless | AI features | Self-host | MPL-2 | ~50k+ | Partial |
| **LibreChat** | `librechat.ai` | Chat + Sandpack artefacts | Tool-use | Self-host | MIT | ~25k+ | Partial |
| **Open WebUI** | `openwebui.com` | Chat + workspace rooms + artefacts | Tool-use | Self-host | MIT | ~80k+ | Partial |

Numbers are point-in-time and directional; verify before quoting.

## Pitfalls and lessons learned

Patterns recurring across projects.

- **Chat-on-the-side is the path of least resistance.** Even teams shipping the right layout primitive (Wave's blocks) bolt the agent on as a side panel rather than a peer. Agent-as-peer is harder than it looks; designing the workspace from the start with the agent as a panel-creating peer (not a dock-attached chat) is the discipline. Wave issue #2168 ("Wave Agent Mode") is direct evidence of the gap.
- **Spatial canvas vs tiled is a fork, not a default.** OpenCove went canvas; Replit went tiled-tree; Cursor went tiled-with-canvas-as-an-artefact-type. Users complain about pan/zoom fatigue at scale (tldraw, Flowith, infinite-canvas note apps). Committing to one mode loses half the audience; configurable per workspace hedges.
- **Files-on-disk are the durable substrate.** Pencil's `.pen` JSON in git, embedded-editor-for-claude-code's per-type files, marimo's `.py` watch mode — every credible bidirectional implementation treats files as source of truth and the browser as a view. Custom server-side state stores create resync bugs and migration debt. Reinforce.
- **MCP + SSE is the working pattern for agent ↔ panel.** Embedded-editor-for-claude-code is the cleanest reference. MCP tools (`add_shape`, `add_row`, `set_text`) for agent → panel; SSE (or watch-mode) for panel → agent. WebSocket-based custom protocols (tldraw, Liveblocks) work but add infrastructure that MCP+SSE doesn't need.
- **Inline preview, full editor.** "Agent sees a low-token PNG / summary, user sees the full canvas" (embedded-editor-for-claude-code; Antigravity artefacts) solves the agent-context-window vs full-fidelity tension. Without it, every canvas operation pushes large state into the agent's window.
- **Per-call permission gating.** Zed and Marimo both implement Manual / Ask / Agent permission tiers explicitly. Without tiers, agents need full trust or perpetual prompts. The tier discipline lets a workspace add panel-write privileges to the gate set rather than re-asking each tool call.
- **Layout is plugin state, dispatched via actions.** Replit's blog post explains why their layout tree is owned by the workspace and plugins dispatch built-in actions. Any new panel type plugs in without re-implementing layout. Worth mirroring.
- **Discoverable, named tool surface, not generic.** Goose's MCP-Apps-returning-embedded-resource, embedded-editor-for-claude-code's per-type tools, Cursor canvases' first-party React component library — all rely on a typed contract. Generic "render this HTML" leads to model-vendor lock to whoever produces reliable HTML; typed contracts let multiple model vendors hit the same panel surface.
- **Sunsetting and category churn.** Vibe Kanban (sunsetting), Crystal → Nimbalyst (rename), Roo Code (May 2026 reported), Devin (closed), Goose moving from Block to AAIF — orchestration-layer category churns fast. Closer-to-the-OS layers (terminals, multiplayer editors) are more stable. Building against ACP / MCP and treating agents as interchangeable backends survives the churn.
- **Bidirectional collaboration surfaces are the empty box.** Almost no project ships true peer editing of structured docs / canvases. Embedded-editor-for-claude-code is the only confirmed both-way reader/writer; Pencil is the only confirmed file-based both-way canvas. This is genuinely under-shipped — close to the design's value proposition, not just inertia.
- **Single-player critique applies even to one-human + one-agent.** Sessions-as-microVMs (Ace) and URL-addressed workspaces (OpenAgents) point to the multi-user extension. Designing the workspace state schema as if multiplayer were imminent (even if not built day-one) makes future expansion free instead of a rewrite.

## Recommended path for our design

- **Strongest fork candidate: `1vav/embedded-editor-for-claude-code`.** It already implements the MCP + SSE bidirectional pattern with multiple panel types and is actively maintained. Gaps to the design: configurable layout, terminal panel, layout save/reopen, more viewer types. Forking and extending — rather than re-implementing — saves the bidirectional-sync engineering and the per-type MCP tool design.
- **Strong extension candidate: BlockSuite + tldraw + xterm.js + xyflow as the panel-implementation library set.** Each is best-in-class for one panel type. Composing these inside the embedded-editor pattern gets configurable structured-doc panels (BlockSuite), canvas (tldraw), terminal (xterm.js), and tile-or-spatial layout (`react-resizable-panels` or `@xyflow/react`) — all maintained, all OSS.
- **Wholesale-borrow patterns:**
    - MCP tools + SSE for panel-creation and live-sync (embedded-editor).
    - Files-on-disk as source of truth, browser as view (Pencil, marimo). No custom server state store.
    - Per-call permission tiers (Zed, Marimo).
    - Layout-tree dispatched via actions (Replit IDE blog).
    - MCP Apps / A2UI typed render contracts (Goose, OpenClaw) so any agent can target the same panel.
    - Inline preview / full editor split (embedded-editor, Antigravity).
- **Learn from, do not adopt:**
    - Wave's `wsh` IPC — informs how terminal panels can be both subjects and observers without privilege.
    - Ace's "social information fabric" — design state as if multiplayer were imminent.
    - Maggie Appleton's manifesto — borrow the "alignment bottleneck" vocabulary for the design doc.
- **Invent only:**
    - Conversation-driven panel-opening UX (most projects open via menu / palette; agent-driven on-demand opening at the configurable-layout level is genuinely under-shipped).
    - Layout-save persistence, if no existing schema maps cleanly. OpenCove's "space archives" is the closest existing primitive — examine before inventing.

## Gaps and open questions

- **How does `embedded-editor-for-claude-code` actually persist layouts across sessions?** README mentions live syncing of editors, not layout configurations across sessions. Worth a code-read.
- **Is OpenCove's spatial canvas actually configurable, or canvas-only?** Alpha status suggests still moving. Direct conversation with the maintainer might be cheaper than reverse-engineering.
- **Why is Vibe Kanban sunsetting?** Could be commercial (BloopAI's company priorities), could be technical (kanban metaphor not fitting agent workflows). The post-mortem post is the highest-leverage read for category lessons; not yet fetched.
- **MCP Apps adoption beyond Goose** — A2UI / AG-UI / MCP Apps are converging-but-not-converged protocols for "agent emits a UI." Picking the right protocol now requires more depth on each.
- **The carcasses are not visible in this search.** "Agent workspace abandoned" returned mostly current launches, not post-mortems. Vibe Kanban announcement is the only direct pointer; deeper carcass research would require targeted searches on specific known-dead projects (Devin, Devika, etc.) plus Hacker News post-mortem threads.
- **Multi-user vs single-user clarity.** Several projects (Ace, OpenAgents) bake multiplayer in. Single-human + agent is the current design; the question is whether the workspace state schema makes future multiplayer free or expensive. Worth a design decision before architecture freezes.

## Sources

- [`DeadWaveWave/opencove`](https://github.com/DeadWaveWave/opencove) — verified MIT, ~1.2k stars, v0.2.0 April 27 2026
- [`1vav/embedded-editor-for-claude-code`](https://github.com/1vav/embedded-editor-for-claude-code) — verified MIT, v1.2.1 April 29 2026, 9 releases
- [`wavetermdev/waveterm`](https://github.com/wavetermdev/waveterm) — verified Apache-2.0, ~20k stars, v0.14.5 April 16 2026
- [Wave Terminal Block System (DeepWiki)](https://deepwiki.com/wavetermdev/waveterm/3.2-block-system)
- [Wave Agent Mode roadmap (issue #2168)](https://github.com/wavetermdev/waveterm/issues/2168)
- [`block/goose`](https://github.com/block/goose) — verified Apache-2.0, AAIF-hosted
- [Goose Extensions Design](https://block.github.io/goose/docs/goose-architecture/extensions-design/)
- [`jupyterlab/jupyter-ai`](https://github.com/jupyterlab/jupyter-ai)
- [`datalayer/jupyter-ai-agents`](https://github.com/datalayer/jupyter-ai-agents)
- [Marimo agents docs](https://docs.marimo.io/guides/editor_features/agents/) and [`riyavsinha/marimo-agents`](https://github.com/riyavsinha/marimo-agents)
- [Zed Agent Panel docs](https://zed.dev/docs/ai/agent-panel) and [Parallel Agents blog](https://zed.dev/blog/parallel-agents)
- [Cursor 3.1 Canvas blog](https://cursor.com/blog/canvas)
- [Replit Modular IDE blog](https://blog.replit.com/ide) — server-rendered IDE design rationale
- [Replit Agent docs](https://docs.replit.com/core-concepts/agent)
- [Windsurf Cascade docs](https://docs.windsurf.com/windsurf/cascade/cascade)
- [`siteboon/claudecodeui`](https://github.com/siteboon/claudecodeui) — verified AGPL-3, ~10.4k stars
- [`slopus/happy`](https://github.com/slopus/happy) — verified MIT, ~19.6k stars
- [Happy issue #802 — Live Preview Panel + Click-to-Edit](https://github.com/slopus/happy/issues/802)
- [`openagents-org/openagents`](https://github.com/openagents-org/openagents) — verified Apache-2.0, ~3.4k stars
- [`generalaction/emdash`](https://github.com/generalaction/emdash) — verified Apache-2.0, ~4.2k stars, YC W26
- [`BloopAI/vibe-kanban`](https://github.com/BloopAI/vibe-kanban) — verified Apache-2.0, ~25.7k stars, sunsetting
- [`stravu/crystal`](https://github.com/stravu/crystal) → [Nimbalyst](https://nimbalyst.com)
- [Conductor docs](https://docs.conductor.build/)
- [Intent — Augment Code](https://www.augmentcode.com/blog/intent-a-workspace-for-agent-orchestration)
- [Google Antigravity docs](https://antigravity.google/docs/workspaces)
- [GitHub Copilot Workspace user manual](https://github.com/githubnext/copilot-workspace-user-manual)
- [Maggie Appleton — One Developer, Two Dozen Agents, Zero Alignment](https://maggieappleton.com/zero-alignment) and [GitHub Next](https://githubnext.com/)
- [`manaflow-ai/cmux`](https://github.com/manaflow-ai/cmux) — verified GPL-3, ~15.9k stars
- [Pencil launch (Tom Krcha)](https://x.com/tomkrcha/status/2014028990810300498) and [`pencil.dev`](https://pencil.dev)
- [tldraw Agent Starter Kit](https://tldraw.dev/starter-kits/agent) and [tldraw MCP App blog](https://tldraw.dev/blog/tldraw-mcp-app)
- [Flowith Canvas Cowork](https://flowith.io/blog/canvas-cowork-skill/)
- [`anyproto/anytype-mcp`](https://github.com/anyproto/anytype-mcp)
- [`openclaw/openclaw`](https://github.com/openclaw/openclaw) — verified MIT
- [`toeverything/blocksuite`](https://github.com/toeverything/blocksuite) and [BlockSuite components](https://blocksuite.affine.pro/components/overview.html)
- [LibreChat artifacts](https://www.librechat.ai/docs/features/artifacts) and [Open WebUI](https://docs.openwebui.com/features/)
- [LobeHub workspace](https://lobehub.com/docs/usage/start)
- [LangChain — Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness)
- [Addy Osmani — Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/)
- [AG-UI Protocol](https://docs.ag-ui.com/introduction) and [A2UI](https://a2ui.org)
- [`react-resizable-panels`](https://github.com/bvaughn/react-resizable-panels)
- [`@xyflow/react`](https://reactflow.dev) — used by OpenCove
