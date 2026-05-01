# Sync mechanism layer

How state stays consistent between human and agent across panels of a locally-served browser workspace driven by a Claude Code session — survey of CRDT engines, sync engines, OT systems, and hybrids; the precedents for wiring an AI agent as a peer; and the recommended path.

## Landscape survey

Versions and stars verified April 2026 via repo fetches; "from training data, may be stale" applies to anything not labeled verified. Every option below self-hosts unless flagged otherwise.

### CRDT engines

User has already verified Yjs, Automerge core, y-sweet, Hocuspocus, Liveblocks. Adding alternatives:

**Yjs** — verified 21.7k stars, v14.0.0-rc.7 March 27 2026 (npm stable still 13.6.30), MIT. Y.Text / Y.Array / Y.Map / Y.XmlElement; broadest provider ecosystem (y-websocket, y-webrtc, Hocuspocus, y-sweet, y-durableobjects). Used by Notion, JupyterLab RTC, Tiptap.

**Automerge 3** — MIT, Rust core + JS/WASM/C bindings. Cut runtime memory ~10×: pasting Moby Dick was 700 MB on Automerge 2, 1.3 MB on Automerge 3; load time 17h → 9s [Automerge 3 announcement](https://automerge.org/blog/automerge-3/). The historic size-blowup that disqualified Automerge for serious docs is now near Yjs parity.

**Automerge Repo** — verified 678 stars, v2.5.5 March 31 2026, MIT. Higher-level layer over the core: storage + network adapters (WebSocket, MessageChannel, BroadcastChannel), document discovery, GC. Defaults to Automerge 3 since v2.1. The practical entry point for new Automerge work.

**Loro** — verified 5.6k stars, v1.12.1 April 29 2026, MIT. Rust + WASM/Swift/Python bindings. Fugue (text), Peritext-derived rich text, movable tree, movable list, LWW map. Differentiators: shallow snapshots (Git-shallow-clone-like), time travel to arbitrary frontiers, fast load. Thinner provider ecosystem than Yjs.

**Yrs (y-crdt)** — ~1.3M crates.io downloads cumulative, 0.25.0 (~Dec 2025). Rust port of Yjs, binary-protocol-compatible — Yrs and Yjs nodes cohabit a doc. Path when you want Yjs semantics from a non-JS host.

**Diamond Types** — verified 1.8k stars, ISC, "WIP". Rust + WASM, plain text only on main; `more_types` branch adds JSON. Speed-king on text per Seph Gentle's benchmarks. Reference, not production substrate.

**Tinybase** — MIT, ~5 KB bundle. Reactive KV + tabular store with native CRDT sync semantics — concurrent edits to different fields of the same row merge automatically. Pluggable persistence (IndexedDB, SQLite, Postgres), pluggable sync. Wrong tool for ProseMirror-style rich text.

**RGA / WOOT / Treedoc / Logoot** — older sequence CRDT algorithms; not yet found a maintained 2026 library preferring any of these over Yjs's YATA or Loro's Fugue.

### Sync engines (relational sync)

Category that emerged 2022–2024 for "we have a Postgres, we want local-first reads/writes" without CRDT data modeling.

**Replicache** — Rocicorp, MIT, **maintenance mode**. Open-sourced and free as of late 2025. Originated the "client-side mutators + server reconciliation" pattern. Rocicorp positions Zero as successor [Retiring Reflect](https://rocicorp.dev/blog/retiring-reflect). Sibling Reflect shut down Nov 1 2024.

**Zero** — alpha April 2026; beta target "late 2025 or early 2026" still pending [Zero roadmap](https://zero.rocicorp.dev/docs/roadmap). Postgres source, SQLite local cache, ZQL queries against a normalized client store. Convergence is **server-authoritative LWW with mutator replay**, not CRDT. Zero's client uses Replicache under the hood. Self-hostable (zero-cache + Postgres). Fit: relational app data, not free text.

**ElectricSQL** — Apache-2.0, "electric-next" rebuild stable, sponsored by Trigger.dev. Read-path-only Postgres sync — server publishes "shapes" (declarative subqueries), clients stream. Writes go through application endpoints, not Electric. Self-host = single Elixir service. Pairs with TanStack DB (FOSDEM 2026 "Query-driven Sync in TanStack DB").

**Triplit** — verified 3.1k stars, **AGPL-3.0**, v1.0.34 July 31 2025. Pluggable storage (IndexedDB, SQLite, DO). **Per-attribute CRDT** — conflicts isolate to individual columns. Self-hostable Node server. AGPL caveat: source-disclosure to network-service users; matters if the workspace is ever shared.

**PowerSync** — Apache-2.0 Open Edition + enterprise tier. Postgres/Mongo/MySQL/SQL Server source via WAL logical replication, SQLite client. Optimistic local + server-authoritative; "most production-tested local-first engine" per their own claim (verifiable from customer logos, not independently quantified).

**TanStack DB** — MIT, v0.6. Not a sync engine — a reactive client-side store designed to plug into Electric, Query-Driven Sync, or any backend. v0.6 added persistence + offline via SQLite-backed adapters (browser/RN/Expo/Node/Electron/Capacitor/Tauri/Cloudflare DO). Three sync modes: Eager, Progressive, Sync.

### Operational Transformation

**ShareDB** — verified 6.5k stars, MIT, v5.2.2 May 20 2025. JSON OT + rich-text-OT plugins. Pluggable persistence (Mongo, Postgres, in-memory). Pubsub adapter for horizontal scaling. Active but slow-moving. Reference open-source OT.

**Etherpad changeset model / Google Docs / Figma / Quip** — closed-source or legacy. Figma is **not** a CRDT despite marketing — server-authoritative OT-shaped reconciliation with 24-hour tombstone GC, accepting brief inconsistency for late-joiners [Figma multiplayer blog](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/), [crdt-website issue 60](https://github.com/ept/crdt-website/issues/60). Google Docs is OT and has not migrated. OT remains the dominant production stack for centralized server-authoritative collab.

### Hybrids and specialty

**Croquet / Multisynq** — deterministic-simulation framework. Every client runs the same simulation on a synchronized pseudo-clock; server only orders messages. Strength: zero-server-state for game-shaped apps. Wrong category for a panel-and-document workspace.

**PartyKit** — acquired by Cloudflare April 2024. Now part of Cloudflare Workers + DO. A substrate other CRDT/sync code runs on (e.g., y-durableobjects), not a CRDT itself. Self-host = run on Cloudflare; not local-only.

**y-durableobjects / yaos / tldraw-sync-cloudflare** — production Yjs-on-Cloudflare-DO patterns. One DO per document; DO holds WebSocket server + Yjs state; persistence to DO KV or R2. tldraw demonstrates production scale. Cloudflare-bound, but the **"one stateful actor per document"** shape transfers to any local actor-per-document server.

**Liveblocks** — SaaS-only. AI Copilots uses `RegisterAiKnowledge` / `RegisterAiTool` / `useAiChats()` / `defineAiTool()` — explicitly **not Yjs-based**; the AI surface is parallel to Storage / Comments. Excluded by self-host requirement.

### State management with sync hooks

**RxDB** — Apache-2.0, v17 in 2026 with "DX-for-LLMs" hooks. Replication plugins for GraphQL, CouchDB, WebSocket, WebRTC, Supabase, Firestore, NATS, Google Drive. Configurable conflict resolution per collection (LWW default); no built-in CRDT semantics.

**WatermelonDB** — Nozbe, MIT. RN + web. First-class sync protocol, timestamp-based dirty-record tracking, native SQLite. Optimized for offline-first mobile, not browser-panel collab.

**TanStack Query + WebSocket subs / Apollo subscriptions** — *transport patterns*, not sync engines. Server-pushes-client-invalidates, no convergence semantics. Fine for read-heavy panels where the agent is sole writer; insufficient for bidirectional collab.

## Comparison table

Fit rating considers a locally-served browser workspace where (a) the agent and human both read and write, (b) self-host on WSL is required, (c) panels include free text, structured JSON, and read-only viewers, (d) operational footprint must be low.

| Name | URL | Type | Maturity | Self-host | Primary use | Fit |
|------|-----|------|----------|-----------|-------------|-----|
| Yjs | [yjs.dev](https://yjs.dev/) | CRDT | 21.7k stars, v14 RC, mature | Trivial — y-websocket / Hocuspocus / y-sweet | Free text, rich text, structured JSON | **Strong — primary candidate** |
| Automerge 3 + Repo | [automerge.org](https://automerge.org/) | CRDT | MIT, Repo 678 stars, post-3.0 inflection | Trivial — automerge-repo-sync-server | JSON document trees | Strong — alt to Yjs |
| Loro | [loro.dev](https://loro.dev/) | CRDT | 5.6k stars, v1.12 | Self-host as a library; no canonical server pairing | Rich text, movable tree, time travel | Watch — newer; thin server ecosystem |
| Yrs | [docs.rs/yrs](https://docs.rs/yrs/) | CRDT | 1.3M downloads, 0.25 | Use as Rust/Python/Ruby/.NET library | Yjs-compatible from non-JS hosts | Useful only if non-JS server |
| Diamond Types | [github.com/josephg/diamond-types](https://github.com/josephg/diamond-types) | CRDT (text) | 1.8k stars, "WIP" | Library only | Plain text only | Reference — not yet broad-fit |
| Tinybase | [tinybase.org](https://tinybase.org/) | CRDT (relational) | MIT, ~5 KB | Trivial — server adapter pluggable | KV / tabular reactive store | Strong — for non-text panels |
| Replicache | [replicache.dev](https://replicache.dev/) | Sync engine | Maintenance mode | OSS + free | Relational app data | Avoid new — Zero is successor |
| Zero | [zero.rocicorp.dev](https://zero.rocicorp.dev/) | Sync engine | Alpha → beta target ~now | Yes (zero-cache + Postgres) | Relational over Postgres | Watch — too early for primary |
| ElectricSQL | [electric-sql.com](https://electric-sql.com/) | Sync engine (read-path) | Stable post-rebuild | Yes (Elixir service) | Postgres → client read sync | Useful adjunct, not primary |
| Triplit | [triplit.dev](https://www.triplit.dev/) | Sync DB | v1.0.34 (Jul 2025) | Yes (Node server) | Per-attribute CRDT relational | Watch — AGPL caveat |
| PowerSync | [powersync.com](https://www.powersync.com/) | Sync engine | Open Edition 2026 | Yes (Open Edition self-host) | Postgres/Mongo/MySQL → SQLite | Heavyweight — overkill for local |
| TanStack DB | [tanstack.com/db](https://tanstack.com/db) | Reactive store + sync hooks | v0.6, MIT | N/A — runs in client | Reactive query, plugs into Electric/etc. | Strong — client-layer adjunct |
| ShareDB | [share.github.io/sharedb](https://share.github.io/sharedb/) | OT | 6.5k stars, v5.2.2 (May 2025) | Yes (Node server) | JSON OT documents | Avoid new — OT is legacy for greenfield |
| Croquet/Multisynq | [croquet.io](https://croquet.io/) | Det. simulation | Active | Limited — designed for DePIN/Multisynq net | Game-shaped multiplayer | Wrong category |
| PartyKit (Cloudflare) | [github.com/cloudflare/partykit](https://github.com/cloudflare/partykit) | Substrate | Cloudflare-hosted | No — Cloudflare-bound | Stateful Workers actors | Wrong substrate (cloud) |
| y-durableobjects | [github.com/napolab/y-durableobjects](https://github.com/napolab/y-durableobjects) | Yjs on DO | Active | No — Cloudflare-bound | Yjs server on Workers | Pattern only — not local |
| Liveblocks | [liveblocks.io](https://liveblocks.io/) | SaaS | Mature | **No — SaaS only** | Comments, AI Copilots, Storage | Excluded by self-host requirement |
| RxDB | [rxdb.info](https://rxdb.info/) | Reactive DB + replication | v17 | Yes — library | Offline-first reactive document DB | Adjunct — not collab-shaped |
| WatermelonDB | [watermelondb.dev](https://watermelondb.dev/) | RN+web local DB | Nozbe-maintained | Yes — library | Offline-first mobile | Wrong target (RN-first) |

## Pitfalls and lessons learned

**CRDT metadata bloat is real.** Basic sequence CRDTs add 16–32 bytes of metadata per character — a 10K-char doc balloons to ~320 KB; kills mobile and embedded perf [Taskade — OT vs CRDT 2026](https://www.taskade.com/blog/ot-vs-crdt). Yjs YATA and Automerge 3 mitigate aggressively but the failure mode persists at scale.

**Tombstones never go away cleanly in P2P.** Removing a tombstone requires every replica to agree it will never be referenced — hard with intermittent peers. Figma reported docs accumulating 10M+ tombstones from deleted shapes; fix was aggressive 24-hour GC that accepts brief late-joiner inconsistency. Centralized server-authoritative architectures sidestep this by treating the server snapshot as the GC checkpoint.

**Figma is not a CRDT.** Server-authoritative OT-shaped reconciliation; considered CRDTs and rejected the overhead. Don't reach for CRDTs by default; reach for them when you actually need decentralized convergence.

**Google Docs has not migrated.** OT remains the production stack for the largest collab product on the internet. The "CRDTs replaced OT" narrative is advocacy overclaim.

**Jupyter RTC's content-triplication problem.** Same content held in three stores — the view, an internal ModelDB, and the Yjs document — each change propagates to all three; bugs are constant; selective undo (ignore-remote) on top of CRDT is extremely hard [JupyterLab issue 11434](https://github.com/jupyterlab/jupyterlab/issues/11434). **Lesson: never let a CRDT be "another store layered on a real store." The CRDT must *be* the source of truth for what it covers; everything else is a derived view.**

**Replicache → Zero migration is a real cost.** Replicache is in maintenance mode; Zero's API is meaningfully different (mutators changed, sync model rewritten). Starting on Replicache today buys a migration. Zero itself remains alpha-to-early-beta in April 2026, behind its original timeline.

**ElectricSQL did one full ground-up rebuild.** Legacy ElectricSQL was abandoned July 2024 for "electric-next." 2022–2024 articles reference a different system; citing the old one as evidence is a footgun.

**Triplit AGPL-3.0** requires source disclosure when the network service is used by others. Non-issue for strictly personal local workspaces; engages the moment the workspace is shared.

**Rocicorp prunes aggressively.** Reflect (Nov 2024) and the early Replicache framework iterations were both killed. Doesn't disqualify Zero — they're betting the company on it — but a signal worth knowing.

**Liveblocks AI Copilots is not Yjs-based.** Worth restating because Liveblocks Storage *is* Yjs-shaped. Adopting Liveblocks AI does not give you "AI peer in your CRDT doc."

## Agent-integration precedents

Projects that wired an AI agent as a peer participant in the sync layer — not as a sidecar that calls APIs to read/write the doc.

**ElectricSQL — "AI agents as CRDT peers with Yjs" (April 8 2026).** [electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs). The canonical reference for this design. Architecture worth studying in detail because it directly answers the user's "is anyone doing this" question:

- **Server-side Yjs peer.** The agent runs on the server with its own `Y.Doc` and `Awareness` instance. Same connection protocol as human clients; no client-side bolt-on.
- **Three Durable Streams.** (1) Yjs document updates with persistence and GC, (2) Yjs awareness — cursors, selections, presence, (3) TanStack AI chat — conversation history and agent responses. All three over the same HTTP streaming protocol; no separate WebSocket infra.
- **Tools follow a read → locate → edit pattern.** `get_document_snapshot`, `search_text` (returns stable match handles), `place_cursor`, `insert_text`, `start_streaming_edit` (toggle that routes subsequent model output into the document instead of chat). Plus selection / bulk replace / formatting / deletion tools.
- **Streaming markdown pipeline.** Model emits tokens; an incremental markdown parser converts `**bold**`, headings, lists into native Yjs nodes in real time as the agent types.
- **Relative-position anchors.** Client-side cursor positions are encoded as Yjs relative positions (anchored to CRDT items, not byte offsets) and sent with chat messages so the agent reasons about user intent against a shifting document.
- **Agent appears as a real collaborator.** Visible cursor with name "Electra," presence states (`thinking`, `composing`, `idle`), edits stream in via the same CRDT sync as humans.
- **Server peer = work continues without a browser.** The agent doesn't require an open client to operate; it's a persistent server actor.
- **Stack:** ProseMirror for rich text, TanStack Start for the app shell, TanStack AI for the chat layer, `@durable-streams/y-durable-streams` and `@durable-streams/tanstack-ai-transport` as the wire adapters. Code pattern in the post is a clean ~20-line server agent setup.

This is the precedent. The user's design intent maps onto this architecture almost cleanly — substitute Claude for the model, substitute the WSL local server for the Durable Streams server, swap in the panels the user wants.

**tldraw + Cloudflare Durable Objects + Yjs.** [github.com/tldraw/tldraw-sync-cloudflare](https://github.com/tldraw/tldraw-sync-cloudflare). Production demonstration of one-DO-per-document Yjs at meaningful scale, with auto-save to DO storage and offline buffering. No AI peer in the canonical pattern, but tldraw has been integrated as a target by many AI canvas demos. Confirms the "actor per document, CRDT inside the actor" pattern is production-shaped.

**CollabCanvas.** [github.com/adam0white/CollabCanvas](https://github.com/adam0white/CollabCanvas) Cloudflare Workers + Durable Objects + Yjs + React + Konva, with "AI-powered natural language commands" as one of its features — meaning a user issues an NL command and it's translated to canvas mutations. Less ambitious than the Electric blog: the AI is a translator, not a peer participant with cursor and presence. Useful as a midpoint reference.

**Cursor 3 (April 2026).** [cursor.com/blog/cursor-3](https://cursor.com/blog/cursor-3). The "agent-first interface" rebuild. Multi-repo workspace, parallel agent panes, unified surface for local + cloud agents. Cursor does *not* publish how its document sync is built — it's closed-source. Cursor is the closest commercial analog to the user's design intent and the closest existing UX shape for what the user described, but the sync mechanism is opaque. Worth tracking the public surface; do not rely on architectural inference.

**Hermes Workspace.** Open-source AI agent workspace with three-panel layout (sessions sidebar / chat / file browser). [github.com/nesquena/hermes-webui](https://github.com/nesquena/hermes-webui). Surface looks similar to the user's design but has no Yjs/CRDT — it's a standard request/response webui talking to the Hermes agent. Cited for layout precedent, not sync precedent.

**Convex + Automerge bridge.** [stack.convex.dev/automerge-and-convex](https://stack.convex.dev/automerge-and-convex). Demonstrates Automerge documents persisted into Convex. Not an AI peer per se, but shows the Automerge Repo pattern bridges into hosted backends cleanly when needed.

**DXOS / ECHO** uses Automerge for replication of its peer-graph database. P2P, agent-as-peer is structurally easy in this model, but ECHO is more an "operating system" framing than a panel-workspace substrate.

**Not yet found:** any project that wires Claude Code or a Claude SDK agent as a CRDT peer in a browser workspace. The Electric blog is OpenAI/TanStack-AI shaped. Searches for `"sync engine" "Claude Code" "Cursor" agent collaboration document live` return only configuration-sync tools (skillshare, skillbook), not data-plane sync. Absence-of-evidence is not evidence-of-absence — but the user's specific combination (Claude Code + browser panel workspace + CRDT peer) does not surface in April 2026 searches.

## Recommended path for our design

Translating the Electric AI-peer architecture into the user's constraints (local WSL server, Claude Code session, panels persisted as files, configurable layout):

**Primary substrate: Yjs.** This is where the AI-peer precedent lives. Yjs also has the densest provider ecosystem, the editor integrations the workspace will want (ProseMirror, CodeMirror, Quill, Tiptap), and a mature awareness / presence model for making the agent visible. Automerge 3 + Repo is a credible alternative now that the memory cliff is gone; pick Yjs because the precedent, editors, and server options (Hocuspocus, y-sweet) are all denser.

**Server: Hocuspocus on the local Node process.** Self-host = Node process alongside the workspace HTTP server. Persistence via the SQLite extension. Skip the Redis extension — single-user. y-sweet is a strong alternative if S3-compatible local blob storage (Garage/SeaweedFS/MinIO) is preferred, but for the user's "content persists as files" framing, Hocuspocus + SQLite is simpler.

**Agent integration: server-side Yjs peer per the Electric pattern.** A small process (or worker thread) holds a `Y.Doc` per open panel and connects to Hocuspocus over the same wire as the browser. It exposes MCP tools to Claude Code — `get_panel_snapshot`, `search_panel_text`, `place_panel_cursor`, `insert_panel_text`, `start_streaming_panel_edit`. Streaming Claude output is routed into the doc inside the peer (not on the Claude Code side): Claude returns text, the peer funnels it through an incremental markdown parser into the Y.Text. Awareness state advertises the agent with a name and presence indicator (`thinking` / `composing` / `idle`).

**Non-text panels.** Y.Map for structured docs (forms, configs); Y.Array for ordered lists (queues, todos); Y.XmlElement for ProseMirror trees. Read-only viewers (PDFs, rendered output, images) need no CRDT — sync file pointers as Y.Map entries; the browser opens the file directly.

**Layout state is itself a Yjs doc.** The "fully configurable layout of panels" is collaborative state — agent opens panels at conversation-driven invocations, user controls layout. One Y.Map: keys = panel IDs, values = `{type, file, position, size}`. Agent calls `open_panel(type, file)` → append a Y.Map entry → UI reacts. "Save layout" = serialize to disk; "load" = deserialize into a fresh Y.Doc. Same sync mechanism as the panels.

**Don't reach for:**

- **Sync engines as primary** (Zero, Electric, Triplit, PowerSync). They solve "optimistic relational rows + server reconciliation," not "bidirectional human-agent collab on prose and structured trees." Wrong shape.
- **OT (ShareDB).** No reason to take on OT's centralized coordination complexity when Yjs + Hocuspocus gives the same server-authoritative profile with simpler logic.
- **Liveblocks.** SaaS-only; the AI Copilots model isn't a CRDT peer.
- **Loro / Diamond Types as primary.** Worth watching — Loro has features (shallow snapshots, time travel) that might matter later, Diamond Types is the speed reference — but thinner provider ecosystems than Yjs in April 2026 mean more glue today.
- **Replicache.** Maintenance mode; if the relational-sync category becomes relevant later, pick Zero.

**Optional adjuncts:**

- **TanStack DB** for non-CRDT reactive state on the client (transcript list, file tree). Clean bridge from a Postgres-like server (or the existing transcripts MCP SQLite) to a reactive client without dragging CRDTs in.
- **Tinybase** only if a panel demands a tabular reactive store with CRDT semantics and nothing rich-text-shaped. Don't introduce both Tinybase and Yjs unless the panel demands it.
- **Yrs** if any part of the peer ends up in Rust — wire-protocol compatibility means Rust and JS peers cohabit a Y.Doc seamlessly.

## Gaps and open questions

1. **MCP Apps protocol overlap.** MCP Apps (Jan 2026, JSON-RPC over postMessage) is request/response over a sandboxed iframe, not a sync mechanism. Define the relationship: is MCP Apps the orchestration channel and Yjs the document-state channel running in parallel? Not yet found a project using both together.

2. **Persistence shape.** "Panel content persists as files" strongly implies filesystem, not SQLite blob. Is the file canonical and the Y.Doc a derived working copy, or vice versa? If the file is canonical, each save needs a "snapshot Y.Doc → write file → reload Y.Doc" cycle. The Electric blog doesn't address this — their docs persist via Durable Streams, not files. The user's design diverges here and warrants its own design pass.

3. **Multi-panel awareness coordination.** Yjs is per-document; N panels = N Y.Docs. Cross-panel awareness (agent cursor in panel A while reading panel B) needs an aggregation layer Hocuspocus doesn't provide. Plausible: one "session" Y.Doc for awareness, per-panel Y.Docs for content.

4. **Workspace lifetime vs session lifetime.** Brief says "shares the session's lifetime." Server-peer pattern's main advantage is *outliving client connections.* If the peer dies with the Claude Code session, that advantage is lost. Confirm whether the lifetime tie is a strict constraint or a starting state.

5. **Validation for non-CRDT data.** Settings, layout, file tree all have natural LWW semantics — Y.Map handles it. Schema validation at the write boundary (e.g., "agent can't open a panel pointing outside the working dir") needs a home: server peer (validate before apply) or client (validate before broadcast)?

6. **"Mirror the live CLI" panel.** A terminal panel mirroring the CLI is a stream, not a document. Should be JSONL-over-WS or a pty-attached emulator, not a Yjs doc. Don't accidentally CRDTify the terminal.

7. **Whether to wait on Zero.** Beta target was "late 2025 / early 2026"; April 2026, beta still pending. If app metadata needs outgrow Y.Map, Zero is the most likely future answer; today, Y.Map suffices.

8. **No verified Claude-as-CRDT-peer precedent.** All AI-peer precedents use OpenAI / generic-LLM-API / TanStack AI shapes. The Electric pattern transfers directly, but wiring Claude Code's MCP-tool-and-skill model into a server-side Yjs peer is a small implementation gap nobody has publicly filled. Worth one sandbox prototype before committing.

## Sources

- [Yjs — repo](https://github.com/yjs/yjs) — verified 21.7k stars, v14.0.0-rc.7 March 27 2026
- [Yjs — homepage](https://yjs.dev/)
- [Automerge — repo](https://github.com/automerge/automerge)
- [Automerge 3.0 announcement](https://automerge.org/blog/automerge-3/) — 10× memory cut, 700 MB → 1.3 MB Moby Dick, 17h → 9s load
- [Automerge Repo](https://github.com/automerge/automerge-repo) — verified 678 stars, v2.5.5 March 31 2026
- [Loro — repo](https://github.com/loro-dev/loro) — verified 5.6k stars, v1.12.1 April 29 2026
- [Loro — Peritext / Fugue rich text](https://loro.dev/blog/crdt-richtext)
- [Yrs (y-crdt) — repo](https://github.com/y-crdt/y-crdt) — Rust port, binary-protocol-compatible with Yjs
- [Diamond Types — repo](https://github.com/josephg/diamond-types) — verified 1.8k stars, ISC
- [Tinybase](https://tinybase.org/) — reactive store with native CRDT sync semantics
- [Replicache](https://replicache.dev/) — maintenance mode
- [Rocicorp — Retiring Reflect](https://rocicorp.dev/blog/retiring-reflect) — Reflect shutdown Nov 2024
- [Zero — Rocicorp](https://zero.rocicorp.dev/) — alpha, beta target ~now
- [Zero — Roadmap](https://zero.rocicorp.dev/docs/roadmap)
- [ElectricSQL](https://electric-sql.com/) — read-path Postgres sync, post-rebuild
- [ElectricSQL — AI agents as CRDT peers with Yjs (April 8 2026)](https://electric.ax/blog/2026/04/08/ai-agents-as-crdt-peers-with-yjs) — **canonical agent-peer reference**
- [Triplit](https://www.triplit.dev/) — verified 3.1k stars, AGPL-3.0, v1.0.34 (Jul 2025)
- [PowerSync](https://www.powersync.com/) — Open Edition self-host
- [TanStack DB](https://tanstack.com/db) — v0.6 with persistence
- [TanStack DB 0.5 — Query-Driven Sync](https://tanstack.com/blog/tanstack-db-0.5-query-driven-sync)
- [ShareDB — repo](https://github.com/share/sharedb) — verified 6.5k stars, v5.2.2 May 20 2025
- [Croquet / Multisynq](https://croquet.io/)
- [PartyKit (Cloudflare)](https://github.com/cloudflare/partykit) — acquired April 2024
- [y-durableobjects](https://github.com/napolab/y-durableobjects) — Yjs on Cloudflare DO pattern
- [tldraw-sync-cloudflare](https://github.com/tldraw/tldraw-sync-cloudflare) — production Yjs-on-DO
- [CollabCanvas](https://github.com/adam0white/CollabCanvas) — Workers + DO + Yjs + AI commands
- [Liveblocks AI Copilots — docs](https://liveblocks.io/docs/ready-made-features/ai-copilots) — RegisterAiKnowledge, RegisterAiTool, not Yjs-based
- [RxDB](https://rxdb.info/) — v17 in 2026
- [WatermelonDB — repo](https://github.com/Nozbe/WatermelonDB)
- [Hocuspocus — repo](https://github.com/ueberdosis/hocuspocus)
- [Hocuspocus — persistence guide](https://tiptap.dev/docs/hocuspocus/guides/persistence)
- [y-sweet — repo](https://github.com/jamsocket/y-sweet) — S3-backed Yjs sync
- [Figma — How Figma's multiplayer technology works](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/) — *not* a CRDT
- [ept/crdt-website issue 60 — Figma is not technically a CRDT](https://github.com/ept/crdt-website/issues/60)
- [Taskade — OT vs CRDT in 2026](https://www.taskade.com/blog/ot-vs-crdt) — metadata bloat figures, Figma 10M+ tombstones
- [Jupyter RTC — JupyterLab issue 11434 next steps](https://github.com/jupyterlab/jupyterlab/issues/11434) — content-triplication problem
- [Jupyter — How we made Jupyter Notebooks collaborative with Yjs (Kevin Jahns)](https://blog.jupyter.org/how-we-made-jupyter-notebooks-collaborative-with-yjs-b8dff6a9d8af)
- [Cursor 3 — Meet the new Cursor](https://cursor.com/blog/cursor-3)
- [Convex + Automerge bridge](https://stack.convex.dev/automerge-and-convex)
- [DXOS / ECHO documentation](https://docs.dxos.org/echo/introduction/)
- [Hermes Workspace — repo](https://github.com/nesquena/hermes-webui)
- [Self-hosted S3 alternatives 2026 — SeaweedFS / Garage / RustFS](https://rilavek.com/resources/self-hosted-s3-compatible-object-storage-2026)
