# MCP Context Resources — Index

## What this directory is

Authoritative reference sources for **how to build MCP (Model Context Protocol) servers**. Each file captures one source (spec, SDK doc, framework doc, host integration doc, registry, awesome list, or community best-practice writeup) with a standard template: identification, scope, takeaway summary, use-for questions it answers, relationship to peers, and quality notes.

## Capture date and regeneration

All resource files in this directory were captured between 2026-04-20 and 2026-04-21. Spec, SDK, and host-integration docs drift materially over quarters — before citing a specific prescription from any file here, verify the corresponding upstream source hasn't changed. Regenerate individual files (or the whole set) if the underlying docs have moved on.

## How this differs from `../repos/`

- **`../repos/`** describes **individual MCP servers** — concrete implementations whose code and structure illustrate how a server gets built.
- **`./context-resources/`** (this dir) describes **sources that inform how to build** — normative specs, SDK documentation, framework guides, host integration pages, registries, curated lists, and community best-practice writeups.

Use `../repos/` when you want to look at a working example. Use this directory when you want to know what the spec says, which SDK to pick, how a host integrates, where to publish, or what patterns the community has settled on.

## Grouped listing

### Spec and official docs

- `mcp-specification.md` — Normative protocol spec (JSON-RPC 2.0, capabilities, security MUST/SHOULD/MAY).
- `modelcontextprotocol-io-home.md` — The docs-site front page and concept primer; start here for newcomers.
- `mcp-build-server-tutorial.md` — Multi-language hello-world (weather server) tutorial.
- `mcp-authorization-tutorial.md` — End-to-end OAuth 2.1 + PRM / DCR / PKCE with Keycloak and TS/Python/C# worked examples.

### Official SDKs

- `python-sdk-readme.md` — Python SDK, FastMCP absorbed layer, OAuth resource-server patterns.
- `typescript-sdk-readme.md` — TS SDK for Node/Bun/Deno; v1.x vs v2 transition.
- `go-sdk-readme.md` — Go SDK, GA, Anthropic+Google co-maintained.
- `rust-sdk-readme.md` — Rust `rmcp` crate with proc macros.
- `kotlin-sdk-readme.md` — Kotlin Multiplatform (JVM/Native/JS/Wasm), widest transport matrix including WebSocket.

### Frameworks and reference code

- `fastmcp-readme.md` — The most-adopted Python MCP framework (standalone v2/v3 by jlowin/PrefectHQ).
- `fastmcp-docs.md` — FastMCP's full doc site (gofastmcp.com).
- `mcp-servers-monorepo.md` — Seven reference servers; use as pattern templates, not production drop-ins.
- `mcp-inspector.md` — Canonical debugging tool (UI + CLI modes).

### Claude Code plugin packaging

- `claude-code-plugins-reference.md` — `plugin.json`, `.mcp.json`, hooks, CLAUDE_PLUGIN_* variables, caching.
- `claude-code-plugin-marketplaces.md` — `marketplace.json`, plugin sources, release channels, seed dirs.
- `claude-code-mcp-docs.md` — `claude mcp add` CLI, local/project/user scopes.

### Host integration docs

- `claude-desktop-mcp-setup.md` — stdio-only local; `claude_desktop_config.json`.
- `cursor-mcp-docs.md` — `.cursor/mcp.json`; stdio/SSE/HTTP; OAuth with fixed callback URL.
- `vscode-mcp-docs.md` — `.vscode/mcp.json`; sandboxing on macOS/Linux; devcontainer integration.
- `windsurf-mcp-docs.md` — `~/.codeium/windsurf/mcp_config.json`; 100-tool cap; `${file:...}` interp.
- `zed-mcp-docs.md` — `context_servers` key (not `mcpServers`); runtime tool-list updates.
- `continue-mcp-docs.md` — `.continue/mcpServers/` drop-folder accepts other hosts' formats; agent-mode-only.
- `cline-mcp-docs.md` — `cline_mcp_settings.json`; `alwaysAllow` per-tool; auto-install-from-GitHub.
- `codex-cli-mcp-docs.md` — `config.toml` (TOML, not JSON); stdio + Streamable HTTP; `codex mcp login`.
- `warp-mcp-docs.md` — Auto-detects configs from Claude Code and Codex; env-scrubbed team sharing.
- `gemini-cli-mcp-docs.md` — `~/.gemini/settings.json`; Docker as a transport; default env sanitization.

### Registries

- `registry-official.md` — `modelcontextprotocol/registry`, community-governed, API v0.1 frozen.
- `registry-smithery.md` — Commercial registry + managed OAuth gateway; "largest open marketplace."
- `registry-glama-ai.md` — Commercial registry with security/ease-of-use ranking and API gateway.
- `registry-pulsemcp.md` — Community hub + weekly newsletter; operated by Steering Committee members.
- `registry-mcpservers-org.md` — Community directory, category-browsable.
- `registry-mcp-so.md` — Community directory; short memorable domain.

### Awesome lists

- `awesome-mcp-punkpeye.md` — 85k stars; most-cited, multi-language editions.
- `awesome-mcp-wong2.md` — Tiered (reference / official / community), ~500 servers.
- `awesome-mcp-appcypher.md` — 30+ emoji-tagged categories, explicit security warning.

### Community best-practice writeups

- `blog-15-best-practices-mcp-production.md` — Janakiram MSV synthesis (2025-09); production checklist.
- `blog-mcpcat-production-guide.md` — Workflow-oriented tool design, namespace conventions at scale.
- `blog-jlowin-fastmcp-middleware.md` — FastMCP 2.9 semantic-layer middleware (2025-06).
- `blog-jlowin-fastmcp-3.md` — FastMCP 3.0 Providers + Transforms architecture (2026-01).
- `blog-jlowin-stop-vibe-testing.md` — In-memory `Client` + pytest for deterministic MCP tests (2025-05).
- `blog-mauro-canuto-mcp-ts-production.md` — TypeScript production-ready lessons (ESM imports, `structuredContent`).
- `blog-simonw-mcp-prompt-injection.md` — Canonical prompt-injection / tool-poisoning threat piece (2025-04).
- `blog-elastic-mcp-attack-defense.md` — Elastic Security Labs four-category threat taxonomy (2025-09).

## Most authoritative for <topic>

- **Protocol questions** → `mcp-specification.md`
- **Python server ergonomics** → `fastmcp-docs.md` (and `fastmcp-readme.md` for the overview)
- **TypeScript servers** → `typescript-sdk-readme.md` and `blog-mauro-canuto-mcp-ts-production.md`
- **Remote-server OAuth** → `mcp-authorization-tutorial.md` (with `mcp-specification.md` for normative backing)
- **Testing strategy** → `blog-jlowin-stop-vibe-testing.md` → `fastmcp-docs.md` testing section
- **Debugging / smoke-testing** → `mcp-inspector.md`
- **Production-readiness checklist** → `blog-15-best-practices-mcp-production.md`
- **Threat model and attack vectors** → `blog-simonw-mcp-prompt-injection.md` → `blog-elastic-mcp-attack-defense.md`
- **Shipping via Claude Code** → `claude-code-plugins-reference.md` + `claude-code-plugin-marketplaces.md`
- **Wiring an MCP server into a specific host** → the matching `<host>-mcp-docs.md` file
- **Publishing a server for discovery** → `registry-official.md` first, then commercial registries as secondary channels
- **FastMCP 3.0 architecture (Providers + Transforms)** → `blog-jlowin-fastmcp-3.md`
- **Reference server implementations to study** → `mcp-servers-monorepo.md`
- **Quick "what is MCP?" orientation** → `modelcontextprotocol-io-home.md` → `mcp-build-server-tutorial.md`

## Notable gaps

Topics where authoritative guidance is thin or scattered across multiple incomplete sources:

- **Streaming large payloads / resources vs handles.** The 15-best-practices post touches on URI/handle returns but there is no authoritative pattern document. SDK examples mostly return inline strings.
- **Multi-tenant server design.** Authorization docs cover per-user auth; there is little guidance on running a single MCP server across many tenants with data isolation.
- **Session-scoped state and lifecycle management.** FastMCP 3.0 introduces it; other SDKs lag; no cross-SDK pattern reference.
- **Server-to-server orchestration.** MCP composition (one server proxying another) is partially covered by FastMCP's Providers + Transforms but is framework-specific. No protocol-layer pattern doc.
- **CI/CD patterns for MCP servers.** Testing docs exist; deployment patterns (blue/green, canary, per-tenant rollout) are largely absent from authoritative sources.
- **Elicitation (client-initiated user input) best practices.** Covered in the spec; very little practical guidance on when to use it, what UX to expect across hosts, or how it fares on hosts that haven't implemented it.
- **Resource subscription semantics in practice.** The spec covers `notifications/resources/updated` and `list_changed`; host support is uneven (Zed implements list-changed for tools; resource subscription adoption is less visible) and no single doc maps which host supports which notification.
- **Server observability beyond logs.** Guidance exists on structured logs with correlation IDs (15-best-practices) and OpenTelemetry (FastMCP 3.0 post); no consolidated "metrics that matter" source.
- **Security audit tooling.** Empirical vulnerability data exists (Elastic, Invariant Labs numbers) but there is no canonical scanner or pre-publish audit checklist an author can run.

Community best-practice coverage is strongest on the Python/FastMCP side (jlowin's blog is effectively a de-facto design-rationale archive), thinner on TypeScript, and mostly absent on Go/Rust/Kotlin outside the SDK READMEs.
