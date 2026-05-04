# Sample

Stage-2 T3 merge of m3 (bins 5+11+13) + m6 (bin 9), 32 samples total.

## Identification

### Governance

Authorship and license signals correlate with project shape.

- Vendor-authored servers ship under permissive licenses (Apache-2.0, MIT) and track product releases [`mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `neondatabase--mcp-server-neon`]
- Project-governed (not single-vendor) — Apache-2.0, formal `DEVELOPER_GUIDE.md` + `USER_GUIDE.md` split [`opensearch-project--opensearch-mcp-server-py`]; academic monorepo with `CITATION.cff` metadata and GitHub Pages site [`pathintegral-institute--mcp.science`]
- Community single-maintainer aggregator — MIT, 27 tools across 21 upstream APIs [`mukul975--cve-mcp-server`]
- AGPL-3.0 is uncommon in the MCP corpus — only single-maintainer dev-assistant project [`normaltusker--kotlin-mcp-server`]

### Star-count band (m6 bin)

Bin spans low-tens to ~1.2K stars: 28 [`normaltusker--kotlin-mcp-server`], 120 [`opensearch-project--opensearch-mcp-server-py`], 128 [`pathintegral-institute--mcp.science`], 257 [`mukul975--cve-mcp-server`], 468 [`motherduckdb--mcp-server-motherduck`], 587 [`neondatabase--mcp-server-neon`], ~1000 [`mongodb-js--mongodb-mcp-server`], ~1200 [`openags--paper-search-mcp`].

### Activity / freshness

- Active vendor releases — MongoDB v1.10.0 April 2026 [`mongodb-js--mongodb-mcp-server`], MotherDuck v1.0.4 March 2026 [`motherduckdb--mcp-server-motherduck`], OpenSearch v0.9.0 March 2026 [`opensearch-project--opensearch-mcp-server-py`], CVE v0.1.0 April 2026 [`mukul975--cve-mcp-server`]
- Possibly dormant — last release v0.2.0 July 2025; sample flags slow maintenance [`pathintegral-institute--mcp.science`]
- Last-commit not surfaced [`neondatabase--mcp-server-neon`, `openags--paper-search-mcp`, `normaltusker--kotlin-mcp-server`]

### Naming-vs-implementation mismatch

- Repo name suggests Kotlin but the server is a Python monolith (`kotlin_mcp_server.py`) — filename heuristics break for this entry [`normaltusker--kotlin-mcp-server`]
- Name "puppeteer-py" reflects user-facing concept; implementation actually wraps Playwright [`twolven--mcp-server-puppeteer-py`]

### Vendor relationship

- First-party (vendor publishes their own MCP) — Slack-hosted remote MCP at `mcp.slack.com` published under `slackapi/` org [`slackapi--slack-mcp-plugin`]
- Third-party canonical (vendor has no MCP; community fills the gap) — DaVinci Resolve has no first-party MCP; this third-party server is effectively canonical for the 833-star community [`samuelgursky--davinci-resolve-mcp`]
- Unofficial vs official competing implementations — `executeautomation--mcp-playwright` (5.5k stars, unofficial) coexists with Microsoft's `@playwright/mcp`. "Both ship, neither is officially crowned" — competitive landscape axis

### Server-as-product vs configs-as-product

Cross-cutting axis surfaced by `slackapi--slack-mcp-plugin` and discriminating most other samples.

- Server-as-product — repo contains the implementation, packaging, tests, and distribution for a runnable server (most samples)
- Configs-as-product — repo contains only configs and skills/commands for client hosts; the MCP server itself is a remote HTTP endpoint operated separately. License may not be specified because the repo holds no implementation [`slackapi--slack-mcp-plugin`]

## Language and runtime

Implementation language is the first-order divergence; everything else (SDK choice, packaging, distribution) follows.

### Python

Python is the dominant language across all four bins.

#### Python version floor

- Python 3.8+ — legacy/`setup.py`-era servers [`twolven--mcp-server-puppeteer-py`]; broad inclusive floor with 3.9+ recommended, black `target-version = py38-py312` [`normaltusker--kotlin-mcp-server`]
- Python 3.10+ — common modern mainstream floor [`duolingo--slack-mcp` (`requires-python = ">=3.10"`, Dockerfile uses `python:3.11-slim` base), `motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server` (3.10+ with 3.11/3.12 recommended), `openags--paper-search-mcp` (3.10–3.13), `pathintegral-institute--mcp.science`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Python 3.10–3.12 inclusive upper bound — driven by an external ABI dependency (DaVinci Resolve's Python scripting module is incompatible with 3.13+) [`samuelgursky--davinci-resolve-mcp`]
- Python 3.11+ — slightly raised floor [`designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos`]
- Python 3.12+ — `requires-python = ">=3.12"` [`sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Python 3.13+ — aggressive cutting-edge floor on a popular production server (287 stars); flagged as uncommon [`voska--hass-mcp`]
- Pinned via `.python-version` only — no explicit `requires-python` surfaced [`sajal2692--mcp-weaviate`, `shreyaskarnik--huggingface-mcp-server`]
- Not surfaced — README and packaging do not state a floor [`shibuiwilliam--mcp-server-scikit-learn`, `opensearch-project--opensearch-mcp-server-py`]

> The 3.11 floor is observed as "a touch more modern than awslabs' 3.10" [`echelon-ai-labs--servicenow-mcp`]. No Python <3.10 observed in bins 5/11; `twolven--mcp-server-puppeteer-py` (3.8+) and `normaltusker--kotlin-mcp-server` (3.8+) are the pre-3.10 outliers. Pitfall: a CI matrix that tests Python versions below `requires-python` is a self-inconsistency — `sandraschi--email-mcp` declares `requires-python = ">=3.12"` but tests 3.10/3.11/3.12 in CI.

### TypeScript / Node.js

- Node.js >=18.0.0 — `exa-labs--exa-mcp-server` (TypeScript 97.9%)
- Node.js 22+ — `docker--hub-mcp` (TypeScript 99.8%)
- Node.js (npx/npm-based) — `executeautomation--mcp-playwright` (TypeScript 93.6%); specific Node version not pinned in README
- Node 16.x+ floor — `v-3--discordmcp` (Pure TypeScript with MCP TypeScript SDK)
- Node `>=20.19.0` or `22.12.0+` or `23+` (specific point releases pinned) — `mongodb-js--mongodb-mcp-server` (TS 98.6%)
- Node v18+ for prod, v22+ for dev — `neondatabase--mcp-server-neon` (TS 97.5%, JS 2.2%)
- TypeScript 91% + JavaScript 8.5%, monorepo with pnpm workspaces — `upstash--context7`

### Rust

- Rust 2024 edition — `elastic--mcp-server-elasticsearch` (Rust 94.3%); exact Rust version not specified in `Cargo.toml`, only edition. A rare axis value across the corpus
- Rust toolchain pinned via `rust-toolchain.toml` — `rust-mcp-stack--rust-mcp-filesystem` (uses `rust-mcp-sdk` + `rust-mcp-schema`)

### Go

- Go MCP SDK with no explicit version constraint specified [`viant--mcp`]
- JSON-RPC 2.0 communication base explicitly named [`viant--mcp`]

### Mixed-language codebase

- Python core with TypeScript companion (likely docs/UI) — Python 74% + TypeScript 22% + Nix 1% [`utensils--mcp-nixos`]
- Python primary plus Kotlin (3.5%) and TypeScript (1.7%) supporting components — server is Python despite the name [`normaltusker--kotlin-mcp-server`]

### Not applicable (remote-only)

- No local code; the repo ships configs only and the MCP server is a remote HTTP service [`slackapi--slack-mcp-plugin`]

## MCP framework / SDK variant

Framework choice diverges within each language family.

### Python SDKs

#### Raw `mcp` Python SDK / `mcp[cli]` (low-level, hand-authored schemas)

- `designcomputer--mysql_mcp_server` (`mcp>=1.0.0`), `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `opensearch-project--opensearch-mcp-server-py` (Anthropic Claude Agent SDK / raw MCP Python SDK), `samuelgursky--davinci-resolve-mcp` (presumed), `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`, `twolven--mcp-server-puppeteer-py`, `voska--hass-mcp`

#### FastMCP-only

- FastMCP (1.x or unspecified) — Pydantic-backed auto-derivation of tool schemas — `sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`
- FastMCP 2.x — `duolingo--slack-mcp` (`fastmcp>=2.13.0`), `mukul975--cve-mcp-server` (27 `@mcp.tool()` decorators in single `server.py`), `motherduckdb--mcp-server-motherduck` (`fastmcp>=2.14,<3` pinned with tight upper bound), `zilliztech--mcp-server-milvus` (`fastmcp >= 2.14.1`)
- FastMCP 3.x — `fastmcp>=3.1.0,<4` is the highest FastMCP floor seen [`sandraschi--email-mcp`]

#### Dual SDK (both `mcp` + `fastmcp` declared)

Notable rare pattern — most repos pick one.

- `openags--paper-search-mcp` — `mcp[cli]>=1.6.0` AND `fastmcp` (no version pin) — likely uses FastMCP for the server surface and `mcp[cli]` for dev/inspector tooling
- `normaltusker--kotlin-mcp-server` — `mcp>=1.0.0` (labeled "Official MCP SDK") AND `fastmcp>=2.0.0` in `requirements.txt`

#### Dispatcher (no top-level SDK at root)

- `pathintegral-institute--mcp.science` — root `pyproject.toml` lists only `click>=8.2.1`; per-server `pyproject.toml`s under `servers/*/` each declare their own SDK choice — root is a dispatcher

> For SSE transport in raw-SDK servers, Starlette is used directly rather than FastAPI [`echelon-ai-labs--servicenow-mcp`] — observed as a viable sub-FastAPI layer for MCP servers wanting HTTP transport without full REST framework overhead.

### TypeScript SDKs

- `@modelcontextprotocol/sdk` (typical for TS MCP) — `docker--hub-mcp` (likely), `executeautomation--mcp-playwright`, `v-3--discordmcp`
- MCP SDK ^1.12.1 with Zod validation and `jose` (JWT) — `exa-labs--exa-mcp-server`; also pulls in `exa-js ^2.8.0` for the underlying API
- Anthropic MCP TypeScript SDK + internal argument parser [`mongodb-js--mongodb-mcp-server`]
- Next.js App Router as hosting surface; MCP tool/handler logic under `mcp-src/` [`neondatabase--mcp-server-neon`]

### Rust SDKs

- `rmcp ^0.2.1` (Rust MCP SDK), `tokio` (async), `axum` (HTTP) — `elastic--mcp-server-elasticsearch`
- `rust-mcp-sdk` + `rust-mcp-schema` — `rust-mcp-stack--rust-mcp-filesystem`

### Go SDKs

- Go MCP SDK with full capability surface — tools, resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, elicitation [`viant--mcp`]

### Remote MCP (no local SDK)

- Protocol terminated server-side; clients connect via HTTP [`slackapi--slack-mcp-plugin`]

### MCP SDK version pinning practice

- Tight upper-bounded — `fastmcp>=2.14,<3` keeps breaking-change surface bounded [`motherduckdb--mcp-server-motherduck`]
- Older pin `mcp[cli]>=1.4.1` on a recent server — version drift from current SDK [`voska--hass-mcp`]
- Lower-bound only, no upper-bound [`zilliztech--mcp-server-milvus`]
- Loose / unpinned — `fastmcp` without version; potential fragility when upstream bumps majors [`openags--paper-search-mcp`]
- Dual-floor — `mcp>=1.0.0` + `fastmcp>=2.0.0` [`normaltusker--kotlin-mcp-server`]

## Transport

Transport surface is a key divergence axis. Two orthogonal questions: which transports supported, and how the choice is exposed.

### Supported transports

#### stdio only

- README explicitly frames as "stdio-based protocol server rather than standalone application" [`designcomputer--mysql_mcp_server`]
- Single-file Python script invoked by host [`twolven--mcp-server-puppeteer-py`]
- TypeScript bot wrapped via stdio to host [`v-3--discordmcp`]
- Docker-wrapped stdio [`voska--hass-mcp`]
- Outbound-HTTPS only, no inbound listener ports [`mukul975--cve-mcp-server`]
- stdio primary; selected at server invocation via `uvx` [`pathintegral-institute--mcp.science`]
- Stdio-only (default or by explicit selection) [`rust-mcp-stack--rust-mcp-filesystem` (inferred), `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]

#### HTTP only

- `duolingo--slack-mcp` (`http://localhost:8001/mcp`, port 8001)
- Remote MCP endpoint at a fixed URL [`slackapi--slack-mcp-plugin`]

#### HTTP + stdio

- CLI `--transport=http|stdio` [`docker--hub-mcp`]
- HTTP (remote endpoint) + stdio + HTTP local; default remote `https://mcp.exa.ai/mcp` [`exa-labs--exa-mcp-server`]
- stdio (default), HTTP with SSE or JSON response modes [`mongodb-js--mongodb-mcp-server`]
- stdio (default), HTTP [`motherduckdb--mcp-server-motherduck`]
- stdio default; HTTP indirectly via academic APIs the server consumes (not first-class MCP transport) [`openags--paper-search-mcp`]

#### stdio + SSE / HTTP/SSE / streamable-http

- Separate console scripts per transport [`echelon-ai-labs--servicenow-mcp`]
- stdio + streamable-HTTP (SSE deprecated) [`elastic--mcp-server-elasticsearch`]
- stdio + SSE + streamable-http (CLI `--transport`) [`feiskyer--mcp-kubernetes-server`]
- stdio (recommended) + HTTP/SSE — single binary; `--port` switches mode [`executeautomation--mcp-playwright`]
- stdio default + SSE option, separate JSON config blocks per mode [`zilliztech--mcp-server-milvus`]
- stdio + HTTP + Docker-wrapped, transport selected via env vars [`utensils--mcp-nixos`]
- Three modes in one binary — stdio, SSE, streamable-http [`opensearch-project--opensearch-mcp-server-py`]

#### stdio + streamable-http

- Multi-transport server with CLI/env selection [`sajal2692--mcp-weaviate`]

#### Multi-transport library (Go)

- HTTP/SSE + Streamable HTTP + Stdio, configured via functional options pattern (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`) and separate entry points (`stdioSrv.ListenAndServe()` / `srv.HTTP()`) [`viant--mcp`]

#### Remote-hosted Streamable HTTP primary

- `neondatabase--mcp-server-neon` — Streamable HTTP (`/mcp` endpoint) primary; SSE (`/sse`) deprecated/legacy. Endpoint-URL based selection: clients hit `/mcp` for streamable HTTP or `/sse` for legacy

#### Dual-protocol same process (rare)

- stdio MCP + HTTP REST bridge running in same process simultaneously; HTTP bridge enabled by default, making the server usable by non-MCP clients out of the box. Distinct from "pick a transport" — this is two protocols at once [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- MCP native + CLI + Skills (without MCP) + HTTP REST backend [`upstash--context7`]
- stdio MCP plus HTTP REST API bridge (`vscode_bridge.py`) on port 8080 (configurable). REST bridge is a separate process surface for IDE-native integration [`normaltusker--kotlin-mcp-server`]

### Transport selection mechanism

How the user picks a transport diverges sharply.

- Implicit / single-transport — [`designcomputer--mysql_mcp_server` (stdio only), `duolingo--slack-mcp` (HTTP only), `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`]
- CLI flag (`--transport`) — [`docker--hub-mcp`, `feiskyer--mcp-kubernetes-server`]
- CLI flag (`--port` switches stdio→HTTP) — `executeautomation--mcp-playwright` ("Dual-transport from one binary — `--port` switches between stdio and HTTP, not separate entry points")
- Docker arg / CLI positional (`stdio` vs `http`) — [`elastic--mcp-server-elasticsearch`]
- Separate console scripts per transport — `echelon-ai-labs--servicenow-mcp`: `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE). "Architecturally split rather than env-var-switched" — opposite of the one-binary multi-transport model
- Client config selects (default remote endpoint) — [`exa-labs--exa-mcp-server`, `motherduckdb--mcp-server-motherduck` (transport selected via Claude Desktop / VS Code settings)]
- CLI argument or env var — [`sajal2692--mcp-weaviate`, `mongodb-js--mongodb-mcp-server` (`TRANSPORT` env / `--transport`, plus `HTTP_HOST`, `HTTP_PORT`), `opensearch-project--opensearch-mcp-server-py`]
- HTTP URL configured at the client side [`slackapi--slack-mcp-plugin`]
- Environment variables — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP` [`utensils--mcp-nixos`]
- Env var toggle for secondary protocol — `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE` [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- CLI flag / env var with separate JSON configs per mode [`zilliztech--mcp-server-milvus`]
- Functional options at construction time (Go) [`viant--mcp`]
- Endpoint-URL based — different paths route to different transports [`neondatabase--mcp-server-neon`]
- Installation mode — entry point selection: portable, system, or module [`normaltusker--kotlin-mcp-server`]

> The transport-selection split (one binary with flag vs separate binaries per transport) is itself a design axis worth tracking.

### stdio hardening

- Explicit stdout/stderr isolation discipline — README emphasizes hardened stdout/stderr separation for JSON-RPC correctness; "zero-tolerance `print` policy" in core handlers to keep stdout clean [`sandraschi--email-mcp`]

### Stateless HTTP mode

- Explicit `MCP_NIXOS_STATELESS_HTTP` flag for shared/multi-user deployments [`utensils--mcp-nixos`]

## Distribution

How the server reaches end users. Multiple mechanisms commonly stack.

### Package managers

#### PyPI / pip

- PyPI publication — `designcomputer--mysql_mcp_server` (`mysql-mcp-server`), `feiskyer--mcp-kubernetes-server` (`mcp-kubernetes-server`), `motherduckdb--mcp-server-motherduck` (`mcp-server-motherduck`), `opensearch-project--opensearch-mcp-server-py` (pip only), `pathintegral-institute--mcp.science` (`mcp-science` namespace, dispatcher pattern), `utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`
- PyPI via `uvx` — primary one-liner install [`motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp` (uvx + `uv tool install`), `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `utensils--mcp-nixos` (`uvx mcp-nixos`), `voska--hass-mcp` (`uvx hass-mcp` alongside Docker), `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`uvx semantic-scholar-fastmcp`)]
- PyPI via `uv` (local install) [`severity1--terraform-cloud-mcp`]

#### npm / npx

- npm — `docker--hub-mcp` (npm-installable), `exa-labs--exa-mcp-server` (`exa-mcp-server`), `executeautomation--mcp-playwright` (`@executeautomation/playwright-mcp-server`), `mongodb-js--mongodb-mcp-server` (npm + npx + Docker `mongodb/mongodb-mcp-server:latest`), `neondatabase--mcp-server-neon` (npm/`npx` for local; `npx neonctl@latest init` for client auto-wiring; Cursor IDE install button)
- `npx ctx7 setup` (recommended, OAuth + API key automation) [`upstash--context7`]
- npm package wrapping a Rust binary — `@rustmcp/rust-mcp-filesystem` [`rust-mcp-stack--rust-mcp-filesystem`]

#### Cargo

- `cargo install rust-mcp-filesystem` [`rust-mcp-stack--rust-mcp-filesystem`]

#### Homebrew

- Homebrew formula [`rust-mcp-stack--rust-mcp-filesystem`]

#### Go modules

- `go get github.com/viant/mcp` for embedding library use [`viant--mcp`]

### Source-only / no package registry

- Source-only distribution [`duolingo--slack-mcp` ("Not published to PyPI; source-only distribution")]
- Source clone + editable install (`pip install -e .` from clone) [`echelon-ai-labs--servicenow-mcp`, `mukul975--cve-mcp-server`, `shibuiwilliam--mcp-server-scikit-learn`]
- Source clone + `uv sync` and run a script directly [`shreyaskarnik--huggingface-mcp-server`]
- Source-only with custom installer — no PyPI; bespoke `install.py` orchestrates venv and per-client config [`samuelgursky--davinci-resolve-mcp`, `normaltusker--kotlin-mcp-server` (`python3 install.py` interactive installer with 3 modes: portable / system / module; auto-generates IDE config files)]
- TypeScript `npm install` + `npm run build` with no npm publish [`v-3--discordmcp`]
- Python clone-only with `pip install -r requirements.txt` [`twolven--mcp-server-puppeteer-py`]
- Source tree + `uv run src/...` (rather than installed console script) [`zilliztech--mcp-server-milvus`]

### Container registries

- Generic Dockerfile in repo — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `executeautomation--mcp-playwright`, `mongodb-js--mongodb-mcp-server` (multi-stage + `deploy/` Azure guides), `openags--paper-search-mcp`, `rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`
- ghcr.io image published — `feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos` (`ghcr.io/utensils/mcp-nixos`)
- Vendor-specific registry — `elastic--mcp-server-elasticsearch` (`docker.elastic.co/mcp/elasticsearch`, distributed via AWS Marketplace and Elastic's container registry)
- Docker Hub MCP Registry presence [`rust-mcp-stack--rust-mcp-filesystem`, `voska--hass-mcp` (`voska/hass-mcp:latest` — primary channel; README leads with `docker pull`), `mongodb-js--mongodb-mcp-server`]

### Container-only / container-first distribution

- `elastic--mcp-server-elasticsearch` — Docker is the only shipping channel ("Container-first distribution")
- `duolingo--slack-mcp` — Docker primary (no PyPI); "Containerization as primary distribution (not Homebrew, npm, Cargo)"; "Inverts the typical Python packaging path"

### Aggregator / installer registries

- Smithery CLI install — `designcomputer--mysql_mcp_server` (`npx -y @smithery/cli install mysql-mcp-server --client claude`), `executeautomation--mcp-playwright`, `exa-labs--exa-mcp-server` (Smithery registry config `smithery.yaml`), `openags--paper-search-mcp` (`npx -y @smithery/cli install @openags/paper-search-mcp --client claude`), `shreyaskarnik--huggingface-mcp-server`
- mcp-get — `executeautomation--mcp-playwright`
- Pre-built IDE installers (one-click for Cursor / VS Code) — `exa-labs--exa-mcp-server`
- Native Claude Desktop connector (no manual config) — `exa-labs--exa-mcp-server`
- MCPB / `.mcpb` bundle (Claude Desktop drag-and-drop) [`sandraschi--email-mcp`, `motherduckdb--mcp-server-motherduck` (`.mcpbignore` file present, suggests MCP bundle packaging workflow)]
- Zed extension [`sandraschi--email-mcp`]

> `executeautomation--mcp-playwright` ships across four mechanisms (npm, mcp-get, Smithery, Docker) — flagged in-sample as "a reference for 'how many channels to publish to' decisions".

### Standalone binaries / installers

- Shell installer / PowerShell installer [`rust-mcp-stack--rust-mcp-filesystem`]
- GitHub release binary downloads [`rust-mcp-stack--rust-mcp-filesystem`, `motherduckdb--mcp-server-motherduck`]
- Standalone bridge binary distributed as alternative to embedding the Go library [`viant--mcp`]

### Declarative install (Nix-native)

- `nix run github:utensils/mcp-nixos` (uses Nix flake) [`utensils--mcp-nixos`]
- Nix flake + declarative NixOS / Home Manager module via nixpkgs entry — flagged as rare for MCP servers [`utensils--mcp-nixos`]

### Remote-hosted endpoint

- Remote MCP endpoint at `https://mcp.exa.ai/mcp` — clients connect to that URL rather than running a local process. Reduces setup friction. Vercel deployment config (`vercel.json`) supports the hosted variant [`exa-labs--exa-mcp-server`]
- `https://mcp.context7.com/mcp` — manual config option as alternative to local install [`upstash--context7`]
- Remote-hosted-only — no install at all; `git clone` is for config review only [`slackapi--slack-mcp-plugin`]
- `mcp.neon.tech` primary; OAuth flow; remote-first model rather than local-process default [`neondatabase--mcp-server-neon`]

### Cross-ecosystem distribution

- A single Rust binary shipped via Homebrew, Cargo, npm, Docker, GitHub releases, plus shell/PowerShell scripts — broadest distribution surface [`rust-mcp-stack--rust-mcp-filesystem`]

### Dispatcher / namespace pattern

- Single PyPI package (`mcp-science`) routes to multiple servers via CLI subcommand (`uvx mcp-science <server-name>`). Hatch `force-include` directive pulls `mcp_science/servers` into the wheel — custom monorepo build shape rather than workspace-based approach [`pathintegral-institute--mcp.science`]

### Distribution posture axis

- Source-only (clone + build) vs published package — TypeScript projects sometimes choose source-only [`v-3--discordmcp`]
- Published package vs hosted MCP endpoint — Context7 offers both [`upstash--context7`]
- Public client + private backend — Context7 keeps API/parsing/crawling engines private [`upstash--context7`]

## Entry point / launch

How the running process is started, after distribution lands the bits.

### Console script via `[project.scripts]`

- `mysql_mcp_server = "mysql_mcp_server:main"` [`designcomputer--mysql_mcp_server`]
- `slack-mcp = "main:main"` — module `main` at top level, no package, unusual [`duolingo--slack-mcp`]
- `mcp-server-milvus` [`zilliztech--mcp-server-milvus`]
- `mcp-server-motherduck = "mcp_server_motherduck:main"` [`motherduckdb--mcp-server-motherduck`]
- `hass-mcp` → `app.run:main` [`voska--hass-mcp`]
- `mcp-nixos` [`utensils--mcp-nixos`]
- `semantic-scholar-mcp-server` [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- `mongodb-mcp-server` — single npm bin [`mongodb-js--mongodb-mcp-server`]
- Dual scripts — `paper-search-mcp` (server) + `paper-search` (standalone CLI) sharing a core library [`openags--paper-search-mcp`]; entries: `paper_search_mcp.server:main`, `paper_search_mcp.cli:main`
- Console script — `uvx <name>` or `uv run <name>` [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Inferred but not surfaced [`opensearch-project--opensearch-mcp-server-py`]

### `python -m <module>`

- `python -m src.mcp_kubernetes_server.main` [`feiskyer--mcp-kubernetes-server`]
- `python -m cve_mcp.server` — no console script defined [`mukul975--cve-mcp-server`]
- Both `python -m servicenow_mcp.cli` (stdio) and console script `servicenow-mcp-sse` (SSE) [`echelon-ai-labs--servicenow-mcp`]

### `uvx <package>`

- [`feiskyer--mcp-kubernetes-server`, `designcomputer--mysql_mcp_server` (VS Code config example uses `uvx --from mysql-mcp-server`)]

### `npx -y <package>`

- [`executeautomation--mcp-playwright`]

### `npm start` / direct `dist/index.js` / `node build/index.js`

- `npm start -- ...` or direct `dist/index.js` [`docker--hub-mcp`]
- `node build/index.js` (production) and `npm run dev` (development) [`v-3--discordmcp`]

### `docker run`

- Entrypoint implicit [`elastic--mcp-server-elasticsearch`]

### Bare `python` / direct script invocation

- `uv run python main.py` — Dockerfile uses bare-script invocation rather than the declared console script. "Entry point not the primary run path" [`duolingo--slack-mcp`]
- `python puppeteer.py` — single-file at repo root [`twolven--mcp-server-puppeteer-py`]
- `uv run src/mcp_server_milvus/server.py --milvus-uri ...` — uv-run against checked-out source tree, unusual; most servers use `uvx <package>` [`zilliztech--mcp-server-milvus`]
- `uv run <path>/<script>.py`, no console-script entry [`shreyaskarnik--huggingface-mcp-server`]
- Bare Python script with absolute paths — `python src/server.py` (no packaging entry point at all) [`samuelgursky--davinci-resolve-mcp`]

### Path-anchored `uv --directory=<path>`

- Implies the package isn't designed for pip-install-everywhere; designed for developer-installed local runs [`shibuiwilliam--mcp-server-scikit-learn`]

### Multi-mode entry points

- Three invocation modes: `python3 kotlin_mcp_server.py` (direct), `kotlin-android-mcp` (system install), `python -m kotlin_mcp_server` (module). Plus `vscode_bridge.py` for HTTP REST bridge [`normaltusker--kotlin-mcp-server`]

### Dispatcher entry

- `mcp-science = "mcp_science:main"` is the dispatcher; users run `uvx mcp-science <server-name>` [`pathintegral-institute--mcp.science`]

### Standalone binary (no interpreter)

- Direct execution [`rust-mcp-stack--rust-mcp-filesystem`]

### CLI subcommand pattern

- `npx ctx7 setup`, `ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>` — multi-verb CLI [`upstash--context7`]

### Library embedding (no entry point)

- Go: server constructed and run from app code via `stdioSrv.ListenAndServe()` or `srv.HTTP(ctx, ":4981").ListenAndServe()` [`viant--mcp`]

### No local entry point (remote HTTP only)

- [`slackapi--slack-mcp-plugin`]

### Wrapper scripts / launchers

- Dockerfile + `deploy/` directory for Azure deployment [`mongodb-js--mongodb-mcp-server`]
- Smithery wrapper [`openags--paper-search-mcp`]
- `vscode_bridge.py` HTTP REST bridge [`normaltusker--kotlin-mcp-server`]
- Vercel deployment pipeline plus `.claude/skills/` skill definitions [`neondatabase--mcp-server-neon`]

### Console script naming

- Matches package name — `mcp-weaviate`, `terraform-cloud-mcp`, `mcp-server-scikit-learn` [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Does NOT match package name — `[project.scripts]` entry is `schip-mcp-email` while the PyPI package is `email-mcp` [`sandraschi--email-mcp`]

> Pitfall: console-script name divergence from package name is unusual. Most pyproject entries match package name; mismatch surfaces in host-config snippets where users must know the script name not the install name.

### Host-config snippet shape

- `uvx <name>` — minimal, single argument [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`]
- `uv run <name>` — dev-style invocation surfaced in README [`sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- `uv --directory=<path> run <name>` — path-anchored [`shibuiwilliam--mcp-server-scikit-learn`]
- `uv run <path>/<script>.py` [`shreyaskarnik--huggingface-mcp-server`]
- Absolute venv-Python path + absolute script path — `"command": "/path/to/venv/bin/python", "args": ["/path/to/repo/src/server.py"]`. The cost of not publishing to PyPI: hosts must know both paths [`samuelgursky--davinci-resolve-mcp`]
- Bare `"command": "python"` relying on system PATH / venv activation — fragile [`twolven--mcp-server-puppeteer-py`]

### Discouraged direct invocation

- README "explicitly discourages `python ...` direct invocation, framing the server strictly as an MCP-protocol bridge for hosts." Unique enforcement of agent-posture mental model [`designcomputer--mysql_mcp_server`]

### Entry-point inconsistencies (anti-pattern)

- README runs `python puppeteer.py` while `setup.py` declares `mcp-server-puppeteer=mcp_server_puppeteer.server:main` — declared and actual entry diverge; neither tested against PyPI [`twolven--mcp-server-puppeteer-py`]
- Module name `app` (bare) rather than conventional `hass_mcp` package — suggests template-derived structure that wasn't renamed [`voska--hass-mcp`]

## Configuration surface

How config reaches the server.

### Environment variables

- All-env-var config — `designcomputer--mysql_mcp_server` (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`), `duolingo--slack-mcp` (`SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_MCP_BASE_URI`, `SLACK_EXTERNAL_URL`, `SLACK_MCP_PORT`), `elastic--mcp-server-elasticsearch` (`ES_URL`, `ES_API_KEY` or `ES_USERNAME`/`ES_PASSWORD`, `ES_SSL_SKIP_VERIFY`)
- Env vars only — `mukul975--cve-mcp-server` (`NVD_API_KEY`, `GITHUB_TOKEN`, `ABUSEIPDB_KEY`, `VIRUSTOTAL_KEY`, `GREYNOISE_API_KEY`, `SHODAN_KEY`, `URLSCAN_KEY`, `CIRCL_PDNS_USER`, `CIRCL_PDNS_PASS`, `REQUEST_TIMEOUT`, `MAX_RETRIES`; `.env` support), `openags--paper-search-mcp` (`.env`, env vars, Claude Desktop JSON `env` block), `v-3--discordmcp` (`DISCORD_TOKEN`), `voska--hass-mcp` (`HA_URL`, `HA_TOKEN`), `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`SEMANTIC_SCHOLAR_API_KEY`)
- Env var (single) — `feiskyer--mcp-kubernetes-server` (`KUBECONFIG`), `exa-labs--exa-mcp-server` (`EXA_API_KEY`)
- Environment variables for credentials, endpoints, feature flags [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- Environment variables for transport selection [`utensils--mcp-nixos`]

### Multi-source (env + CLI + JSON config)

- Three sources: env vars prefixed `MDB_MCP_` (e.g. `CONNECTION_STRING`, `API_CLIENT_ID`, `READ_ONLY`, `DISABLED_TOOLS`, `LOGGERS`); camelCase CLI args (`--readOnly`, `--apiClientId`); JSON config file loaded via `MDB_MCP_CONFIG` [`mongodb-js--mongodb-mcp-server`]
- CLI arguments for flags, env vars for credentials (`motherduck_token`, AWS credentials) [`motherduckdb--mcp-server-motherduck`]

### YAML-first

- YAML config file (`example_config.yml`) plus env vars `OPENSEARCH_DISABLED_CATEGORIES` / `OPENSEARCH_ENABLED_CATEGORIES` for tool filtering; CLI args for further customization. Rarer than env-var-only in the MCP ecosystem [`opensearch-project--opensearch-mcp-server-py`]

### URL query params + headers (remote-hosted)

- URL query params (`readonly`, `category` for tool filtering, `projectId` for single-project scoping); Authorization bearer header for API-key auth [`neondatabase--mcp-server-neon`]

### Auto-generated IDE config files

- Three mechanisms: (1) interactive setup `install.py`; (2) env vars (`PROJECT_PATH`, `WORKSPACE_PATH`, `MCP_ENCRYPTION_PASSWORD`, compliance modes); (3) auto-generated IDE config files (`mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config_vscode.json`, `mcp_config.json`); optional `.env` [`normaltusker--kotlin-mcp-server`]
- Auto-generated per-client JSON config by an installer script [`samuelgursky--davinci-resolve-mcp`]

### CLI args

- CLI args (transport-specific) — `echelon-ai-labs--servicenow-mcp` SSE mode accepts `--instance-url=`, `--username=`, `--password=`; stdio mode uses env vars
- CLI args + env vars (mixed) — `docker--hub-mcp` (`HUB_PAT_TOKEN` env, `--transport`/`--port`/`--username` CLI)
- Capability gating CLI flags — `feiskyer--mcp-kubernetes-server`: `--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`. Per-verb enable/disable as an argument surface pattern (kubectl vs helm vs write vs delete split into four independent flags)
- CLI flags for mode selection (in addition to env) [`samuelgursky--davinci-resolve-mcp` (`--full` for tool-set choice)]
- `.env` + CLI args + env vars combined [`zilliztech--mcp-server-milvus`]

### Config files

- Tool catalog as data file — `docker--hub-mcp` (`tools.json`/`tools.txt` ship tool definitions; "Declarative catalog rather than inline schemas in source. Opens an authoring path that doesn't require TS expertise.")
- `mcp-config.json` for settings — `executeautomation--mcp-playwright`
- URL parameter as config (alternative to env var) — `exa-labs--exa-mcp-server` (`EXA_API_KEY` either env var or URL parameter)
- MCP server JSON config (command/args) — no env config at all [`shibuiwilliam--mcp-server-scikit-learn`]

### Library-construction-time options

- Functional options at library-construction time (Go) [`viant--mcp`]

### OAuth / setup-flow-driven config

- OAuth setup flow + API key header — `npx ctx7 setup` automates [`upstash--context7`]
- Client-side OAuth config — `clientId` / `callbackPort` shipped to consumers [`slackapi--slack-mcp-plugin`]

### Per-tool parameters only

- No global config documented [`twolven--mcp-server-puppeteer-py`]

### Per-server (monorepo)

- Client app JSON files; per-server API keys; optional MCPM (Model Context Protocol Manager) for automated wiring [`pathintegral-institute--mcp.science`]

### Runtime reconfiguration

- `configure_service` switches backends without restart [`sandraschi--email-mcp`]

### Built-in safety toggles

- Single-axis read-only flag [`rust-mcp-stack--rust-mcp-filesystem`]
- Two-axis safety: `READ_ONLY_TOOLS` + separate `ENABLE_DELETE_TOOLS` (delete is treated as more dangerous than write and gets its own toggle) [`severity1--terraform-cloud-mcp`]
- Read-only-only stance — README explicitly scopes the entire server to read-only access [`shreyaskarnik--huggingface-mcp-server`]
- Tool disabling at the CLI to reduce surface area and prompt-token usage [`rust-mcp-stack--rust-mcp-filesystem`]
- Compound vs full tool-set as a launch flag — `--full` flips between 27 aggregate tools and 342 granular tools [`samuelgursky--davinci-resolve-mcp`]
- Per-verb capability gating — `--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete` as four independent flags [`feiskyer--mcp-kubernetes-server`]

### Configuration precedence

- `.env` takes priority over CLI args — inverse of common "CLI overrides env"; reflects bias toward reproducible host-config-driven deployments [`zilliztech--mcp-server-milvus`]

### CLI parsing library

- `click` for CLI arg parsing despite FastMCP providing its own `fastmcp` CLI — server launched via plain Python entry point not FastMCP launcher [`zilliztech--mcp-server-milvus`]

### Env-var prefix conventions

- `MDB_MCP_` [`mongodb-js--mongodb-mcp-server`] — single uniform prefix across all keys
- `PAPER_SEARCH_MCP_` [`openags--paper-search-mcp`] — single uniform prefix across 20+ provider keys (e.g. `_UNPAYWALL_EMAIL`, `_CORE_API_KEY`, `_SEMANTIC_SCHOLAR_API_KEY`, `_ZENODO_ACCESS_TOKEN`, `_GOOGLE_SCHOLAR_PROXY_URL`, `_IEEE_API_KEY`, `_ACM_API_KEY`)
- `OPENSEARCH_` [`opensearch-project--opensearch-mcp-server-py`] — env var convention for category filtering
- No prefix — raw upstream-API names (`NVD_API_KEY`, `GITHUB_TOKEN`) [`mukul975--cve-mcp-server`]

### CLI-flag casing

- camelCase CLI args — e.g. `--readOnly`, `--apiClientId` — unusual relative to dash-separated convention [`mongodb-js--mongodb-mcp-server`]
- Hyphenated flags — `--db-path`, `--read-write`, `--allow-switch-databases`, `--motherduck-token` — standard [`motherduckdb--mcp-server-motherduck`]

## Authentication

Auth mechanism, where credentials originate, and whether the server itself implements an auth flow.

### No auth

- Browser automation against public web — `executeautomation--mcp-playwright`: "Not applicable — browser automation against public web; no service-level auth. Sites that require auth rely on Playwright's own cookie/state mechanisms, not an MCP-layer auth flow"
- Browser automation against public web [`twolven--mcp-server-puppeteer-py`]
- Public NixOS endpoints [`utensils--mcp-nixos`]
- Server talks to local-only API or local-only data [`rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

### Static credentials in env

- DB username/password — `designcomputer--mysql_mcp_server`. README emphasizes "never commit" credentials and restricting to minimum-permission DB users. Security guidance baked into README
- DB connection string + cloud API credential pair — MongoDB connection string for direct DB; Atlas Service Account (Client ID/Secret) for Atlas API; IP allowlist required for API credentials; temporary auto-generated DB users with configurable TTL (default 4h) [`mongodb-js--mongodb-mcp-server`]
- API key — `exa-labs--exa-mcp-server` (`EXA_API_KEY` from dashboard.exa.ai), `elastic--mcp-server-elasticsearch` (`ES_API_KEY`) or username/password against the cluster
- Personal Access Token — `docker--hub-mcp` (Docker Hub PAT in `HUB_PAT_TOKEN`)
- API token via env var — single-tenant, single-token-per-process [`severity1--terraform-cloud-mcp` (`TFC_TOKEN`), `shreyaskarnik--huggingface-mcp-server` (optional `HF_TOKEN`)]
- Static token — `motherduck_token` env var or `--motherduck-token` parameter; AWS credentials for S3 access [`motherduckdb--mcp-server-motherduck`]
- Per-provider API keys — multi-backend dispatch (SendGrid, Mailgun, Resend, Postmark, SES, plus SMTP/IMAP app passwords, plus ProtonMail Bridge, plus webhooks) [`sandraschi--email-mcp`]
- Embedding-provider keys + cloud-service keys — OpenAI / Cohere / WCS [`sajal2692--mcp-weaviate`]

### Bot token / long-lived token

- Discord bot token from Developer Portal [`v-3--discordmcp`]
- Home Assistant long-lived access token via `HA_TOKEN` env [`voska--hass-mcp`]

### Optional API key (for elevated capability)

- `SEMANTIC_SCHOLAR_API_KEY` for higher rate limits [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- `MILVUS_TOKEN` env var [`zilliztech--mcp-server-milvus`]
- Optional bearer token for elevated capability — anonymous access works for public data; token unlocks rate limit and private data [`shreyaskarnik--huggingface-mcp-server`]

### Credential delegation to local context

- kubeconfig — `feiskyer--mcp-kubernetes-server` delegates entirely to kubeconfig credentials; permissions check via kubectl's auth subsystem (`k8s_auth_can_i`, `k8s_auth_whoami`)

### Multi-mechanism with env-var selector

- Three methods (Basic Auth, OAuth client credentials, API Key); `SERVICENOW_AUTH_TYPE` env var selects mechanism. "Multi-auth support as a first-class feature — enterprise SaaS servers often need it because different customer deployments mandate different auth; most community servers pick one" [`echelon-ai-labs--servicenow-mcp`]

### Multiple auth schemes in one binary

- Basic auth, IAM roles (AWS OpenSearch Service), header-based auth, mTLS — covers self-hosted, managed AWS, and mTLS deployments [`opensearch-project--opensearch-mcp-server-py`]
- Multiple external API auth schemes: API Keys, OAuth 2.0, JWT tokens, Basic HTTP, Bearer tokens; server-side rate limiting, circuit breaker, audit logging [`normaltusker--kotlin-mcp-server`]

### OAuth flow implemented in server

- `duolingo--slack-mcp` — OAuth 2.1 per-user; "when your MCP client first connects. Your client will open a browser window for Slack authorization". Server itself drives a browser-based OAuth handshake. Local dev requires ngrok for OAuth callback
- OAuth 2.0 with workspace admin approval — callback-port flow [`slackapi--slack-mcp-plugin`]

### OAuth + API key (hybrid / remote-hosted)

- OAuth setup via `npx ctx7 setup`; free API key registration at dashboard for higher rate limits [`upstash--context7`]
- OAuth 2.0 with scopes (`read`, `write`, `*`) primary; API key bearer token as headless alternative. Browser OAuth redirect or `Authorization: Bearer <api-key>` header [`neondatabase--mcp-server-neon`]

### OAuth2/OIDC with full SDK support

- Two modes: global resource protection via bearer tokens, fine-grained tool/resource control (experimental) [`viant--mcp`]
- Client-side automatic token acquisition: "401 challenge, discovers protected resource metadata, acquires tokens and retries" — unusual for MCP servers [`viant--mcp`]

### Per-source key (graceful-degradation aggregator)

- 21 independent API-key authentications, each optional; server degrades gracefully when a key is absent. Keys never logged or cached in audit entries [`mukul975--cve-mcp-server`]
- Per-provider API keys, one email (Unpaywall); per-provider credentials applied globally [`openags--paper-search-mcp`]

### No centralized auth

- Server-specific API keys for specialized integrations; no centralized authentication mechanism [`pathintegral-institute--mcp.science`]

### Optional vs required credentials

- Required — server cannot start without the credential [`severity1--terraform-cloud-mcp`]
- Optional bearer token for elevated capability [`shreyaskarnik--huggingface-mcp-server`]

## Multi-tenancy

How many tenants share a process.

### Single-tenant per process

- Single DB connection per server, no per-request tenancy [`designcomputer--mysql_mcp_server`]
- Single ServiceNow instance per deployment [`echelon-ai-labs--servicenow-mcp`]
- Single Elasticsearch cluster — per-client MCP connection in HTTP mode but single ES backend [`elastic--mcp-server-elasticsearch`]
- Single user per process (one PAT plus username) [`docker--hub-mcp`]
- Single kubeconfig context [`feiskyer--mcp-kubernetes-server`]
- Single browser context per server process [`executeautomation--mcp-playwright`]
- Single-user — bound to one process / one credential [`motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server` (one key-set per server instance), `opensearch-project--opensearch-mcp-server-py`, `openags--paper-search-mcp` (per-provider credentials applied globally), `pathintegral-institute--mcp.science` (each sub-server is single-user), `rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Single-user single-process (one browser per process; one HA instance; one Milvus URI/DB) [`twolven--mcp-server-puppeteer-py`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Per-request multi-tenancy

- OAuth 2.1 per-user, multi-user via separate tokens per user [`duolingo--slack-mcp`]. Per-request tenant is a rare value across the bins
- Per-client multi-tenancy via HTTP endpoint, API key scoped to user account [`exa-labs--exa-mcp-server`]
- Per-call tenancy as a tool argument — first-class multi-tenancy in tool signatures rather than server config [`sajal2692--mcp-weaviate`]
- Per-request via bearer token; OAuth2 discovery enables per-request tenant identification [`viant--mcp`]
- Stateless HTTP mode supports shared/multi-user deployments [`utensils--mcp-nixos`]
- Per-request tenancy via OAuth token scoping; supports organization and personal project access via `org_id`/`project_id` in prompts; remote hosted multi-tenant service [`neondatabase--mcp-server-neon`]

### Per-session via header

- HTTP transport supports externally-managed session IDs via `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true` — per-session, not per-tenant [`mongodb-js--mongodb-mcp-server`]

### Per-workspace OAuth token

- Workspace admin scope; tenant boundary is the OAuth grant [`slackapi--slack-mcp-plugin`]
- Per-user OAuth token + per-workspace API key [`upstash--context7`]
- Single-user per workspace; workspace-specific via `WORKSPACE_PATH` env var; audit logging suggests multi-tenant awareness [`normaltusker--kotlin-mcp-server`]

### Bot-scoped

- Bot's server memberships define reachable tenants; auto server/channel discovery from bot's perspective [`v-3--discordmcp`]

### Database switching as flag

- Single-user with ability to switch databases via `--allow-switch-databases` — feature-flagged multi-database workflow [`motherduckdb--mcp-server-motherduck`]

### Fine-grained authorization (experimental)

- Suggests multi-user workspace scenarios being designed for [`viant--mcp`]

> Notable: `sajal2692--mcp-weaviate` calls out per-tenant search tools as a first-class MCP concept. Tenancy becomes an argument, not a server-config dimension. Rare across Python MCP servers.

## Capabilities exposed

Tools / resources / prompts surface area; tool count is one observable axis of breadth.

### MCP surface coverage

#### Tools-only

- 5 read-only Slack tools — `duolingo--slack-mcp` (channel messages, thread replies, search messages, list users, enumerate channels). "Read-only Slack integration (no write capabilities)"
- 5 ES tools — `elastic--mcp-server-elasticsearch` (`list_indices`, `get_mappings`, `search`, `esql`, `get_shards`)
- 3 web-search tools + advanced filtering — `exa-labs--exa-mcp-server` (`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`)
- Tools defined in `tools.json` — `docker--hub-mcp` (specific tool list not enumerated)
- Browser automation surface — `executeautomation--mcp-playwright` (navigation, click, fill, screenshot, test code generation, web scraping, JavaScript execution, device emulation with 143+ device presets)
- 50+ tools — `feiskyer--mcp-kubernetes-server` (kubectl/helm command execution, read-only queries, write, delete, rollout/scaling)
- 60+ tools across 9 functional areas — `echelon-ai-labs--servicenow-mcp` (Incident, Service catalog, Change requests, Agile, Workflows, Script includes, Changesets, Knowledge bases, User management). "Enterprise-tool density — 60+ tools in 9 functional areas; enterprise platforms generate more surface area than consumer SaaS does"
- Tools-only [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `slackapi--slack-mcp-plugin`]

#### Tools + resources

- Tables-as-resources — `designcomputer--mysql_mcp_server`. "Exposes tables as MCP resources (not only tools) — one of the few DB MCP servers to use the resource surface; resources-as-tables pattern is rare — most DB MCP servers expose everything through tools"
- Library index + documentation cache as resources [`upstash--context7`]
- `config://config` (redacted), `debug://mongodb` (diagnostics), `exported-data://{name}` (temporary exports with auto-cleanup, default 5 min) [`mongodb-js--mongodb-mcp-server`]

#### Tools + resources + prompts

- Uses all three core MCP surfaces with a custom `hf://` URI scheme [`shreyaskarnik--huggingface-mcp-server`]

#### Tools + resources + prompts + sampling + skills

- Broadest surface in the corpus (custom `email_compose_request` prompt, `email_agentic_assist` sampling tool) [`sandraschi--email-mcp`]

#### Tools + MCP Roots (opt-in)

- [`rust-mcp-stack--rust-mcp-filesystem`]

#### Full MCP capability surface

- Tools, resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, elicitation — full MCP capability surface as a Go SDK [`viant--mcp`]

> Notable: most Python servers stick to tools-only. Two samples (`sandraschi--email-mcp`, `shreyaskarnik--huggingface-mcp-server`) demonstrate prompts and resources, with the latter exposing a custom URI scheme via the resources surface. Most m6 samples explicitly report no prompts/sampling/roots [`mongodb-js--mongodb-mcp-server`].

### Tool count and design

#### Minimal (≤5 tools)

- 2 tools — `nix()` unified query (~1,030 tokens) + `nix_versions()` helper; deliberate token-efficiency strategy contrasting with 50–250-tool peers [`utensils--mcp-nixos`]
- 2 tools — `send-message` + `read-messages`; minimal Discord surface [`v-3--discordmcp`]
- 2 tools — `resolve-library-id`, `query-docs` plus library/documentation cache resources [`upstash--context7`]
- 5 tools — `puppeteer_navigate`, `puppeteer_screenshot`, `puppeteer_click`, `puppeteer_fill`, `puppeteer_evaluate` [`twolven--mcp-server-puppeteer-py`]
- Small focused set — under 15 tools [`sajal2692--mcp-weaviate` (11), `sandraschi--email-mcp` (6 core)]

#### Medium (10–30)

- SQL query execution (read/write), database listing, table listing, column inspection, database switching, support for local files / S3 / MotherDuck / in-memory [`motherduckdb--mcp-server-motherduck`]
- 20+ tools across Projects, Branches, SQL, Migrations, Optimization, Auth/Data API provisioning, Discovery; read-only mode exposes 13 specific tools [`neondatabase--mcp-server-neon`]
- 27 tools across 8 categories (vulnerability intelligence, exploits, risk reporting, network intelligence, threat intel, DevSecOps) over 21 upstream data sources [`mukul975--cve-mcp-server`]

#### Mid (~15–50 tools, grouped)

- ~15 tools across text/vector/hybrid search, query, collection CRUD, insert, delete [`zilliztech--mcp-server-milvus`]
- 16 tools organized into 4 explicit functional groups (8 paper search/discovery, 2 citation analysis, 4 author info, 2 recommendation) — categorization baked into docs structure [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Mid-range — 50+ tools [`severity1--terraform-cloud-mcp`]

#### Large (30–60)

- 32 tools across 10 categories (Core Development 7, UI 4, Architecture 6, Security & Compliance 4, AI/ML 3, File Mgmt 2, API 4, Testing 2, Git 4, QoL 7) [`normaltusker--kotlin-mcp-server`]
- 40+ tools — 9 core (default-enabled), 10 additional analysis (default-disabled), 21 Search Relevance Workbench (`search_relevance` category), 2 Skills tools [`opensearch-project--opensearch-mcp-server-py`]
- ~60 tools spanning DB ops (find/aggregate/insert/update/delete/explain), metadata, DDL, Atlas management (clusters, projects, users, access lists, alerts), Atlas Stream Processing, Assistant KB search [`mongodb-js--mongodb-mcp-server`]

#### Two-mode design (compound vs full)

- 27 aggregate tools vs 342 granular; explicit context-window-vs-expressiveness trade [`samuelgursky--davinci-resolve-mcp`]
- 342 granular tools — among the largest tool surfaces seen; the dual-mode design exists specifically to counter context-window pressure

#### Multiplexed across many backends

- Unified `search_papers` and `download_with_fallback` tools plus platform-specific search/download/read across 20+ academic sources (arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, Crossref, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, optional Sci-Hub) [`openags--paper-search-mcp`]

#### Per-sub-server (monorepo)

- Specialized functions per sub-server: web content retrieval, academic searches, code execution (Python, SSH), scientific computation (DFT via GPAW), database operations (TinyDB), Jupyter kernel interaction, Wolfram Language evaluation [`pathintegral-institute--mcp.science`]

### Tool gating mechanisms

#### Per-tool disable list

- `DISABLED_TOOLS` env var [`mongodb-js--mongodb-mcp-server`]

#### Read-only mode flag

- `--readOnly` disables mutating tool surface [`mongodb-js--mongodb-mcp-server`]
- `--read-write` flag toggles safety posture [`motherduckdb--mcp-server-motherduck`]
- `readonly` URL query param; read-only mode exposes 13 specific tools [`neondatabase--mcp-server-neon`]

#### Index-check / safety-rejection flag

- `--indexCheck` rejects collection scans (unusual safety posture beyond simple read-only) [`mongodb-js--mongodb-mcp-server`]

#### Confirmation-required tool list

- `CONFIRMATION_REQUIRED_TOOLS` triggers MCP elicitation for destructive tools like drop-database [`mongodb-js--mongodb-mcp-server`]

#### Category-based on/off

- Env vars `OPENSEARCH_ENABLED_CATEGORIES` / `OPENSEARCH_DISABLED_CATEGORIES`; category-level on/off rather than per-tool. Default-disabled categories let operators prune the 40-tool surface to just the core 9 [`opensearch-project--opensearch-mcp-server-py`]
- `category` URL query param for tool filtering (granular scope beyond simple read-only) [`neondatabase--mcp-server-neon`]

#### Dry-run

- `--dryRun` dumps resolved config and exits without booting server [`mongodb-js--mongodb-mcp-server`]

#### Per-request override

- `--allowRequestOverrides=true` lets per-request headers/query params override config — powerful for HTTP multi-client setups [`mongodb-js--mongodb-mcp-server`]

### Tool surface design philosophy axis

- Few-but-broad tools (token efficiency) vs many-narrow tools — explicit design call [`utensils--mcp-nixos`]
- Minimal scope as trust signal — README emphasizes user-approval before sending Discord messages, reflecting awareness of agent-action-on-public-surfaces risk [`v-3--discordmcp`]

### Multi-backend unified surface

- One tool, many backends — `send_email` dispatches to SMTP or to an API provider based on configuration; backend heterogeneity is hidden from the LLM caller [`sandraschi--email-mcp`]

### Vertical / specialized skills shipped alongside

- `exa-labs--exa-mcp-server` skills directory — company research, code search, people research, financial reports, academic papers. "Vertical-specific research skills shipped alongside the server — axis: 'skills' as first-class shipping artifact"

## Observability

Logging, metrics, tracing, debug surface.

### Pluggable / multi-target

- `LOGGERS` env var; targets: `disk` (default `~/.mongodb/mongodb-mcp/.app-logs`), `mcp` (to client), `stderr`. `MCP_CLIENT_LOG_LEVEL` controls severity (default `debug`) [`mongodb-js--mongodb-mcp-server`]

### File-based logging (stdio framing constraint)

- `executeautomation--mcp-playwright` — logs written to `~/playwright-mcp-server.log` in stdio mode "specifically to keep stdout clean for JSON-RPC framing. File-based log is the observability surface". A deliberate design response to the stdio framing constraint — the server cannot log to stdout without corrupting JSON-RPC

### Container stdout/stderr + health endpoint

- `elastic--mcp-server-elasticsearch` — container logs (stdout/stderr); health check at `/ping` returning "pong"

### Health endpoints

- Optional monitoring-server health endpoint (HTTP transport only) — separable sidecar [`mongodb-js--mongodb-mcp-server`]

### Separate monitoring directory + web dashboard

- Vite + Uvicorn on ports 10812/10813 for health/metrics/control [`sandraschi--email-mcp`]

### Rotating JSON audit log as a capability surface

- Rotating JSON audit log at `~/.cve-mcp/audit.log` (50MB, 5 backups); fields: timestamp, tool name, parameters, duration, cache-hit status; API keys and response payloads explicitly redacted. Audit-log surfaced as a capability, not just ops telemetry [`mukul975--cve-mcp-server`]

### Compliance / GDPR / HIPAA modes

- Audit logging for security events; GDPR, HIPAA modes mentioned [`normaltusker--kotlin-mcp-server`]

### Vendor logging stack

- Winston-based logging with configurable levels; Sentry integration; analytics integration [`neondatabase--mcp-server-neon`]

### Debug logging enabled by default

- Format/destination not surfaced [`severity1--terraform-cloud-mcp`]

### FastMCP-standard logging

- No explicit metrics/tracing [`zilliztech--mcp-server-milvus`]

### Explicit Logging() method

- For log levels; progress reporting + request cancellation as separate capabilities [`viant--mcp`]

### Server-side only

- Telemetry lives on the hosted service, not in the repo [`slackapi--slack-mcp-plugin`]

### Underspecified / not documented

- "Comprehensive logging" mentioned, no specifics [`designcomputer--mysql_mcp_server`]
- "No explicit monitoring, logging, or metrics documentation" [`duolingo--slack-mcp`]
- "Detailed error handling and logging" claimed without destination — likely stderr [`twolven--mcp-server-puppeteer-py`]
- Not surfaced [`docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server`, `motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science`, `rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`, `upstash--context7`, `utensils--mcp-nixos`, `voska--hass-mcp`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Stdio stdout-pollution discipline

- Not stated whether Python stdout is protected from log pollution (important for stdio JSON-RPC correctness) [`twolven--mcp-server-puppeteer-py`]

## Host integrations

Which MCP host configs the README documents.

### Claude Desktop

JSON `mcpServers` entry standard across nearly all samples. Notable platform-specific config paths surfaced — `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%APPDATA%\Claude\` (Windows) [`mukul975--cve-mcp-server`].

- `claude_desktop_config.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `executeautomation--mcp-playwright` (primary host integration)
- Implies standard MCP configuration without explicit detail [`duolingo--slack-mcp`]
- JSON `mcpServers` entry [`feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos` (uvx form), `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (uvx command)]
- JSON config snippet (Docker `command`/`args` + env) [`voska--hass-mcp`]
- JSON config snippets — separate stdio and SSE variants [`zilliztech--mcp-server-milvus`]
- Native Claude Desktop connector (no manual config needed) — distinct from JSON-snippet hosts [`exa-labs--exa-mcp-server`]
- Listed as MCP-compatible (assumed) [`elastic--mcp-server-elasticsearch`, `opensearch-project--opensearch-mcp-server-py` (Claude Desktop and LangChain)]
- Standard `mcpServers` JSON entry [`mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`]

### Claude Code

- Native support documented as one of 30+ supported agents [`upstash--context7`]
- Standard `claude mcp add` CLI registration alongside JSON `mcpServers` for desktop hosts [`severity1--terraform-cloud-mcp`]
- Dedicated CLI commands [`motherduckdb--mcp-server-motherduck`]
- `claude mcp add cve-mcp --env-file .env -- python -m cve_mcp.server` [`mukul975--cve-mcp-server`]
- Supported but not explicitly documented [`openags--paper-search-mcp`, `neondatabase--mcp-server-neon`, `normaltusker--kotlin-mcp-server` (Claude Code not explicitly mentioned)]
- Not documented [`pathintegral-institute--mcp.science`]

### VS Code

- `mcp.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp` (User Settings JSON), `exa-labs--exa-mcp-server` (pre-built installer)
- Documented via GitHub Copilot integration [`executeautomation--mcp-playwright`]
- VS Code (Insiders), Copilot CLI, OpenCode (install badges) [`mongodb-js--mongodb-mcp-server`]
- VS Code, Codex CLI, Gemini CLI [`motherduckdb--mcp-server-motherduck`]
- VS Code + GitHub Copilot [`neondatabase--mcp-server-neon`]
- VS Code (auto-generated `mcp_config_vscode.json` shared between Cursor/VS Code) [`normaltusker--kotlin-mcp-server`]

### Cursor

- JSON `mcpServers` entry [`feiskyer--mcp-kubernetes-server`]
- Pre-built installer [`exa-labs--exa-mcp-server`]
- Documented host integration [`executeautomation--mcp-playwright`, `mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`]
- Cursor IDE install button [`neondatabase--mcp-server-neon`]
- Listed (assumed) [`elastic--mcp-server-elasticsearch`]
- Listed as supported agent [`upstash--context7`]
- `.cursor/` directory present + dedicated JSON snippet [`zilliztech--mcp-server-milvus`]
- Native JetBrains support [`normaltusker--kotlin-mcp-server`]

### Other hosts

- Cline, Windsurf, Zed [`neondatabase--mcp-server-neon`]
- GitHub Copilot / ChatGPT Copilot — JSON `mcpServers` entry [`feiskyer--mcp-kubernetes-server`]
- Cline — `executeautomation--mcp-playwright` documented host integration
- OpenAI Code — listed as supported agent [`upstash--context7`]
- LangChain integration supported [`opensearch-project--opensearch-mcp-server-py`]

### Vendor-specific companion integration

- `docker--hub-mcp` ships `gordon-mcp.yml` for Docker's Ask Gordon agent. "MCP server pre-shaping its config for a first-party downstream tool, distinct from generic host config"

### Many-host enumeration

- `exa-labs--exa-mcp-server` documents JSON `mcp.json` configs for Codex, OpenCode, Antigravity, Windsurf, Zed, Gemini CLI, v0 by Vercel, Warp, Kiro, Roo Code — 15+ platforms. "High client compatibility (15+ platforms)"
- Context7 documents support across 30+ client platforms [`upstash--context7`]

### NixOS / Home Manager

- Declarative config entry available in nixpkgs [`utensils--mcp-nixos`]

### Smithery / MCPM

- Smithery registered install target [`openags--paper-search-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- MCPM (Model Context Protocol Manager) for automated client integration [`pathintegral-institute--mcp.science`]

### Universal installer pattern

- Custom `install.py` walks every supported client and writes per-client JSON to that client's standard config location. Replaces both pip and uv roles. Flags `--clients`, `--dry-run`, `--no-venv`, `--full` [`samuelgursky--davinci-resolve-mcp`]
- Many hosts via universal installer — 10 MCP clients auto-configured in one pass [`samuelgursky--davinci-resolve-mcp`]
- Auto-generated config files for Claude Desktop, VS Code, Cursor, generic MCP clients [`normaltusker--kotlin-mcp-server`]

### Documented host integration count

- One host (Claude Desktop only) [`shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- A few hosts — Claude Desktop, Cursor, plus optionally Glama, Zed [`sandraschi--email-mcp`]
- Two hosts shipped as configs — Claude Code + Cursor with separate plugin layouts [`slackapi--slack-mcp-plugin`]

### Host-specific config files

- `manifest.json` — MCPB / Claude Desktop bundle [`sandraschi--email-mcp`]
- `mcp.json` — Cursor [`sandraschi--email-mcp`]
- `glama.json` — Glama discovery [`sandraschi--email-mcp`]
- `.cursor-mcp.json` — Cursor (alternate location) [`slackapi--slack-mcp-plugin`]
- `.mcp.json` — Claude Code [`slackapi--slack-mcp-plugin`]
- `.claude-plugin/` directory — Claude Code plugin layout [`slackapi--slack-mcp-plugin`]
- `.cursor-plugin/` directory — Cursor plugin layout [`slackapi--slack-mcp-plugin`]

## Claude Code plugin wrapper

Whether the repo ships `.claude-plugin/` or co-located Claude Code skill bundles.

### Present — plugin.json

- `.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`) [`exa-labs--exa-mcp-server`]
- Configs-only `.claude-plugin/` directory in a remote-hosted MCP — plugin layout used to ship configs, not server code [`slackapi--slack-mcp-plugin`]

### Marketplace metadata vs plugin install

- `.claude-plugin/marketplace.json` (marketplace metadata only, not full plugin.json) — distinct from plugin-wrapper install [`upstash--context7`]

### Skill files in-tree

- `claude-code/` directory contains Claude Code skill files; explicit skill-layer integration rather than just host-config JSON [`openags--paper-search-mcp`]
- `.claude/skills/` skill definitions present in repo; Claude Code skill wiring rather than a plugin manifest [`neondatabase--mcp-server-neon`]

### Wrapper mentioned but shape ambiguous

- `.claude-plugin` wrapper mentioned with dedicated CLI commands [`motherduckdb--mcp-server-motherduck`]

### Not present

- [`designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`, `mongodb-js--mongodb-mcp-server`, `mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science`, `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `utensils--mcp-nixos`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `viant--mcp`]

## Tests

### Framework

- pytest — `designcomputer--mysql_mcp_server` (`pytest.ini`, `requirements-dev.txt`, `tests/` directory), `duolingo--slack-mcp` (`pytest>=8.0.0` in test extras, `uv run pytest`), `sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`, `utensils--mcp-nixos`, `voska--hass-mcp`
- pytest + pytest-asyncio — `motherduckdb--mcp-server-motherduck` (8.0+ with pytest-asyncio 0.24+; `asyncio_mode = "auto"`; custom `slow` marker), `mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server` (dual-config layout: `pytest.ini` + `pyproject.toml`), `openags--paper-search-mcp` (inferred)
- pytest + pytest-asyncio + pytest-cov via a `test` extra [`sandraschi--email-mcp`]
- Vitest (`vitest.config.ts`, tests under `/tests`) [`mongodb-js--mongodb-mcp-server`]
- Jest [`executeautomation--mcp-playwright` (`src/__tests__`)]
- Playwright (web E2E) [`neondatabase--mcp-server-neon`]
- cargo-nextest [`rust-mcp-stack--rust-mcp-filesystem`]
- Custom 5-phase live suite — read-only / destructive / media / AI/ML / advanced; framework not surfaced; 319/324 methods live-tested with claimed 100% pass [`samuelgursky--davinci-resolve-mcp`]
- Go stdlib testing — `client.go` / `server.go` test patterns [`viant--mcp`]
- Monorepo test suite via `npm run test` in workspace [`upstash--context7`]
- Framework not surfaced but `tests/` + `integration_tests/` directories present [`opensearch-project--opensearch-mcp-server-py`]
- Framework not surfaced — `tests/` directory present [`echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- CI-driven tests implied [`feiskyer--mcp-kubernetes-server` (CI `build.yml`)]
- ESLint config present, no test files explicitly called out [`docker--hub-mcp`]
- Not documented [`exa-labs--exa-mcp-server`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`, `pathintegral-institute--mcp.science`]
- Not observed / no test framework documented [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`]
- Not applicable — config-only repo [`slackapi--slack-mcp-plugin`]

### Test stratification

#### Unit + integration

- pytest 8.0+ with pytest-asyncio 0.24+; `asyncio_mode = "auto"`; custom `slow` marker for deselection [`motherduckdb--mcp-server-motherduck`]
- `tests/` and `integration_tests/` separate dirs (suggests against-real-OpenSearch validation) [`opensearch-project--opensearch-mcp-server-py`]

#### Unit + integration + cache + security

- Unit tests (risk scoring, CVSS parsing, validation), integration tests (tool registration, error handling), cache tests (SQLite TTL), security tests (private IP blocking, XML bomb protection — defusedxml) [`mukul975--cve-mcp-server`]

#### Unit + integration + E2E + web E2E

- Pyramid: unit (pure logic), integration (tool contracts), E2E (MCP protocol with real clients), web E2E (Playwright, ephemeral DB). `pnpm run test` [`neondatabase--mcp-server-neon`]

#### End-to-end regression

- E2E regression tests mentioned [`openags--paper-search-mcp`]

### Lint / type-check stack

- Black (100-char line limit), isort, MyPy strict, Bandit security scans excluding tests [`normaltusker--kotlin-mcp-server`]
- ruff [`motherduckdb--mcp-server-motherduck`]
- Custom `eslint-rules/` shipped in repo (suggests codebase-scale discipline) [`mongodb-js--mongodb-mcp-server`]

### Async test support

- `asyncio_default_fixture_loop_scope = "function"`, `testpaths = ["tests"]` [`motherduckdb--mcp-server-motherduck`]
- Fully async/await throughout; httpx-based; aiosqlite for cache [`mukul975--cve-mcp-server`]
- pytest_asyncio configured; dual-config layout [`normaltusker--kotlin-mcp-server`]
- pytest-asyncio not declared [`duolingo--slack-mcp` ("may be sync-style tools"), `designcomputer--mysql_mcp_server`]

### Test layout

- `tests/` directory at repo root [`rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- `pytest.ini` at root alongside `pyproject.toml` — legacy dual-config [`sandraschi--email-mcp`]

## CI

### GitHub Actions

- Present — `designcomputer--mysql_mcp_server` (test.yml badge), `docker--hub-mcp` (`.github/`), `feiskyer--mcp-kubernetes-server` (`build.yml`), `executeautomation--mcp-playwright` (`.github/workflows`), `mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server`, `neondatabase--mcp-server-neon`, `normaltusker--kotlin-mcp-server` (implied via pyproject tool config), `openags--paper-search-mcp`, `opensearch-project--opensearch-mcp-server-py`, `rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `utensils--mcp-nixos`, `voska--hass-mcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `viant--mcp`, `upstash--context7`

### Multi-system CI

- `elastic--mcp-server-elasticsearch` — both `.github/` (GitHub Actions) and `.buildkite/` (Buildkite pipeline) — multi-platform testing across two CI systems. "CI system diversity beyond the GitHub-only assumption"

### What CI runs

- fmt + clippy + test + check via Makefile.toml (cargo-make) [`rust-mcp-stack--rust-mcp-filesystem`]
- Multi-Python matrix (3.10/3.11/3.12) + Ruff + MyPy + Bandit; webapp linted with Biome [`sandraschi--email-mcp`]
- ruff + black + mypy [`severity1--terraform-cloud-mcp`]
- Black/isort/MyPy/Bandit configured in `pyproject.toml` (CI pipeline implied) [`normaltusker--kotlin-mcp-server`]
- Vercel automatic deployment from branches; preview environments per PR [`neondatabase--mcp-server-neon`]
- Details not surfaced beyond presence [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

### CI extras

- CodeRabbit reviews used alongside GitHub Actions [`utensils--mcp-nixos`]

### Unspecified / not extracted

- [`duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`]
- Not observed [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`, `shreyaskarnik--huggingface-mcp-server`]
- Not applicable [`slackapi--slack-mcp-plugin`]

> Most samples flag exact workflow contents as out-of-budget — common gap.

## Container / packaging artifacts

### Dockerfile only

- [`designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server` (Dockerfile + Vercel `vercel.json`), `openags--paper-search-mcp` (with `.env.example` for container env injection), `rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]

### Dockerfile + docker-compose

- [`executeautomation--mcp-playwright`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `normaltusker--kotlin-mcp-server` (`docker-compose up -d kotlin-mcp-server`)]

### Multi-stage Docker build

- Multi-stage Dockerfile + `deploy/` Azure guides; image published `mongodb/mongodb-mcp-server:latest` [`mongodb-js--mongodb-mcp-server`]
- `clux/muslrust:stable` builder + `alpine:latest` final, static binary, non-root user [`rust-mcp-stack--rust-mcp-filesystem`]

### Multiple Dockerfiles / multi-target

- `elastic--mcp-server-elasticsearch` — `Dockerfile` (main), `Dockerfile-8000` (alternative), `.dockerignore`. Multi-container deployment ready (EC2, ECS, EKS deployment targets)

### Container as primary distribution

- `duolingo--slack-mcp` — Dockerfile uses `python:3.11-slim` base, env vars `NO_COLOR=1`, `CI=true`, `TERM=dumb`, port 8001 exposed, startup `uv run python main.py`
- `voska--hass-mcp` — official image on Docker Hub as primary distribution channel

### Docker Hub MCP Registry presence

- [`rust-mcp-stack--rust-mcp-filesystem`]

### MCPB bundle replaces Docker

- [`sandraschi--email-mcp`]

### Vercel / serverless

- Vercel-hosted deployment; no Dockerfile observed [`neondatabase--mcp-server-neon`]

### Windows installer via WiX toolset

- `wix/` directory for Windows installer [`rust-mcp-stack--rust-mcp-filesystem`]

### Nix-native packaging

- Nix flake for nix-native install [`utensils--mcp-nixos`]
- Declarative NixOS / Home Manager module via nixpkgs [`utensils--mcp-nixos`]

### Intentionally absent

- No container — intentional when the server must run on the same host as a local app [`samuelgursky--davinci-resolve-mcp`]
- No Dockerfile — pip/uv-based installs preferred [`opensearch-project--opensearch-mcp-server-py`]
- No Docker — uv-based Python packaging preferred [`motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server`]
- No Docker — PyPI distribution [`pathintegral-institute--mcp.science`]
- Dockerfile existence ambiguous [`normaltusker--kotlin-mcp-server`]
- Not observed [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`, `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`, `viant--mcp`]

## Example client / developer ergonomics

### Task runner

- Makefile [`shibuiwilliam--mcp-server-scikit-learn`, `motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`]
- Makefile.toml (cargo-make) — Rust task runner [`rust-mcp-stack--rust-mcp-filesystem`]
- Justfile recipes — uncommon in MCP servers; Windows-first repo [`sandraschi--email-mcp`]
- PowerShell scripts (`build.ps1`, `start.ps1`, `build_mcpb.bat`) — Windows-first dev posture [`sandraschi--email-mcp`]
- Plain `uv run <tool>` invocations [`sajal2692--mcp-weaviate`]

### Sample configs

- Per-host JSON snippets in README — `mcpServers` blocks per host [`severity1--terraform-cloud-mcp`, `slackapi--slack-mcp-plugin`]
- `examples/` directory [`sandraschi--email-mcp`, `samuelgursky--davinci-resolve-mcp`]
- Glob-pattern usage examples — `*.rs`, `src/**/*.txt`, `logs/error-???.log` [`rust-mcp-stack--rust-mcp-filesystem`]
- Claude Desktop JSON sample [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `voska--hass-mcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Claude Desktop + Cursor JSON snippets, plus `.env` example [`zilliztech--mcp-server-milvus`]
- Install badges for multiple hosts [`mongodb-js--mongodb-mcp-server`]
- Sample configs for Claude Desktop integration [`motherduckdb--mcp-server-motherduck`]
- `.env.example` [`mukul975--cve-mcp-server`, `openags--paper-search-mcp`]
- JSON config examples per host + `.claude/skills/` definitions + Cursor install button [`neondatabase--mcp-server-neon`]
- Auto-generated config files for Claude Desktop, VS Code, Cursor, generic MCP clients [`normaltusker--kotlin-mcp-server`]
- `example_config.yml`, `DEVELOPER_GUIDE.md`, `USER_GUIDE.md` [`opensearch-project--opensearch-mcp-server-py`] — formal docs split into developer + user guides
- Per-server dedicated README + GitHub Pages site at mcp.science for discoverability [`pathintegral-institute--mcp.science`]

### Dev shells / toolchain

- `nix develop` reproducible dev shell + ruff/mypy toolchain [`utensils--mcp-nixos`]
- `[dev]` optional extra [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- `requirements.txt` only — no lock, no dev extras [`twolven--mcp-server-puppeteer-py`]

### MCP Inspector

- Explicit Inspector launcher in README — `npx @modelcontextprotocol/inspector node build/index.js` [`v-3--discordmcp`]
- `npx @modelcontextprotocol/inspector python -m cve_mcp.server` at `http://localhost:6274` [`mukul975--cve-mcp-server`]
- `mcp[cli]` dev inspector [`openags--paper-search-mcp`]
- MCP Inspector support documented + Smithery registry config [`upstash--context7`]
- MCP Inspector debugging support referenced [`designcomputer--mysql_mcp_server`]

### Examples directory

- `/example` directory demonstrating server, auth, client, bridge binary use [`viant--mcp`]

### Other dev ergonomics

- ruff in dev extra [`duolingo--slack-mcp`]
- ngrok required for OAuth callback during local dev [`duolingo--slack-mcp`]
- Custom eslint rules + `api-extractor/` for API docs [`mongodb-js--mongodb-mcp-server`]

## Repo layout

### Single-package

- All eight bin-5 samples are single-package — `designcomputer--mysql_mcp_server` (`src/mysql_mcp_server/`), `docker--hub-mcp` (`src/`), `duolingo--slack-mcp` (root `main.py` only), `echelon-ai-labs--servicenow-mcp` (`servicenow_mcp/`), `elastic--mcp-server-elasticsearch` (Rust `src/`), `exa-labs--exa-mcp-server` (`src/`, `api/`, `skills/`, `public/`), `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server` (`src/mcp_kubernetes_server/`)
- Single-package — `src/<package>/` [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Single-package with support directories — `install.py`, `src/`, `tests/`, `docs/`, `examples/` [`samuelgursky--davinci-resolve-mcp`]
- Single-file script repo — `puppeteer.py` + `requirements.txt` [`twolven--mcp-server-puppeteer-py`]
- Single-package TypeScript — `/src`, `package.json`, `tsconfig.json` [`v-3--discordmcp`]
- Single-package Python — `src/mcp_server_milvus/` [`zilliztech--mcp-server-milvus`]
- Single-package Python — `app/` module — bare `app` name unusual [`voska--hass-mcp`]
- Single-package Python with `server.py`, `mcp.py`, `config.py`, utility modules [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Single-package Python core + TypeScript companion (likely docs/UI) [`utensils--mcp-nixos`]
- Single-package Rust — `src/`, `tests/`, `docs/`, `wix/`, `Dockerfile`, `Makefile.toml`, `Cargo.toml/Cargo.lock` [`rust-mcp-stack--rust-mcp-filesystem`]
- Single-package Go library — root-level `client.go`, `server.go`, `doc.go`; subdirectories `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example` [`viant--mcp`]
- Single-package with auxiliary folders: `src`, `tests`, `deploy`, `scripts`, `resources`, `eslint-rules`, `api-extractor` [`mongodb-js--mongodb-mcp-server`]
- Single-package Python project with `src/`, `tests/`, `pyproject.toml`, `uv.lock` [`motherduckdb--mcp-server-motherduck`]
- Single package under `src/cve_mcp/` with `api/` (12 client modules), `cache/sqlite_cache.py`, `utils/` (validators, risk_scorer), `models.py`, `audit.py`, `config.py`, `server.py` [`mukul975--cve-mcp-server`]
- Single-package Python; primary `kotlin_mcp_server.py` (unified 32-tool server, ~112 KB monolith); `vscode_bridge.py` HTTP REST bridge [`normaltusker--kotlin-mcp-server`]
- Single package under `src/`; separate `tests/` and `integration_tests/`; `docs/` [`opensearch-project--opensearch-mcp-server-py`]
- Single-package `paper_search_mcp/` + `claude-code/` skill sibling + `tests/` + `docs/` [`openags--paper-search-mcp`]

### Multi-directory single-repo

- Distinct concerns split: `src/<pkg>/` core, `mcp-server/` packaging, `webapp/` monitoring dashboard, `monitoring/` health/metrics, `tests/`, `examples/`, `scripts/`, `.github/workflows/` [`sandraschi--email-mcp`]

### Hosted-app layout (not pure single-package)

- `landing/` Next.js app with `app/api/` transport + OAuth endpoints; `mcp-src/` server/tools/handlers; `lib/` OAuth/config helpers; `landing/tests/` test suites; `.claude/skills/` [`neondatabase--mcp-server-neon`]

### Monorepo

- pnpm workspaces — `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n`; configs `pnpm-workspace.yaml`, `package.json`, `tsconfig.json`, `eslint.config.js`, `prettier.config.mjs`; `.changeset/` for changesets versioning [`upstash--context7`]
- `/servers/` subdirectories containing individual server implementations, each with dedicated README, `pyproject.toml`, source. Root has documentation (`README.md`, `CITATION.cff`), config (`pyproject.toml`, `uv.lock`), assets, web (`index.html`, `CNAME` for GitHub Pages) [`pathintegral-institute--mcp.science`]

### Config-only repository

- No server implementation, just per-host configs [`slackapi--slack-mcp-plugin`]

### `src/`-layout vs flat

- `src/`-layout — `designcomputer--mysql_mcp_server`, `feiskyer--mcp-kubernetes-server`
- Flat package — `echelon-ai-labs--servicenow-mcp` (top-level `servicenow_mcp/`)
- Flat — main server file at repo root, `src/<pkg>/` for helpers [`shreyaskarnik--huggingface-mcp-server`]
- No package, top-level `main.py` only — `duolingo--slack-mcp`. "Module entry `main:main` (top-level, no package) — unusual; most servers use a nested package module path"

### Domain-per-module decomposition

- One module per domain area for a REST-API-wrapping server (account, workspace, run, plan, apply, project, organization) [`severity1--terraform-cloud-mcp`]

### Module-naming oddities

- Bare `app` module instead of `hass_mcp` [`voska--hass-mcp`]
- Separate `mcp.py` and `server.py` — likely splits MCP-protocol surface from HTTP/business-logic surface [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Monolith vs modular

- Monolithic single-file server — `kotlin_mcp_server.py` (~112 KB) [`normaltusker--kotlin-mcp-server`]
- Single `server.py` with 27 decorated tools (rather than per-category module splits) [`mukul975--cve-mcp-server`]

## Python-specific

### Build backend

- `hatchling.build` — `designcomputer--mysql_mcp_server`, `motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`, `pathintegral-institute--mcp.science`, `sandraschi--email-mcp`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`
- `setuptools.build_meta` — `duolingo--slack-mcp`. "Setuptools backend (minority in the Python sample; hatchling dominant)"
- pyproject.toml with uv (build backend not surfaced) — `feiskyer--mcp-kubernetes-server`, `severity1--terraform-cloud-mcp`
- Not surfaced (uv-backed) [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`]
- Likely hatchling given uv convention [`shreyaskarnik--huggingface-mcp-server`]
- Not captured [`echelon-ai-labs--servicenow-mcp`, `mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server`, `opensearch-project--opensearch-mcp-server-py`]
- `pyproject.toml`, backend not surfaced [`utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Legacy `setup.py` only (no pyproject.toml) — pre-modern packaging [`twolven--mcp-server-puppeteer-py`]
- No `pyproject.toml` at all — installation is entirely orchestrated by a bespoke script [`samuelgursky--davinci-resolve-mcp`]

### Lock file / version manager

- `uv.lock` present, uv convention — `duolingo--slack-mcp`, `feiskyer--mcp-kubernetes-server` (implied), `motherduckdb--mcp-server-motherduck`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science` (root), `sajal2692--mcp-weaviate` (likely), `sandraschi--email-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server` (likely), `zilliztech--mcp-server-milvus`
- `uv.lock` implied but not confirmed [`openags--paper-search-mcp`]
- `.python-version` file referenced [`voska--hass-mcp`]
- pip (`pip install -e .`) — `echelon-ai-labs--servicenow-mcp` ("more conservative than the uv/uvx-heavy trend among newer servers")
- Lock file not noted; uses uv/uvx — `designcomputer--mysql_mcp_server` (also has legacy `pytest.ini` + `requirements-dev.txt` coexisting with pyproject.toml — older Python project layout; most newer projects in the corpus consolidate into pyproject.toml)
- `requirements.txt` primary [`normaltusker--kotlin-mcp-server`] — no lock file confirmed
- None — venv managed by a bespoke installer [`samuelgursky--davinci-resolve-mcp`]
- None [`twolven--mcp-server-puppeteer-py`]
- Not surfaced [`mukul975--cve-mcp-server`, `utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Version manager convention

- uv [`motherduckdb--mcp-server-motherduck`, `opensearch-project--opensearch-mcp-server-py`, `openags--paper-search-mcp`, `pathintegral-institute--mcp.science`, `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- uv + uvx [`voska--hass-mcp`, `zilliztech--mcp-server-milvus`]
- uv + nix [`utensils--mcp-nixos`]
- pip + uvx [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- pip / uv compatible [`mukul975--cve-mcp-server`]
- Plain pip + `python3 install.py` orchestrates [`normaltusker--kotlin-mcp-server`]
- Plain pip inside a venv managed by `install.py` [`samuelgursky--davinci-resolve-mcp`]
- pip + `requirements.txt` only — pre-modern [`twolven--mcp-server-puppeteer-py`]

### Schema / type strategy

- FastMCP auto-derives — `duolingo--slack-mcp`, `motherduckdb--mcp-server-motherduck`
- Pydantic via FastMCP — auto-derived from signatures [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `openags--paper-search-mcp` (Pydantic via FastMCP / MCP SDK; schema auto-derived)]
- Pydantic via raw MCP SDK [`shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Pydantic via FastMCP, schema auto-derived from type hints [`zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- mypy-checked + FastMCP auto-derived schemas [`utensils--mcp-nixos`]
- Pydantic likely arrives via `mcp[cli]` extra; not confirmed [`voska--hass-mcp`]
- Pydantic v2 hand-authored models (`CVERecord`, `KEVEntry`, `EPSSScore`, etc.) with custom validators [`mukul975--cve-mcp-server`]
- Modern Python type hints inferred [`opensearch-project--opensearch-mcp-server-py`]
- MyPy strict; hand-authored schemas likely given raw MCP SDK usage [`normaltusker--kotlin-mcp-server`]
- Hand-authored schemas (low-level SDK) — `designcomputer--mysql_mcp_server` (likely)
- Hand-authored — likely given raw SDK + 324 method surface [`samuelgursky--davinci-resolve-mcp`]
- Raw `mcp` SDK — hand-authored schemas likely [`twolven--mcp-server-puppeteer-py`]
- Not surfaced [`echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`]

### Async/sync style

- Sync subprocess wrapping — `feiskyer--mcp-kubernetes-server` ("wraps kubectl/helm subprocess calls. The underlying kubectl/helm wrapping is synchronous subprocess. Sync subprocess wrapping rather than using the kubernetes-client async Python library")
- Starlette suggests async — `echelon-ai-labs--servicenow-mcp` (SSE path)
- Async — FastMCP-driven; weaviate-client's async surface used; aiosmtplib-style connection pooling [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Sync — domain library is sync-only (sklearn) and wrapping it async would introduce thread complexity for no benefit [`shibuiwilliam--mcp-server-scikit-learn`]
- Mixed — MCP SDK accepts both [`shreyaskarnik--huggingface-mcp-server`]
- Sync inherited from a binary scripting module — DaVinci Resolve's Python bindings are Lua-derived synchronous [`samuelgursky--davinci-resolve-mcp`]
- Playwright is async — tools likely `async def` (no test framework to confirm) [`twolven--mcp-server-puppeteer-py`]
- httpx + MCP SDK — likely async [`voska--hass-mcp`]
- FastMCP-standard mix; `pymilvus` client calls generally sync [`zilliztech--mcp-server-milvus`]
- Likely async (FastMCP + httpx) [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Fully async/await throughout; httpx-based async I/O; aiosqlite for cache [`mukul975--cve-mcp-server`]
- Async (httpx + asyncio); FastMCP-standard [`openags--paper-search-mcp`]
- pytest_asyncio configured; async tool execution stated in README [`normaltusker--kotlin-mcp-server`]
- FastMCP 2.14 supports both sync and async signatures (exact repo style not inspected) [`motherduckdb--mcp-server-motherduck`]
- Not surfaced [`duolingo--slack-mcp`, `designcomputer--mysql_mcp_server`, `utensils--mcp-nixos`]

### Dev toolchain

- ruff in dev extra [`duolingo--slack-mcp`]
- ruff + mypy [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`]
- ruff + black + mypy [`severity1--terraform-cloud-mcp`]
- Ruff + MyPy + Bandit (security) + Biome (webapp) [`sandraschi--email-mcp`]

### Dev dep placement

- `ruff` pinned in project-level dependencies rather than dev extra — blurs lint tooling into runtime install, adds weight for end users [`zilliztech--mcp-server-milvus`]
- `[dev]` optional extra [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Mixed-language packaging

- `Cargo.toml` alongside `pyproject.toml` — Rust artifacts for MCPB bundle signing [`sandraschi--email-mcp`]

### Notable Python-stack choices

- `defusedxml + aiosqlite + Pydantic v2` — tighter security/typing baseline than most community MCP servers [`mukul975--cve-mcp-server`]
- `httpx[socks]` for SOCKS-proxy support — reflects real-world scraping/proxy needs for Google Scholar [`openags--paper-search-mcp`]
- `pypdf + lxml + beautifulsoup4` in core deps — paper ingestion does PDF parse and HTML/XML handling in-process rather than deferring to external services [`openags--paper-search-mcp`]
- Tight upper-bounded SDK pin `fastmcp>=2.14,<3` — keeps breaking-change surface bounded [`motherduckdb--mcp-server-motherduck`]
- Loose unpinned `fastmcp` — likely follows latest; potential fragility [`openags--paper-search-mcp`]
- Carries both `mcp` + `fastmcp` as dependencies — unusual; most repos pick one [`normaltusker--kotlin-mcp-server`, `openags--paper-search-mcp`]
- Broad Python version range (3.8–3.12 targeted) — inclusive floor for compatibility [`normaltusker--kotlin-mcp-server`]
- Massive single-file `kotlin_mcp_server.py` (~112 KB) — monolith architecture [`normaltusker--kotlin-mcp-server`]
- Hatch `force-include` directive for monorepo build — non-standard Hatch configuration [`pathintegral-institute--mcp.science`]
- `uv.lock` committed alongside `pyproject.toml` for reproducible dev envs [`opensearch-project--opensearch-mcp-server-py`]

## Notable structural choices

Cross-cutting design decisions worth elevating, including unanticipated divergence axes.

### Per-verb capability gating

- Granular per-capability CLI toggles (`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`) instead of a single read-only/full switch. "Four-way verb disable flags is a denial-ish denominator for capability gating" [`feiskyer--mcp-kubernetes-server`]

### Two-axis safety toggles

- Read-only and delete-enabling are independent toggles, not collapsed into one write-mode flag [`severity1--terraform-cloud-mcp`]

### Read-only by default

- Server starts in least-privilege mode; write access opt-in [`rust-mcp-stack--rust-mcp-filesystem`, `shreyaskarnik--huggingface-mcp-server`]

### Read-only server pattern

- Explicit read-only design (5 tools, no write capabilities) [`duolingo--slack-mcp`]

### Migration review pattern

- Start/commit migration pattern: agents prepare migrations for human review before applying [`neondatabase--mcp-server-neon`]

> Read-only / index-check / confirmation-required gating consolidated under Capabilities exposed → Tool gating mechanisms.

### Tool catalog as data file

- `tools.json`/`tools.txt` ship tool definitions outside source. "Declarative catalog rather than inline schemas in source — opens an authoring path that doesn't require TS expertise" [`docker--hub-mcp`]

### Architectural transport split vs single-binary multi-transport

- Separate console scripts per transport rather than env-var-switched. "A cleaner separation but more install-time ceremony" [`echelon-ai-labs--servicenow-mcp`]
- `--port` switches between stdio and HTTP from one binary. Direct contrast with the architectural split pattern [`executeautomation--mcp-playwright`]

### Container as the only artifact

- Both ship Docker as the only/primary distribution channel; for `duolingo`, this "inverts the typical Python packaging path" [`elastic--mcp-server-elasticsearch`, `duolingo--slack-mcp`]

### LLM-targeted in-repo documentation

- `llm_mcp_docs.txt` (411.7 KB) shipped as in-repo doc designed for LLM ingestion [`exa-labs--exa-mcp-server`]

### Vertical / domain-specific skills as first-class shipping artifact

- Skills directory with company research, code search, people research, financial reports, academic papers shipped alongside the server [`exa-labs--exa-mcp-server`]
- Ships `Skills` folder and `rules` folder alongside the MCP server in the same monorepo [`upstash--context7`]

### Co-located Claude Code skills

- `claude-code/` skill files alongside the MCP server [`openags--paper-search-mcp`]
- `.claude/skills/` checked into repo [`neondatabase--mcp-server-neon`]

### Vendor-specific companion config

- `gordon-mcp.yml` pre-shaping config for Docker's Ask Gordon agent [`docker--hub-mcp`]

### Built-in security guidance in README

- "least-privilege user, never commit credentials" baked into README. Security guidance as a first-class README element [`designcomputer--mysql_mcp_server`]

### Remote-hosted endpoint as primary

- `https://mcp.exa.ai/mcp` as primary distribution; reduces setup friction. Native Claude Desktop connector eliminates manual config [`exa-labs--exa-mcp-server`]

### Hosted-first vs local-first

- Remote-hosted with OAuth as primary auth — Next.js bundles landing page, OAuth UI, and MCP endpoint together [`neondatabase--mcp-server-neon`]
- Local-process default — most other samples

### Lifecycle declaration in README

- Explicit deprecation notice in README; "the project is superseded by Elastic Agent Builder in ES 9.2.0+". A deprecation-status axis most repos don't surface [`elastic--mcp-server-elasticsearch`]

### High distribution-channel count

- npm + mcp-get + Smithery + Docker — four distribution mechanisms; flagged as "a reference for 'how many channels to publish to' decisions" [`executeautomation--mcp-playwright`]

### Dual-mode tool surface

- Context-efficient compound vs full granular, user-selectable at launch [`samuelgursky--davinci-resolve-mcp`]

### Tool disabling / surface scoping

- CLI tool disable to reduce token usage in narrow workflows [`rust-mcp-stack--rust-mcp-filesystem`]
- Category-based enable/disable via env vars rather than per-tool [`opensearch-project--opensearch-mcp-server-py`]
- URL query param tool filtering [`neondatabase--mcp-server-neon`]
- Per-request header/query overrides (`--allowRequestOverrides=true`) [`mongodb-js--mongodb-mcp-server`]

### Lazy connection / auto-launch

- Auto-reconnect and auto-launch of the underlying app on first tool call, smoothing cold-start UX [`samuelgursky--davinci-resolve-mcp`]

### Path-traversal protection

- File-op tools validate paths stay within expected directories [`samuelgursky--davinci-resolve-mcp`]

### Disk-bloat protection

- Auto-cleanup of exports after response encoding to prevent disk bloat [`samuelgursky--davinci-resolve-mcp`]
- Export-artifact resource with auto-cleanup (default 5 min) [`mongodb-js--mongodb-mcp-server`]

### Cross-platform sandbox handling

- Temp paths redirected per-OS (macOS/Linux/Windows) [`samuelgursky--davinci-resolve-mcp`]

### Multi-stage Docker for minimal image

- Multi-stage Docker build to a non-root static-binary alpine final image [`rust-mcp-stack--rust-mcp-filesystem`]

### Runtime backend reconfiguration

- Via a tool call rather than a restart [`sandraschi--email-mcp`]

### Multi-backend unified surface (cross-cutting)

- One tool dispatches to many providers; heterogeneity hidden from the caller [`sandraschi--email-mcp`]
- 21 upstream APIs behind 27 MCP tools, each API key optional with graceful degradation [`mukul975--cve-mcp-server`]
- 20+ academic backends multiplexed through a common tool surface with uniform env-var prefix convention [`openags--paper-search-mcp`]

### Per-tenant tools as first-class concept

- Tenancy is an argument, not server config [`sajal2692--mcp-weaviate`]

### Three-MCP-surface adoption with custom URI

- All three MCP surfaces (tools + resources + prompts) plus a custom URI scheme — uncommon among Python servers [`shreyaskarnik--huggingface-mcp-server`]

### Author quality-tier framing

- "Industrial Quality Stack" / "SOTA 14.1" framing — author self-labels quality tiers; idiosyncratic and may be marketing rather than engineering signal [`sandraschi--email-mcp`]

### Cross-language port

- Author-cross-language port — Rust rewrite of the official JavaScript `@modelcontextprotocol/server-filesystem` for performance [`rust-mcp-stack--rust-mcp-filesystem`]

### Headless vs non-headless browser mode

- Deliberately non-headless for easier debugging — trades production efficiency for interactive visibility [`twolven--mcp-server-puppeteer-py`]

### In-memory binary handoff

- In-memory base64-encoded screenshot storage — flows through MCP responses without disk intermediate [`twolven--mcp-server-puppeteer-py`]

### User-approval framing

- README explicitly calls out user approval before message sending — reflects trust concern of letting LLM post to public surfaces [`v-3--discordmcp`]

### Public client + private backend

- Public MCP repo distinct from private backend (API, parsing, crawling engines) — disclosing-vs-withholding-implementation axis [`upstash--context7`]

### Bridge-binary alternative to library embedding

- Standalone bridge binary gives non-Go consumers an MCP-to-tool bridge without Go embedding [`viant--mcp`]

### Two-dep minimalism

- `mcp[cli]` + `httpx` only — minimal abstraction over backend REST API [`voska--hass-mcp`]

### Concurrent dual protocol exposure

- HTTP bridge bundled in-process alongside MCP — server speaks two protocols at once, on by default [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Changesets-based release discipline

- Monorepo coordinated releases via `.changeset/` [`upstash--context7`]

### Env-vs-CLI precedence inversion

- Env > CLI inversion (most servers do CLI > env); reflects bias toward reproducible host-config-driven deployments [`zilliztech--mcp-server-milvus`]

### Token-efficiency tool design

- Few-but-broad tools deliberately — 2 tools where peers offer 50–250 [`utensils--mcp-nixos`]

### Stateless vs stateful HTTP

- Stateless HTTP transport flag separates cacheable deployments from stateful ones [`utensils--mcp-nixos`]

### Declarative-config distribution

- nixpkgs as a first-class install channel — declarative install path rare among MCP servers [`utensils--mcp-nixos`]

### Source-only TypeScript posture

- TS project with no npm publish; clone-and-build only [`v-3--discordmcp`]

### Marketplace metadata as plugin integration

- `.claude-plugin/marketplace.json` (not `plugin.json`) — marketplace-style integration distinct from full plugin wrapper [`upstash--context7`]

### OAuth2 client-side automatic token acquisition

- Automatic token acquisition on 401 response — unusual client-side feature [`viant--mcp`]

### Aggressive Python version floor

- 3.13 floor on a popular production server — uncommon [`voska--hass-mcp`]

### Pre-modern Python packaging

- `setup.py` only, no pyproject.toml — only legacy server in this corpus [`twolven--mcp-server-puppeteer-py`]

### Ruff in runtime deps

- Lint tooling pinned in `[project.dependencies]` rather than dev extras [`zilliztech--mcp-server-milvus`]

### Credential lifecycle

- Temporary auto-generated DB users with configurable TTL (default 4h) instead of long-lived DB credentials [`mongodb-js--mongodb-mcp-server`]

### Audit / hardening

- Rotating JSON audit log with explicit redaction of API keys and response payloads [`mukul975--cve-mcp-server`] — security-conscious by default
- defusedxml usage for XML-bomb hardening (explicitly tested) [`mukul975--cve-mcp-server`]
- Bandit security scans excluding tests [`normaltusker--kotlin-mcp-server`]
- Server-side rate limiting + circuit breaker + audit logging [`normaltusker--kotlin-mcp-server`]

### Caching tier

- SQLite TTL cache layer per call (cross-cutting module inside the MCP server) [`mukul975--cve-mcp-server`]
- Token-bucket rate-limiter module for NVD throttling [`mukul975--cve-mcp-server`]

### Monorepo dispatcher

- Single PyPI package routes to multiple servers via CLI subcommand — Hatch `force-include` directive pulls `mcp_science/servers` into the wheel; custom monorepo build shape rather than workspace-based approach [`pathintegral-institute--mcp.science`]

### Bespoke installer scripts

- `python3 install.py` interactive installer with 3 modes (portable / system / module); auto-generates IDE config files — bespoke installer replacing pip [`normaltusker--kotlin-mcp-server`]
- Custom `install.py` walks every supported client and writes per-client JSON to that client's standard config location [`samuelgursky--davinci-resolve-mcp`]

### Intelligent proxy / transformation systems

- v2.0 proxy architecture with intelligent transformations; "complete, context-aware implementations" rather than stubs [`normaltusker--kotlin-mcp-server`]

### LSP-like / IDE-bridge

- HTTP REST API bridge (`vscode_bridge.py`) on port 8080 — separate process surface for IDE-native integration [`normaltusker--kotlin-mcp-server`]
- Auto-generated IDE config files per IDE (Claude Desktop, VS Code, Cursor, JetBrains, generic) [`normaltusker--kotlin-mcp-server`]

### KB-search / docs-retrieval embedded

- Assistant/KB search tools embed MongoDB documentation retrieval into the same server [`mongodb-js--mongodb-mcp-server`]
- Discovery tools (search/docs fetch) [`neondatabase--mcp-server-neon`]

### Stream-processing capabilities

- Atlas Stream Processing tool surface [`mongodb-js--mongodb-mcp-server`]

### Specialized scientific compute

- DFT (GPAW), Wolfram Language, Jupyter kernel interaction — uncommon in MCP ecosystem [`pathintegral-institute--mcp.science`]

### Codebase-scale discipline

- Custom eslint rules shipped in repo [`mongodb-js--mongodb-mcp-server`]
- API extractor for API docs [`mongodb-js--mongodb-mcp-server`]
- MyPy strict + Bandit + Black + isort [`normaltusker--kotlin-mcp-server`]

### Fine-grained authorization (experimental)

- Experimental fine-grained tool/resource control — suggests multi-user workspace scenarios being designed for [`viant--mcp`]

## Unanticipated axes observed

### Audit log as a capability surface

Rotating JSON audit log surfaced as a capability (structured fields, key redaction), not just ops telemetry [`mukul975--cve-mcp-server`].

### Per-source key optionality with graceful degradation

21 independent integrations, each testable alone, each optional [`mukul975--cve-mcp-server`] — a distinct design discipline for aggregator servers.

### Scope-based tool filtering via URL param

Notable alternative to env-var tool lists [`neondatabase--mcp-server-neon`].

### Database switching as feature flag

Multi-database workflows via `--allow-switch-databases` [`motherduckdb--mcp-server-motherduck`].

### Web E2E with Playwright + ephemeral DB

Contrasts with most MCP servers that test only in unit/integration [`neondatabase--mcp-server-neon`].

### Domain specialization (rare niches)

- Android/Kotlin-specific MCP server [`normaltusker--kotlin-mcp-server`] — most servers are language-agnostic
- Scientific computing (DFT, Wolfram, Jupyter) [`pathintegral-institute--mcp.science`] — academic publication focus with `CITATION.cff`
- 21 security data sources behind one server [`mukul975--cve-mcp-server`] — security-research aggregator

### IDE bridge sidecar

HTTP REST bridge as a separate process surface for IDE-native integration [`normaltusker--kotlin-mcp-server`] — pattern beyond MCP transport.

### Compliance modes baked in

GDPR, HIPAA modes mentioned [`normaltusker--kotlin-mcp-server`] — compliance-specific operation modes encoded in the server.

### Monitoring server as separable sidecar

Health endpoint as a separable sidecar for HTTP mode [`mongodb-js--mongodb-mcp-server`].

### Externally-managed sessions

`mcp-session-id` header support when `EXTERNALLY_MANAGED_SESSIONS=true` lets the host control session identity [`mongodb-js--mongodb-mcp-server`].

### Citation metadata

`CITATION.cff` for academic publication focus — uncommon in MCP ecosystem [`pathintegral-institute--mcp.science`].

### Configs-as-product

The GitHub repo ships only configs; the actual MCP server is a remote HTTP service [`slackapi--slack-mcp-plugin`].

## Domain-imposed constraints

### External ABI-driven version ceilings

- Python 3.10–3.12 inclusive — Resolve's binary scripting module is incompatible with 3.13+; the MCP inherits the application's ABI floor and ceiling [`samuelgursky--davinci-resolve-mcp`]

### Free-edition exclusion

- Resolve Studio 18.5+ required; the free edition has no scripting API and is unsupported. The MCP inherits the application's licensing constraint [`samuelgursky--davinci-resolve-mcp`]

### Local-app-required

- Server must run on the same host as the controlled application; Docker is intentionally absent because it would break the local-app contract [`samuelgursky--davinci-resolve-mcp`]

### Local-data-only

- Server operates on local filesystems / local datasets / local models — no remote auth or remote state [`rust-mcp-stack--rust-mcp-filesystem`, `shibuiwilliam--mcp-server-scikit-learn`]

## State lifecycle

### Trained-model persistence as a tool surface (ML-specific)

- Exposing an ML training pipeline over MCP raises a state-lifecycle question (where do trained models persist? who owns them?) that the tool surface implicitly answers via `model_persistence` tools [`shibuiwilliam--mcp-server-scikit-learn`]

## License

- MIT — `designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `mukul975--cve-mcp-server`
- Apache-2.0 — `docker--hub-mcp`, `duolingo--slack-mcp`, `elastic--mcp-server-elasticsearch`, `feiskyer--mcp-kubernetes-server` ("Apache-2.0 license — rarer for independent-maintainer MCP servers, which skew MIT"), `mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `neondatabase--mcp-server-neon`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science`
- AGPL-3.0 — uncommon in MCP corpus [`normaltusker--kotlin-mcp-server`]
- pyproject license field not present despite README MIT badge [`voska--hass-mcp`]
- License may not be specified because the repo holds no implementation [`slackapi--slack-mcp-plugin`]

## Default branch

- `main` — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`
- `master` — `duolingo--slack-mcp`

## Star counts (popularity)

- Bin 5: 7 [`duolingo--slack-mcp`], 16 [`feiskyer--mcp-kubernetes-server`], 137 [`docker--hub-mcp`], 241 [`echelon-ai-labs--servicenow-mcp`], 646 [`elastic--mcp-server-elasticsearch`], 1.2k [`designcomputer--mysql_mcp_server`], 4.3k [`exa-labs--exa-mcp-server`], 5.5k [`executeautomation--mcp-playwright`]
- Bin 9: 28 [`normaltusker--kotlin-mcp-server`], 120 [`opensearch-project--opensearch-mcp-server-py`], 128 [`pathintegral-institute--mcp.science`], 257 [`mukul975--cve-mcp-server`], 468 [`motherduckdb--mcp-server-motherduck`], 587 [`neondatabase--mcp-server-neon`], ~1000 [`mongodb-js--mongodb-mcp-server`], ~1200 [`openags--paper-search-mcp`]
- Bin 11/13 (selected): 287 [`voska--hass-mcp`], 833 [`samuelgursky--davinci-resolve-mcp`]

## Gaps observed

### Across bins (recurring)

- Python version floor and PyPI publication status frequently unconfirmed in extracted content
- Logging destination/format almost universally undocumented
- Last-commit date and CI trigger details often not surfaced
- Whether multi-backend servers share a common abstraction internally or use per-provider adapters typically not externally documented [`sandraschi--email-mcp`]
- Exact CI workflow triggers / contents — flagged by `mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server`, `openags--paper-search-mcp`
- Last-commit dates not surfaced [`neondatabase--mcp-server-neon`, `openags--paper-search-mcp`, `normaltusker--kotlin-mcp-server`]
- Exact SDK version pins / `requires-python` floors not surfaced [`opensearch-project--opensearch-mcp-server-py`, `mukul975--cve-mcp-server`]

### Per-sample gaps / unknowns

- Last commit dates not extracted [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Backend architecture intentionally private [`upstash--context7`]
- HTTP bridge internals not inspected — is it `streamable-http`, `sse`, or custom FastAPI? [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Exact tool count / use of resources or prompts not captured [`voska--hass-mcp`]
- Go version constraints not documented in CI [`viant--mcp`]
- Docker artifacts absent despite Milvus typically being containerized [`zilliztech--mcp-server-milvus`]
- Whether server protects Python stdout from log pollution (stdio JSON-RPC correctness) [`twolven--mcp-server-puppeteer-py`]
- Changelog/release notes not visible in README [`upstash--context7`]
- Logging destination + format (requires code inspection) [`motherduckdb--mcp-server-motherduck`]
- Console-script names not surfaced [`opensearch-project--opensearch-mcp-server-py`]
- Dockerfile existence ambiguous [`mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server`]
- Test framework / fixture style not surfaced [`opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science`]
- `.claude-plugin` wrapper shape ambiguous [`motherduckdb--mcp-server-motherduck`]
- HTTP bridge transport implementation details [`normaltusker--kotlin-mcp-server`]
- v2.0 proxy architecture not fully explained [`normaltusker--kotlin-mcp-server`]
