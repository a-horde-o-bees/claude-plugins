# Sample

Pass-1 Phase-1a partial for bin 4. Atomic knowledge chunks from 8 samples (`ckreiling--mcp-server-docker`, `cloudflare--mcp-server-cloudflare`, `conikeec--mcpr`, `crystaldba--postgres-mcp`, `cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server`, `datalayer--earthdata-mcp-server`, `datalayer--jupyter-mcp-server`), organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

### License

- MIT — [`conikeec--mcpr`], [`crystaldba--postgres-mcp`]
- Apache-2.0 — [`cloudflare--mcp-server-cloudflare`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- BSD-3-Clause — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- GPL-3.0 — [`ckreiling--mcp-server-docker`] (called out as unusual: "ecosystem skews MIT/Apache")

### Repository status

- Active main-branch development is the norm.
- Archived repository — [`conikeec--mcpr`] archived as of February 8, 2026; v0.2.0 yanked due to SSE issues, v0.2.3+ recommended. Sample author flags this as a path the merger should consider: ecosystem captures pre-archive Rust libs that may already be superseded.

### Star-count spread

- 22 stars [`cyanheads--perplexity-mcp-server`] up to 3.6k [`cloudflare--mcp-server-cloudflare`]; ~25 [`datalayer--earthdata-mcp-server`], ~1,000 [`datalayer--jupyter-mcp-server`], 207 [`cyanheads--git-mcp-server`], 350 [`conikeec--mcpr`], 701 [`ckreiling--mcp-server-docker`], 2.6k [`crystaldba--postgres-mcp`].

## Language and runtime

### Implementation language

- Python — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- TypeScript on Node.js — [`cyanheads--git-mcp-server`] (Node >=20 + Bun >=1.2 dual runtime), [`cyanheads--perplexity-mcp-server`] (Node >=18)
- TypeScript on Cloudflare Workers (V8 isolate runtime, not Node) — [`cloudflare--mcp-server-cloudflare`]
- Rust — [`conikeec--mcpr`]

### Multi-runtime support

- Dual-runtime auto-detection (Node + Bun) — [`cyanheads--git-mcp-server`] is the only sample in the bin running on more than one runtime; treats Node ≥20 and Bun ≥1.2 as first-class peers.

## SDK / framework

### Python SDK variants

- Raw `mcp[cli]` SDK (low-level handler API, hand-authored schemas) — [`crystaldba--postgres-mcp`] (`mcp[cli]>=1.25.0`; "deliberate use of low-level hooks for custom tool gating"), [`datalayer--earthdata-mcp-server`] (`mcp[cli]>=1.2.1`), [`datalayer--jupyter-mcp-server`] (`mcp[cli]>=1.10.1`, also pulls `mcp.server.fastmcp` via the extra)
- FastMCP not explicitly used in any of the bin's Python samples; [`ckreiling--mcp-server-docker`] uses raw MCP Python SDK with FastMCP not surfaced

### TypeScript SDK + supporting libraries

- `@modelcontextprotocol/sdk` (`MCP SDK`) versions: ^1.29.0 [`cyanheads--git-mcp-server`], ^1.15.0 [`cyanheads--perplexity-mcp-server`]
- Hono for HTTP layer — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Zod validation — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Pino structured logging + tsyringe DI + optional OpenTelemetry — [`cyanheads--git-mcp-server`]

### Cloudflare Workers stack

- Workers-native (no Node SDK) with Turbo monorepo + internal `@repo/mcp-common` shared scaffolding — [`cloudflare--mcp-server-cloudflare`]; 14 domain Workers factor common server concerns into a shared package.

### Rust SDK

- Custom MCP library (this repo *is* the SDK) — [`conikeec--mcpr`]; ServerConfig builder pattern (`.with_name()`, `.with_version()`, `.with_tool()`).

## Transport

### Supported transport modes

- stdio only — [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`]
- stdio + SSE — [`crystaldba--postgres-mcp`] (default stdio, `--transport=sse` flag)
- stdio + Streamable HTTP — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--jupyter-mcp-server`]
- stdio + SSE in same library — [`conikeec--mcpr`] (WebSocket planned but unimplemented)
- Streamable HTTP + SSE on same Worker, distinguished by URL path — [`cloudflare--mcp-server-cloudflare`] (`/mcp` primary, `/sse` deprecated; "lets clients migrate at their own pace")

### Transport-selection mechanism

- Default; no flag — [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`]
- CLI flag — `--transport=sse` [`crystaldba--postgres-mcp`]; `mcpr generate-project --transport [stdio|sse]` selects at scaffold time [`conikeec--mcpr`]
- Environment-config selection (Zod-validated) — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- URL path on the server side — [`cloudflare--mcp-server-cloudflare`]
- npm script — `npm run start:stdio` vs `npm run start:http` [`cyanheads--git-mcp-server`]
- CLI launcher flag / config — [`datalayer--jupyter-mcp-server`]

### HTTP host/port defaults

- 127.0.0.1:3010 [`cyanheads--perplexity-mcp-server`]
- configurable hostname, port 3015 [`cyanheads--git-mcp-server`]

## Distribution

### Package managers / mechanisms

- PyPI (`pip install`) — [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- pipx — [`crystaldba--postgres-mcp`]
- uvx — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--jupyter-mcp-server`]
- `uv pip install` / `uv run` — [`crystaldba--postgres-mcp`]
- npm via npx — [`cyanheads--git-mcp-server`] (`npx @cyanheads/git-mcp-server@latest`)
- Bun via bunx — [`cyanheads--git-mcp-server`]
- Source clone + `npm install && npm run build && npm start` — [`cyanheads--perplexity-mcp-server`] (no published npm package; source-only)
- Cargo crate registry + `cargo install` for CLI — [`conikeec--mcpr`]
- Docker Hub image — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (`crystaldba/postgres-mcp`), [`datalayer--earthdata-mcp-server`] (`datalayer/earthdata-mcp-server:latest`), [`datalayer--jupyter-mcp-server`] (`datalayer/jupyter-mcp-server:latest`), [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine)
- Smithery registry registration via `smithery.yaml` — [`datalayer--earthdata-mcp-server`] flagged as a "first-class artifact"

### Remote-hosted (no local install)

- Cloudflare Workers — server author operates the runtime, end users only consume URLs; users install via `mcp-remote` shim that bridges stdio (host side) to streamable-HTTP (Worker side) [`cloudflare--mcp-server-cloudflare`]

### Source-only distribution

- [`cyanheads--perplexity-mcp-server`] — no npm package found, README walks through `git clone` → build → run.

## Entry point and launch

### Console-script names

- `mcp-server-docker` [`ckreiling--mcp-server-docker`]
- `postgres-mcp = "postgres_mcp:main"` [`crystaldba--postgres-mcp`]
- `earthdata-mcp-server` → `earthdata_mcp_server.server:server` [`datalayer--earthdata-mcp-server`]
- `jupyter-mcp-server` → `jupyter_mcp_server.CLI:server` [`datalayer--jupyter-mcp-server`]

### Wrapper / launcher patterns

- Dockerfile as launcher artifact — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- npm scripts split by transport — `npm run start:stdio` vs `npm run start:http` [`cyanheads--git-mcp-server`]
- npm build script compiles TS to `dist/` [`cyanheads--perplexity-mcp-server`]
- `mcpr generate-project --name [name]` scaffolds a fresh project [`conikeec--mcpr`]
- Jupyter Server extension config under `jupyter-config/` so the server can mount inside Jupyter rather than running standalone — [`datalayer--jupyter-mcp-server`]
- `mcp-remote` (npm) as a host-side shim translating stdio↔streamable-HTTP for remote servers — [`cloudflare--mcp-server-cloudflare`]

### Launch modes / shapes documented

- `uvx mcp-server-docker` [`ckreiling--mcp-server-docker`]
- `uvx postgres-mcp` / `postgres-mcp` (post-pipx) / `uv run postgres-mcp` / `docker run crystaldba/postgres-mcp` [`crystaldba--postgres-mcp`]
- `uvx jupyter-mcp-server@latest` / pip-installed console / Docker [`datalayer--jupyter-mcp-server`]
- pip-installed console / Docker [`datalayer--earthdata-mcp-server`]
- `npx @cyanheads/git-mcp-server@latest` / `bunx @cyanheads/git-mcp-server@latest` [`cyanheads--git-mcp-server`]
- `npx mcp-remote <url>` for remote — [`cloudflare--mcp-server-cloudflare`]

## Configuration surface

### Mechanism for delivering config

- Environment variables — [`ckreiling--mcp-server-docker`] (`DOCKER_HOST`), [`crystaldba--postgres-mcp`] (`DATABASE_URI`), [`datalayer--earthdata-mcp-server`] (`EARTHDATA_USERNAME`/`PASSWORD`), [`datalayer--jupyter-mcp-server`] (`JUPYTER_URL`, `JUPYTER_TOKEN`, `ALLOW_IMG_OUTPUT`, `DOCUMENT_ID`, `MCP_TOKEN`)
- `.env` file validated by Zod — [`cyanheads--perplexity-mcp-server`]
- Zod-validated env var bundle (transport, session, response format, Git identity, base-dir, GPG/SSH signing, auth, log level) — [`cyanheads--git-mcp-server`]
- CLI flags — [`crystaldba--postgres-mcp`] (`--access-mode unrestricted/restricted`, `--transport`)
- MCP client JSON `mcpServers` block — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- ServerConfig builder pattern (Rust) — [`conikeec--mcpr`] (`.with_name()`, `.with_version()`, `.with_tool()`; tool parameter schemas as JSON objects)
- Wrangler config (`wrangler.toml` / `wrangler.jsonc`) per Worker for server-side deployment; client side carries only the URL — [`cloudflare--mcp-server-cloudflare`]

### Schema/validation strategy on env

- Zod for env-var validation is the TS pattern in this bin — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`].

## Authentication

### Auth mode

- None / not applicable — [`conikeec--mcpr`] (library, "transport-layer security implied for production SSE deployments")
- Local OS / SDK credentials discovery — [`ckreiling--mcp-server-docker`] (Docker SDK `from_env()` discovery)
- Connection-string / URI-embedded credentials — [`crystaldba--postgres-mcp`] (`DATABASE_URI`)
- Username/password env vars — [`datalayer--earthdata-mcp-server`] (NASA Earthdata Login via `earthaccess` library, which "delegates the auth dance")
- Token env vars (single layer) — [`datalayer--jupyter-mcp-server`] 0.x had only `JUPYTER_TOKEN`
- Layered tokens — [`datalayer--jupyter-mcp-server`] v1.0.0+ split into `JUPYTER_TOKEN` (upstream Jupyter) + `MCP_TOKEN` (MCP interface) — "auth split by protocol layer"; called out as a breaking change
- API key + optional JWT/OAuth on HTTP transport — [`cyanheads--perplexity-mcp-server`] (`PERPLEXITY_API_KEY` + optional JWT or OAuth 2.1)
- Three-mode auth (`none` / `jwt` / `oauth`) selected via env config — [`cyanheads--git-mcp-server`] (`jwt` requires 32+ char secret; `oauth` uses OIDC provider)
- Cloudflare API tokens with per-service scopes; OAuth-like handshake negotiated by the `mcp-remote` shim — [`cloudflare--mcp-server-cloudflare`]

### Remote-host auth / SSH

- SSH-based auth for remote Docker daemons via `DOCKER_HOST=ssh://...` — [`ckreiling--mcp-server-docker`] flagged "first-class supported path, not just local socket"

### Read-only / restricted-access enforcement

- In-process SQL parsing rejects writes (not DB-level permissions) — [`crystaldba--postgres-mcp`] uses `pglast` to reject COMMIT/ROLLBACK in restricted mode

## Multi-tenancy

### Tenancy model

- Single-user per process — [`ckreiling--mcp-server-docker`] (one Docker daemon connection), [`datalayer--earthdata-mcp-server`] (bound to one NASA account), [`crystaldba--postgres-mcp`] (single DB connection per instance; SSE multiplexes clients but not tenants)
- Per-notebook scoped at runtime — [`datalayer--jupyter-mcp-server`] (`DOCUMENT_ID`, `use_notebook` switches target; one JupyterLab instance per server process)
- Per-user single instance with multi-client option in HTTP mode via JWT/OAuth — [`cyanheads--perplexity-mcp-server`]
- Workspace-keyed via base-directory restriction; per-session working-directory management — [`cyanheads--git-mcp-server`] (multi-tenant sandboxing within a stdio server)
- Per-request tenancy — [`cloudflare--mcp-server-cloudflare`] (each Worker invocation scoped by bearer token → authenticated Cloudflare account; one Worker serves any account)
- Not applicable (library, no tenancy concerns) — [`conikeec--mcpr`]

## Capabilities exposed

### Surface composition

- Tools only — [`crystaldba--postgres-mcp`] (deliberate; "the MCP client ecosystem has widespread support for MCP tools" cited as rationale for skipping resources/prompts), [`datalayer--earthdata-mcp-server`] (3 tools), [`cyanheads--perplexity-mcp-server`] (2 tools)
- Tools + resources + prompts — [`ckreiling--mcp-server-docker`] (28+ tools, container stats/logs resources, docker-compose workflow prompt — "advertises prompts as a first-class capability"), [`cyanheads--git-mcp-server`] (28 tools across 7 categories, 1 resource for repo metadata, 1 prompt)
- Tools only across many domain servers — [`cloudflare--mcp-server-cloudflare`] (14 domain Workers each exposing tools per domain)
- Tools + library scaffolding only — [`conikeec--mcpr`] (tool registration/invocation, handshake with version negotiation, disconnection handling, interactive vs one-shot modes)
- Tools (16+) — [`datalayer--jupyter-mcp-server`] (file/kernel listing, notebook CRUD, cell ops, full-notebook run, selected-cell fetch)

### Tool count bands

- 2 — [`cyanheads--perplexity-mcp-server`]
- 3 — [`datalayer--earthdata-mcp-server`]
- 9 — [`crystaldba--postgres-mcp`]
- 16+ — [`datalayer--jupyter-mcp-server`]
- 28 / 28+ — [`cyanheads--git-mcp-server`], [`ckreiling--mcp-server-docker`]

### Prompts as orchestration primitives

- Docker-compose natural-language → multi-step workflow prompt — [`ckreiling--mcp-server-docker`] flagged "MCP prompts as orchestration primitives rather than just tools"

### Single-tool, multi-mode parameter

- Three download modes (manifest, download, script) on one tool — [`datalayer--earthdata-mcp-server`] called out as "clean separation of 'describe what you would do' from 'do it'"

## Observability

### Approach

- Not surfaced — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (not in budget), [`conikeec--mcpr`]
- `rich` library implies colorized console output, no structured observability — [`datalayer--earthdata-mcp-server`]
- Worker logs via Cloudflare dashboard (host-side; not self-hostable) — [`cloudflare--mcp-server-cloudflare`]
- Structured Pino logging + request-context audit trails + optional OpenTelemetry — [`cyanheads--git-mcp-server`]
- Structured logging with file rotation (centralized utilities) — [`cyanheads--perplexity-mcp-server`]
- OpenTelemetry api+sdk (>=1.24.0) baked into core deps, not optional — [`datalayer--jupyter-mcp-server`] flagged "every installation ships observability"

### Audit trails

- Request context tracking for auditing — [`cyanheads--git-mcp-server`].

## Host / client integrations documented

### Hosts in the readmes

- Claude Desktop JSON `mcpServers` config — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`cloudflare--mcp-server-cloudflare`] (implied)
- Cursor — [`crystaldba--postgres-mcp`], [`cloudflare--mcp-server-cloudflare`]
- Windsurf — [`crystaldba--postgres-mcp`]
- Goose — [`crystaldba--postgres-mcp`]
- Qodo Gen — [`crystaldba--postgres-mcp`]
- Cline (config files like `cline_mcp_settings.json`) — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Cloudflare AI Playground (first-party) — [`cloudflare--mcp-server-cloudflare`]
- OpenAI Responses API — [`cloudflare--mcp-server-cloudflare`]
- JupyterLab as host (server mounts as Jupyter Server extension) — [`datalayer--jupyter-mcp-server`]
- Cloud-DB targets explicitly listed: AWS RDS, Azure SQL, Google Cloud SQL — [`crystaldba--postgres-mcp`]
- Generic JSON snippet pattern; not host-specific — [`datalayer--jupyter-mcp-server`], [`conikeec--mcpr`]

### Claude Code plugin wrapper

- None observed across all 8 samples — [`ckreiling--mcp-server-docker`], [`cloudflare--mcp-server-cloudflare`], [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`].

## Tests

### Framework

- pytest + pytest-asyncio — [`crystaldba--postgres-mcp`] (`asyncio_default_fixture_loop_scope = "function"`, `pythonpath = ["./src"]` src-layout)
- pytest with `test` extra — [`datalayer--earthdata-mcp-server`] (`pytest>=7.0`), [`datalayer--jupyter-mcp-server`] (pulls jupyter components and collab tools; `pytest.ini` present)
- Bun test runner with Vitest compatibility, coverage reports — [`cyanheads--git-mcp-server`]
- Vitest across the monorepo — [`cloudflare--mcp-server-cloudflare`]
- Mock transport implementations for testing across stdio and SSE — [`conikeec--mcpr`]
- TypeScript noEmit type check via `npm test` — [`cyanheads--perplexity-mcp-server`] (type-check as test)
- Not surfaced in README — [`ckreiling--mcp-server-docker`]

### Test data strategy

- AI-generated adversarial workloads — [`crystaldba--postgres-mcp`].

## CI

### System

- GitHub Actions — present in [`ckreiling--mcp-server-docker`] (specifics not surfaced), [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], [`cyanheads--perplexity-mcp-server`] (`.github/` present, README does not document), [`datalayer--earthdata-mcp-server`] (lint + type-check pipeline), [`datalayer--jupyter-mcp-server`]
- GitHub Actions + Turbo monorepo orchestration — [`cloudflare--mcp-server-cloudflare`]
- `npm run devcheck` (lint, format, typecheck) + dependency audit + unit + integration suite — [`cyanheads--git-mcp-server`]

## Container / packaging artifacts

### Dockerfile presence

- Present — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`] (also pre-built image on Docker Hub), [`datalayer--jupyter-mcp-server`], [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine), [`cyanheads--git-mcp-server`] (implied by Bun build)
- N/A — Workers not containers — [`cloudflare--mcp-server-cloudflare`]
- Not documented — [`conikeec--mcpr`]

### Container quality-of-life

- Docker host-address auto-remap (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux) — [`crystaldba--postgres-mcp`] flagged "rarely seen"
- Multi-stage Docker build — [`cyanheads--perplexity-mcp-server`].

### Registry registration

- `smithery.yaml` for Smithery registry — [`datalayer--earthdata-mcp-server`] (first-class repo artifact).

## Repo layout

### Layout shape

- Single Python package under `src/<name>/` — [`crystaldba--postgres-mcp`] (src-layout with `pythonpath = ["./src"]`), [`ckreiling--mcp-server-docker`] (`src/mcp_server_docker/`)
- Single Python package without explicit src-layout — [`datalayer--earthdata-mcp-server`] (`earthdata_mcp_server/` + `dev/` + `docs/`), [`datalayer--jupyter-mcp-server`] (`jupyter_mcp_server/` + `jupyter-config/` + `docs/`)
- Single TS Node package — [`cyanheads--perplexity-mcp-server`] (`.github/`, `src/`, `docs/`), [`cyanheads--git-mcp-server`] (organized by concern: tools/, resources/, transports/, services/, storage/, config/, utils/, container/; tests mirror structure)
- Single Rust library + `/examples/` — [`conikeec--mcpr`]
- Turbo/pnpm monorepo — [`cloudflare--mcp-server-cloudflare`] (14 domain Workers + shared `@repo/mcp-common`)

### Docs sets

- README + MCP.md + CHANGELOG + CONTRIBUTING — [`conikeec--mcpr`]
- README + `docs/` — [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]

## Notable structural choices

### Hosting responsibility as a design axis

- Server author operates the runtime, end users only consume URLs — [`cloudflare--mcp-server-cloudflare`] flags this as "axis: hosting responsibility" with downstream effects on release, auth, and observability concerns. Opposite end of the spectrum from local stdio servers like [`ckreiling--mcp-server-docker`] / [`datalayer--earthdata-mcp-server`].
- Stdio emulation via shim on the client side rather than on the server — `mcp-remote` translates stdio↔HTTP so hosts still speak stdio while server speaks HTTP [`cloudflare--mcp-server-cloudflare`].
- Paid-plan gating: some Cloudflare features require Workers paid plan; "operational cost surfaces as a server capability axis" — [`cloudflare--mcp-server-cloudflare`].

### Server-as-extension vs server-as-standalone

- Dual deployment: standalone MCP server OR Jupyter Server extension mounted inside Jupyter process — [`datalayer--jupyter-mcp-server`] called out "deployment axis".

### Runtime auto-detection

- Runtime auto-detection between Node and Bun — [`cyanheads--git-mcp-server`] flagged "axis: multi-runtime support".

### Tenant sandboxing in stdio

- Multi-tenant sandboxing via base-directory restriction in a stdio server — [`cyanheads--git-mcp-server`] flagged "axis: workspace isolation in a stdio server"; pairs with session-based working-directory isolation.

### Domain knowledge embedded in server

- Deterministic optimization algorithms (greedy search adapted from Microsoft Anytime), workload compression, hypothetical indexing via `hypopg`, Pareto-front cost-benefit balancing — [`crystaldba--postgres-mcp`] flagged "embedded performance-tuning intelligence goes far beyond typical SQL-execution MCP servers". Optional OpenAI integration for experimental LLM-based index tuning.
- Auto-complexity detection to switch between fast search and deep research tools — [`cyanheads--perplexity-mcp-server`].
- Two-phase version negotiation in server initialization handshake — [`conikeec--mcpr`].

### Sibling-package factoring

- Tool definitions factored into a separate PyPI project (`jupyter-mcp-tools>=0.1.6`) — [`datalayer--jupyter-mcp-server`] flagged "unusual reuse pattern in MCP land".

### Shared monorepo scaffolding

- Internal `@repo/mcp-common` workspace package abstracts shared server scaffolding across 14 domain Workers — [`cloudflare--mcp-server-cloudflare`] mirrors Cloudflare's own platform composition patterns.

### Auth split by protocol layer

- Dedicated MCP-level token (`MCP_TOKEN`) introduced separate from upstream Jupyter token (`JUPYTER_TOKEN`) in v1.0.0 — [`datalayer--jupyter-mcp-server`] called out "auth split by protocol layer".

### Three-mode tool design

- A single tool exposing manifest/download/script modes via parameter — [`datalayer--earthdata-mcp-server`] separating planning from execution.

### Library vs server

- A Rust library *for* building MCP servers (this repo *is* the SDK), not a server itself — [`conikeec--mcpr`]; ships `mcpr generate-project` CLI to scaffold new implementations and reduce boilerplate; ships mock transport for offline testing.

## Python-specific

### `requires-python` floor

- `>=3.10` — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- `>=3.12` — [`crystaldba--postgres-mcp`] (highest floor in the bin's Python set; "allows `TypeAliasType` and other 3.12 typing features"; ruff target-version intentionally lags at `py39` as style target separate from runtime floor)
- Pinned via `.python-version` file, value not surfaced — [`ckreiling--mcp-server-docker`]

### Build backend

- hatchling — [`crystaldba--postgres-mcp`] (`hatchling.build`), [`datalayer--earthdata-mcp-server`] (~1.21), [`datalayer--jupyter-mcp-server`] (~1.21)
- pyproject.toml present, backend not surfaced — [`ckreiling--mcp-server-docker`]

### Lock file / version manager

- uv.lock + uv-managed (`uv sync`) — [`crystaldba--postgres-mcp`]
- Devbox + uv combo — [`ckreiling--mcp-server-docker`]
- Standard PyPI publication via hatchling, lock not confirmed — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]

### Type / schema strategy

- Hand-authored JSON schemas (low-level MCP SDK) — [`crystaldba--postgres-mcp`]; project also pins pyright (`pyright==1.1.408` exact) for strict typing.
- Pydantic via MCP SDK — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`] (also FastAPI models for HTTP layer; schema auto-derived).

### Async profile

- `pytest-asyncio>=1.3.0` in dev deps; async tool surface — [`crystaldba--postgres-mcp`]
- async tornado/fastapi under the hood; pytest suite is async — [`datalayer--jupyter-mcp-server`]
- Likely sync (`earthaccess` is sync) — [`datalayer--earthdata-mcp-server`]
- async/sync behavior not surfaced — [`ckreiling--mcp-server-docker`]

### Optional-deps taxonomy

- Clean PEP 621 grouping into `test` / `lint` / `typing` extras — [`datalayer--earthdata-mcp-server`] (also `mdformat` + `mdformat-gfm` in lint extras for markdown-as-CI), [`datalayer--jupyter-mcp-server`] (`lint`, `typing`, `mcp[cli]` extras)

### Dev tooling pinning

- Exact-version pinning of dev tooling — [`crystaldba--postgres-mcp`] (`ruff==0.14.13`, `pyright==1.1.408`); flagged as "unusually strict for this sample".
- Devbox for reproducible dev environment (rarer than direnv/asdf) — [`ckreiling--mcp-server-docker`].
- `devenv.*` files for reproducible environments — [`crystaldba--postgres-mcp`].

### Heavy-deps note

- `jupyter_server`, `tornado>=6.1`, `fastapi`, `uvicorn` baked in — [`datalayer--jupyter-mcp-server`] reflects "this server brokers a live Jupyter kernel rather than a stateless data layer".
- `opentelemetry-api/sdk` as hard deps — [`datalayer--jupyter-mcp-server`] designed for production observability out of the box.

## Unanticipated axes observed

### Hosting model

- Hosting responsibility (operator-runs vs user-runs) — [`cloudflare--mcp-server-cloudflare`].

### Stdio-on-client emulation

- Stdio bridge on the host side via `mcp-remote` so the server can speak HTTP — [`cloudflare--mcp-server-cloudflare`].

### Context-length mitigation

- README guidance flagging chained-tool calls against high-cardinality data as a context-window concern the client must manage — [`cloudflare--mcp-server-cloudflare`].

### Capability declaration

- Advertising prompts as a first-class capability alongside tools — [`ckreiling--mcp-server-docker`].

### Workspace isolation in stdio

- Multi-tenant sandboxing via base-directory restriction — [`cyanheads--git-mcp-server`].

### Multi-runtime auto-detection

- Auto-detection between Node and Bun — [`cyanheads--git-mcp-server`].

### Auth layering

- MCP-level token distinct from upstream-service token — [`datalayer--jupyter-mcp-server`].

### Sibling-package tool factoring

- Tools published as a separate PyPI project — [`datalayer--jupyter-mcp-server`].

### Multi-mode single tool

- Manifest / download / script modes on one tool — [`datalayer--earthdata-mcp-server`].

### Reproducible-env tooling spread

- Devbox — [`ckreiling--mcp-server-docker`]
- devenv — [`crystaldba--postgres-mcp`]

## Gaps observed across the bin

- Exact last-commit dates often inferred from release tags or pushed_at timestamps rather than raw commit dates — [`cloudflare--mcp-server-cloudflare`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`ckreiling--mcp-server-docker`].
- Async/sync behavior, schema strategy, and test presence sometimes not surfaced in READMEs — [`ckreiling--mcp-server-docker`].
- Lock-file conventions not always confirmed — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`].
- Whether CI publishes to PyPI on tag not always confirmed — [`datalayer--earthdata-mcp-server`].
- Logging/observability specifics not always documented — [`crystaldba--postgres-mcp`].
- Toolset-gating consistency across domain servers in monorepos not always documented — [`cloudflare--mcp-server-cloudflare`].
- Self-hostable variant deployability for hosted-only repos sometimes unclear — [`cloudflare--mcp-server-cloudflare`] (source ships, docs focus on hosted URLs).
- For archived libs, supersession status often unclear — [`conikeec--mcpr`].
