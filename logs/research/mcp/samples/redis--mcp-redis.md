# Sample

## Identification
- url: https://github.com/redis/mcp-redis
- stars: 488
- last-commit (date or relative): v0.5.0 released March 16, 2026
- license: MIT
- default branch: main
- one-line purpose: Redis MCP server — key/value/data-structure operations; uses `uv_build` native backend.

## 1. Language and runtime
- language(s) + version constraints: Python (99.9%)
- framework/SDK in use: Anthropic Claude Agent SDK (per README phrasing); `uv` tooling throughout
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (README notes "streamable-http transport will be added in the future")
- how selected (flag, env, separate entry, auto-detect, etc.): Implicit stdio only for now
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (via `uvx --from redis-mcp-server@latest`), Git (via `uvx --from git+...`), Docker (`docker build -t mcp-redis .`)
- published package name(s): redis-mcp-server
- install commands shown in README: `uvx --from redis-mcp-server@latest redis-mcp-server --url "redis://localhost:6379/0"`; Docker build
- pitfalls observed:
  - `uv`-first Python tooling (uvx, uv.lock) rather than pip/poetry

## 4. Entry point / launch
- command(s) users/hosts run: `redis-mcp-server --url <redis-uri>` (CLI bin) with optional flags
- wrapper scripts, launchers, stubs: Dockerfile; `server.json` MCP server config
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Three sources — CLI flags (`--url`, `--host`, `--port`, `--username`, `--password`, `--db`, `--ssl`, `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile`, `--cluster-mode`); environment variables and `.env` files; Redis URI scheme (`redis://`, `rediss://`). `MCP_REDIS_LOG_LEVEL` for log severity. `MCP_DOCS_SEARCH_URL` for docs search HTTP API.
- pitfalls observed:
  - CLI-first with env var fallback rather than env-first

## 6. Authentication
- flow: Standard Redis ACL (username/password) plus Azure EntraID with three sub-flows — service principal, managed identity, default Azure credential; automatic token renewal with background refresh
- where credentials come from: CLI flags, env vars, or cloud-native identity (EntraID)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single Redis connection per server instance; cluster mode available but no per-request tenancy
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tools across eight categories — strings, hashes, lists, sets, sorted sets, pub/sub, streams, JSON manipulation; vector search via query engine; server management info; documentation search via `MCP_DOCS_SEARCH_URL`. Resources/prompts/sampling/roots not documented.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Standard Python logging; `MCP_REDIS_LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR/CRITICAL); default WARNING
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop: JSON config example
- VS Code + GitHub Copilot: Supported, requires `chat.agent.enabled: true`
- Augment: Supported via its Easy MCP feature
- OpenAI Agents SDK: Supported
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present (no `.claude-plugin` directory)

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Tests under `/tests`; codecov integration
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (integration workflow badge shown); specifics not extracted within budget
- pitfalls observed:
  - Exact CI workflow list not extracted

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present; no compose/helm/systemd
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `examples/` directory for usage demos; `server.json` for MCP server registry wiring; codecov badge
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python project — `src/`, `tests/`, `examples/`, Dockerfile, `pyproject.toml`, `server.json`, `uv.lock`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- `uv`-first Python tooling (uvx, uv.lock) rather than pip/poetry
- CLI-first with env var fallback rather than env-first
- Granular SSL knobs (ca-path, keyfile, certfile) alongside URI schemes
- EntraID support with managed identity is rare among community MCP servers — reflects enterprise Azure deployment pressure
- Per-data-structure tool grouping mirrors Redis command families

## 18. Unanticipated axes observed
- In-server documentation-search tool via a separate HTTP endpoint (`MCP_DOCS_SEARCH_URL`) is an unusual design — RAG-style augmentation attached to a database server
- Vector search as a first-class capability alongside core Redis data structures
- Cluster-mode flag as a first-class config axis

## 19. Python-specific

### SDK / framework variant
- Raw `mcp` Python SDK — `mcp[cli]>=1.26.0` in dependencies; no fastmcp
- Import pattern: low-level MCP server API (inferred)

### Python version floor
- `requires-python = ">=3.10"`
- CI matrix not extracted

### Packaging
- build backend: `uv_build` (one of the very few repos in the sample using uv's native build backend) — `requires = ["uv_build>=0.8.3,<0.12.0"]`
- lock file: `uv.lock` present
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `redis-mcp-server = "src.main:cli"` — note unusual `src.` prefix in the module path
- README host-config snippet: `"command": "/Users/.../uvx"` with `"args": ["--from", "redis-mcp-server@latest", "redis-mcp-server", "--url", "redis://..."]` — `uvx --from` pattern with explicit package reference

### Install workflow expected of end users
- `pip install redis-mcp-server` or `uvx --from redis-mcp-server@latest`, or `uvx --from git+https://...` for a GitHub install, Docker image `mcp/redis`, or from-source `uv sync`

### Async and tool signatures
- Low-level `mcp[cli]` SDK — tool handlers likely `async def`
- `pytest-asyncio` + `asyncio_mode = "auto"` in pytest config confirms async

### Type / schema strategy
- Low-level MCP SDK — hand-authored tool schemas likely
- mypy + black + bandit + safety in dev extras — heavy typing/security tooling

### Testing
- pytest + pytest-asyncio + pytest-cov + pytest-mock in dev group; separate `test` dependency-group
- `addopts` includes `--cov=src --cov-fail-under=80` — coverage gate enforced at 80%
- `asyncio_mode = "auto"`

### Dev ergonomics
- `uv_build` native backend and dependency-groups (PEP 735) — modern uv-native project layout
- bandit + safety in dev — security scanning as first-class tooling
- twine for PyPI publishing pipeline

### Notable Python-specific choices
- `uv_build` backend adoption — one of the few in the sample; mainstream choice is hatchling
- PEP 735 `[dependency-groups]` with distinct `dev` and `test` groups
- Coverage fail-threshold (`--cov-fail-under=80`) configured in `addopts`
- `src.main:cli` entry point path is unusual — most projects use top-level module path without the `src.` prefix

## 20. Gaps
- Exact CI workflow list not extracted
- Streamable-HTTP transport promised but not yet shipped
- `server.json` contents not inspected
