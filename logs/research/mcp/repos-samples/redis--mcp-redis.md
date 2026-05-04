# Sample

Mirrors of `https://github.com/redis/mcp-redis`. Redis MCP server — key/value/data-structure operations across eight Redis families plus vector search; uses `uv_build` native backend; EntraID + standard Redis ACL auth. 488 stars, MIT, default branch `main`, v0.5.0 released March 16, 2026.

## Server runtime

### Python with raw MCP SDK

Python (99.9%); raw `mcp` Python SDK — `mcp[cli]>=1.26.0` in dependencies; no fastmcp. Low-level MCP server API (inferred). README phrasing references Anthropic Claude Agent SDK; `uv` tooling throughout.

## Transport

### stdio

stdio is the only currently-supported transport (README notes "streamable-http transport will be added in the future").

### Selection mechanism

Implicit single mode — stdio only for now.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools across eight Redis categories — strings, hashes, lists, sets, sorted sets, pub/sub, streams, JSON manipulation. Per-data-structure tool grouping mirrors Redis command families.

### Tools-only, hand-curated narrow surface

Resources/prompts/sampling/roots not documented — tools-only surface.

## Configuration delivery

### CLI flags

`--url`, `--host`, `--port`, `--username`, `--password`, `--db`, `--ssl`, `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile`, `--cluster-mode`. CLI-first with env var fallback rather than env-first.

### Environment variables

Env vars and `.env` files supported. `MCP_REDIS_LOG_LEVEL` for log severity (DEBUG/INFO/WARNING/ERROR/CRITICAL; default WARNING). `MCP_DOCS_SEARCH_URL` for docs search HTTP API.

### Connection URI scheme

Redis URI scheme (`redis://`, `rediss://`).

### Dotenv file

`.env` files supported.

### Host-side JSON config snippet

Claude Desktop JSON config example with `"command": "/Users/.../uvx"` and `"args": ["--from", "redis-mcp-server@latest", "redis-mcp-server", "--url", "redis://..."]` — `uvx --from` pattern with explicit package reference.

## Authentication

### Database connection string

Standard Redis ACL via username/password supplied through CLI flags, env vars, or URI.

### Cloud-native identity / credential chain

Azure EntraID with three sub-flows — service principal, managed identity, default Azure credential; automatic token renewal with background refresh. EntraID support with managed identity is layered as an alternative to the standard Redis ACL credential path — same server speaks both auth schemes.

## Multi-tenancy

### Single connection per server instance

Single Redis connection per server instance; cluster mode available but no per-request tenancy.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx --from redis-mcp-server@latest redis-mcp-server --url "redis://localhost:6379/0"`; package name `redis-mcp-server`.

### PyPI via pip / pipx

`pip install redis-mcp-server` also documented.

### Install-from-git via uvx

`uvx --from git+https://...` for a GitHub install.

### Docker / OCI image

`docker build -t mcp-redis .` documented; Dockerfile present.

### Source clone with editable install

From-source `uv sync` documented.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `redis-mcp-server = "src.main:cli"` — `src.` prefix in the module path means the project's `src/` directory is itself imported as a top-level package rather than serving as a layout container. CLI bin: `redis-mcp-server --url <redis-uri>` with optional flags.

### `uvx <package>`

`uvx --from redis-mcp-server@latest redis-mcp-server --url "..."` — host-config snippet shape uses `uvx --from` pattern.

## Build and packaging

### uv_build backend (Python)

Build backend: `uv_build` (one of the very few repos in the sample using uv's native build backend) — `requires = ["uv_build>=0.8.3,<0.12.0"]`. Mainstream choice elsewhere is hatchling.

### `uv.lock` committed

`uv.lock` present.

## Schema and types

### Hand-authored tool schemas

Low-level MCP SDK — hand-authored tool schemas likely.

### Async model (cross-cutting)

Low-level `mcp[cli]` SDK with `pytest-asyncio` + `asyncio_mode = "auto"` — async tool handlers (`async def`).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present; no compose/helm/systemd.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov + pytest-mock in dev group; separate `test` dependency-group. `addopts` includes `--cov=src --cov-fail-under=80` — coverage gate enforced at 80%. `asyncio_mode = "auto"`.

### Branch coverage enforcement

Coverage fail-threshold (`--cov-fail-under=80`) configured in `addopts`.

### MyPy strict + Bandit security scans alongside tests

mypy + black + bandit + safety in dev extras — heavy typing/security tooling. bandit + safety in dev — security scanning as first-class tooling.

## CI

### GitHub Actions

GitHub Actions (integration workflow badge shown); specifics not extracted within budget.

### Codecov integration

codecov badge / integration in tests.

## Host integration

### Claude Desktop

JSON config example.

### VS Code / VS Code Insiders / Visual Studio family

VS Code + GitHub Copilot supported; requires `chat.agent.enabled: true`.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Augment supported via its Easy MCP feature.

### Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK

OpenAI Agents SDK supported.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present (no `.claude-plugin` directory).

## Documentation surface

### README as the canonical surface

README is canonical; `examples/` directory for usage demos; `server.json` for MCP server registry wiring; codecov badge.

## Developer ergonomics

### Examples directory with many patterns

`examples/` directory for usage demos.

### `uv run <tool>` invocations

`uv`-first Python tooling (uvx, uv.lock) rather than pip/poetry.

## Repository layout

### Single-package src-layout

Single-package Python project — `src/`, `tests/`, `examples/`, Dockerfile, `pyproject.toml`, `server.json`, `uv.lock`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Tagged release with version in changelog

v0.5.0 released March 16, 2026.

### Active development

Active development; integration workflow CI badge.

## Safety and security posture

### None / not surfaced

Not explicitly surfaced; SSL knobs (ca-path, keyfile, certfile) provide transport-level integrity but no application-level safety gates documented.
