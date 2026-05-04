# Pass 2 Refinements — Bin 9

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Release and lifecycle > License — Copyleft (AGPLv3)` — `normaltusker--kotlin-mcp-server.md` (AGPL-3.0) — Strong network-copyleft license, rare for MCP servers (most are MIT/Apache). Carries copyleft implications for hosts embedding the server. Distinct from `License — Permissive (MIT / Apache-2.0)` (no copyleft) and `License — Copyleft / non-commercial (CC BY-NC-SA)` (non-commercial restriction). Trade-off: signals derivatives must remain open, but does not block commercial use the way CC BY-NC-SA would. Note: bin 1 also proposed this exact path for `HenkDz--postgresql-mcp-server.md` — second cross-bin agreement strengthens the case.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Capability surface > Aggregator-tool catalog (many upstreams, normalized tool surface)` — `mukul975--cve-mcp-server.md` is a corpus-extreme case: 27 normalized tools dispatching across 21 independent upstream APIs, with each upstream's credentials independent (`Per-source independent API keys with graceful degradation`). The aggregator pattern co-occurs with per-source key optionality — when each upstream has its own credential and the surface is unified, missing keys produce graceful tool-level degradation rather than process failure. Existing description names per-upstream credentials as independent but doesn't surface graceful-degradation as a co-occurring design choice when the upstream count is high.

- `Configuration delivery > Auto-generated host-config JSON files` — `normaltusker--kotlin-mcp-server.md` writes `mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json` from a single `install.py` covering Claude Desktop, VS Code, Cursor, and a generic MCP-client target. Sharpening: auto-generated host-config files often pair with a single installer script that walks the user through host selection — the installer becomes the documentation surface, and the generated files replace per-host README JSON snippets. The pattern fits installer-first distributions.

- `Distribution channel > Hosted endpoint (no install)` — `neondatabase--mcp-server-neon.md` makes the hosted endpoint the *primary* distribution path with `mcp.neon.tech/mcp` as the canonical install instruction; local/npm install is positioned as developer-mode rather than user-mode. Sharpening: hosted endpoints can fully replace installable distribution when the vendor owns the runtime and can iterate without user redeploys; the local server becomes a developer artifact, not a user artifact. The README's role is then a single URL plus OAuth bootstrap instructions.

- `Distribution channel > Multi-channel publication` — `openags--paper-search-mcp.md` adds another corpus instance of broad multi-channel publication: PyPI (pip), uvx, Smithery, Docker, and source clone (5 channels) — same 5-channel pattern previously observed in `googleapis--mcp-toolbox` (per bin 6). The repeating pattern is "language-native registry + zero-install runner + MCP-aware aggregator + container + clone" — five channels covering five distinct install audiences with overlap. Sharpening: 5-channel publication recurs across distinct ecosystems (Python, Go) when the project deliberately pursues cross-audience reach.

- `Build and packaging > Hatch force-include for monorepo wheel` — `pathintegral-institute--mcp.science.md` is a clean reference case for this path: the root `pyproject.toml` uses `hatchling.build` with a `force-include` directive that pulls `mcp_science/servers` into the wheel, enabling the dispatcher (single PyPI package) + per-server (subdirectory) monorepo shape. Sharpening: Hatch force-include is the build-system substrate that makes the `Repository layout > Monorepo with per-server subdirectories and one PyPI package` pattern work — the two paths co-occur as a design cluster.

- `Capability surface > Capability gating flags (per-tool, per-category, write-mode)` — `opensearch-project--opensearch-mcp-server-py.md` exhibits *category-based* enable/disable as the gating unit (40-tool surface partitioned into categories: 9 core enabled by default, 10 additional analysis disabled by default, 21 search-relevance, 2 skills). Sharpening: capability gating sometimes operates at category granularity rather than individual-tool granularity — particularly when the tool count is high (40+) and tools cluster naturally into operator-meaningful groups. Default-on-vs-default-off per category lets operators reason at a higher abstraction than per-tool flags.

- `Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline` — `mongodb-js--mongodb-mcp-server.md` adds a corpus instance where the RAG/retrieval pipeline is a *vendor docs* lookup integrated alongside the database tools (Assistant/KB search tools embed MongoDB documentation retrieval into the same server). Sharpening: embedded RAG can serve as documentation-lookup-as-tool, distinct from RAG-as-primary-capability — the docs/KB search rides alongside the operational tools so the agent can self-reference vendor documentation while operating against the database.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`mongodb-js--mongodb-mcp-server.md` HTTP response modes.** The sample documents both SSE response mode and JSON response mode under the HTTP transport (`HTTP_HOST`, `HTTP_PORT` shared between them). I placed them as separate `Streamable HTTP` and `SSE (Server-Sent Events)` paths under Transport, since both response modes are documented MCP transport options. Reconciler may want to clarify whether `HTTP with JSON response mode` and `Streamable HTTP` are distinct paths — the consolidated has both `### HTTP with JSON response mode` and `### Streamable HTTP` as separate paths, but the mongodb-js README phrases JSON and SSE as response *modes* of the same HTTP transport rather than distinct transports.

- **`normaltusker--kotlin-mcp-server.md` AGPL-3.0 license placement.** Same issue as bin 1's `HenkDz--postgresql-mcp-server.md`. The consolidated only has Permissive and CC BY-NC-SA license paths — neither matches AGPL-3.0. I omitted the path from the sample's `Release and lifecycle` section rather than placing it under one that doesn't apply (the bin 1 approach was to place under CC BY-NC-SA with a flag; my approach is omission with a refinement-report entry). The refinement report formally proposes the new path. Reconciler should resolve before next pass; two cross-bin samples now support adding the AGPL-3.0 path.

- **`normaltusker--kotlin-mcp-server.md` HTTP REST bridge as transport vs entry point.** The `vscode_bridge.py` HTTP REST bridge runs on port 8080 (configurable) for IDE-native integration — it's not the MCP transport, it's a parallel REST API alongside the MCP server. I placed it under `Transport > REST API bridge alongside MCP` (the existing path explicitly designed for this case) and again under `Entry point and launch > Multiple entry points per transport` (since selecting the bridge means launching `vscode_bridge.py` rather than the main entry). Reconciler should verify dual placement is intended — both seem applicable.

- **`neondatabase--mcp-server-neon.md` SDK / framework declaration.** The sample notes Next.js App Router as hosting surface with MCP tool/handler logic under `mcp-src/`. The MCP SDK itself isn't named explicitly; I placed the server runtime under `Next.js (TypeScript) as MCP host` — the consolidated has this exact path. The sample does not surface which underlying MCP SDK is wrapped (official TS SDK? bespoke?) — the gap is preserved without speculation.

- **`mukul975--cve-mcp-server.md` SQLite TTL cache and security tier.** The sample exhibits both a `SQLite TTL cache` (existing path under `Caching and rate-limiting infrastructure`) and a security test tier covering private-IP blocking and XML-bomb protection. I placed the security test tier under `Test stack > Stratified suite with unit + integration + cache + security tiers` (existing path) — but this path was likely created based on `mukul975` itself in an earlier pass, so it's tautological. The defusedxml hardening also surfaces under `Safety and security posture > defusedxml for XML hardening` (existing path). Reconciler should verify the cross-role placement (test tier vs safety posture) is intended.

- **`pathintegral-institute--mcp.science.md` server runtime declaration ambiguity.** The root `pyproject.toml` lists only `click>=8.2.1` (no MCP SDK at root); each sub-server in `servers/*/` carries its own SDK. I placed the root entry under `Server runtime > Python with hand-rolled MCP` — but it's not strictly hand-rolled; the dispatcher *contains* sub-servers each using their own SDK. There is no consolidated path for "monorepo dispatcher with per-subserver runtimes." Reconciler may want to either flag this as a structural sample-content gap (it could fit `Multi-spec / multi-source composition` from Multi-tenancy, but that's about tenancy not runtime) or leave the placement as-is given the dispatcher itself has no MCP SDK and the sub-servers are out of scope of this sample.

- **`openags--paper-search-mcp.md` `claude-code/` directory placement.** Placed under `Claude Code plugin / skill wrapper > claude-code/ directory with skill files` (existing path) — explicit skill-layer integration co-located with a generic MCP server. Distinct from `.claude/skills/ directory in repo` (the convention used by `neondatabase--mcp-server-neon.md`). Reconciler should verify the consolidated treats `claude-code/` and `.claude/skills/` as genuinely distinct paths (they appear to be — one is a directory at repo root with skill files, the other is a `.claude/skills/` substructure aligned with Claude Code's standard layout).

- **`mongodb-js--mongodb-mcp-server.md` multiple safety paths.** The sample exhibits four distinct safety mechanisms — `Read-only by default with explicit write flag` (`--readOnly`), `Destructive-tool elicitation list` (`CONFIRMATION_REQUIRED_TOOLS`), `Index-scan rejection` (`--indexCheck`), `Temporary-user lifecycle with TTL` (default 4h), and `Dry-run config dump` (`--dryRun`). Plus the cross-role `Capability surface > Destructive-tool elicitation list` placement. Five-mechanism stack is unusual; reconciler should verify all paths exist in the consolidated (they do, per spot-check) and that the cross-role pairing of destructive-tool-elicitation-list under both Capability surface and Safety posture is the intended convention.
