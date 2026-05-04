# Sample

Pass-1 Phase-1a partial for bin 7. Atomic knowledge chunks from `jbeno--cursor-notebook-mcp.md`, `jlowin--fastmcp.md`, `jparkerweb--mcp-sqlite.md`, `korotovsky--slack-mcp-server.md`, `ktanaka101--mcp-server-duckdb.md`, `labeveryday--mcp_pdf_reader.md`, `lanbaoshen--mcp-jenkins.md`, `mahdin75--gis-mcp.md`, organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

### License

- MIT predominates [`jparkerweb--mcp-sqlite`, `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- Apache-2.0 [`jlowin--fastmcp`]
- Creative Commons NonCommercial — `CC BY-NC-SA 4.0` is rare for MCP servers, restricts commercial adoption [`jbeno--cursor-notebook-mcp`]

### Default branch

- `main` is dominant [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `mahdin75--gis-mcp`]
- `master` still in active use [`korotovsky--slack-mcp-server`, `lanbaoshen--mcp-jenkins`]

## Language and runtime

### Language

- Python — most common in this bin [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- TypeScript / JavaScript [`jparkerweb--mcp-sqlite`]
- Go [`korotovsky--slack-mcp-server`]

### Python version floor

- `>=3.10` is the modal floor across Python servers [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`]
- `.python-version` file present without explicit floor in pyproject [`labeveryday--mcp_pdf_reader`]
- Floor not surfaced [`lanbaoshen--mcp-jenkins`]

### Node version floor

- `>=14.0.0` [`jparkerweb--mcp-sqlite`]

### Go version

- `1.21+` inferred from go.mod features [`korotovsky--slack-mcp-server`]

### SDK / framework variant

#### FastMCP 2.x

- `fastmcp >= 2.7.0, < 2.11` — narrow window guarding against FastMCP 2.11 breaking changes [`jbeno--cursor-notebook-mcp`]
- `fastmcp == 2.13.1` exact pin — conservative against API drift [`mahdin75--gis-mcp`]
- Version not pinned precisely; `pip install fastmcp` [`labeveryday--mcp_pdf_reader`]

#### Raw MCP Python SDK

- `mcp >= 1.0.0`; low-level server API; hand-authored schemas [`ktanaka101--mcp-server-duckdb`]
- Raw MCP SDK with no FastMCP reference [`lanbaoshen--mcp-jenkins`]

#### Dual MCP-framework declarations

- Both `fastmcp >= 2.7.0, < 2.11` and `mcp >= 0.1.0` declared as deps — suggests migration / compatibility shim [`jbeno--cursor-notebook-mcp`]

#### FastMCP itself

- `jlowin--fastmcp` is the framework, not a server. Wraps and was absorbed into the official MCP Python SDK in 2024. Self-claims to power "70% of MCP servers across all languages." Three-pillar model: Servers, Clients, Apps. Decorator-based API (`@mcp.tool`, etc.) is the canonical Python authoring path

#### TypeScript SDK

- `@modelcontextprotocol/sdk ^1.12.1` [`jparkerweb--mcp-sqlite`]

#### Go: custom implementation

- No standard Go MCP framework; custom MCP implementation [`korotovsky--slack-mcp-server`]

## Transport

### Supported transports

#### stdio only

- [`jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`]

#### stdio + HTTP variants

- stdio + Streamable HTTP + SSE [`jbeno--cursor-notebook-mcp`, `mahdin75--gis-mcp`]
- stdio + SSE + streamable-http (default port 9887) [`lanbaoshen--mcp-jenkins`]
- stdio + SSE + HTTP [`korotovsky--slack-mcp-server`]
- stdio + HTTP at framework level [`jlowin--fastmcp`]

### How transport is selected

- CLI flags (`--host`, `--port`) plus inference from host JSON config [`jbeno--cursor-notebook-mcp`]
- CLI flag selection [`lanbaoshen--mcp-jenkins`]
- Env var (`SLACK_MCP_TRANSPORT`, default stdio) [`korotovsky--slack-mcp-server`]
- Env var (`GIS_MCP_TRANSPORT`) [`mahdin75--gis-mcp`]
- Implicit / default — stdio only [`jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`]
- Programmatic via `mcp.run()` signature in consumer code [`jlowin--fastmcp`]

### Default ports for HTTP

- 9887 [`lanbaoshen--mcp-jenkins`]
- 9010 (HTTP via Docker) [`mahdin75--gis-mcp`]
- 13080 [`korotovsky--slack-mcp-server`]
- 8080 / `127.0.0.1:8080/mcp` host-config example [`jbeno--cursor-notebook-mcp`]

## Distribution

### Distribution mechanisms

#### PyPI / uvx

- PyPI + uvx + Smithery installer (`npx @smithery/cli install …`) [`ktanaka101--mcp-server-duckdb`]
- PyPI + uvx + Docker (ghcr.io image) [`lanbaoshen--mcp-jenkins`]
- PyPI + editable dev install [`jbeno--cursor-notebook-mcp`]
- PyPI + editable + Docker (two Dockerfiles) + Smithery [`mahdin75--gis-mcp`]
- PyPI only [`jlowin--fastmcp`]

#### npm

- npm package; `npx -y mcp-sqlite <database-path>` direct invocation without intermediate config [`jparkerweb--mcp-sqlite`]

#### Docker / source

- Docker (Dockerfile + 3 docker-compose variants), npm tool for MCP Inspector, source build via Go [`korotovsky--slack-mcp-server`]

#### Source-only / clone-and-run

- No PyPI publication — clone-and-run consumption [`labeveryday--mcp_pdf_reader`]

### Install commands shown in README

- `uvx <package>` is the canonical Python launcher [`ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]
- `uv pip install <package>` [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `mahdin75--gis-mcp`]
- `pip install <package>` (also offered) [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `lanbaoshen--mcp-jenkins`]
- `uv sync` + `uv run python <script>.py` (clone-then-run) [`labeveryday--mcp_pdf_reader`]
- `npx -y <package> <args>` direct [`jparkerweb--mcp-sqlite`]
- `go run <main>.go --transport stdio` source build [`korotovsky--slack-mcp-server`]

## Entry point / launch

### Console script vs bare script vs framework

#### Named console script

- `cursor-notebook-mcp` (also `python -m cursor_notebook_mcp.server`) [`jbeno--cursor-notebook-mcp`]
- `mcp-server-duckdb` registered to `mcp_server_duckdb:main` [`ktanaka101--mcp-server-duckdb`]
- `mcp-jenkins` console script [`lanbaoshen--mcp-jenkins`]
- `gis-mcp` (also `python -m gis_mcp`) [`mahdin75--gis-mcp`]
- `mcp-sqlite-server` (CommonJS, package.json `bin`) [`jparkerweb--mcp-sqlite`]

#### Bare script (no console-script entry)

- `python pdf_reader_server.py` directly — the "script as a server" simpler distribution tier [`labeveryday--mcp_pdf_reader`]

#### Framework-level CLI

- `fastmcp = "fastmcp.cli:app"` — `fastmcp dev`, `fastmcp run`, `fastmcp install` for dev workflow rather than serving [`jlowin--fastmcp`]

#### Source-build only

- `go run mcp/mcp-server.go --transport stdio` (no published binary) [`korotovsky--slack-mcp-server`]

### Wrapper scripts and helpers

- `run_tests.sh` + `run_tests.ps1` — explicit Windows parity [`jbeno--cursor-notebook-mcp`]
- Makefile (~5.7 KB) for cross-platform build automation [`korotovsky--slack-mcp-server`]
- Multi-platform Dockerfile under `/docker/` [`lanbaoshen--mcp-jenkins`]
- Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev) [`mahdin75--gis-mcp`]
- 3 docker-compose variants — base, dev, toolkit [`korotovsky--slack-mcp-server`]

## Configuration surface

### Config delivery mechanism

- CLI flags only [`ktanaka101--mcp-server-duckdb`, `jparkerweb--mcp-sqlite`]
- CLI flags + host JSON config [`jbeno--cursor-notebook-mcp`]
- CLI flags + HTTP headers for per-request credential passthrough [`lanbaoshen--mcp-jenkins`]
- Env vars [`korotovsky--slack-mcp-server`, `mahdin75--gis-mcp`]
- System-level dependency only (Tesseract install) — no runtime config surface [`labeveryday--mcp_pdf_reader`]
- Programmatic — framework consumers wire their own config [`jlowin--fastmcp`]

## Authentication

### No authentication

- Local DuckDB file access [`ktanaka101--mcp-server-duckdb`]
- Local SQLite file access [`jparkerweb--mcp-sqlite`]
- Local PDF processing [`labeveryday--mcp_pdf_reader`]
- No MCP-layer auth; downstream API keys handled per dataset [`mahdin75--gis-mcp`]

### Multi-mode auth

- Four Slack token types: `XOXC` (browser), `XOXD` (cookie), `XOXP` (user OAuth), `XOXB` (bot) — flexible choice covers stealth mode and OAuth [`korotovsky--slack-mcp-server`]
- Jenkins username + password (or API token) via CLI (static) OR HTTP headers (per-request) [`lanbaoshen--mcp-jenkins`]
- SFTP/SSH key vs password vs key+interactive (`--sftp-auth-mode auto/key/password/key+interactive`) [`jbeno--cursor-notebook-mcp`]

### Framework-level

- Consumer-defined; framework supports middleware patterns for auth layering [`jlowin--fastmcp`]

## Multi-tenancy

### Tenancy model

#### Single-user / single-database

- One DuckDB file per server instance [`ktanaka101--mcp-server-duckdb`]
- One SQLite database per instance [`jparkerweb--mcp-sqlite`]
- Single-user, file-processing only [`labeveryday--mcp_pdf_reader`]
- Single-user; HTTP mode exposes upload/download but no tenant isolation [`mahdin75--gis-mcp`]

#### Workspace-keyed

- Workspace root restrictions enforced via `os.path.realpath`; `--allow-root` required for local-path access [`jbeno--cursor-notebook-mcp`]
- Per-workspace tenancy via Slack API token; per-user isolation via DM/channel context [`korotovsky--slack-mcp-server`]

#### Per-request credentials (HTTP-mode multi-tenancy)

- `x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password` headers — single deployed server can target multiple Jenkins instances per request; turns single-tenant stdio into multi-tenant HTTP service [`lanbaoshen--mcp-jenkins`]

#### Framework

- Arbitrary tenancy patterns — consumer decides; HTTP transport enables shared deployments [`jlowin--fastmcp`]

## Capabilities exposed

### Tool count and shape

#### Single generic tool delegating to LLM

- Single `query` tool accepting arbitrary SQL — delegates SQL generation entirely to LLM [`ktanaka101--mcp-server-duckdb`]

#### Few specialized tools

- Database introspection + CRUD + parameterized SQL queries [`jparkerweb--mcp-sqlite`]
- PDF text extraction + image extraction + OCR text recognition [`labeveryday--mcp_pdf_reader`]

#### Many specialized tools (10–30)

- 14 tools — conversation history, thread replies, message search, reactions, user-group management, unread tracking; plus 2 resources as CSV directories (channel list, user list) [`korotovsky--slack-mcp-server`]
- 24 tools covering job management, build operations, queue handling, node/view queries, console output retrieval [`lanbaoshen--mcp-jenkins`]
- 25+ tools — `notebook_create`, `notebook_read`, `notebook_edit_cell`, `notebook_add_cell`, `notebook_export`, `notebook_search`, `notebook_get_outline`, `notebook_get_server_path_context`, plus SFTP-compatible variants [`jbeno--cursor-notebook-mcp`]

#### Massive tool count (50+)

- 92 tools across 5 libraries — Shapely (29), PyProj (13), GeoPandas (13), Rasterio (20), PySAL (18), visualization (2), plus data-acquisition modules. HTTP mode adds REST `/storage/upload`, `/storage/download`, `/storage/list` for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]

### Capability types beyond tools

- Tools + resources (CSV channel/user lists exposed as resources) [`korotovsky--slack-mcp-server`]
- Three-pillar framework: Servers (tools/resources/prompts), Clients, Apps (interactive UIs in conversations) [`jlowin--fastmcp`]
- REST endpoints alongside MCP tools to handle binary file transfer [`mahdin75--gis-mcp`]

## Observability

### Logging

- `SLACK_MCP_LOG_LEVEL` env var; macOS log location `~/Library/Logs/Claude/mcp*.log`; Inspector tool for debugging [`korotovsky--slack-mcp-server`]
- Framework-level logging utilities; consumers configure destinations [`jlowin--fastmcp`]
- Not surfaced [`jbeno--cursor-notebook-mcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- MCP Inspector script via `npm test` [`jparkerweb--mcp-sqlite`]

## Host integrations

### Cursor

- `.cursor/mcp.json` (project-scoped) and `~/.cursor/mcp.json` (global) — explicit dual-level config documented [`jbeno--cursor-notebook-mcp`]
- `.cursor/mcp.json` snippet [`mahdin75--gis-mcp`]
- npx command [`jparkerweb--mcp-sqlite`]

### Claude Desktop

- `claude_desktop_config.json` JSON entry [`ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `lanbaoshen--mcp-jenkins`]
- Implied via stdio transport [`jbeno--cursor-notebook-mcp`]
- Primary integration documented [`korotovsky--slack-mcp-server`]

### VSCode

- `.vscode/mcp.json` entry [`lanbaoshen--mcp-jenkins`]
- npx command [`jparkerweb--mcp-sqlite`]

### JetBrains IDE

- Documented integration — unusual; most MCP servers focus on Claude/Cursor/VSCode [`lanbaoshen--mcp-jenkins`]

### Smithery registry

- Smithery installer for host registration [`ktanaka101--mcp-server-duckdb`]
- `smithery.yaml` registered [`mahdin75--gis-mcp`]

### Enterprise Slack / GovSlack

- Custom User-Agent + TLS config for Slack environments [`korotovsky--slack-mcp-server`]

### DXT (Desktop Extensions) manifest

- `manifest-dxt.json` — Claude Desktop-specific packaging format distinct from `.mcp.json` [`korotovsky--slack-mcp-server`]

## Claude Code plugin wrapper

### Presence

- None observed across this bin [`jbeno--cursor-notebook-mcp`, `jparkerweb--mcp-sqlite`, `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- Not applicable — framework level [`jlowin--fastmcp`]

## Tests

### Test framework and tooling

#### Python — pytest variants

- pytest + pytest-asyncio + pytest-cov + pytest-timeout; `tests/` directory; `test_plan.md` for scenario documentation; cross-platform shell-script runners [`jbeno--cursor-notebook-mcp`]
- Extreme tooling stack: pytest + pytest-asyncio + pytest-cov + pytest-env + pytest-flakefinder + pytest-httpx + pytest-report + pytest-retry + pytest-timeout + pytest-xdist + inline-snapshot + pytest-examples; `asyncio_mode = "auto"`, `timeout = 5`, `testpaths = ["tests"]` [`jlowin--fastmcp`]
- pytest with coverage and async support in `test` extra [`mahdin75--gis-mcp`]
- pytest in dev deps; no pytest config in pyproject.toml — minimal [`ktanaka101--mcp-server-duckdb`]
- `tests/` directory present; framework not surfaced [`lanbaoshen--mcp-jenkins`]

#### Node / npm

- MCP Inspector framework; `npm test` script [`jparkerweb--mcp-sqlite`]

#### None / undocumented

- Tests not documented [`korotovsky--slack-mcp-server`, `labeveryday--mcp_pdf_reader`]

## CI

### CI presence

- GitHub Actions in `.github/` [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp` (`run-tests.yml`), `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- codecov integration [`lanbaoshen--mcp-jenkins`]
- CI badge visible [`mahdin75--gis-mcp`]
- Not documented [`jparkerweb--mcp-sqlite`, `labeveryday--mcp_pdf_reader`]

## Container / packaging artifacts

### Container strategy

#### None

- [`jbeno--cursor-notebook-mcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`]

#### Single Dockerfile

- Multi-platform Dockerfile under `/docker/` [`lanbaoshen--mcp-jenkins`]
- Dockerfile (874 bytes) + `.dockerignore` [`korotovsky--slack-mcp-server`]

#### Multiple Dockerfiles / compose variants

- 3 docker-compose variants: `docker-compose.yml` (base), `docker-compose.dev.yml`, `docker-compose.toolkit.yml` [`korotovsky--slack-mcp-server`]
- Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev) [`mahdin75--gis-mcp`]

#### Framework-level — consumer-containerized

- [`jlowin--fastmcp`]

## Example client / developer ergonomics

### Inspector / curl / make

- MCP Inspector recommended (`npx @modelcontextprotocol/inspector`) [`ktanaka101--mcp-server-duckdb`, `korotovsky--slack-mcp-server`, `jparkerweb--mcp-sqlite`]
- Makefile for build automation [`korotovsky--slack-mcp-server`]
- `cursor_rules.md` (AI guidance file shipped alongside the server — not an MCP tool/prompt, just bundled doc for the LLM to read) [`jbeno--cursor-notebook-mcp`]
- `agents/` directory with runnable example clients [`mahdin75--gis-mcp`]
- `.vscode/mcp.json` sample [`lanbaoshen--mcp-jenkins`]
- `examples/` + `docs/` directories; community Discord; docs at gofastmcp.com [`jlowin--fastmcp`]

### LLM-consumable docs

- `llms.txt` and `llms-full.txt` for AI-consumable docs ("vibe coding" context) [`jlowin--fastmcp`, `mahdin75--gis-mcp`]

## Repo layout

### Layout patterns

- Single-package Python with src-layout (`src/<package>/`) using uv [`jlowin--fastmcp`, `mahdin75--gis-mcp`]
- Single-package Python (flat layout) + `examples/` + `tests/` [`jbeno--cursor-notebook-mcp`]
- Single-package Python [`ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]
- Single npm package with `package.json`, README, `bin` entry [`jparkerweb--mcp-sqlite`]
- Single Go package with `cmd/`, `pkg/`, `build/`, `docs/`, `.github/`, `.vscode/`, `npm/`, plus `manifest-dxt.json`, `SECURITY.md` [`korotovsky--slack-mcp-server`]
- Single-file server (`pdf_reader_server.py`) — no package [`labeveryday--mcp_pdf_reader`]

## Python-specific

### Build backend

- `hatchling.build` is the dominant choice [`ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `jlowin--fastmcp`]
- pyproject.toml (uv-based); backend not surfaced [`lanbaoshen--mcp-jenkins`]
- Not applicable — single script [`labeveryday--mcp_pdf_reader`]

### Lock file

- `uv.lock` present [`jlowin--fastmcp`]
- `uv.lock` implied [`labeveryday--mcp_pdf_reader`, `ktanaka101--mcp-server-duckdb`]
- Not explicitly confirmed [`mahdin75--gis-mcp`, `jbeno--cursor-notebook-mcp`, `lanbaoshen--mcp-jenkins`]

### Version manager convention

- `uv` / `uvx` overwhelmingly [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]

### Optional-extras strategy

- Per-library opt-in fan-out — 8 domain-specific extras (`administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, `test`) plus an `all` extra; users install only the toolchain they need [`mahdin75--gis-mcp`]
- Very broad optional-dependencies surface — `anthropic`, `azure`, `gemini`, `openai`, `apps`, `code-mode`, `tasks` — each opt-in, avoiding bloat on core install [`jlowin--fastmcp`]

### Async vs sync handlers

- async (FastMCP + starlette + uvicorn) [`jbeno--cursor-notebook-mcp`]
- Both `def` and `async def` dispatched transparently; anyio/asyncio under the hood [`jlowin--fastmcp`]
- FastMCP auto-wraps both [`mahdin75--gis-mcp`]
- Sync handlers — file-processing stack (PyMuPDF, pytesseract) is CPU-bound; async offers little value [`labeveryday--mcp_pdf_reader`]
- Not surfaced [`ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]

### Type / schema strategy

- Pydantic 2.x (`>=2.0.0, <2.12.0`); FastMCP auto-derives from signatures [`jbeno--cursor-notebook-mcp`]
- Auto-derived JSON Schema from type hints + docstrings; `Annotated[type, Field(description=...)]` patterns; pydantic + jsonschema-path + jsonref [`jlowin--fastmcp`]
- Pydantic via FastMCP; auto-derived [`mahdin75--gis-mcp`]
- FastMCP auto-derives from type hints [`labeveryday--mcp_pdf_reader`]
- Hand-authored schemas (low-level MCP SDK) [`ktanaka101--mcp-server-duckdb`]

### Type checker / linter / pre-commit

- `prek` (pre-commit replacement) in dev deps; ruff + `ty` (Astral's new type checker) — adopting newer tooling ahead of the ecosystem [`jlowin--fastmcp`]
- Pre-commit-style workflow [`mahdin75--gis-mcp`]
- Minimal dev tooling — only pytest in dev; no ruff/mypy/coverage [`ktanaka101--mcp-server-duckdb`]

## Notable structural choices

### Path-traversal defense

- Workspace-root enforcement via `os.path.realpath`; `--allow-root` required for local-path access [`jbeno--cursor-notebook-mcp`]

### Connection lifecycle as user-visible knob

- `--keep-connection` flag enables TEMP objects across calls — deliberate session-state trade-off [`ktanaka101--mcp-server-duckdb`]
- Session-singleton toggle reuses one client across tool calls for connection pooling [`lanbaoshen--mcp-jenkins`]

### Read-only mode strategies

- `--readonly` flag delegates to DuckDB's native protection (not tool-layer validation); non-readonly auto-creates DB file and parent dirs [`ktanaka101--mcp-server-duckdb`]
- Read-only mode flag at server level [`lanbaoshen--mcp-jenkins`]

### Cross-platform parity

- Dual-platform shell scripts (`.sh` + `.ps1`) — Windows parity is explicit, not afterthought [`jbeno--cursor-notebook-mcp`]
- Makefile for cross-platform build automation [`korotovsky--slack-mcp-server`]

### Documentation as test

- `griffelib`, `inline-snapshot`, `pytest-examples` — docs are test-verified [`jlowin--fastmcp`]

### Flake hunting and parallelism in tests

- `pytest-flakefinder` + `pytest-retry` + `pytest-xdist` — flake hunting and parallelism built in [`jlowin--fastmcp`]

### Heavy core deps over minimal footprint

- `paramiko` as core dep — SFTP support is mainline, not optional [`jbeno--cursor-notebook-mcp`]
- Heavy geospatial deps (rasterio, fiona, geopandas) kept as core deps — prioritizes install simplicity over minimal wheel size [`mahdin75--gis-mcp`]

## Unanticipated axes observed

### Remote-filesystem MCP (over SFTP)

- MCP server is local but operates on remote files over SFTP — distinct from HTTP/REST remote access [`jbeno--cursor-notebook-mcp`]

### Bundled AI-guidance content

- `cursor_rules.md` shipped alongside server — neither MCP tool nor prompt, just LLM-readable guidance [`jbeno--cursor-notebook-mcp`]
- `llms.txt` / `llms-full.txt` — design-for-AI-consumption documentation format [`jlowin--fastmcp`, `mahdin75--gis-mcp`]

### Multi-token-type auth as flexibility

- Four Slack token types within one server — multiple auth mechanisms covering stealth mode and OAuth [`korotovsky--slack-mcp-server`]

### Per-request HTTP-header credentials

- Header-based credential passthrough turning single-tenant stdio server into multi-tenant HTTP service [`lanbaoshen--mcp-jenkins`]

### REST endpoints alongside MCP tools

- File-transfer REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]

### Massive cross-library tool fan-out

- 92 tools wrapping 5+ Python libraries into one "GIS Swiss army knife" MCP surface [`mahdin75--gis-mcp`]

### Bare-script server

- "Script as a server" pattern (`python <script>.py`) competes with console-script-PyPI as a simpler distribution tier [`labeveryday--mcp_pdf_reader`]

### System-tool dependency

- Tesseract OCR install required out-of-band on host — server cannot self-install (similar to ffmpeg servers) [`labeveryday--mcp_pdf_reader`]

### Zero-auth file-processing family

- Distinct family of MCP servers operating on local file inputs without any auth [`labeveryday--mcp_pdf_reader`]

### "Apps" pillar

- FastMCP's third pillar (Servers, Clients, Apps) extends MCP into UI territory beyond the standard tool/resource/prompt triad [`jlowin--fastmcp`]

### Self-claimed ecosystem centrality

- "Powers 70% of MCP servers across all languages" — market self-assessment worth noting as ecosystem signal [`jlowin--fastmcp`]
