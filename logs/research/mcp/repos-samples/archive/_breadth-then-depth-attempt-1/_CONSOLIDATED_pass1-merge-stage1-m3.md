# Sample

Stage-1 M3 merge of bins 5, 11, 13. See `_BINS.md` for input partials list.

## Language and runtime

Implementation language is the first-order divergence; everything else (SDK choice, packaging, distribution) follows.

### Python

Python is the dominant language across the three bins.

#### Python version floor

- Python 3.8+ — legacy/`setup.py`-era servers [`twolven--mcp-server-puppeteer-py`]
- Python 3.10+ — common modern mainstream floor [`duolingo--slack-mcp` (`requires-python = ">=3.10"`, Dockerfile uses `python:3.11-slim` base), `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Python 3.10–3.12 inclusive upper bound — driven by an external ABI dependency (DaVinci Resolve's Python scripting module is incompatible with 3.13+) [`samuelgursky--davinci-resolve-mcp`]
- Python 3.11+ — slightly raised floor [`designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos`]
- Python 3.12+ — `requires-python = ">=3.12"` [`sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Python 3.13+ — aggressive cutting-edge floor on a popular production server (287 stars); flagged as uncommon [`voska--hass-mcp`]
- Pinned via `.python-version` only — no explicit `requires-python` surfaced [`sajal2692--mcp-weaviate`, `shreyaskarnik--huggingface-mcp-server`]
- Not surfaced — README and packaging do not state a floor [`shibuiwilliam--mcp-server-scikit-learn`]

> The 3.11 floor is observed as "a touch more modern than awslabs' 3.10" [`echelon-ai-labs--servicenow-mcp`]. No Python <3.10 observed in bins 5/11; `twolven--mcp-server-puppeteer-py` (3.8+) is the lone pre-3.10 outlier. Pitfall: a CI matrix that tests Python versions below `requires-python` is a self-inconsistency — `sandraschi--email-mcp` declares `requires-python = ">=3.12"` but tests 3.10/3.11/3.12 in CI.

### TypeScript / Node.js

- Node.js >=18.0.0 — `exa-labs--exa-mcp-server` (TypeScript 97.9%)
- Node.js 22+ — `docker--hub-mcp` (TypeScript 99.8%)
- Node.js (npx/npm-based) — `executeautomation--mcp-playwright` (TypeScript 93.6%); specific Node version not pinned in README
- Node 16.x+ floor — `v-3--discordmcp` (Pure TypeScript with MCP TypeScript SDK)
- TypeScript 91% + JavaScript 8.5%, monorepo with pnpm workspaces — `upstash--context7`

### Rust

- Rust 2024 edition — `elastic--mcp-server-elasticsearch` (Rust 94.3%); exact Rust version not specified in `Cargo.toml`, only edition. A rare axis value across the corpus
- Rust toolchain pinned via `rust-toolchain.toml` — `rust-mcp-stack--rust-mcp-filesystem` (uses `rust-mcp-sdk` + `rust-mcp-schema`)

### Go

- Go MCP SDK with no explicit version constraint specified [`viant--mcp`]
- JSON-RPC 2.0 communication base explicitly named [`viant--mcp`]

### Mixed-language

- Python 74% + TypeScript 22% + Nix 1% — Python core with TypeScript companion (likely docs/UI) [`utensils--mcp-nixos`]

### Not applicable (remote-only)

- No local code; the repo ships configs only and the MCP server is a remote HTTP service [`slackapi--slack-mcp-plugin`]

### MCP framework / SDK variant

Framework choice diverges within each language family.

#### Python SDKs

- Raw `mcp` Python SDK / `mcp[cli]` (low-level, hand-authored schemas) — `designcomputer--mysql_mcp_server` (`mcp>=1.0.0`), `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `samuelgursky--davinci-resolve-mcp` (presumed), `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`, `twolven--mcp-server-puppeteer-py`, `voska--hass-mcp`
- FastMCP (1.x or unspecified) — Pydantic-backed auto-derivation of tool schemas — `sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`
- FastMCP 2.x — `duolingo--slack-mcp` (`fastmcp>=2.13.0`), `zilliztech--mcp-server-milvus` (`fastmcp >= 2.14.1`)
- FastMCP 3.x — `fastmcp>=3.1.0,<4` is the highest FastMCP floor seen [`sandraschi--email-mcp`]

> For SSE transport in raw-SDK servers, Starlette is used directly rather than FastAPI [`echelon-ai-labs--servicenow-mcp`] — observed as a viable sub-FastAPI layer for MCP servers wanting HTTP transport without full REST framework overhead.

#### TypeScript SDKs

- `@modelcontextprotocol/sdk` (typical for TS MCP) — `docker--hub-mcp` (likely; not explicitly extracted), `executeautomation--mcp-playwright`, `v-3--discordmcp`
- MCP SDK ^1.12.1 with Zod validation and `jose` (JWT) — `exa-labs--exa-mcp-server`; also pulls in `exa-js ^2.8.0` for the underlying API

#### Rust SDKs

- `rmcp ^0.2.1` (Rust MCP SDK), `tokio` (async), `axum` (HTTP) — `elastic--mcp-server-elasticsearch`
- `rust-mcp-sdk` + `rust-mcp-schema` — `rust-mcp-stack--rust-mcp-filesystem`

#### Go SDKs

- Go MCP SDK with full capability surface — tools, resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, elicitation [`viant--mcp`]

#### Remote MCP (no local SDK)

- Protocol terminated server-side; clients connect via HTTP [`slackapi--slack-mcp-plugin`]

#### MCP SDK version pinning practice

- Older pin `mcp[cli]>=1.4.1` on a recent server — version drift from current SDK [`voska--hass-mcp`]
- Lower-bound only, no upper-bound [`zilliztech--mcp-server-milvus`]

## Transport

Transport surface is a key divergence axis. Two orthogonal questions: which transports supported, and how the choice is exposed.

### Supported transports

#### stdio only

- README explicitly frames as "stdio-based protocol server rather than standalone application" [`designcomputer--mysql_mcp_server`]
- Single-file Python script invoked by host [`twolven--mcp-server-puppeteer-py`]
- TypeScript bot wrapped via stdio to host [`v-3--discordmcp`]
- Docker-wrapped stdio [`voska--hass-mcp`]
- Stdio-only (default or by explicit selection) [`rust-mcp-stack--rust-mcp-filesystem` (inferred), `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]

#### HTTP only

- `duolingo--slack-mcp` (`http://localhost:8001/mcp`, port 8001)
- Remote MCP endpoint at a fixed URL [`slackapi--slack-mcp-plugin`]

#### HTTP + stdio

- CLI `--transport=http|stdio` [`docker--hub-mcp`]
- HTTP (remote endpoint) + stdio + HTTP local; default remote `https://mcp.exa.ai/mcp` [`exa-labs--exa-mcp-server`]

#### stdio + SSE / HTTP/SSE

- Separate console scripts per transport [`echelon-ai-labs--servicenow-mcp`]
- stdio + streamable-HTTP (SSE deprecated) [`elastic--mcp-server-elasticsearch`]
- stdio + SSE + streamable-http (CLI `--transport`) [`feiskyer--mcp-kubernetes-server`]
- stdio (recommended) + HTTP/SSE — single binary; `--port` switches mode [`executeautomation--mcp-playwright`]
- stdio default + SSE option, separate JSON config blocks per mode [`zilliztech--mcp-server-milvus`]
- stdio + HTTP + Docker-wrapped, transport selected via env vars [`utensils--mcp-nixos`]

#### stdio + streamable-http

- Multi-transport server with CLI/env selection [`sajal2692--mcp-weaviate`]

#### Multi-transport library (Go)

- HTTP/SSE + Streamable HTTP + Stdio, configured via functional options pattern (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`) and separate entry points (`stdioSrv.ListenAndServe()` / `srv.HTTP()`) [`viant--mcp`]

#### Dual-protocol same process (rare)

- stdio MCP + HTTP REST bridge running in same process simultaneously; HTTP bridge enabled by default, making the server usable by non-MCP clients out of the box. Distinct from "pick a transport" — this is two protocols at once [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- MCP native + CLI + Skills (without MCP) + HTTP REST backend [`upstash--context7`]

### Transport selection mechanism

How the user picks a transport diverges sharply.

- Implicit / single-transport — [`designcomputer--mysql_mcp_server` (stdio only), `duolingo--slack-mcp` (HTTP only), `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`]
- CLI flag (`--transport`) — [`docker--hub-mcp`, `feiskyer--mcp-kubernetes-server`]
- CLI flag (`--port` switches stdio→HTTP) — `executeautomation--mcp-playwright` ("Dual-transport from one binary — `--port` switches between stdio and HTTP, not separate entry points")
- Docker arg / CLI positional (`stdio` vs `http`) — [`elastic--mcp-server-elasticsearch`]
- Separate console scripts per transport — `echelon-ai-labs--servicenow-mcp`: `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE). "Architecturally split rather than env-var-switched" — opposite of the one-binary multi-transport model
- Client config selects (default remote endpoint) — [`exa-labs--exa-mcp-server`]
- CLI argument or env var [`sajal2692--mcp-weaviate`]
- HTTP URL configured at the client side [`slackapi--slack-mcp-plugin`]
- Environment variables — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP` [`utensils--mcp-nixos`]
- Env var toggle for secondary protocol — `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE` [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- CLI flag / env var with separate JSON configs per mode [`zilliztech--mcp-server-milvus`]
- Functional options at construction time (Go) [`viant--mcp`]

> The transport-selection split (one binary with flag vs separate binaries per transport) is itself a design axis worth tracking.

### stdio hardening

- Explicit stdout/stderr isolation discipline — README emphasizes hardened stdout/stderr separation for JSON-RPC correctness; "zero-tolerance `print` policy" in core handlers to keep stdout clean [`sandraschi--email-mcp`]

### Stateless HTTP mode

- Explicit `MCP_NIXOS_STATELESS_HTTP` flag for shared/multi-user deployments [`utensils--mcp-nixos`]

## Distribution

How the server reaches end users. Multiple mechanisms commonly stack.

### Package managers

#### PyPI / pip

- PyPI publication — `designcomputer--mysql_mcp_server` (`mysql-mcp-server`), `feiskyer--mcp-kubernetes-server` (`mcp-kubernetes-server`), `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `utensils--mcp-nixos`
- PyPI via `uvx` — primary one-liner install [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `voska--hass-mcp` (`uvx hass-mcp` alongside Docker), `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`uvx semantic-scholar-fastmcp`), `utensils--mcp-nixos` (`uvx mcp-nixos`)]
- PyPI via `uv` (local install) [`severity1--terraform-cloud-mcp`]

#### npm / npx

- npm — `docker--hub-mcp` (npm-installable), `exa-labs--exa-mcp-server` (`exa-mcp-server`), `executeautomation--mcp-playwright` (`@executeautomation/playwright-mcp-server`)
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
- Source clone + editable install (`pip install -e .` from clone) [`echelon-ai-labs--servicenow-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Source clone + `uv sync` and run a script directly [`shreyaskarnik--huggingface-mcp-server`]
- Source-only with custom installer — no PyPI; bespoke `install.py` orchestrates venv and per-client config [`samuelgursky--davinci-resolve-mcp`]
- TypeScript `npm install` + `npm run build` with no npm publish [`v-3--discordmcp`]
- Python clone-only with `pip install -r requirements.txt` [`twolven--mcp-server-puppeteer-py`]
- Source tree + `uv run src/...` (rather than installed console script) [`zilliztech--mcp-server-milvus`]

### Container registries

- Generic Dockerfile in repo — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `executeautomation--mcp-playwright`, `rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`
- ghcr.io image published — `feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos` (`ghcr.io/utensils/mcp-nixos`)
- Vendor-specific registry — `elastic--mcp-server-elasticsearch` (`docker.elastic.co/mcp/elasticsearch`, distributed via AWS Marketplace and Elastic's container registry)
- Docker Hub MCP Registry presence [`rust-mcp-stack--rust-mcp-filesystem`, `voska--hass-mcp` (`voska/hass-mcp:latest` — primary channel; README leads with `docker pull`)]

### Container-only / container-first distribution

- `elastic--mcp-server-elasticsearch` — Docker is the only shipping channel ("Container-first distribution — Docker is the only shipping channel")
- `duolingo--slack-mcp` — Docker primary (no PyPI); "Containerization as primary distribution (not Homebrew, npm, Cargo)"; "Inverts the typical Python packaging path; container as the only artifact"

### Aggregator / installer registries

- Smithery CLI install — `designcomputer--mysql_mcp_server` (`npx -y @smithery/cli install mysql-mcp-server --client claude`), `executeautomation--mcp-playwright`, `exa-labs--exa-mcp-server` (Smithery registry config `smithery.yaml`), `shreyaskarnik--huggingface-mcp-server`
- mcp-get — `executeautomation--mcp-playwright`
- Pre-built IDE installers (one-click for Cursor / VS Code) — `exa-labs--exa-mcp-server`
- Native Claude Desktop connector (no manual config) — `exa-labs--exa-mcp-server`
- MCPB bundle (Claude Desktop drag-and-drop) [`sandraschi--email-mcp`]
- Zed extension [`sandraschi--email-mcp`]

> `executeautomation--mcp-playwright` ships across four mechanisms (npm, mcp-get, Smithery, Docker) — flagged in-sample as "a reference for 'how many channels to publish to' decisions".

### Standalone binaries / installers

- Shell installer / PowerShell installer [`rust-mcp-stack--rust-mcp-filesystem`]
- GitHub release binary downloads [`rust-mcp-stack--rust-mcp-filesystem`]
- Standalone bridge binary distributed as alternative to embedding the Go library [`viant--mcp`]

### Declarative install (Nix-native)

- `nix run github:utensils/mcp-nixos` (uses Nix flake) [`utensils--mcp-nixos`]
- Nix flake + declarative NixOS / Home Manager module via nixpkgs entry — flagged as rare for MCP servers [`utensils--mcp-nixos`]

### Remote-hosted endpoint

- `exa-labs--exa-mcp-server` — operates a remote MCP endpoint at `https://mcp.exa.ai/mcp`; clients connect to that URL rather than running a local process. Reduces setup friction. Vercel deployment config (`vercel.json`) supports the hosted variant
- `https://mcp.context7.com/mcp` — manual config option as alternative to local install [`upstash--context7`]
- Remote-hosted-only — no install at all; `git clone` is for config review only [`slackapi--slack-mcp-plugin`]

### Cross-ecosystem distribution

- A single Rust binary shipped via Homebrew, Cargo, npm, Docker, GitHub releases, plus shell/PowerShell scripts — broadest distribution surface in this bin [`rust-mcp-stack--rust-mcp-filesystem`]

### Distribution posture axis

- Source-only (clone + build) vs published package — TypeScript projects sometimes choose source-only [`v-3--discordmcp`]
- Published package vs hosted MCP endpoint — Context7 offers both [`upstash--context7`]
- Public client + private backend — Context7 keeps API/parsing/crawling engines private [`upstash--context7`]

## Entry point / launch

How the running process is started, after distribution lands the bits.

### Launch shape

#### Console script via `[project.scripts]`

- `mysql_mcp_server = "mysql_mcp_server:main"` [`designcomputer--mysql_mcp_server`]
- `slack-mcp = "main:main"` — module `main` at top level, no package, unusual [`duolingo--slack-mcp`]
- `mcp-server-milvus` [`zilliztech--mcp-server-milvus`]
- `hass-mcp` → `app.run:main` [`voska--hass-mcp`]
- `mcp-nixos` [`utensils--mcp-nixos`]
- `semantic-scholar-mcp-server` [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Console script — `uvx <name>` or `uv run <name>` [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

#### `python -m <module>`

- `python -m src.mcp_kubernetes_server.main` [`feiskyer--mcp-kubernetes-server`]
- Both `python -m servicenow_mcp.cli` (stdio) and console script `servicenow-mcp-sse` (SSE) [`echelon-ai-labs--servicenow-mcp`]

#### `uvx <package>`

- [`feiskyer--mcp-kubernetes-server`, `designcomputer--mysql_mcp_server` (VS Code config example uses `uvx --from mysql-mcp-server`)]

#### `npx -y <package>`

- [`executeautomation--mcp-playwright`]

#### `npm start` / direct `dist/index.js` / `node build/index.js`

- `npm start -- ...` or direct `dist/index.js` [`docker--hub-mcp`]
- `node build/index.js` (production) and `npm run dev` (development) [`v-3--discordmcp`]

#### `docker run`

- Entrypoint implicit [`elastic--mcp-server-elasticsearch`]

#### Bare `python` / direct script invocation

- `uv run python main.py` — Dockerfile uses bare-script invocation rather than the declared console script. "Entry point not the primary run path" [`duolingo--slack-mcp`]
- `python puppeteer.py` — single-file at repo root [`twolven--mcp-server-puppeteer-py`]
- `uv run src/mcp_server_milvus/server.py --milvus-uri ...` — uv-run against checked-out source tree, unusual; most servers use `uvx <package>` [`zilliztech--mcp-server-milvus`]
- `uv run <path>/<script>.py`, no console-script entry [`shreyaskarnik--huggingface-mcp-server`]
- Bare Python script with absolute paths — `python src/server.py` (no packaging entry point at all) [`samuelgursky--davinci-resolve-mcp`]

#### Path-anchored `uv --directory=<path>`

- Implies the package isn't designed for pip-install-everywhere; designed for developer-installed local runs [`shibuiwilliam--mcp-server-scikit-learn`]

#### Standalone binary (no interpreter)

- Direct execution [`rust-mcp-stack--rust-mcp-filesystem`]

#### CLI subcommand pattern

- `npx ctx7 setup`, `ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>` — multi-verb CLI [`upstash--context7`]

#### Library embedding (no entry point)

- Go: server constructed and run from app code via `stdioSrv.ListenAndServe()` or `srv.HTTP(ctx, ":4981").ListenAndServe()` [`viant--mcp`]

#### No local entry point (remote HTTP only)

- [`slackapi--slack-mcp-plugin`]

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

- `designcomputer--mysql_mcp_server` README "explicitly discourages `python ...` direct invocation, framing the server strictly as an MCP-protocol bridge for hosts." Unique enforcement of agent-posture mental model

### Entry-point inconsistencies (anti-pattern)

- README runs `python puppeteer.py` while `setup.py` declares `mcp-server-puppeteer=mcp_server_puppeteer.server:main` — declared and actual entry diverge; neither tested against PyPI [`twolven--mcp-server-puppeteer-py`]
- Module name `app` (bare) rather than conventional `hass_mcp` package — suggests template-derived structure that wasn't renamed [`voska--hass-mcp`]

## Configuration surface

How config reaches the server.

### Environment variables

- All-env-var config — `designcomputer--mysql_mcp_server` (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`), `duolingo--slack-mcp` (`SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_MCP_BASE_URI`, `SLACK_EXTERNAL_URL`, `SLACK_MCP_PORT`), `elastic--mcp-server-elasticsearch` (`ES_URL`, `ES_API_KEY` or `ES_USERNAME`/`ES_PASSWORD`, `ES_SSL_SKIP_VERIFY`)
- Env vars only — `v-3--discordmcp` (`DISCORD_TOKEN`), `voska--hass-mcp` (`HA_URL`, `HA_TOKEN`), `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`SEMANTIC_SCHOLAR_API_KEY`)
- Env var (single) — `feiskyer--mcp-kubernetes-server` (`KUBECONFIG`), `exa-labs--exa-mcp-server` (`EXA_API_KEY`)
- Environment variables for credentials, endpoints, feature flags [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- Environment variables for transport selection [`utensils--mcp-nixos`]

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
- Auto-generated per-client JSON config by an installer script [`samuelgursky--davinci-resolve-mcp`]

### Library-construction-time options

- Functional options at library-construction time (Go) [`viant--mcp`]

### OAuth / setup-flow-driven config

- OAuth setup flow + API key header — `npx ctx7 setup` automates [`upstash--context7`]
- Client-side OAuth config — `clientId` / `callbackPort` shipped to consumers [`slackapi--slack-mcp-plugin`]

### Per-tool parameters only

- No global config documented [`twolven--mcp-server-puppeteer-py`]

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

## Authentication

Auth mechanism, where credentials originate, and whether the server itself implements an auth flow.

### No auth

- Browser automation against public web — `executeautomation--mcp-playwright`: "Not applicable — browser automation against public web; no service-level auth. Sites that require auth rely on Playwright's own cookie/state mechanisms, not an MCP-layer auth flow." User-driven within browser session
- Browser automation against public web [`twolven--mcp-server-puppeteer-py`]
- Public NixOS endpoints [`utensils--mcp-nixos`]
- Server talks to local-only API or local-only data [`rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

### Static credentials in env

- DB username/password — `designcomputer--mysql_mcp_server`. README emphasizes "never commit" credentials and restricting to minimum-permission DB users. Security guidance baked into README
- API key — `exa-labs--exa-mcp-server` (`EXA_API_KEY` from dashboard.exa.ai), `elastic--mcp-server-elasticsearch` (`ES_API_KEY`) or username/password against the cluster
- Personal Access Token — `docker--hub-mcp` (Docker Hub PAT in `HUB_PAT_TOKEN`)
- API token via env var — single-tenant, single-token-per-process [`severity1--terraform-cloud-mcp` (`TFC_TOKEN`), `shreyaskarnik--huggingface-mcp-server` (optional `HF_TOKEN`)]
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

- `echelon-ai-labs--servicenow-mcp` — three methods (Basic Auth, OAuth client credentials, API Key); `SERVICENOW_AUTH_TYPE` env var selects mechanism. "Multi-auth support as a first-class feature — enterprise SaaS servers often need it because different customer deployments mandate different auth; most community servers pick one"

### OAuth flow implemented in server

- `duolingo--slack-mcp` — OAuth 2.1 per-user; "when your MCP client first connects. Your client will open a browser window for Slack authorization". Server itself drives a browser-based OAuth handshake. Local dev requires ngrok for OAuth callback
- OAuth 2.0 with workspace admin approval — callback-port flow [`slackapi--slack-mcp-plugin`]

### OAuth + API key (hybrid)

- OAuth setup via `npx ctx7 setup`; free API key registration at dashboard for higher rate limits [`upstash--context7`]

### OAuth2/OIDC with full SDK support

- Two modes: global resource protection via bearer tokens, fine-grained tool/resource control (experimental) [`viant--mcp`]
- Client-side automatic token acquisition: "401 challenge, discovers protected resource metadata, acquires tokens and retries" — unusual for MCP servers [`viant--mcp`]

### Optional vs required credentials

- Required — server cannot start without the credential [`severity1--terraform-cloud-mcp`]
- Optional bearer token for elevated capability [`shreyaskarnik--huggingface-mcp-server`]

## Multi-tenancy

How many tenants share a process.

### Single-tenant per process

- Single DB connection per server, no per-request tenancy [`designcomputer--mysql_mcp_server`]
- Single ServiceNow instance per deployment [`echelon-ai-labs--servicenow-mcp`]
- Single Elasticsearch cluster [`elastic--mcp-server-elasticsearch` — per-client MCP connection in HTTP mode but single ES backend]
- Single user per process (one PAT plus username) [`docker--hub-mcp`]
- Single kubeconfig context [`feiskyer--mcp-kubernetes-server`]
- Single browser context per server process [`executeautomation--mcp-playwright`]
- Single-user — bound to one process / one credential [`rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Single-user single-process (one browser per process; one HA instance; one Milvus URI/DB) [`twolven--mcp-server-puppeteer-py`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Per-request multi-tenancy

- OAuth 2.1 per-user, multi-user via separate tokens per user [`duolingo--slack-mcp`]. Per-request tenant is a rare value across the bins
- Per-client multi-tenancy via HTTP endpoint, API key scoped to user account [`exa-labs--exa-mcp-server`]
- Per-call tenancy as a tool argument — first-class multi-tenancy in tool signatures rather than server config [`sajal2692--mcp-weaviate`]
- Per-request via bearer token; OAuth2 discovery enables per-request tenant identification [`viant--mcp`]
- Stateless HTTP mode supports shared/multi-user deployments [`utensils--mcp-nixos`]

### Per-workspace OAuth token

- Workspace admin scope; tenant boundary is the OAuth grant [`slackapi--slack-mcp-plugin`]
- Per-user OAuth token + per-workspace API key [`upstash--context7`]

### Bot-scoped

- Bot's server memberships define reachable tenants; auto server/channel discovery from bot's perspective [`v-3--discordmcp`]

### Fine-grained authorization (experimental)

- Suggests multi-user workspace scenarios being designed for [`viant--mcp`]

> Notable: `sajal2692--mcp-weaviate` calls out per-tenant search tools as a first-class MCP concept. Tenancy becomes an argument, not a server-config dimension. Rare across Python MCP servers.

## Capabilities exposed

Tools / resources / prompts surface area; tool count is one observable axis of breadth.

### MCP surface coverage

#### Tools-only

- 5 read-only Slack tools — `duolingo--slack-mcp` (channel messages, thread replies, search messages, list users, enumerate channels). "Read-only Slack integration (no write capabilities)" — Read-only MCP server pattern as an axis value
- 5 ES tools — `elastic--mcp-server-elasticsearch` (`list_indices`, `get_mappings`, `search`, `esql`, `get_shards`)
- 3 web-search tools + advanced filtering — `exa-labs--exa-mcp-server` (`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`)
- Tools defined in `tools.json` — `docker--hub-mcp` (specific tool list not enumerated)
- Browser automation surface — `executeautomation--mcp-playwright` (navigation, click, fill, screenshot, test code generation, web scraping, JavaScript execution, device emulation with 143+ device presets)
- 50+ tools — `feiskyer--mcp-kubernetes-server` (kubectl/helm command execution, read-only queries, write, delete, rollout/scaling)
- 60+ tools across 9 functional areas — `echelon-ai-labs--servicenow-mcp` (Incident, Service catalog, Change requests, Agile, Workflows, Script includes, Changesets, Knowledge bases, User management). "Enterprise-tool density — 60+ tools in 9 functional areas; enterprise platforms generate more surface area than consumer SaaS does"
- Tools-only [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `slackapi--slack-mcp-plugin`]

#### Tools + resources

- Tables-as-resources — `designcomputer--mysql_mcp_server`. "MySQL tables listed as resources, table contents readable. Tools — SQL query execution with error handling. Exposes tables as MCP resources (not only tools) — one of the few DB MCP servers to use the resource surface" / "Resources-as-tables pattern is rare — most DB MCP servers expose everything through tools"
- Library index + documentation cache as resources [`upstash--context7`]

#### Tools + resources + prompts

- Uses all three core MCP surfaces with a custom `hf://` URI scheme [`shreyaskarnik--huggingface-mcp-server`]

#### Tools + resources + prompts + sampling + skills

- Broadest surface in the corpus (custom `email_compose_request` prompt, `email_agentic_assist` sampling tool) [`sandraschi--email-mcp`]

#### Tools + MCP Roots (opt-in)

- [`rust-mcp-stack--rust-mcp-filesystem`]

#### Full MCP capability surface

- Tools, resources, prompts, sampling, roots, logging, progress reporting, request cancellation, subscriptions, elicitation — full MCP capability surface as a Go SDK [`viant--mcp`]

> Notable: most Python servers stick to tools-only. Two samples (`sandraschi--email-mcp`, `shreyaskarnik--huggingface-mcp-server`) demonstrate prompts and resources, with the latter exposing a custom URI scheme via the resources surface.

### Tool count and design

#### Minimal (≤5 tools)

- 2 tools — `nix()` unified query (~1,030 tokens) + `nix_versions()` helper; deliberate token-efficiency strategy contrasting with 50–250-tool peers [`utensils--mcp-nixos`]
- 2 tools — `send-message` + `read-messages`; minimal Discord surface [`v-3--discordmcp`]
- 2 tools — `resolve-library-id`, `query-docs` plus library/documentation cache resources [`upstash--context7`]
- 5 tools — `puppeteer_navigate`, `puppeteer_screenshot`, `puppeteer_click`, `puppeteer_fill`, `puppeteer_evaluate` [`twolven--mcp-server-puppeteer-py`]
- Small focused set — under 15 tools [`sajal2692--mcp-weaviate` (11), `sandraschi--email-mcp` (6 core)]

#### Mid (~15–50 tools, grouped)

- ~15 tools across text/vector/hybrid search, query, collection CRUD, insert, delete [`zilliztech--mcp-server-milvus`]
- 16 tools organized into 4 explicit functional groups (8 paper search/discovery, 2 citation analysis, 4 author info, 2 recommendation) — categorization baked into docs structure [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Mid-range — 50+ tools [`severity1--terraform-cloud-mcp`]

#### Large surface

- 50+ tools — kubectl/helm command execution, read-only queries, write, delete, rollout/scaling [`feiskyer--mcp-kubernetes-server`]
- 60+ tools across 9 functional areas [`echelon-ai-labs--servicenow-mcp`]

#### Two-mode design (compound vs full)

- 27 aggregate tools vs 342 granular; explicit context-window-vs-expressiveness trade [`samuelgursky--davinci-resolve-mcp`]
- 342 granular tools — among the largest tool surfaces seen; the dual-mode design exists specifically to counter context-window pressure

### Tool surface design philosophy axis

- Few-but-broad tools (token efficiency) vs many-narrow tools — explicit design call [`utensils--mcp-nixos`]
- Minimal scope as trust signal — README emphasizes user-approval before sending Discord messages, reflecting awareness of agent-action-on-public-surfaces risk [`v-3--discordmcp`]

### Multi-backend unified surface

- One tool, many backends — `send_email` dispatches to SMTP or to an API provider based on configuration; backend heterogeneity is hidden from the LLM caller [`sandraschi--email-mcp`]

### Vertical / specialized skills shipped alongside

- `exa-labs--exa-mcp-server` skills directory — company research, code search, people research, financial reports, academic papers. "Vertical-specific research skills shipped alongside the server — axis: 'skills' as first-class shipping artifact"

## Observability

Logging, metrics, tracing, debug surface.

### File-based logging (stdio framing constraint)

- `executeautomation--mcp-playwright` — logs written to `~/playwright-mcp-server.log` in stdio mode "specifically to keep stdout clean for JSON-RPC framing. File-based log is the observability surface". A deliberate design response to the stdio framing constraint — the server cannot log to stdout without corrupting JSON-RPC

### Container stdout/stderr + health endpoint

- `elastic--mcp-server-elasticsearch` — container logs (stdout/stderr); health check at `/ping` returning "pong"

### Separate monitoring directory + web dashboard

- Vite + Uvicorn on ports 10812/10813 for health/metrics/control [`sandraschi--email-mcp`]

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
- Not surfaced [`docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server`, `rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`, `upstash--context7`, `utensils--mcp-nixos`, `voska--hass-mcp`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Stdio stdout-pollution discipline

- Not stated whether Python stdout is protected from log pollution (important for stdio JSON-RPC correctness) [`twolven--mcp-server-puppeteer-py`]

## Host integrations

Which MCP host configs the README documents.

### Claude Desktop

- `claude_desktop_config.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `executeautomation--mcp-playwright` (primary host integration)
- Implies standard MCP configuration without explicit detail [`duolingo--slack-mcp`]
- JSON `mcpServers` entry [`feiskyer--mcp-kubernetes-server`, `utensils--mcp-nixos` (uvx form), `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (uvx command)]
- JSON config snippet (Docker `command`/`args` + env) [`voska--hass-mcp`]
- JSON config snippets — separate stdio and SSE variants [`zilliztech--mcp-server-milvus`]
- Native Claude Desktop connector (no manual config needed) — distinct from JSON-snippet hosts [`exa-labs--exa-mcp-server`]
- Listed as MCP-compatible (assumed) [`elastic--mcp-server-elasticsearch`]

### Claude Code

- Native support documented as one of 30+ supported agents [`upstash--context7`]
- Standard `claude mcp add` CLI registration alongside JSON `mcpServers` for desktop hosts [`severity1--terraform-cloud-mcp`]

### VS Code

- `mcp.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp` (User Settings JSON), `exa-labs--exa-mcp-server` (pre-built installer)
- Documented via GitHub Copilot integration [`executeautomation--mcp-playwright`]

### Cursor

- JSON `mcpServers` entry [`feiskyer--mcp-kubernetes-server`]
- Pre-built installer [`exa-labs--exa-mcp-server`]
- Documented host integration [`executeautomation--mcp-playwright`]
- Listed (assumed) [`elastic--mcp-server-elasticsearch`]
- Listed as supported agent [`upstash--context7`]
- `.cursor/` directory present + dedicated JSON snippet [`zilliztech--mcp-server-milvus`]

### Vendor-specific companion integration

- `docker--hub-mcp` ships `gordon-mcp.yml` for Docker's Ask Gordon agent. "MCP server pre-shaping its config for a first-party downstream tool, distinct from generic host config"

### Many-host enumeration

- `exa-labs--exa-mcp-server` documents JSON `mcp.json` configs for Codex, OpenCode, Antigravity, Windsurf, Zed, Gemini CLI, v0 by Vercel, Warp, Kiro, Roo Code — 15+ platforms. "High client compatibility (15+ platforms)"
- Context7 documents support across 30+ client platforms [`upstash--context7`]

### GitHub Copilot / ChatGPT Copilot

- `feiskyer--mcp-kubernetes-server` documents JSON `mcpServers` entry for both

### Cline

- `executeautomation--mcp-playwright` documented host integration

### OpenAI Code

- Listed as supported agent [`upstash--context7`]

### NixOS / Home Manager

- Declarative config entry available in nixpkgs [`utensils--mcp-nixos`]

### Universal installer pattern

- Custom `install.py` walks every supported client and writes per-client JSON to that client's standard config location. Replaces both pip and uv roles. Flags `--clients`, `--dry-run`, `--no-venv`, `--full` [`samuelgursky--davinci-resolve-mcp`]
- Many hosts via universal installer — 10 MCP clients auto-configured in one pass [`samuelgursky--davinci-resolve-mcp`]

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

Whether the repo ships `.claude-plugin/`.

### Present

- `.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`) [`exa-labs--exa-mcp-server`]
- Configs-only `.claude-plugin/` directory in a remote-hosted MCP — plugin layout used to ship configs, not server code [`slackapi--slack-mcp-plugin`]
- `.claude-plugin/marketplace.json` (marketplace metadata only, not full plugin.json) — distinct from plugin-wrapper install [`upstash--context7`]

### Marketplace metadata vs plugin install

- `.claude-plugin/marketplace.json` is a marketplace-style integration; separate concept from a full plugin wrapper [`upstash--context7`]

### Not present

- [`designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`, `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `utensils--mcp-nixos`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `viant--mcp`]

## Tests

### Framework

- pytest — `designcomputer--mysql_mcp_server` (`pytest.ini`, `requirements-dev.txt`, `tests/` directory), `duolingo--slack-mcp` (`pytest>=8.0.0` in test extras, `uv run pytest`), `sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`, `utensils--mcp-nixos`, `voska--hass-mcp`
- pytest + pytest-asyncio + pytest-cov via a `test` extra [`sandraschi--email-mcp`]
- Jest [`executeautomation--mcp-playwright` (`src/__tests__`)]
- cargo-nextest [`rust-mcp-stack--rust-mcp-filesystem`]
- Custom 5-phase live suite — read-only / destructive / media / AI/ML / advanced; framework not surfaced; 319/324 methods live-tested with claimed 100% pass [`samuelgursky--davinci-resolve-mcp`]
- Go stdlib testing — `client.go` / `server.go` test patterns [`viant--mcp`]
- Monorepo test suite via `npm run test` in workspace [`upstash--context7`]
- Framework not surfaced [`echelon-ai-labs--servicenow-mcp` (`tests/` directory present), `elastic--mcp-server-elasticsearch` (`tests/` directory), `feiskyer--mcp-kubernetes-server` (CI `build.yml` suggests CI-driven tests), `docker--hub-mcp` (ESLint config present, no test files explicitly called out), `exa-labs--exa-mcp-server` (not documented), `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`tests/` directory present)]
- Not observed / no test framework documented [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`]
- Not applicable — config-only repo [`slackapi--slack-mcp-plugin`]

### Async test support

- pytest-asyncio not declared — `duolingo--slack-mcp` ("may be sync-style tools")
- pytest-asyncio not confirmed — `designcomputer--mysql_mcp_server`

### Test layout

- `tests/` directory at repo root [`rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- `pytest.ini` at root alongside `pyproject.toml` — legacy dual-config [`sandraschi--email-mcp`]

## CI

### GitHub Actions

- Present — `designcomputer--mysql_mcp_server` (test.yml badge), `docker--hub-mcp` (`.github/`), `feiskyer--mcp-kubernetes-server` (`build.yml`), `executeautomation--mcp-playwright` (`.github/workflows`), `rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `utensils--mcp-nixos` (badge referenced), `voska--hass-mcp` (`.github/`, details not extracted), `zongmin-yu--semantic-scholar-fastmcp-mcp-server` (`.github/`, details not extracted), `viant--mcp` (configured, typical Go test/lint workflows implied), `upstash--context7` (`.github/` present with `npm run lint`, `npm run format` scripts)

### Multi-system CI

- `elastic--mcp-server-elasticsearch` — both `.github/` (GitHub Actions) and `.buildkite/` (Buildkite pipeline) — multi-platform testing across two CI systems. "CI system diversity beyond the GitHub-only assumption"

### What CI runs

- fmt + clippy + test + check via Makefile.toml (cargo-make) [`rust-mcp-stack--rust-mcp-filesystem`]
- Multi-Python matrix (3.10/3.11/3.12) + Ruff + MyPy + Bandit; webapp linted with Biome [`sandraschi--email-mcp`]
- ruff + black + mypy [`severity1--terraform-cloud-mcp`]
- Details not surfaced beyond presence [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

### CI extras

- CodeRabbit reviews used alongside GitHub Actions [`utensils--mcp-nixos`]

### Unspecified / not extracted

- [`duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`]
- Not observed [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`, `shreyaskarnik--huggingface-mcp-server`]
- Not applicable [`slackapi--slack-mcp-plugin`]

## Container / packaging artifacts

### Dockerfile only

- [`designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server` (Dockerfile + Vercel `vercel.json`), `rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]

### Dockerfile + docker-compose

- [`executeautomation--mcp-playwright`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Multiple Dockerfiles / multi-target

- `elastic--mcp-server-elasticsearch` — `Dockerfile` (main), `Dockerfile-8000` (alternative), `.dockerignore`. Multi-container deployment ready (EC2, ECS, EKS deployment targets)

### Multi-stage Docker build

- Multi-stage Docker build with minimal final image — `clux/muslrust:stable` builder + `alpine:latest` final, static binary, non-root user [`rust-mcp-stack--rust-mcp-filesystem`]

### Container as primary distribution

- `duolingo--slack-mcp` — Dockerfile uses `python:3.11-slim` base, env vars `NO_COLOR=1`, `CI=true`, `TERM=dumb`, port 8001 exposed, startup `uv run python main.py`
- `voska--hass-mcp` — official image on Docker Hub as primary distribution channel

### Docker Hub MCP Registry presence

- [`rust-mcp-stack--rust-mcp-filesystem`]

### MCPB bundle replaces Docker

- [`sandraschi--email-mcp`]

### Windows installer via WiX toolset

- `wix/` directory for Windows installer [`rust-mcp-stack--rust-mcp-filesystem`]

### Nix-native packaging

- Nix flake for nix-native install [`utensils--mcp-nixos`]
- Declarative NixOS / Home Manager module via nixpkgs [`utensils--mcp-nixos`]

### Intentionally absent

- No container — intentional when the server must run on the same host as a local app [`samuelgursky--davinci-resolve-mcp`]
- Not observed [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`, `twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zilliztech--mcp-server-milvus`, `viant--mcp`]

## Example client / developer ergonomics

### Task runner

- Makefile [`shibuiwilliam--mcp-server-scikit-learn`]
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

### Dev shells / toolchain

- `nix develop` reproducible dev shell + ruff/mypy toolchain [`utensils--mcp-nixos`]
- `[dev]` optional extra [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- `requirements.txt` only — no lock, no dev extras [`twolven--mcp-server-puppeteer-py`]

### MCP Inspector

- Explicit Inspector launcher in README — `npx @modelcontextprotocol/inspector node build/index.js` [`v-3--discordmcp`]
- MCP Inspector support documented + Smithery registry config [`upstash--context7`]
- MCP Inspector debugging support referenced [`designcomputer--mysql_mcp_server`]

### Examples directory

- `/example` directory demonstrating server, auth, client, bridge binary use [`viant--mcp`]

### Other dev ergonomics

- ruff in dev extra [`duolingo--slack-mcp`]
- ngrok required for OAuth callback during local dev [`duolingo--slack-mcp`]

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

### Multi-directory single-repo

- Distinct concerns split: `src/<pkg>/` core, `mcp-server/` packaging, `webapp/` monitoring dashboard, `monitoring/` health/metrics, `tests/`, `examples/`, `scripts/`, `.github/workflows/` [`sandraschi--email-mcp`]

### Monorepo

- pnpm workspaces — `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n`; configs `pnpm-workspace.yaml`, `package.json`, `tsconfig.json`, `eslint.config.js`, `prettier.config.mjs`; `.changeset/` for changesets versioning [`upstash--context7`]

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

## Python-specific

### Build backend

- `hatchling.build` — `designcomputer--mysql_mcp_server`, `sandraschi--email-mcp`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`
- `setuptools.build_meta` — `duolingo--slack-mcp`. "Setuptools backend (minority in the Python sample; hatchling dominant)"
- pyproject.toml with uv (build backend not surfaced) — `feiskyer--mcp-kubernetes-server`, `severity1--terraform-cloud-mcp`
- Not surfaced (uv-backed) [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`]
- Likely hatchling given uv convention [`shreyaskarnik--huggingface-mcp-server`]
- Not captured [`echelon-ai-labs--servicenow-mcp`]
- `pyproject.toml`, backend not surfaced [`utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Legacy `setup.py` only (no pyproject.toml) — pre-modern packaging [`twolven--mcp-server-puppeteer-py`]
- No `pyproject.toml` at all — installation is entirely orchestrated by a bespoke script [`samuelgursky--davinci-resolve-mcp`]

### Lock file / version manager

- `uv.lock` present, uv convention — `duolingo--slack-mcp`, `feiskyer--mcp-kubernetes-server` (implied), `sajal2692--mcp-weaviate` (likely), `sandraschi--email-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server` (likely), `zilliztech--mcp-server-milvus`
- `.python-version` file referenced [`voska--hass-mcp`]
- pip (`pip install -e .`) — `echelon-ai-labs--servicenow-mcp` ("more conservative than the uv/uvx-heavy trend among newer servers")
- Lock file not noted; uses uv/uvx — `designcomputer--mysql_mcp_server` (also has legacy `pytest.ini` + `requirements-dev.txt` coexisting with pyproject.toml — "Requirements split across `pyproject.toml` + `pytest.ini` + `requirements-dev.txt` — older Python project layout; most newer projects in the corpus consolidate into pyproject.toml")
- None — venv managed by a bespoke installer [`samuelgursky--davinci-resolve-mcp`]
- None [`twolven--mcp-server-puppeteer-py`]
- Not surfaced [`utensils--mcp-nixos`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]

### Version manager convention

- uv [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- uv + uvx [`voska--hass-mcp`, `zilliztech--mcp-server-milvus`]
- uv + nix [`utensils--mcp-nixos`]
- pip + uvx [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Plain pip inside a venv managed by `install.py` [`samuelgursky--davinci-resolve-mcp`]
- pip + `requirements.txt` only — pre-modern [`twolven--mcp-server-puppeteer-py`]

### Schema / type strategy

- FastMCP auto-derives — `duolingo--slack-mcp`
- Pydantic via FastMCP — auto-derived from signatures [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Pydantic via raw MCP SDK [`shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Pydantic via FastMCP, schema auto-derived from type hints [`zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- mypy-checked + FastMCP auto-derived schemas [`utensils--mcp-nixos`]
- Pydantic likely arrives via `mcp[cli]` extra; not confirmed [`voska--hass-mcp`]
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

## Notable structural choices

Cross-cutting design decisions worth elevating, including unanticipated divergence axes.

### Per-verb capability gating

- `feiskyer--mcp-kubernetes-server` — granular per-capability CLI toggles (`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`) instead of a single read-only/full switch. Per-verb enable/disable as an argument surface pattern. "Four-way verb disable flags is a denial-ish denominator for capability gating"

### Two-axis safety toggles

- Read-only and delete-enabling are independent toggles, not collapsed into one write-mode flag [`severity1--terraform-cloud-mcp`]

### Read-only by default

- Server starts in least-privilege mode; write access opt-in [`rust-mcp-stack--rust-mcp-filesystem`, `shreyaskarnik--huggingface-mcp-server`]

### Read-only server pattern

- `duolingo--slack-mcp` — explicit read-only design (5 tools, no write capabilities)

### Tool catalog as data file

- `docker--hub-mcp` — `tools.json`/`tools.txt` ship tool definitions outside source. "Declarative catalog rather than inline schemas in source — opens an authoring path that doesn't require TS expertise"

### Architectural transport split

- `echelon-ai-labs--servicenow-mcp` — separate console scripts per transport rather than env-var-switched. "A cleaner separation but more install-time ceremony"

### Single-binary multi-transport

- `executeautomation--mcp-playwright` — `--port` switches between stdio and HTTP from one binary. Direct contrast with the architectural split pattern above

### Container as the only artifact

- `elastic--mcp-server-elasticsearch`, `duolingo--slack-mcp` — both ship Docker as the only/primary distribution channel; for `duolingo`, this "inverts the typical Python packaging path"

### LLM-targeted in-repo documentation

- `exa-labs--exa-mcp-server` — `llm_mcp_docs.txt` (411.7 KB) shipped as in-repo doc designed for LLM ingestion

### Vertical / domain-specific skills as first-class shipping artifact

- `exa-labs--exa-mcp-server` — skills directory with company research, code search, people research, financial reports, academic papers shipped alongside the server
- `upstash--context7` — ships `Skills` folder and `rules` folder alongside the MCP server in the same monorepo

### Vendor-specific companion config

- `docker--hub-mcp` — `gordon-mcp.yml` pre-shaping config for Docker's Ask Gordon agent

### Built-in security guidance in README

- `designcomputer--mysql_mcp_server` — "least-privilege user, never commit credentials" baked into README. Security guidance as a first-class README element

### Remote-hosted endpoint as primary

- `exa-labs--exa-mcp-server` — `https://mcp.exa.ai/mcp` as primary distribution; reduces setup friction. Native Claude Desktop connector eliminates manual config

### Lifecycle declaration in README

- `elastic--mcp-server-elasticsearch` — explicit deprecation notice in README; "the project is superseded by Elastic Agent Builder in ES 9.2.0+". A deprecation-status axis most repos don't surface

### High distribution-channel count

- `executeautomation--mcp-playwright` — npm + mcp-get + Smithery + Docker — four distribution mechanisms; flagged as "a reference for 'how many channels to publish to' decisions"

### Unofficial vs official competing implementations

- `executeautomation--mcp-playwright` (5.5k stars, unofficial) coexists with Microsoft's `@playwright/mcp`. "Both ship, neither is officially crowned" — competitive landscape axis

### Dual-mode tool surface

- Context-efficient compound vs full granular, user-selectable at launch [`samuelgursky--davinci-resolve-mcp`]

### Tool disabling at the CLI

- To reduce token usage in narrow workflows [`rust-mcp-stack--rust-mcp-filesystem`]

### Lazy connection / auto-launch

- Auto-reconnect and auto-launch of the underlying app on first tool call, smoothing cold-start UX [`samuelgursky--davinci-resolve-mcp`]

### Path-traversal protection

- File-op tools validate paths stay within expected directories [`samuelgursky--davinci-resolve-mcp`]

### Disk-bloat protection

- Auto-cleanup of exports after response encoding to prevent disk bloat [`samuelgursky--davinci-resolve-mcp`]

### Cross-platform sandbox handling

- Temp paths redirected per-OS (macOS/Linux/Windows) [`samuelgursky--davinci-resolve-mcp`]

### Multi-stage Docker for minimal image

- Multi-stage Docker build to a non-root static-binary alpine final image [`rust-mcp-stack--rust-mcp-filesystem`]

### Runtime backend reconfiguration

- Via a tool call rather than a restart [`sandraschi--email-mcp`]

### Multi-backend unified surface

- One tool dispatches to many providers; heterogeneity hidden from the caller [`sandraschi--email-mcp`]

### Per-tenant tools as first-class concept

- Tenancy is an argument, not server config [`sajal2692--mcp-weaviate`]

### Three-MCP-surface adoption with custom URI

- All three MCP surfaces (tools + resources + prompts) plus a custom URI scheme — uncommon among Python servers [`shreyaskarnik--huggingface-mcp-server`]

### Configs-as-product

- The GitHub repo ships only configs; the actual MCP server is a remote HTTP service [`slackapi--slack-mcp-plugin`]

### Author quality-tier framing

- "Industrial Quality Stack" / "SOTA 14.1" framing — author self-labels quality tiers; idiosyncratic and may be marketing rather than engineering signal [`sandraschi--email-mcp`]

### Cross-language port

- Author-cross-language port — Rust rewrite of the official JavaScript `@modelcontextprotocol/server-filesystem` for performance [`rust-mcp-stack--rust-mcp-filesystem`]

### Headless vs non-headless browser mode

- Deliberately non-headless for easier debugging — trades production efficiency for interactive visibility [`twolven--mcp-server-puppeteer-py`]

### In-memory binary handoff

- In-memory base64-encoded screenshot storage — flows through MCP responses without disk intermediate [`twolven--mcp-server-puppeteer-py`]

### Terminology vs implementation asymmetry

- Name "puppeteer-py" reflects user-facing concept; implementation actually wraps Playwright (Python equivalent) [`twolven--mcp-server-puppeteer-py`]

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

- TS project with no npm publish; clone-and-build only — distribution posture worth contrasting with TS peers that publish to npm [`v-3--discordmcp`]

### Marketplace metadata as plugin integration

- `.claude-plugin/marketplace.json` (not `plugin.json`) — marketplace-style integration distinct from full plugin wrapper [`upstash--context7`]

### OAuth2 client-side automatic token acquisition

- Automatic token acquisition on 401 response — unusual client-side feature [`viant--mcp`]

### Fine-grained authorization (experimental)

- Experimental fine-grained tool/resource control — suggests multi-user workspace scenarios being designed for [`viant--mcp`]

### Aggressive Python version floor

- 3.13 floor on a popular production server — uncommon [`voska--hass-mcp`]

### Pre-modern Python packaging

- `setup.py` only, no pyproject.toml — only legacy server in this bin [`twolven--mcp-server-puppeteer-py`]

### Ruff in runtime deps

- Lint tooling pinned in `[project.dependencies]` rather than dev extras [`zilliztech--mcp-server-milvus`]

## Server-as-product vs configs-as-product

> Cross-cutting axis surfaced by `slackapi--slack-mcp-plugin` and discriminating most other samples in the bins.

### Server-as-product

- Repo contains the implementation, packaging, tests, and distribution for a runnable server [most samples in these bins]

### Configs-as-product

- Repo contains only configs and skills/commands for client hosts; the MCP server itself is a remote HTTP endpoint operated separately. License may not be specified because the repo holds no implementation [`slackapi--slack-mcp-plugin`]

## Vendor relationship

### First-party (vendor publishes their own MCP)

- Slack-hosted remote MCP at `mcp.slack.com` published under `slackapi/` org [`slackapi--slack-mcp-plugin`]

### Third-party canonical (vendor has no MCP; community fills the gap)

- DaVinci Resolve has no first-party MCP from Blackmagic Design; this third-party server is effectively canonical for the 833-star community [`samuelgursky--davinci-resolve-mcp`]

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

- MIT — `designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`
- Apache-2.0 — `docker--hub-mcp`, `duolingo--slack-mcp`, `elastic--mcp-server-elasticsearch`, `feiskyer--mcp-kubernetes-server` ("Apache-2.0 license — rarer for independent-maintainer MCP servers, which skew MIT")
- pyproject license field not present despite README MIT badge [`voska--hass-mcp`]
- License may not be specified because the repo holds no implementation [`slackapi--slack-mcp-plugin`]

## Default branch

- `main` — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`
- `master` — `duolingo--slack-mcp`

## Star counts (popularity)

For bin 5: 7 (`duolingo--slack-mcp`), 16 (`feiskyer--mcp-kubernetes-server`), 137 (`docker--hub-mcp`), 241 (`echelon-ai-labs--servicenow-mcp`), 646 (`elastic--mcp-server-elasticsearch`), 1.2k (`designcomputer--mysql_mcp_server`), 4.3k (`exa-labs--exa-mcp-server`), 5.5k (`executeautomation--mcp-playwright`).

For bin 11/13 (selected): 287 (`voska--hass-mcp`), 833 (`samuelgursky--davinci-resolve-mcp`).

## Gaps observed

### Across bins (recurring)

- Python version floor and PyPI publication status frequently unconfirmed in extracted content
- Logging destination/format almost universally undocumented
- Last-commit date and CI trigger details often not surfaced
- Whether multi-backend servers share a common abstraction internally or use per-provider adapters typically not externally documented [`sandraschi--email-mcp`]

### Per-sample gaps / unknowns

- Last commit dates not extracted [`twolven--mcp-server-puppeteer-py`, `v-3--discordmcp`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Backend architecture intentionally private [`upstash--context7`]
- HTTP bridge internals not inspected — is it `streamable-http`, `sse`, or custom FastAPI? [`zongmin-yu--semantic-scholar-fastmcp-mcp-server`]
- Exact tool count / use of resources or prompts not captured [`voska--hass-mcp`]
- Go version constraints not documented in CI [`viant--mcp`]
- Docker artifacts absent despite Milvus typically being containerized [`zilliztech--mcp-server-milvus`]
- Whether server protects Python stdout from log pollution (stdio JSON-RPC correctness) [`twolven--mcp-server-puppeteer-py`]
- Changelog/release notes not visible in README [`upstash--context7`]
