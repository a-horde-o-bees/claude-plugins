# Sample

Pass-1 Phase-1a partial for bin 13. Atomic knowledge chunks from twolven--mcp-server-puppeteer-py, upstash--context7, utensils--mcp-nixos, v-3--discordmcp, viant--mcp, voska--hass-mcp, zilliztech--mcp-server-milvus, zongmin-yu--semantic-scholar-fastmcp-mcp-server, organized by divergence axes. Phase-1b merger will unify with other partials.

## Language and runtime

### Python

#### Python version floor

- 3.8+ — legacy/setup.py-era servers ([`twolven--mcp-server-puppeteer-py`])
- 3.10+ — modern mainstream floor ([`zilliztech--mcp-server-milvus`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- 3.11+ — slightly raised floor ([`utensils--mcp-nixos`])
- 3.13+ — aggressive cutting-edge floor on a popular production server (287 stars); flagged as uncommon ([`voska--hass-mcp`])

#### SDK / framework variant

- raw `mcp` SDK / `mcp[cli]` — minimal abstraction, hand-authored schemas ([`twolven--mcp-server-puppeteer-py`], [`voska--hass-mcp`])
- FastMCP (1.x or unspecified) — Pydantic via FastMCP, schema auto-derived ([`utensils--mcp-nixos`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- FastMCP 2.x — explicit `fastmcp >= 2.14.1` pin ([`zilliztech--mcp-server-milvus`])

#### MCP SDK version pinning practice

- older pin `mcp[cli]>=1.4.1` on a recent server — version drift from current SDK ([`voska--hass-mcp`])
- lower-bound only, no upper-bound ([`zilliztech--mcp-server-milvus`])

### TypeScript / Node.js

- Node 16.x+ floor ([`v-3--discordmcp`])
- Pure TypeScript with MCP TypeScript SDK ([`v-3--discordmcp`])
- TypeScript 91% + JavaScript 8.5%, monorepo with pnpm workspaces ([`upstash--context7`])

### Go

- Go MCP SDK with no explicit version constraint specified ([`viant--mcp`])
- JSON-RPC 2.0 communication base explicitly named ([`viant--mcp`])

### Mixed-language

- Python 74% + TypeScript 22% + Nix 1% — Python core with TypeScript companion (likely docs/UI) ([`utensils--mcp-nixos`])

## Transport

### Supported transports

#### stdio only

- single-file Python script invoked by host ([`twolven--mcp-server-puppeteer-py`])
- TypeScript bot wrapped via stdio to host ([`v-3--discordmcp`])
- Docker-wrapped stdio ([`voska--hass-mcp`])

#### stdio + HTTP/SSE

- stdio default + SSE option, separate JSON config blocks per mode ([`zilliztech--mcp-server-milvus`])
- stdio + HTTP + Docker-wrapped, transport selected via env vars ([`utensils--mcp-nixos`])

#### Multi-transport library

- HTTP/SSE + Streamable HTTP + Stdio, configured via functional options pattern (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`) and separate entry points (`stdioSrv.ListenAndServe()` / `srv.HTTP()`) ([`viant--mcp`])

#### Dual-protocol same process (rare)

- stdio MCP + HTTP REST bridge running in same process simultaneously ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]); HTTP bridge is enabled by default, making the server usable by non-MCP clients out of the box. Distinct from "pick a transport" — this is two protocols at once
- MCP native + CLI + Skills (without MCP) + HTTP REST backend ([`upstash--context7`])

### How transport is selected

- environment variables — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP` ([`utensils--mcp-nixos`])
- env var toggle for secondary protocol — `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE` ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- CLI flag / env var with separate JSON configs per mode ([`zilliztech--mcp-server-milvus`])
- functional options at construction time (Go) ([`viant--mcp`])
- implicit stdio — launched via direct script invocation, no flag ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`])

### Stateless HTTP mode

- explicit `MCP_NIXOS_STATELESS_HTTP` flag for shared/multi-user deployments ([`utensils--mcp-nixos`])

## Distribution

### Distribution channels observed

#### PyPI / pip

- `pip install <pkg>` — straightforward Python channel ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`], [`utensils--mcp-nixos`])

#### uvx

- `uvx mcp-nixos` ([`utensils--mcp-nixos`])
- `uvx hass-mcp` (alongside Docker) ([`voska--hass-mcp`])
- `uvx semantic-scholar-fastmcp` ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

#### npx / npm

- `npx ctx7 setup` (recommended, OAuth + API key automation) ([`upstash--context7`])

#### Docker / OCI

- Docker Hub `voska/hass-mcp:latest` — primary channel; README leads with `docker pull` ([`voska--hass-mcp`])
- ghcr.io `ghcr.io/utensils/mcp-nixos` ([`utensils--mcp-nixos`])
- Dockerfile + docker-compose orchestration shipped ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

#### Source-only / clone-and-build

- TypeScript `npm install` + `npm run build` with no npm publish ([`v-3--discordmcp`])
- Python clone-only with `pip install -r requirements.txt` ([`twolven--mcp-server-puppeteer-py`])
- Source tree + `uv run src/...` (rather than installed console script) ([`zilliztech--mcp-server-milvus`])

#### go get

- `go get github.com/viant/mcp` for embedding library use ([`viant--mcp`])

#### Standalone bridge binary

- bridge binary distributed as alternative to embedding the Go library ([`viant--mcp`])

#### Hosted MCP HTTP endpoint

- `https://mcp.context7.com/mcp` — manual config option as alternative to local install ([`upstash--context7`])

#### Declarative install (Nix-native)

- `nix run github:utensils/mcp-nixos` (uses Nix flake) ([`utensils--mcp-nixos`])
- Nix flake + declarative NixOS / Home Manager module via nixpkgs entry — flagged as rare for MCP servers ([`utensils--mcp-nixos`])

### Distribution posture axis

- source-only (clone + build) vs published package — TypeScript projects sometimes choose source-only ([`v-3--discordmcp`])
- published package vs hosted MCP endpoint — Context7 offers both ([`upstash--context7`])
- public client + private backend — Context7 keeps API/parsing/crawling engines private ([`upstash--context7`])

## Entry point / launch

### Launch command shapes

#### Direct script invocation

- `python puppeteer.py` — single-file at repo root ([`twolven--mcp-server-puppeteer-py`])
- `node build/index.js` (production) and `npm run dev` (development) ([`v-3--discordmcp`])
- `uv run src/mcp_server_milvus/server.py --milvus-uri ...` — uv-run against checked-out source tree, unusual; most servers use `uvx <package>` ([`zilliztech--mcp-server-milvus`])

#### Console script after install

- `mcp-server-milvus` ([`zilliztech--mcp-server-milvus`])
- `hass-mcp` → `app.run:main` ([`voska--hass-mcp`])
- `mcp-nixos` ([`utensils--mcp-nixos`])
- `semantic-scholar-mcp-server` ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

#### CLI subcommand pattern

- `npx ctx7 setup`, `ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>` — multi-verb CLI ([`upstash--context7`])

#### Library embedding (no entry point)

- Go: server constructed and run from app code via `stdioSrv.ListenAndServe()` or `srv.HTTP(ctx, ":4981").ListenAndServe()` ([`viant--mcp`])

### Entry-point inconsistencies (anti-pattern)

- README runs `python puppeteer.py` while setup.py declares `mcp-server-puppeteer=mcp_server_puppeteer.server:main` — declared and actual entry diverge; neither tested against PyPI ([`twolven--mcp-server-puppeteer-py`])
- Module name `app` (bare) rather than conventional `hass_mcp` package — suggests template-derived structure that wasn't renamed ([`voska--hass-mcp`])

### Bare `python` in host config (fragile)

- Claude Desktop config uses `"command": "python"` relying on system PATH / venv activation ([`twolven--mcp-server-puppeteer-py`])

## Configuration surface

### Configuration sources

- environment variables only ([`v-3--discordmcp`] — `DISCORD_TOKEN`; [`voska--hass-mcp`] — `HA_URL`, `HA_TOKEN`; [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`] — `SEMANTIC_SCHOLAR_API_KEY`)
- environment variables for transport selection ([`utensils--mcp-nixos`])
- `.env` + CLI args + env vars combined ([`zilliztech--mcp-server-milvus`])
- functional options at library-construction time (Go) ([`viant--mcp`])
- OAuth setup flow + API key header — `npx ctx7 setup` automates ([`upstash--context7`])
- per-tool parameters only; no global config documented ([`twolven--mcp-server-puppeteer-py`])

### Configuration precedence

- `.env` takes priority over CLI args — inverse of common "CLI overrides env"; reflects bias toward reproducible host-config-driven deployments ([`zilliztech--mcp-server-milvus`])

### CLI parsing

- `click` for CLI arg parsing despite FastMCP providing its own `fastmcp` CLI — server launched via plain Python entry point not FastMCP launcher ([`zilliztech--mcp-server-milvus`])

## Authentication

### Flow types

#### No auth

- Browser automation against public web ([`twolven--mcp-server-puppeteer-py`])
- Public NixOS endpoints ([`utensils--mcp-nixos`])

#### Bot token / long-lived token

- Discord bot token from Developer Portal ([`v-3--discordmcp`])
- Home Assistant long-lived access token via `HA_TOKEN` env ([`voska--hass-mcp`])

#### Optional API key

- `SEMANTIC_SCHOLAR_API_KEY` for higher rate limits ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- `MILVUS_TOKEN` env var ([`zilliztech--mcp-server-milvus`])

#### OAuth + API key (hybrid)

- OAuth setup via `npx ctx7 setup`; free API key registration at dashboard for higher rate limits ([`upstash--context7`])

#### OAuth2/OIDC with full SDK support

- two modes: global resource protection via bearer tokens, fine-grained tool/resource control (experimental) ([`viant--mcp`])
- client-side automatic token acquisition: "401 challenge, discovers protected resource metadata, acquires tokens and retries" — unusual for MCP servers ([`viant--mcp`])

## Multi-tenancy

### Tenancy models

- single-user single-process (one browser per process; one HA instance; one Milvus URI/DB) ([`twolven--mcp-server-puppeteer-py`], [`voska--hass-mcp`], [`zilliztech--mcp-server-milvus`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- per-user OAuth token + per-workspace API key ([`upstash--context7`])
- bot-scoped — bot's server memberships define reachable tenants; auto server/channel discovery from bot's perspective ([`v-3--discordmcp`])
- per-request via bearer token; OAuth2 discovery enables per-request tenant identification ([`viant--mcp`])
- stateless HTTP mode supports shared/multi-user deployments ([`utensils--mcp-nixos`])
- fine-grained authorization (experimental) suggests multi-user workspace scenarios being designed for ([`viant--mcp`])

## Capabilities exposed

### Tool surface size

#### Minimal (≤5 tools)

- 2 tools — `nix()` unified query (~1,030 tokens) + `nix_versions()` helper; deliberate token-efficiency strategy contrasting with 50–250-tool peers ([`utensils--mcp-nixos`])
- 2 tools — `send-message` + `read-messages`; minimal Discord surface ([`v-3--discordmcp`])
- 5 tools — `puppeteer_navigate`, `puppeteer_screenshot`, `puppeteer_click`, `puppeteer_fill`, `puppeteer_evaluate` ([`twolven--mcp-server-puppeteer-py`])

#### Mid (~15–20 tools, grouped)

- ~15 tools across text/vector/hybrid search, query, collection CRUD, insert, delete ([`zilliztech--mcp-server-milvus`])
- 16 tools organized into 4 explicit functional groups (8 paper search/discovery, 2 citation analysis, 4 author info, 2 recommendation) — categorization baked into docs structure ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

#### Compact public surface

- 2 tools — `resolve-library-id`, `query-docs` plus library/documentation cache resources ([`upstash--context7`])

### Capabilities other than tools

- resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, elicitation — full MCP capability surface as a Go SDK ([`viant--mcp`])
- library index + documentation cache as resources ([`upstash--context7`])

### Tool surface design philosophy axis

- few-but-broad tools (token efficiency) vs many-narrow tools — explicit design call ([`utensils--mcp-nixos`])
- minimal scope as trust signal — README emphasizes user-approval before sending Discord messages, reflecting awareness of agent-action-on-public-surfaces risk ([`v-3--discordmcp`])

## Observability

### Logging destination + format

- not explicitly documented ([`upstash--context7`], [`utensils--mcp-nixos`], [`voska--hass-mcp`], [`v-3--discordmcp`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- "Detailed error handling and logging" claimed without destination — likely stderr ([`twolven--mcp-server-puppeteer-py`])
- FastMCP-standard logging, no explicit metrics/tracing ([`zilliztech--mcp-server-milvus`])
- explicit `Logging()` method for log levels; progress reporting + request cancellation as separate capabilities ([`viant--mcp`])

### Stdio stdout-pollution discipline

- not stated whether Python stdout is protected from log pollution (important for stdio JSON-RPC correctness) ([`twolven--mcp-server-puppeteer-py`])

## Host integrations

### Claude Desktop

- JSON `mcpServers` entry shown — uvx form ([`utensils--mcp-nixos`])
- JSON config snippet (Docker `command`/`args` + env) ([`voska--hass-mcp`])
- JSON config snippet — uvx command ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- JSON config snippets — separate stdio and SSE variants ([`zilliztech--mcp-server-milvus`])
- JSON config example shown ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`])

### Claude Code

- native support documented as one of 30+ supported agents ([`upstash--context7`])

### Cursor

- listed as supported agent ([`upstash--context7`])
- `.cursor/` directory present + dedicated JSON snippet ([`zilliztech--mcp-server-milvus`])

### OpenAI Code

- listed as supported agent ([`upstash--context7`])

### NixOS / Home Manager

- declarative config entry available in nixpkgs ([`utensils--mcp-nixos`])

### 30+ agents broadly

- Context7 documents support across 30+ client platforms ([`upstash--context7`])

## Claude Code plugin wrapper

### Presence

- not present ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`utensils--mcp-nixos`], [`voska--hass-mcp`], [`zilliztech--mcp-server-milvus`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`], [`viant--mcp`])
- present as `.claude-plugin/marketplace.json` (marketplace metadata only, not full plugin.json) — distinct from plugin-wrapper install ([`upstash--context7`])

### Marketplace metadata vs plugin install

- `.claude-plugin/marketplace.json` is a marketplace-style integration; separate concept from a full plugin wrapper ([`upstash--context7`])

## Tests

### Presence and framework

- pytest mentioned ([`utensils--mcp-nixos`], [`voska--hass-mcp`])
- `tests/` directory present, framework not detailed ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- Go stdlib testing — `client.go` / `server.go` test patterns ([`viant--mcp`])
- monorepo test suite via `npm run test` in workspace ([`upstash--context7`])
- not observed / no test framework documented ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`zilliztech--mcp-server-milvus`])

## CI

### Presence

- GitHub Actions present, badge referenced ([`utensils--mcp-nixos`])
- GitHub Actions in `.github/`, details not extracted ([`voska--hass-mcp`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- GitHub Actions configured, typical Go test/lint workflows implied ([`viant--mcp`])
- `.github/` present with `npm run lint`, `npm run format` scripts ([`upstash--context7`])
- not observed ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`zilliztech--mcp-server-milvus`])

### CI extras

- CodeRabbit reviews used alongside GitHub Actions ([`utensils--mcp-nixos`])

## Container / packaging artifacts

### Dockerfile / image

- official image on Docker Hub as primary distribution channel ([`voska--hass-mcp`])
- ghcr.io image alongside other channels ([`utensils--mcp-nixos`])
- Dockerfile + docker-compose.yml present ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Nix-native packaging

- Nix flake for nix-native install ([`utensils--mcp-nixos`])
- Declarative NixOS / Home Manager module via nixpkgs ([`utensils--mcp-nixos`])

### None

- ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`zilliztech--mcp-server-milvus`], [`viant--mcp`])

## Example client / developer ergonomics

### MCP Inspector

- explicit Inspector launcher in README — `npx @modelcontextprotocol/inspector node build/index.js` ([`v-3--discordmcp`])
- MCP Inspector support documented + Smithery registry config ([`upstash--context7`])

### Sample host configs

- Claude Desktop JSON sample ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`voska--hass-mcp`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- Claude Desktop + Cursor JSON snippets, plus `.env` example ([`zilliztech--mcp-server-milvus`])

### Dev shells / toolchain

- `nix develop` reproducible dev shell + ruff/mypy toolchain ([`utensils--mcp-nixos`])
- `[dev]` optional extra ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- `requirements.txt` only — no lock, no dev extras ([`twolven--mcp-server-puppeteer-py`])

### Examples directory

- `/example` directory demonstrating server, auth, client, bridge binary use ([`viant--mcp`])

## Repo layout

### Single-package vs monorepo

- single-file script repo (`puppeteer.py` + `requirements.txt`) ([`twolven--mcp-server-puppeteer-py`])
- single-package TypeScript (`/src`, `package.json`, `tsconfig.json`) ([`v-3--discordmcp`])
- single-package Python (`src/mcp_server_milvus/`) ([`zilliztech--mcp-server-milvus`])
- single-package Python (`app/` module) — bare `app` name unusual ([`voska--hass-mcp`])
- single-package Python with `server.py`, `mcp.py`, `config.py`, utility modules ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- single-package Python core + TypeScript companion (likely docs/UI) ([`utensils--mcp-nixos`])
- single-package Go library — root-level `client.go`, `server.go`, `doc.go`; subdirectories `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example` ([`viant--mcp`])
- monorepo with pnpm workspaces — `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n`; configs `pnpm-workspace.yaml`, `package.json`, `tsconfig.json`, `eslint.config.js`, `prettier.config.mjs`; `.changeset/` for changesets versioning ([`upstash--context7`])

### Module-naming oddities

- bare `app` module instead of `hass_mcp` ([`voska--hass-mcp`])
- separate `mcp.py` and `server.py` — likely splits MCP-protocol surface from HTTP/business-logic surface ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

## Python packaging

### Build backend

- legacy `setup.py` only (no pyproject.toml) — pre-modern packaging ([`twolven--mcp-server-puppeteer-py`])
- `pyproject.toml` with hatchling ([`voska--hass-mcp`], [`zilliztech--mcp-server-milvus`])
- `pyproject.toml`, backend not surfaced ([`utensils--mcp-nixos`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Lock file

- `uv.lock` committed — uv lock workflow ([`zilliztech--mcp-server-milvus`])
- `.python-version` file referenced ([`voska--hass-mcp`])
- none ([`twolven--mcp-server-puppeteer-py`])
- not surfaced ([`utensils--mcp-nixos`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Version manager convention

- pip + `requirements.txt` only — pre-modern ([`twolven--mcp-server-puppeteer-py`])
- uv + uvx ([`voska--hass-mcp`], [`zilliztech--mcp-server-milvus`])
- uv + nix ([`utensils--mcp-nixos`])
- pip + uvx ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Dev dep placement

- `ruff` pinned in project-level dependencies rather than dev extra — blurs lint tooling into runtime install, adds weight for end users ([`zilliztech--mcp-server-milvus`])
- `[dev]` optional extra ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

## Async and tool signatures

- Playwright is async — tools likely `async def` (no test framework to confirm) ([`twolven--mcp-server-puppeteer-py`])
- httpx + MCP SDK — likely async ([`voska--hass-mcp`])
- FastMCP-standard mix; `pymilvus` client calls generally sync ([`zilliztech--mcp-server-milvus`])
- likely async (FastMCP + httpx) ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- not surfaced ([`utensils--mcp-nixos`])

## Type / schema strategy

- raw `mcp` SDK — hand-authored schemas likely ([`twolven--mcp-server-puppeteer-py`])
- Pydantic via FastMCP, schema auto-derived from type hints ([`zilliztech--mcp-server-milvus`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- mypy-checked + FastMCP auto-derived schemas ([`utensils--mcp-nixos`])
- Pydantic likely arrives via `mcp[cli]` extra; not confirmed ([`voska--hass-mcp`])

## Notable structural choices

### Headless vs non-headless browser mode

- deliberately non-headless for easier debugging — trades production efficiency for interactive visibility ([`twolven--mcp-server-puppeteer-py`])

### In-memory binary handoff

- in-memory base64-encoded screenshot storage — flows through MCP responses without disk intermediate ([`twolven--mcp-server-puppeteer-py`])

### Terminology vs implementation asymmetry

- name "puppeteer-py" reflects user-facing concept; implementation actually wraps Playwright (Python equivalent) ([`twolven--mcp-server-puppeteer-py`])

### User-approval framing

- README explicitly calls out user approval before message sending — reflects trust concern of letting LLM post to public surfaces ([`v-3--discordmcp`])

### Public client + private backend

- public MCP repo distinct from private backend (API, parsing, crawling engines) — disclosing-vs-withholding-implementation axis ([`upstash--context7`])

### Bridge-binary alternative to library embedding

- standalone bridge binary gives non-Go consumers an MCP-to-tool bridge without Go embedding ([`viant--mcp`])

### Two-dep minimalism

- `mcp[cli]` + `httpx` only — minimal abstraction over backend REST API ([`voska--hass-mcp`])

### Concurrent dual protocol

- HTTP bridge bundled in-process alongside MCP — server speaks two protocols at once, on by default ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Skills + rules folders alongside MCP

- ships `Skills` folder and `rules` folder alongside the MCP server in the same monorepo ([`upstash--context7`])

### Changesets-based release discipline

- monorepo coordinated releases via `.changeset/` ([`upstash--context7`])

## Unanticipated divergence axes

### env-vs-CLI precedence

- env > CLI inversion (most servers do CLI > env); reflects bias toward reproducible host-config-driven deployments ([`zilliztech--mcp-server-milvus`])

### Token-efficiency tool design

- few-but-broad tools deliberately — 2 tools where peers offer 50–250 ([`utensils--mcp-nixos`])

### Stateless vs stateful HTTP

- stateless HTTP transport flag separates cacheable deployments from stateful ones ([`utensils--mcp-nixos`])

### Declarative-config distribution

- nixpkgs as a first-class install channel — declarative install path rare among MCP servers ([`utensils--mcp-nixos`])

### Source-only TypeScript posture

- TS project with no npm publish; clone-and-build only — distribution posture worth contrasting with TS peers that publish to npm ([`v-3--discordmcp`])

### Disclosing vs withholding server implementation

- hybrid public client + private backend ([`upstash--context7`])

### Marketplace metadata as plugin integration

- `.claude-plugin/marketplace.json` (not `plugin.json`) — marketplace-style integration distinct from full plugin wrapper ([`upstash--context7`])

### OAuth2 client-side automatic token acquisition

- automatic token acquisition on 401 response — unusual client-side feature ([`viant--mcp`])

### Fine-grained authorization (experimental)

- experimental fine-grained tool/resource control — suggests multi-user workspace scenarios being designed for ([`viant--mcp`])

### Aggressive Python version floor

- 3.13 floor on a popular production server — uncommon ([`voska--hass-mcp`])

### Pre-modern Python packaging

- `setup.py` only, no pyproject.toml — only legacy server in this bin ([`twolven--mcp-server-puppeteer-py`])

### Concurrent dual protocol exposure

- MCP + HTTP REST in same process simultaneously — distinct from "pick a transport" ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])

### Ruff in runtime deps

- lint tooling pinned in `[project.dependencies]` rather than dev extras ([`zilliztech--mcp-server-milvus`])

## Gaps / unknowns observed

- last commit dates not extracted ([`twolven--mcp-server-puppeteer-py`], [`v-3--discordmcp`], [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- backend architecture intentionally private ([`upstash--context7`])
- HTTP bridge internals not inspected — is it `streamable-http`, `sse`, or custom FastAPI? ([`zongmin-yu--semantic-scholar-fastmcp-mcp-server`])
- exact tool count / use of resources or prompts not captured ([`voska--hass-mcp`])
- pyproject license field not present despite README MIT badge ([`voska--hass-mcp`])
- Go version constraints not documented in CI ([`viant--mcp`])
- Docker artifacts absent despite Milvus typically being containerized ([`zilliztech--mcp-server-milvus`])
- whether server protects Python stdout from log pollution (stdio JSON-RPC correctness) ([`twolven--mcp-server-puppeteer-py`])
- changelog/release notes not visible in README ([`upstash--context7`])
