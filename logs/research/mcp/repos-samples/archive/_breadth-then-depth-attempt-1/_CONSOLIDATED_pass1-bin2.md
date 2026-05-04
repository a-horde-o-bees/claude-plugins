# Sample

Pass-1 Phase-1a partial for bin 2. Atomic knowledge chunks from JackKuo666--PubMed-MCP-Server, PagerDuty--pagerduty-mcp-server, ahmedmustahid--postgres-mcp-server, alexei-led--k8s-mcp-server, alpacahq--alpaca-mcp-server, apollographql--apollo-mcp-server, awslabs--aws-api-mcp-server, awslabs--aws-documentation-mcp-server, organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

### License

- MIT — [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`]
- Apache-2.0 — [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]

### Default branch

- `main` — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`ahmedmustahid--postgres-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `master` — [`alexei-led--k8s-mcp-server`]

### Authorship

- Vendor-authored (official organization repo) — [`PagerDuty--pagerduty-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Community / individual maintainer — [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`]

> Vendor-authored vs community-authored is a trust dimension surfaced explicitly by [`alpacahq--alpaca-mcp-server`] — the vendor's own MCP server carries credibility that derivative servers don't.

## Language and runtime

### Language

- Python — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- TypeScript / Node.js — [`ahmedmustahid--postgres-mcp-server`] (with secondary `pyproject.toml` of unclear purpose)
- Rust — [`apollographql--apollo-mcp-server`]

### Python version floor

- `>=3.10` — [`JackKuo666--PubMed-MCP-Server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `>=3.13` — [`alexei-led--k8s-mcp-server`] (unusually high floor for April 2026 work)
- Pinned via `.tool-versions` (asdf), specific value not surfaced — [`PagerDuty--pagerduty-mcp-server`]

### Python version pin mechanism

- `.python-version` file (pyenv-style) — [`JackKuo666--PubMed-MCP-Server`]
- `requires-python` in pyproject.toml — [`alpacahq--alpaca-mcp-server`], [`alexei-led--k8s-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `.tool-versions` (asdf) — [`PagerDuty--pagerduty-mcp-server`]

> asdf-based pinning is rarer than uv-native or `.python-version`; flagged as notable by [`PagerDuty--pagerduty-mcp-server`].

## Framework / SDK

### Python SDK choice

- FastMCP — [`JackKuo666--PubMed-MCP-Server`] (version not pinned in README)
- FastMCP 2.x (`fastmcp>=2.0.0`) — [`alpacahq--alpaca-mcp-server`]
- FastMCP 3.x (`fastmcp>=3.0.1`) **alongside** raw `mcp>=1.23.0` — [`awslabs--aws-api-mcp-server`] (one server bridging two SDK generations)
- Raw MCP Python SDK — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`]
- Raw `mcp[cli]>=1.23.0` — [`awslabs--aws-documentation-mcp-server`]

### Non-Python SDK

- Anthropic MCP TypeScript SDK (`StreamableHTTPServerTransport`, `StdioServerTransport`) — [`ahmedmustahid--postgres-mcp-server`]
- Rust MCP implementation in the Apollo GraphQL ecosystem — [`apollographql--apollo-mcp-server`]

## Transport

### Supported transports

- stdio only — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- stdio + streamable-http — [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`ahmedmustahid--postgres-mcp-server`] (HTTP is default; stdio via subcommand)
- stdio + streamable-http + sse (deprecated) — [`alexei-led--k8s-mcp-server`]
- Not enumerated in fetched view (config-file driven) — [`apollographql--apollo-mcp-server`]

### Transport selection mechanism

- Implicit / default stdio — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- CLI flag / environment variable — [`alpacahq--alpaca-mcp-server`], [`alexei-led--k8s-mcp-server`], [`awslabs--aws-api-mcp-server`]
- Positional subcommand (e.g. `npx ... stdio` switches from default HTTP to stdio) — [`ahmedmustahid--postgres-mcp-server`]
- Configuration file — [`apollographql--apollo-mcp-server`]

## Distribution

### Distribution channels (one server may use several)

- PyPI (`uvx`) — [`PagerDuty--pagerduty-mcp-server`] (`pagerduty-mcp`), [`alpacahq--alpaca-mcp-server`] (`alpaca-mcp-server`), [`awslabs--aws-api-mcp-server`] (`awslabs.aws-api-mcp-server`), [`awslabs--aws-documentation-mcp-server`] (`awslabs.aws-documentation-mcp-server`)
- npm (`npx`) — [`ahmedmustahid--postgres-mcp-server`] (`@ahmedmustahid/postgres-mcp-server`)
- Cargo crate / GitHub binary releases — [`apollographql--apollo-mcp-server`]
- Docker / OCI image — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`] (ghcr.io), [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`awslabs--aws-api-mcp-server`] (AWS public ECR), [`awslabs--aws-documentation-mcp-server`]
- Source clone (`git clone` + `pip install -r requirements.txt` / `uv sync` / `cargo build`) — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`apollographql--apollo-mcp-server`]
- Smithery (`smithery.yaml` for Smithery CLI install) — [`JackKuo666--PubMed-MCP-Server`]
- Windows `.exe` via `uv tool run --from <pkg>@latest <pkg>.exe` — [`awslabs--aws-documentation-mcp-server`]
- Podman (alongside Docker) — [`ahmedmustahid--postgres-mcp-server`]

> Smithery distribution is observed on [`JackKuo666--PubMed-MCP-Server`] **without** PyPI publication — the package manager path is optional when a curator like Smithery handles install.

### Container registry

- Docker Hub or unspecified — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`ahmedmustahid--postgres-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- ghcr.io (GitHub Container Registry) — [`alexei-led--k8s-mcp-server`]
- AWS public ECR — [`awslabs--aws-api-mcp-server`]
- Built via release-container GitHub Actions workflow — [`apollographql--apollo-mcp-server`]

## Entry point / launch

### Launch shape

- Bare script (e.g. `python pubmed_server.py`) — [`JackKuo666--PubMed-MCP-Server`]
- Python `-m` module entry (`python -m <pkg>`) — [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-api-mcp-server`] (via `python -m awslabs.aws_api_mcp_server.server`)
- Console script via `[project.scripts]` — [`alpacahq--alpaca-mcp-server`] (`alpaca-mcp-server` → `alpaca_mcp_server.cli:main`), [`awslabs--aws-api-mcp-server`] (`awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main`), [`awslabs--aws-documentation-mcp-server`] (`awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main`)
- `uvx <package>` zero-install — [`PagerDuty--pagerduty-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `npx <package>` (with optional positional subcommand) — [`ahmedmustahid--postgres-mcp-server`]
- Docker `run` (canonical for container-first servers) — [`alexei-led--k8s-mcp-server`]
- Compiled Rust binary — [`apollographql--apollo-mcp-server`]

### CLI orchestration

- `click`-based CLI wrapper around FastMCP — [`alpacahq--alpaca-mcp-server`] (richer argument handling than typical `fastmcp.run()` entry)
- CLI flag `--enable-write-tools` gates mutation tools — [`PagerDuty--pagerduty-mcp-server`]
- `--verbose` flag — [`ahmedmustahid--postgres-mcp-server`]

## Configuration surface

### How config reaches the server

- Environment variables — [`PagerDuty--pagerduty-mcp-server`] (`PAGERDUTY_USER_API_KEY`, `PAGERDUTY_API_HOST`), [`ahmedmustahid--postgres-mcp-server`] (Postgres + HTTP server settings via `.env`), [`alexei-led--k8s-mcp-server`] (`K8S_CONTEXT`, `K8S_NAMESPACE`, security modes, cloud creds), [`alpacahq--alpaca-mcp-server`] (`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_PAPER_TRADE`), [`awslabs--aws-api-mcp-server`] (`AWS_PROFILE`, `AWS_REGION`, transport mode, OAuth endpoints, feature flags), [`awslabs--aws-documentation-mcp-server`] (User-Agent override, partition selection)
- Claude Desktop `claude_desktop_config.json` `command`/`args` (absolute path injection) — [`JackKuo666--PubMed-MCP-Server`]
- CLI flags — [`PagerDuty--pagerduty-mcp-server`] (`--enable-write-tools`), [`alexei-led--k8s-mcp-server`], [`awslabs--aws-api-mcp-server`]
- Configuration file — [`apollographql--apollo-mcp-server`] (points at GraphQL endpoint, operation definitions, and the config file itself; format not extracted)
- Docker `-e` env injection for containerized runs — [`awslabs--aws-api-mcp-server`]

### CORS configuration at the MCP layer

- `CORS_ORIGIN` env var — [`ahmedmustahid--postgres-mcp-server`] (HTTP-transport-specific, rare)

## Authentication

### Auth flow

- None (anonymous public-data fetching) — [`JackKuo666--PubMed-MCP-Server`] (PubMed web), [`awslabs--aws-documentation-mcp-server`] (public AWS docs)
- API token / key (single-pair) — [`PagerDuty--pagerduty-mcp-server`] (PagerDuty User API Token via env), [`alpacahq--alpaca-mcp-server`] (Alpaca API key + secret pair)
- Standard database credentials — [`ahmedmustahid--postgres-mcp-server`] (Postgres user/password via env)
- Inherited host credentials (kubeconfig + cloud provider files mounted) — [`alexei-led--k8s-mcp-server`]
- AWS credential chain (env / `~/.aws/credentials` / profile) — [`awslabs--aws-api-mcp-server`]
- Optional OAuth on streamable-http (configurable issuer + JWKS endpoints), or no-auth — [`awslabs--aws-api-mcp-server`]
- Per-GraphQL-endpoint auth via headers in config file (Apollo Router conventions) — [`apollographql--apollo-mcp-server`]

> [`awslabs--aws-api-mcp-server`] is the only Python sample in this bin with explicit OAuth on streamable-http (configurable issuer/JWKS) — a richer auth story than typical Python MCP servers, which bypass auth and rely on the stdio channel.

## Multi-tenancy

### Tenancy model

- Single-user per process — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`] (one user token), [`alpacahq--alpaca-mcp-server`] (per key pair), [`alexei-led--k8s-mcp-server`] (one container per kubeconfig/context), [`awslabs--aws-api-mcp-server`] (README explicitly states "NOT designed for multi-tenant environments")
- Single database per server, HTTP transport supports stateful sessions but not per-request tenant switching — [`ahmedmustahid--postgres-mcp-server`]
- Stateless / N/A — [`awslabs--aws-documentation-mcp-server`] (read-only public-doc fetching)
- Not extracted — [`apollographql--apollo-mcp-server`]

> Explicit anti-multi-tenancy statement is rare; [`awslabs--aws-api-mcp-server`] documents the boundary rather than leaving it implicit.

## Capabilities exposed

### Tool count and surface

- 5 tools (PubMed search, metadata, PDF download, deep analysis) — [`JackKuo666--PubMed-MCP-Server`]
- 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events — [`PagerDuty--pagerduty-mcp-server`]
- ~60 tools across 10 categories (Account/Trading/Positions/Watchlists/Assets/Stock/Crypto/Options/CorpActions/News) — [`alpacahq--alpaca-mcp-server`]
- 3 tools (`call_aws`, `suggest_aws_commands`, experimental `get_execution_plan`) — [`awslabs--aws-api-mcp-server`]
- 5 partition-scoped tools (`read_documentation`, `search_documentation` global-only, `read_sections`, `recommend`, `get_available_services` China-only) — [`awslabs--aws-documentation-mcp-server`]
- Tool wrappers around `kubectl`/`helm`/`istioctl`/`argocd` plus Unix piping (`jq`/`grep`/`sed`) — [`alexei-led--k8s-mcp-server`]
- 1 tool (read-only SQL) + 2 resources (Database Tables, Database Schema) — [`ahmedmustahid--postgres-mcp-server`]
- Tools generated from configured GraphQL operation definitions — [`apollographql--apollo-mcp-server`]

### Capability source

- Hand-coded tool handlers — most samples in this bin
- Generated from OpenAPI / pre-generated from spec — [`alpacahq--alpaca-mcp-server`] ("complete rewrite built with FastMCP and OpenAPI")
- Generated from GraphQL operation definitions at config time — [`apollographql--apollo-mcp-server`] (operators shape the catalog by choosing which operations to expose)
- CLI command wrapping — [`alexei-led--k8s-mcp-server`] (wraps existing CLIs), [`awslabs--aws-api-mcp-server`] (wraps AWS CLI, ships pinned `awscli==1.44.81`)

> Operation-driven tool surface in [`apollographql--apollo-mcp-server`]: tool definitions live as GraphQL operations, not as MCP tool declarations. Reduces tool authoring to operation authoring — a rare capability-sourcing pattern.

### Resources

- Resources — `Database Tables`, `Database Schema` — [`ahmedmustahid--postgres-mcp-server`]
- Tools-only (no resources/prompts) — [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`]

### Read-only vs mutation gating

- Read-only-by-default with mutation gated behind a CLI flag (`--enable-write-tools`) — [`PagerDuty--pagerduty-mcp-server`]
- Paper-trading mode default (`ALPACA_PAPER_TRADE=true`) — mutation-capable but sandbox-by-default — [`alpacahq--alpaca-mcp-server`]
- Read-only by design (`SQL` execution restricted to read-only queries) — [`ahmedmustahid--postgres-mcp-server`]
- Pure read-only documentation bridge — [`awslabs--aws-documentation-mcp-server`]
- Experimental tools gated by feature flag — [`awslabs--aws-api-mcp-server`] (`get_execution_plan`)

> Paper-mode-as-default is a safety pattern surfaced by [`alpacahq--alpaca-mcp-server`] — mutation-capable MCP server with a sandbox default that other trading/finance servers should emulate.

## Observability

### Logging

- Standard Python `logging` — [`JackKuo666--PubMed-MCP-Server`]
- `loguru` — [`awslabs--aws-documentation-mcp-server`]
- `loguru` + `python-json-logger` (dual logging paths) — [`awslabs--aws-api-mcp-server`]
- Not surfaced — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`]
- `--verbose` flag — [`ahmedmustahid--postgres-mcp-server`]

## Host integrations

### Documented hosts

- Claude Desktop (JSON `mcpServers` entry / `claude_desktop_config.json` for Mac+Windows) — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`]
- Cline (dedicated example) — [`JackKuo666--PubMed-MCP-Server`]
- Smithery — [`JackKuo666--PubMed-MCP-Server`] (`smithery.yaml` in repo root)
- MCP Inspector — [`ahmedmustahid--postgres-mcp-server`], [`apollographql--apollo-mcp-server`]
- Cursor (`~/.cursor/mcp.json`) — [`alpacahq--alpaca-mcp-server`]
- VS Code (`.vscode/mcp.json`) — [`alpacahq--alpaca-mcp-server`]
- PyCharm (Settings → Tools → MCP) — [`alpacahq--alpaca-mcp-server`] (less widely advertised than Claude Desktop)
- Gemini CLI (`settings.json`) — [`alpacahq--alpaca-mcp-server`]
- Generic AI client / generic JSON `mcpServers` — [`PagerDuty--pagerduty-mcp-server`], [`apollographql--apollo-mcp-server`]

> [`alpacahq--alpaca-mcp-server`] documents 5 different MCP clients (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI) — broader host-integration coverage than any other repo in this bin.

### Claude Code plugin wrapper

- Not present — every sample in this bin reports either "None observed", "None at sub-server level", or absence
- `.claude/` directory + `CLAUDE.md` at repo root (operational Claude docs; may be Claude Code workspace state, not a `.claude-plugin/plugin.json` wrapper) — [`apollographql--apollo-mcp-server`]

## Tests

### Test framework

- pytest + pytest-asyncio — [`alpacahq--alpaca-mcp-server`]
- pytest + pytest-asyncio + pytest-cov + pytest-mock — [`awslabs--aws-api-mcp-server`]
- pytest with `--cov --cov-branch` and a custom `--run-live` flag for live-AWS integration tests — [`awslabs--aws-documentation-mcp-server`]
- `tests/` directory present, framework not surfaced — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`], [`ahmedmustahid--postgres-mcp-server`]
- None observed — [`JackKuo666--PubMed-MCP-Server`]
- End-to-end harness in `/e2e/mcp-server-tester` — [`apollographql--apollo-mcp-server`]

### Notable testing patterns

- Multi-layered test suite (integrity / server-construction / paper-API integration) — [`alpacahq--alpaca-mcp-server`]
- Bedrock test result files in repo (cross-platform agent validation) — [`PagerDuty--pagerduty-mcp-server`]
- Live-network integration gated behind opt-in flag (`--run-live`) — [`awslabs--aws-documentation-mcp-server`]
- Protocol-conformance e2e tester as a first-class component — [`apollographql--apollo-mcp-server`]

## CI

### CI system

- GitHub Actions on every PR — [`alpacahq--alpaca-mcp-server`]
- GitHub Actions (`.github/`) — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`] (`release.yml`, `ci.yml`), [`apollographql--apollo-mcp-server`] (CI + release-binaries + release-container workflows)
- Parent monorepo CI (sub-server-specific config not extracted) — [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `.github/` present, workflow details not surfaced — [`JackKuo666--PubMed-MCP-Server`]
- Not detailed — [`ahmedmustahid--postgres-mcp-server`]

## Container / packaging artifacts

### Container artifacts

- Dockerfile only — [`JackKuo666--PubMed-MCP-Server`], [`PagerDuty--pagerduty-mcp-server`] (with stdio transport), [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Dockerfile + docker-compose — [`ahmedmustahid--postgres-mcp-server`]
- Container built via release workflow — [`apollographql--apollo-mcp-server`]

## Dev ergonomics

### Dev tooling

- Makefile — [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`]
- `scripts/` directory — [`PagerDuty--pagerduty-mcp-server`]
- `website/` directory (docs site alongside server) — [`PagerDuty--pagerduty-mcp-server`]
- `/docs/` directory — [`alexei-led--k8s-mcp-server`]
- `/examples/` directory — [`apollographql--apollo-mcp-server`]
- ruff + mypy + pytest dev stack — [`alpacahq--alpaca-mcp-server`]
- pre-commit + commitizen + ruff + pyright (commit-style enforcement) — [`awslabs--aws-api-mcp-server`]
- None explicit — [`JackKuo666--PubMed-MCP-Server`]

## Repo layout

### Layout

- Bare-script style (entry script + helper at repo root; `pyproject.toml` and `requirements.txt` side by side) — [`JackKuo666--PubMed-MCP-Server`]
- Single package under `<pkg>/` — [`PagerDuty--pagerduty-mcp-server`], [`alpacahq--alpaca-mcp-server`]
- Single package under `src/<pkg>/` — [`alexei-led--k8s-mcp-server`]
- Mixed single-package (TS-majority `src/` + `package.json`, sibling `pyproject.toml` and `images/` directory) — [`ahmedmustahid--postgres-mcp-server`]
- Single Rust crate (`Cargo.toml` + `/examples` + `/e2e`) — [`apollographql--apollo-mcp-server`]
- Sub-package inside parent monorepo (each sub-server has its own `pyproject.toml`, console script, PyPI release) — [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]

> Sub-server-as-first-class-package surfaced by [`awslabs--aws-api-mcp-server`]: every monorepo sub-server has its own `pyproject.toml`, console script, and PyPI release, so consumers install one sub-server without pulling the rest.

### Manifest patterns

- Both `pyproject.toml` and `requirements.txt` (redundant manifests; suggests requirements-driven bootstrap) — [`JackKuo666--PubMed-MCP-Server`]
- Both Poetry (`poetry.lock`) and uv workflows supported — [`PagerDuty--pagerduty-mcp-server`]
- `package.json` + sibling `pyproject.toml` in TS-majority repo (purpose unexplained) — [`ahmedmustahid--postgres-mcp-server`]

## Python packaging

### Build backend

- `hatchling` — [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Poetry (`poetry.lock` present) — [`PagerDuty--pagerduty-mcp-server`]
- Not surfaced — [`JackKuo666--PubMed-MCP-Server`], [`alexei-led--k8s-mcp-server`]

### Lock file / version manager

- `uv` / `uvx` (uv lock implied) — [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- `poetry.lock` (also supports uv) — [`PagerDuty--pagerduty-mcp-server`]
- `requirements.txt` (no lock) — [`JackKuo666--PubMed-MCP-Server`]

### Async / concurrency

- `httpx` (network-bound work; likely async) — [`alpacahq--alpaca-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Mentions `asyncio` — [`JackKuo666--PubMed-MCP-Server`]
- Not surfaced — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`], [`awslabs--aws-api-mcp-server`]

### Type / schema strategy

- FastMCP-auto-derived from type hints — [`JackKuo666--PubMed-MCP-Server`], [`alpacahq--alpaca-mcp-server`]
- `pydantic>=2.10.6` — [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Not surfaced — [`PagerDuty--pagerduty-mcp-server`], [`alexei-led--k8s-mcp-server`]

### Notable Python-specific dependencies

- `markdownify` (HTML→markdown) + `beautifulsoup4` (selective HTML parsing) — [`awslabs--aws-documentation-mcp-server`]
- Pinned `awscli==1.44.81` (CLI tool distributed as a Python dep of the MCP server) — [`awslabs--aws-api-mcp-server`]
- `lxml`, `requests`, `python-frontmatter`, `importlib_resources` (suggests embedded docs/assets) — [`awslabs--aws-api-mcp-server`]
- `setuptools>=69.0.0` as runtime dep (unusual for a hatchling-built package) — [`awslabs--aws-api-mcp-server`]
- No vendor SDK (`alpaca-py`); hand-rolled HTTPS via `httpx` — [`alpacahq--alpaca-mcp-server`]
- `click` for CLI orchestration around FastMCP — [`alpacahq--alpaca-mcp-server`]
- Minimalist 6-runtime-dep set — [`awslabs--aws-documentation-mcp-server`]

## Notable structural / cross-cutting patterns

### Capability sourcing axes

- CLI-wrapping (existing CLIs become tools) — [`alexei-led--k8s-mcp-server`], [`awslabs--aws-api-mcp-server`]
- SDK-wrapping (boto3 / vendor SDK) — sibling repos to [`awslabs--aws-api-mcp-server`] flagged this contrast
- Spec-generated (OpenAPI / GraphQL operations) — [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`]
- Hand-coded tool handlers — bulk of bin

### Safety posture

- Anti-multi-tenancy explicit in README — [`awslabs--aws-api-mcp-server`]
- Mutation gated by CLI flag — [`PagerDuty--pagerduty-mcp-server`]
- Sandbox/paper mode by default — [`alpacahq--alpaca-mcp-server`]
- Read-only design — [`ahmedmustahid--postgres-mcp-server`], [`awslabs--aws-documentation-mcp-server`]
- Experimental-tool feature-flagging — [`awslabs--aws-api-mcp-server`]

### Operational concerns

- Corporate proxy support (User-Agent override env var) — [`awslabs--aws-documentation-mcp-server`]
- Partition-scoped tool surface (same binary, different tools depending on AWS partition) — [`awslabs--aws-documentation-mcp-server`]
- HTTP session statefulness as an explicit design axis — [`ahmedmustahid--postgres-mcp-server`]
- Graceful shutdown / error handling highlighted — [`ahmedmustahid--postgres-mcp-server`]

## Unanticipated axes (for merger to consider)

- Dual SDK dependency (one server pulling both `mcp` and `fastmcp`) — [`awslabs--aws-api-mcp-server`]
- Operation-driven tool catalog (GraphQL operations as MCP tool declarations) — [`apollographql--apollo-mcp-server`]
- Smithery-only distribution without PyPI — [`JackKuo666--PubMed-MCP-Server`]
- Windows `.exe` distribution via `uv tool run` — [`awslabs--aws-documentation-mcp-server`]
- Pinned-CLI-version-as-MCP-dependency — [`awslabs--aws-api-mcp-server`]
- asdf-based Python version pinning — [`PagerDuty--pagerduty-mcp-server`]
- Python 3.13+ floor (unusually high) — [`alexei-led--k8s-mcp-server`]
- CORS at MCP layer (HTTP-transport-specific config) — [`ahmedmustahid--postgres-mcp-server`]
- `.claude/` + `CLAUDE.md` in-repo (Claude-assisted authoring surface for contributors, distinct from a Claude Code plugin wrapper) — [`apollographql--apollo-mcp-server`]
- Rust as an MCP-server language (different distribution channels: crates.io, binary releases, Docker) — [`apollographql--apollo-mcp-server`]
