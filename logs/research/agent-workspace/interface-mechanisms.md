# Interface mechanisms

Survey of interface mechanisms that could host the agent-workspace described in prior conversation: a locally-served, dynamically tiled, multi-panel surface where Claude Code opens panels at conversation-driven invocations, the user controls layout, panels mix terminals / editors / canvases / viewers / tables, and panel content persists as files in the session's working directory. Browser-based stacks are the existing default; this document evaluates them against alternatives so the choice of mechanism is deliberate rather than incidental.

The candidate space is broad — native desktop frameworks, TUI frameworks, panel-aware terminal multiplexers, IDE-as-host integrations, hybrid backends — and the requirements are non-negotiable on six axes: tiled dynamic panels, agent-as-participant via tool calls, self-hostable, reachable from WSL, layout persistence, live state-sync. Mechanisms are ranked on those axes and on the secondary criteria of implementation effort, capability ceiling, real precedent, and lock-in.

Findings up front: the requirement for *mixed-content panels including a true canvas (vector / pixel / drawable)* is the dominant constraint. Terminal-only mechanisms cap out before they reach the workspace's stated content types; native frameworks can hit it but only by re-importing a webview anyway; the browser stack hits every requirement directly. The credible alternatives are not "abandon the browser" but "wrap a webview in a thinner host" (Tauri) or "drive the workspace from a panel-aware terminal" (Wave / Zellij with plugins) — each carries trade-offs documented below.

## Mechanisms surveyed

### Browser (local server + browser client) — baseline

A local web server (e.g., FastAPI / Express / Hono) serves a SPA into the user's existing browser; agent and frontend communicate via WebSocket / SSE; panels are React (or Vue / Svelte) components managed by a tiling layout library.

Tiling layout libraries with established adoption:

- **react-mosaic** — i3-style tiling, drag-to-resize, drag-to-rearrange. ~48k weekly downloads, 4.7k GitHub stars. Layout serializes to a JSON tree — straightforward to persist. ([react-mosaic](https://github.com/nomcopter/react-mosaic))
- **dockview** — IDE-style docking with tabs, groups, grids, splitviews, floating panels, popout to new browser windows. Zero dependencies, supports React / Vue / Angular / vanilla. ([dockview](https://github.com/mathuo/dockview))
- **golden-layout** — older, ~14.7k weekly downloads, established in trading / dashboarding apps.
- **react-grid-layout** — grid-based rather than tree-based; simpler for fixed grid dashboards but weaker for free-form tiling.

Capability ceiling is effectively the modern web platform: terminals via xterm.js, editors via Monaco / CodeMirror, canvases via Konva / Fabric / tldraw / Excalidraw / native `<canvas>`, PDFs via PDF.js, tables via AG Grid / TanStack Table, video / audio natively. Self-host is trivial (it's a local process). WSL reach is the standard "expose a port, browser on Windows side hits localhost via WSL forwarding" — works out of the box on WSL2.

Real precedent for agent-driven multi-panel browser apps: **Jupyter Lab** (panel-tiled, kernel-as-agent, live state-sync), **VS Code for the Web**, **Theia**. Multi-panel browser-served apps are the most common shape for this category.

### Native desktop frameworks

#### Electron

Chromium + Node bundled. Mature, ~80–200 MB bundles, 120 MB+ RAM, decade of production use. Tiling is solved by re-importing the same React libraries listed above; Electron just hosts the renderer process. Agent-as-participant works via IPC between main and renderer plus the same WebSocket/MCP plumbing. ([Tauri vs Electron 2026](https://tech-insider.org/tauri-vs-electron-2026/))

Real examples: VS Code, Discord, Slack, Notion. Proven at scale for everything we'd want. The cost is bundle size and resource use; the gain over a browser tab is OS-window integration (menu bar, dock, file associations, transparent / decorated chrome).

#### Tauri

Rust core + the system's native webview (WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux). 600 KB to ~10 MB bundles, ~50 MB RAM, ~96% smaller than equivalent Electron apps. Production apps include Hoppscotch, Spacedrive, Padloc, AppFlowy. ([Tauri vs Electron 2026](https://www.pkgpulse.com/blog/electron-vs-tauri-2026); [tauri.app](https://tauri.app/))

Multi-window is a first-class feature via `WebviewWindowBuilder`. Multi-webview within a single window — the shape we'd actually want for tiled panels — landed in Tauri 2 via the unstable `add_child(webview_builder, position, size)` API; an example exists at [tauri-apps/tauri/tree/dev/examples/multiwebview](https://github.com/tauri-apps/tauri/issues/2975). The "unstable" tag matters: API churn is a real risk if we adopt it now, and the underlying shape (one webview per panel rather than one webview managing tiling) means each panel runs a separate process — heavier than tiling inside one webview.

WSL reach: Tauri builds Windows and Linux binaries; under WSL the Linux binary runs in WSLg (works for GUI), but cross-platform packaging from a single host is still less seamless than pure-browser. For this project's WSL-first workflow, building inside WSL targets Linux comfortably; a Windows companion build adds CI complexity.

Lock-in: Rust + system webview means JavaScript libraries written for Chromium quirks may misbehave on WebKitGTK and WebView2. Real-world friction shows up most often on cutting-edge CSS, WebGL nuances, and audio/video codec gaps.

#### Wails

Go core + system webview, similar architecture to Tauri. Smaller community than Tauri; chosen mainly when the team is Go-native. No specific advantage over Tauri for this project unless Go is preferred over Rust.

#### Native UI (Cocoa/Swift, GTK, Qt, JUCE)

True native widget toolkits. Tiling is achievable but the panel content types we need (canvas drawing, PDF rendering, modern editor) almost always end up embedding a webview anyway — at which point we've reproduced Electron / Tauri the hard way. Cross-platform from WSL is also weakest here. Not recommended for this design.

#### Compose Multiplatform (Kotlin), Flutter Desktop

Single codebase to multiple platforms; canvas-rich, native rendering. Both can render rich panels, but neither has a strong story for embedded terminals or PDF viewers — they'd require platform-channel bridges to existing native renderers. Capability ceiling is high but with substantial integration cost. Better fit for graphical apps than for the heterogeneous-panel workspace we want.

### TUI / terminal frameworks

#### Textual (Python)

"Rapid Application Development framework for Python" with grid + flexbox-style layouts, DOM-style queries, and the ability to run apps in a terminal *or* in a web browser via `textual serve`. Real apps include **Toad** (terminal frontend for AI coding tools), **Posting** (API client), **Toolong** (log viewer), **Memray** (Bloomberg memory profiler), **Dolphie** (MySQL dashboard), **Harlequin** (SQL client). ([textual.textualize.io](https://textual.textualize.io/))

Capability ceiling is the binding constraint: Textual can render Markdown via `MarkdownViewer`, formatted text, tables, and Rich-based content. Image and PDF rendering are not first-class — they depend on terminal-level image protocols (Kitty, iTerm2, Sixel) which work in *some* terminals on *some* platforms. A *drawable canvas* in the conversational sense (free-form vector / pixel surface the user and agent both edit) is not a Textual concept. Embedded terminal panes — i.e., another shell running inside a Textual app — are not part of the framework.

For an agent-workspace whose stated content types include canvases and PDFs, Textual hits a hard ceiling.

#### Bubble Tea (Go)

Elm-architecture TUI framework, ~42k stars, ~18k applications. Production users include Microsoft Azure (Aztify), AWS (eks-node-viewer), CockroachDB, Ubuntu, NVIDIA. The Charm ecosystem (lipgloss styling, bubbles components, harmonica animation) is rich. The closest existing AI/LLM work is **Mods** — a CLI for piping shell output through an LLM — not a multi-panel agent workspace. ([Bubble Tea](https://github.com/charmbracelet/bubbletea))

Same content-ceiling constraint as Textual: it's a terminal framework, so canvases and PDFs are out of scope.

#### ratatui (Rust)

Constraint-based responsive layouts, used by Netflix, OpenAI, AWS, Vercel, Hugging Face for internal tooling. Notable apps: binsider, csvlens, openapi-tui, oxker. ([ratatui.rs](https://ratatui.rs/)) Strong layout primitives but the same ceiling on panel content types as Textual and Bubble Tea.

#### Ink (React for CLI), blessed (JS)

Ink lets developers write CLI UIs using React. Used by GitHub Copilot CLI, Gatsby's installer, and others. Rendering is character-cell only; same ceiling. blessed is older and less actively maintained; superseded in practice by Ink.

**TUI summary.** TUI frameworks are the right choice when the workspace is *terminal-shaped* (text, tables, light formatting). They are not the right choice when the workspace requires drawable canvases, PDFs, images, or other graphical content. The user's stated panel mix includes those — so TUI alone disqualifies on requirement 1 (mixed content types).

### Terminal multiplexers as panel hosts

#### tmux + control mode

tmux's `-C` flag puts it in control mode: a text protocol where external programs can issue commands and receive event streams (pane creation, output, resize). The protocol is stable and well-understood. ([tmux Control Mode](https://deepwiki.com/tmux/tmux/7.1-control-mode))

Real precedent for AI agents driving tmux:

- **Tmux Automation** — Rust-based MCP server exposing tmux as tools an LLM can call. ([Tmux Automation](https://mcpmarket.com/server/tmux-automation))
- **NTM (Named Tmux Manager)** — Python tool that "spawns, tiles, and coordinates multiple AI coding agents (Claude, Codex, Gemini) across tmux panes." ([Dicklesworthstone/ntm](https://github.com/Dicklesworthstone/ntm))
- **tmux-agents** — orchestration skill for controlling agent instances inside tmux panes.
- **cmux** — purpose-built "AI agent terminal" descended from tmux.

So: agent-driving-tmux is a known, exercised pattern. The constraint is the same content ceiling as TUI frameworks — every pane is a terminal; canvases and PDFs are not panel types. tmux is excellent for *terminal-shaped* multi-panel agent workspaces (multiple shells, multiple log streams, multiple agent instances), and disqualifying for *graphical-shaped* ones.

#### Zellij

Modern Rust-based multiplexer with a documented WebAssembly / WASI plugin system — plugins "function as first-class workspace components alongside terminal panes" and can render custom UIs, react to state changes, control Zellij. ([Zellij plugins](https://zellij.dev/documentation/plugins)) Layouts are declarative (KDL files) and persist by design. Rust is the only officially supported plugin language today; community work toward other WASM languages is in progress.

External-control story: less mature than tmux. Discussions show users asking how to send commands to specific panes from external processes; canonical socket / IPC documentation is thin compared to tmux's control mode.

Capability ceiling in plugins: still terminal-rendered (the plugin draws into a pane, which is a character grid). Same content ceiling.

#### Wave Terminal

Self-described as an "open-source AI-native terminal" with "screen splitting," inline graphical widgets ("stickers"), file previews (images, markdown, audio/video, HTML, CSVs), VSCode-like file editing, built-in browser pane, remote SSH / file management. ([Wave Terminal](https://www.waveterm.dev/))

The "AI-native" claim deserves caveats. The marketing landing page lists AI as a feature category but does not document agent-integration mechanics, supported models, or an SDK that an external Claude Code session could plug into. A `docs.waveterm.dev/features/wave-ai` URL returned 404 at fetch time — feature documentation is either unstable, moved, or not yet published. Wave is interesting *as a panel-aware terminal that can render images and viewers*, but treating its AI claim as production-ready integration is unsupported.

If the design adopts Wave, the practical pattern is "Claude Code runs in one Wave pane, opens new Wave panes via Wave's CLI / config, content panels are file previews of the working directory" — not "Wave is the agent host." That's a different, weaker integration than what the design contemplates.

#### Ghostty, WezTerm

Ghostty is a fast cross-platform terminal (Zig). WezTerm is Lua-scriptable and has a documented protocol for spawning panes / tabs from external scripts. Both are excellent terminals; neither is a *panel host for non-terminal content*. Same ceiling.

### IDE-as-host

#### VS Code extension

The webview API lets extensions create webview panels with arbitrary HTML / JS / CSS, placed in editor columns (`ViewColumn.One`, `Two`, `Three`, …) with bidirectional `postMessage` between extension and webview. ([VS Code webview](https://code.visualstudio.com/api/extension-guides/webview))

Tiling caveat: webview panels appear "as distinct editors" — VS Code manages tab and column placement, not custom drag-to-resize tiling within an editor area. For an *IDE-style* tiled workspace this is fine; for a *fully user-controlled freeform tiling layout* it is constrained by VS Code's window-management model.

Capability ceiling is excellent — webviews are full Chromium views, so any content type the browser supports renders. Self-host fit: VS Code is the host, and the extension runs locally. WSL reach is exceptional — VS Code's Remote-WSL extension is the canonical way many users *already* drive Claude Code from WSL.

Agent precedent: Claude Code itself ships VS Code integration. The MCP ecosystem is fluent in VS Code as a host. Layout persistence is partial — VS Code persists workbench layout, but custom webview-panel arrangements are managed by the extension.

Lock-in is real. The extension is a VS Code-only artifact. Users not on VS Code lose the workspace.

#### JetBrains plugin

Tool windows + Swing / IntelliJ Platform UI. JetBrains has a webview shim (JCEF) but it is heavier and less ubiquitous than VS Code's. Smaller agent-integration ecosystem. Strong fit for users already in JetBrains; less broadly applicable than VS Code.

#### Zed

Rust-based, fast editor with extensions written in Rust compiled to WebAssembly via WIT (WebAssembly Interface Types). ([Zed extensions](https://zed.dev/docs/extensions); [Life of a Zed Extension](https://zed.dev/blog/zed-decoded-extensions)) Extension surface today: language extensions, debugger extensions, themes, snippets, **agent server extensions**, **MCP server extensions**. MCP integration is via Zed's Agent Panel; servers register through `extension.toml` and a `context_server_command` method.

The decisive limitation for our use: "In the future, we plan on increasing the extension surface to allow you to customize Zed's UI and more." — meaning custom UI panels and views are *not yet supported*. Today, Zed extensions can wire MCP servers and language tooling but cannot create the tiled panel UI the workspace requires. ([Zed MCP extensions](https://zed.dev/docs/extensions/mcp-extensions))

### Hybrid (backend + multiple frontends)

Most of the mechanisms above are frontend strategies; the backend (the part Claude Code talks to) can be the same regardless. A clean architecture is: a local server exposing an MCP transport plus a panel-state API; multiple frontend types (browser, Tauri webview, VS Code extension, even a TUI for terminal-only sessions) each subscribing to the same state. Jupyter's protocol ecosystem (server + multiple clients: Lab, Notebook, VS Code, console) is the canonical proof this shape works.

### Specialty

PWA (progressive web app) installs the browser frontend as a standalone app. No new capability; it's a packaging detail. Mobile remote and AR/VR are out of scope for the working-directory-tied, WSL-reachable use case stated.

## Comparison table

| Mechanism | Effort | Capability ceiling | Self-host | WSL reach | Real examples | Agent precedent | Fit |
|---|---|---|---|---|---|---|---|
| Browser (local server + react-mosaic / dockview) | Medium | Highest — full web platform | Native | Native | Jupyter Lab, Theia, VS Code Web | Jupyter kernel, OpenInterpreter, every browser-based agent UI | **A** |
| Electron | Medium-large | Same as browser + OS integration | Native | Good (Linux build under WSLg) | VS Code, Discord, Slack, Notion | Cursor, many AI desktop apps | **B+** |
| Tauri | Medium-large | High; webview-quirk caveats | Native | Good (Linux + Windows builds) | Hoppscotch, Spacedrive, AppFlowy | Smaller ecosystem; multi-webview API still unstable | **B** |
| Wails (Go) | Medium | Same as Tauri | Native | Good | Smaller ecosystem | Minimal | C |
| Native UI (Qt, GTK, Cocoa) | Large | High but webview re-imported in practice | Native | Mixed (GTK fine, Qt fine, Cocoa not on WSL) | Many; not agent-shaped | Minimal | C- |
| Compose / Flutter Desktop | Medium-large | High graphical, weak on terminal/PDF | Native | Mixed | Few in this shape | Minimal | C |
| Textual | Small-medium | **Capped** — no canvas, no PDF, no embedded terminals | Native | Native | Toad, Posting, Toolong, Memray, Harlequin | Toad (frontend for AI coding tools) | C (disqualifies on content) |
| Bubble Tea | Small-medium | **Capped** — same | Native | Native | Mods, eks-node-viewer, Aztify | Mods (CLI LLM) | C (disqualifies on content) |
| ratatui | Small-medium | **Capped** — same | Native | Native | binsider, csvlens, oxker | Internal tools at OpenAI/Netflix | C (disqualifies on content) |
| Ink | Small | **Capped** — same | Native | Native | Copilot CLI, Gatsby installer | Copilot CLI | C (disqualifies on content) |
| tmux + control mode | Small (existing tmux) + medium (agent layer) | **Capped** — terminal panes only | Native | Native | tmux-agents, NTM, cmux, Tmux Automation MCP | Strong (multiple production agent systems) | C for graphical workspace; **A** for terminal-only workspace |
| Zellij + plugins | Medium | **Capped** — terminal panes only | Native | Native | Zellij plugin ecosystem (small) | Minimal | C for graphical; B for terminal-only |
| Wave Terminal | Small (consume) — large (extend) | Higher than pure TUI (images, file previews); unclear for canvases | Native | Native (Linux build) | Wave's own demos | "AI-native" claim unverified at doc level | C+ (interesting, under-documented) |
| Ghostty / WezTerm | Small | **Capped** — terminal panes only | Native | Native | Many | Minimal as agent host | C |
| VS Code extension | Medium | High — webview panels | Native (VS Code is local) | Excellent (Remote-WSL is canonical) | Cursor, GitHub Copilot Chat, Continue, many | Strong | **A-** (VS Code lock-in) |
| JetBrains plugin | Medium-large | Medium — JCEF webview is heavier | Native | Good | JetBrains AI Assistant | Smaller ecosystem | C+ |
| Zed extension | Small (MCP) — blocked (UI panels) | **Currently capped** at no custom UI | Native | Good | OpenCode, MCP server extensions | MCP-only today | C until UI extension lands |
| Hybrid (server + multiple frontends) | Medium-large (one extra layer) | Inherits from chosen frontend | Native | Native | Jupyter ecosystem | Jupyter | **A** if multi-frontend is a real need |

Fit ratings: **A** = clears every requirement and has strong precedent; **B** = clears every requirement with caveats; **C** = blocks on at least one stated requirement.

## Recommended interface for our design

Two recommendations, in priority order. Both clear all six stated requirements; the difference is packaging and OS integration.

### 1. Browser (local server + tiling library) — recommended

The browser stack is the unique mechanism that clears every requirement *with no caveats*:

1. Tiled, dynamically arrangeable panels with mixed content — **react-mosaic** or **dockview**, plus xterm.js / Monaco / tldraw / PDF.js / AG Grid as panel implementations.
2. Agent-as-participant — the local server exposes panel operations as tools (open / close / focus / patch); Claude Code calls them via MCP; the server pushes state diffs to the frontend over WebSocket / SSE.
3. Self-hostable — a local Python or Node process, no cloud.
4. WSL reach — localhost port forwarding is automatic on WSL2; the browser opens on the Windows side and hits the WSL-side server.
5. Layout persistence — react-mosaic and dockview both serialize to JSON; save to a `.workspace.json` in the project, reload on session start.
6. Live state-sync — WebSocket is the canonical pattern; precedent everywhere from Jupyter Lab to VS Code's web port.

Real precedent at workspace scale: Jupyter Lab (multiple kernels, multi-panel, file-backed), VS Code for the Web, Theia, Hex, Observable. Agent precedent: every browser-based AI tool.

Lock-in is the lowest of all options — the frontend is web standards; the backend is plain HTTP / WebSocket / MCP. Migrating to Tauri or Electron later is *re-using the same frontend code*, not rewriting.

Effort: medium. The novel work is the agent-side panel-orchestration tools and the panel implementations the design requires. The framing (server + tiled SPA) is well-trodden.

### 2. Tauri — recommended runner-up

Tauri reuses the entire web frontend (libraries, components, layout) and packages it as a native app with a system webview. The gain is OS integration — file associations, dock / taskbar presence, native menu bar, native window chrome — and a smaller resource footprint than Electron. The trade-offs:

- Multi-webview-in-one-window is still unstable in Tauri 2; one-webview-per-panel via separate windows is the stable path but loses the in-window tiling shape we want. The pragmatic Tauri shape is **one webview, web-based tiling inside it** — i.e., the same react-mosaic / dockview layer as the browser baseline. We get OS chrome but not multi-process panel isolation.
- WebKitGTK / WebView2 quirks: any time we lean on Chromium-specific behavior (some advanced Canvas / WebGL / codec features) we add a per-platform debugging tax.
- WSL packaging adds complexity. Building Linux binaries inside WSL is fine; producing matched Windows builds requires either a Windows host or cross-build CI.

Recommendation: build the browser baseline first — every line of frontend code is reusable in a Tauri shell later. Adopt Tauri only if and when OS integration becomes a stated requirement.

### When the recommendation flips

If the workspace's stated content types narrow to *terminal-shaped only* (multiple shells, log streams, agent instances, text-based dashboards), the recommendation reverses: **tmux + control mode + an MCP server** is the right answer. Real production-tier precedent exists (NTM, tmux-agents, Tmux Automation MCP), the install footprint is tiny, and WSL is the native habitat. The design's stated panel mix (canvases, PDFs, viewers) excludes this branch — but it is the correct answer for a different version of the problem and worth noting if the design later splits.

## Hybrid possibility

The cleanest forward path is a **headless backend + pluggable frontend**, even if only one frontend ships first. The architecture:

- **Backend** — a local process (Python or Node) holding the canonical panel state, exposing:
  - MCP server interface for Claude Code (panel CRUD, content read / write, layout save / load).
  - WebSocket / SSE event channel for any frontend that wants live state-sync.
  - HTTP REST for snapshot reads (debugging, scripting, screen-recording-style replays).
- **Frontends**, all consuming the same WebSocket protocol:
  - **Browser SPA** — react-mosaic / dockview tiling. Default frontend.
  - **Tauri shell** — the same SPA wrapped for OS integration. Optional, ships later.
  - **VS Code extension** — webview panels as views into the same state, for users who live in VS Code.
  - **TUI fallback** — Textual or ratatui app showing panel titles + simple text-rendering of text-shaped panels, for SSH-only or no-GUI sessions.

Each frontend is a viewer onto the same authoritative state; layout persistence lives in the backend (one source of truth); Claude Code talks only to the backend regardless of which frontend the user is in.

Cost: the backend needs to be designed *as a protocol* from the start, not as "the SPA's helper." That's a real upfront design step. Benefit: optionality — if WSL users prefer the browser, macOS users prefer Tauri, and VS Code users prefer the extension, the same backend serves all three without forking the agent integration.

Precedent: Jupyter is exactly this shape (one kernel protocol, many clients: Lab, Notebook, VS Code, IntelliJ, Emacs, terminal). It works.

## Pitfalls and lessons

- **Browser** — port collision in long-running dev sessions; CORS / CSP nuance for self-host; WebSocket reconnection logic is non-trivial when the agent and frontend lose sync; "browser was closed but the session is still alive" UX needs explicit handling.
- **Electron** — bundle bloat, RAM use, security defaults are permissive (must be locked down explicitly), auto-update infrastructure adds operational surface.
- **Tauri** — multi-webview API instability; WebKitGTK / WebView2 quirks; Rust learning curve if the team is JS-only; cross-platform packaging needs more CI than browser-only delivery.
- **Native UI (Qt/GTK/etc.)** — every modern panel content type re-introduces a webview anyway; cross-platform parity is hardest here; the team rebuilds capabilities the web platform already ships.
- **Compose / Flutter Desktop** — embedded terminal panes are hard; PDF rendering needs platform-channel bridges; great for graphical apps, weak for heterogeneous-content workspaces.
- **Textual / Bubble Tea / ratatui / Ink** — content ceiling is real and immovable; image rendering in terminals is per-terminal-emulator and per-OS; PDFs and freeform canvases are out of scope; great for terminal-shaped workspaces only.
- **tmux** — content ceiling same as TUI; control-mode protocol is text-based and chatty; race conditions when multiple agents drive the same session require careful sequencing.
- **Zellij** — plugin language is effectively Rust today; external-control / IPC story is less mature than tmux's control mode.
- **Wave Terminal** — "AI-native" marketing claim is not backed by documented integration mechanics at fetch time; treat as a panel-aware terminal, not as an agent host. The `docs.waveterm.dev/features/wave-ai` URL returned 404.
- **Ghostty / WezTerm** — terminals, not workspaces. WezTerm's Lua scripting is powerful but doesn't change the content ceiling.
- **VS Code extension** — "panels appear as distinct editors" — VS Code, not the extension, controls tile arrangement; users not on VS Code lose the workspace; webview lifecycle is fiddly (panels disposed when tabs close unless explicitly retained).
- **JetBrains plugin** — JCEF (embedded Chromium) is heavier than VS Code webviews; smaller agent ecosystem; users not on JetBrains lose the workspace.
- **Zed** — extensions cannot create custom UI panels yet; MCP-only integration today; promising once UI extension lands.

## Gaps and open questions

- **Confirm panel content list.** The recommendation hinges on whether the workspace genuinely needs canvases, PDFs, and embedded viewers, or whether the stated panel types could narrow to text-shaped surfaces. A narrow scope flips the recommendation toward tmux + MCP and dramatically reduces effort. Worth an explicit "does the workspace need to render a PDF?" question before committing.
- **Layout-persistence shape.** Per-project (`.workspace.json` in the working directory) vs. per-user (`~/.config/agent-workspace/layouts/<project>.json`) is a design choice with downstream implications for portability, sharing, and conflict-resolution between concurrent sessions in the same directory.
- **Multi-session collision.** Two Claude Code sessions in the same working directory both opening panels — does the workspace serialize, fork, or refuse? Needs a designed answer before the implementation can serialize state cleanly.
- **State authority for collaboration surfaces.** When user and agent both edit the same panel (e.g., a shared canvas), conflict-resolution shape (CRDT, OT, last-write-wins, lock-on-edit) is undecided. Tldraw and Excalidraw both ship CRDT-based collaboration primitives — worth surveying before designing from scratch.
- **Tauri's multi-webview stability timeline.** "Unstable" in Tauri 2 is the blocker for adopting Tauri-native multi-webview tiling. Worth tracking for next-pass evaluation.
- **Wave Terminal's actual integration surface.** Wave's "AI-native" framing implies an SDK or extension API; the public docs don't make this discoverable. A direct conversation with the project (or deep dive into the source) would resolve whether Wave is a credible host or a passive panel-aware terminal.
- **Zed's UI extension roadmap.** Zed is the most architecturally promising IDE host (Rust core, WASM extensions, MCP-native), but UI extension is on a future-roadmap label. If the timeline is "this year" the recommendation could shift; if "eventually" it stays browser-first.

## Sources

- [react-mosaic (GitHub)](https://github.com/nomcopter/react-mosaic)
- [dockview (GitHub)](https://github.com/mathuo/dockview)
- [react-mosaic (homepage)](https://nomcopter.github.io/react-mosaic/)
- [npm trends — golden-layout / rc-dock / react-grid-layout / react-mosaic](https://npmtrends.com/golden-layout-vs-rc-dock-vs-react-grid-layout-vs-react-mosaic-component-vs-react-stonecutter)
- [Tauri (homepage)](https://tauri.app/)
- [Tauri 2 — window customization](https://v2.tauri.app/learn/window-customization/)
- [Tauri issue #2975 — multiple webviews in one window](https://github.com/tauri-apps/tauri/issues/2975)
- [Tauri vs Electron (PkgPulse, 2026)](https://www.pkgpulse.com/blog/electron-vs-tauri-2026)
- [Tauri vs Electron (tech-insider, 2026)](https://tech-insider.org/tauri-vs-electron-2026/)
- [Textual (homepage)](https://textual.textualize.io/)
- [Bubble Tea (GitHub)](https://github.com/charmbracelet/bubbletea)
- [ratatui (homepage)](https://ratatui.rs/)
- [Zellij plugins documentation](https://zellij.dev/documentation/plugins)
- [Zellij (homepage)](https://zellij.dev/)
- [Wave Terminal (homepage)](https://www.waveterm.dev/)
- [tmux Control Mode (DeepWiki)](https://deepwiki.com/tmux/tmux/7.1-control-mode)
- [Tmux Automation MCP](https://mcpmarket.com/server/tmux-automation)
- [NTM — Named Tmux Manager](https://github.com/Dicklesworthstone/ntm)
- [VS Code Webview API guide](https://code.visualstudio.com/api/extension-guides/webview)
- [Zed Extensions](https://zed.dev/docs/extensions)
- [Zed MCP Server Extensions](https://zed.dev/docs/extensions/mcp-extensions)
- [Life of a Zed Extension (Zed blog)](https://zed.dev/blog/zed-decoded-extensions)
