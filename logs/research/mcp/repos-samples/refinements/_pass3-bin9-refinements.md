# Pass 3 Refinements — Bin 9

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 9 samples. Samples were already in role-tree format from Pass 2; this pass verified alignment, scrubbed cross-corpus phrasings, restored the AGPL-3.0 license placement now that the consolidated path exists, and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — the AGPL-3.0 path proposed in Pass 2 was integrated into the consolidated as `Release and lifecycle > License — Copyleft (AGPL-3.0)`; `normaltusker--kotlin-mcp-server.md` now sits under that path)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Capability surface > Aggregator-tool catalog (many upstreams, normalized tool surface)` — `mukul975--cve-mcp-server.md` is a corpus-extreme case: 27 normalized tools dispatching across 21 independent upstream APIs, with each upstream's credentials independent (`Per-source independent API keys with graceful degradation`). The aggregator pattern co-occurs with per-source key optionality — when each upstream has its own credential and the surface is unified, missing keys produce graceful tool-level degradation rather than process failure. Existing description names per-upstream credentials as independent but doesn't surface graceful-degradation as a co-occurring design choice when the upstream count is high. Carried forward from Pass 2 unresolved.

- `Configuration delivery > Auto-generated host-config JSON files` — `normaltusker--kotlin-mcp-server.md` writes `mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json` from a single `install.py` covering Claude Desktop, VS Code, Cursor, and a generic MCP-client target. Sharpening: auto-generated host-config files often pair with a single installer script that walks the user through host selection — the installer becomes the documentation surface, and the generated files replace per-host README JSON snippets. The pattern fits installer-first distributions. Carried forward from Pass 2 unresolved.

- `Distribution channel > Hosted endpoint (no install)` — `neondatabase--mcp-server-neon.md` makes the hosted endpoint the *primary* distribution path with `mcp.neon.tech/mcp` as the canonical install instruction; local/npm install is positioned as developer-mode rather than user-mode. Sharpening: hosted endpoints can fully replace installable distribution when the vendor owns the runtime and can iterate without user redeploys; the local server becomes a developer artifact, not a user artifact. The README's role is then a single URL plus OAuth bootstrap instructions. Carried forward from Pass 2 unresolved.

- `Distribution channel > Multi-channel publication` — `openags--paper-search-mcp.md` is a clean reference case: PyPI (pip), uvx, Smithery, Docker, and source clone (5 channels) — language-native registry + zero-install runner + MCP-aware aggregator + container + clone. Sharpening: 5-channel publication shows up when the project deliberately pursues cross-audience reach. Carried forward from Pass 2 unresolved.

- `Build and packaging > Hatch force-include for monorepo wheel` — `pathintegral-institute--mcp.science.md` is a clean reference case for this path: the root `pyproject.toml` uses `hatchling.build` with a `force-include` directive that pulls `mcp_science/servers` into the wheel, enabling the dispatcher (single PyPI package) + per-server (subdirectory) monorepo shape. Sharpening: Hatch force-include is the build-system substrate that makes the `Repository layout > Monorepo with per-server subdirectories and one PyPI package` pattern work — the two paths co-occur as a design cluster. Carried forward from Pass 2 unresolved.

- `Capability surface > Capability gating flags (per-tool, per-category, write-mode)` — `opensearch-project--opensearch-mcp-server-py.md` exhibits *category-based* enable/disable as the gating unit (40-tool surface partitioned into categories: 9 core enabled by default, 10 additional analysis disabled by default, 21 search-relevance, 2 skills). Sharpening: capability gating sometimes operates at category granularity rather than individual-tool granularity — particularly when the tool count is high (40+) and tools cluster naturally into operator-meaningful groups. Default-on-vs-default-off per category lets operators reason at a higher abstraction than per-tool flags. Carried forward from Pass 2 unresolved.

- `Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline` — `mongodb-js--mongodb-mcp-server.md` adds a corpus instance where the RAG/retrieval pipeline is a *vendor docs* lookup integrated alongside the database tools (Assistant/KB search tools embed MongoDB documentation retrieval into the same server). Sharpening: embedded RAG can serve as documentation-lookup-as-tool, distinct from RAG-as-primary-capability — the docs/KB search rides alongside the operational tools so the agent can self-reference vendor documentation while operating against the database. Carried forward from Pass 2 unresolved.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every fact in this bin maps to an existing role)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`mongodb-js--mongodb-mcp-server.md` HTTP response modes vs transport paths.** The sample documents both SSE response mode and JSON response mode under the HTTP transport (`HTTP_HOST`, `HTTP_PORT` shared between them). Pass 3 retains separate `Streamable HTTP` and `SSE (Server-Sent Events)` paths under Transport since both response modes are documented MCP transport options, but the consolidated also has `HTTP with JSON response mode` as a distinct path — reconciler may want to clarify whether `HTTP with JSON response mode` and `Streamable HTTP` are genuinely distinct or whether the mongodb-js README's phrasing (JSON and SSE as response *modes* of the same HTTP transport) is the more accurate mental model. Carried forward from Pass 2 unresolved.

- **`normaltusker--kotlin-mcp-server.md` HTTP REST bridge dual placement.** The `vscode_bridge.py` HTTP REST bridge runs on port 8080 (configurable) for IDE-native integration — it's not the MCP transport, it's a parallel REST API alongside the MCP server. Placed under `Transport > REST API bridge alongside MCP` and again under `Entry point and launch > Multiple entry points per transport`. Reconciler should verify dual placement is intended — both seem applicable but the cross-role pairing is non-obvious. Carried forward from Pass 2 unresolved.

- **`neondatabase--mcp-server-neon.md` SDK / framework declaration ambiguity.** The sample notes Next.js App Router as hosting surface with MCP tool/handler logic under `mcp-src/`. The MCP SDK itself isn't named explicitly; placed under `Server runtime > Next.js (TypeScript) as MCP host`. The sample does not surface which underlying MCP SDK is wrapped (official TS SDK? bespoke?) — the gap is preserved without speculation. Carried forward from Pass 2 unresolved.

- **`mukul975--cve-mcp-server.md` SQLite TTL cache and security tier cross-role placement.** The sample exhibits both a `SQLite TTL cache` (under `Caching and rate-limiting infrastructure`) and a security test tier covering private-IP blocking and XML-bomb protection (under `Test stack > Stratified suite with unit + integration + cache + security tiers`). The defusedxml hardening also surfaces under `Safety and security posture > defusedxml for XML hardening`. Reconciler should verify the cross-role placement (test tier vs safety posture) is intended; the test-tier path appears to have been created based on this very sample, so the placement is tautological in a sense. Carried forward from Pass 2 unresolved.

- **`pathintegral-institute--mcp.science.md` server runtime declaration ambiguity.** The root `pyproject.toml` lists only `click>=8.2.1` (no MCP SDK at root); each sub-server in `servers/*/` carries its own SDK. Placed under `Server runtime > Python with hand-rolled MCP` — but the dispatcher *contains* sub-servers each using their own SDK. There is no consolidated path for "monorepo dispatcher with per-subserver runtimes." Reconciler may want to flag this as a structural sample-content gap or leave the placement as-is given the dispatcher itself has no MCP SDK and the sub-servers are out of scope of this sample. Carried forward from Pass 2 unresolved.

- **`openags--paper-search-mcp.md` `claude-code/` directory placement.** Placed under `Claude Code plugin / skill wrapper > claude-code/ directory with skill files` (existing path) — explicit skill-layer integration co-located with a generic MCP server. Distinct from `.claude/skills/ directory in repo` (the convention used by `neondatabase--mcp-server-neon.md`). Reconciler should verify the consolidated treats `claude-code/` and `.claude/skills/` as genuinely distinct paths. Carried forward from Pass 2 unresolved.

- **`mongodb-js--mongodb-mcp-server.md` multi-mechanism safety stack.** The sample exhibits five distinct safety mechanisms — `Read-only by default with explicit write flag` (`--readOnly`), `Destructive-tool elicitation list` (`CONFIRMATION_REQUIRED_TOOLS`), `Index-scan rejection` (`--indexCheck`), `Temporary-user lifecycle with TTL` (default 4h), and `Dry-run config dump` (`--dryRun`). Plus the cross-role `Capability surface > Destructive-tool elicitation list` placement (the same path appears under both Capability surface and Safety posture in the consolidated). Reconciler should verify that the cross-role pairing of `Destructive-tool elicitation list` under both Capability surface and Safety posture is intended. Carried forward from Pass 2 unresolved.

## Convergence assessment

The bin is **converged**. All sample level-2 and level-3 headings exactly match consolidated role/path names. Pass 3 changes were narrow:

- Restored `Release and lifecycle > License — Copyleft (AGPL-3.0)` to `normaltusker--kotlin-mcp-server.md` (Pass 2 omitted because the path didn't yet exist; the consolidated has integrated it).
- Scrubbed cross-corpus phrasings from five samples — `opensearch-project--opensearch-mcp-server-py.md` (three sites: "rarer than env-var-only in the MCP ecosystem", "notable absence", "characteristic of project-governed servers"), `pathintegral-institute--mcp.science.md` (one: "distinct from monorepos that ship one PyPI package per server (e.g., awslabs)"), `neondatabase--mcp-server-neon.md` (one: "contrasts with most MCP servers that test only at unit/integration levels"), `openags--paper-search-mcp.md` (one: "Unusual first-class plugin wrapper co-located with server"). Each replaced with self-describing prose that preserves the underlying fact.

No new paths needed beyond what Pass 2 already proposed (and Pass 2's AGPL-3.0 path is now integrated). The structural concerns above are all carry-forwards awaiting reconciler decisions; none are blocking. Pass 4 should not be required.
