# Sample

## Identification

### url

https://github.com/DiversioTeam/clickup-mcp

### stars

3

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

ClickUp task-management MCP server — 28 tools covering task CRUD, discovery, assignments, bulk ops, time tracking, analytics, and user management.

## 1. Language and runtime

### language(s) + version constraints

Python 100%; `requires-python = ">=3.10"`.

### framework/SDK in use

raw `mcp>=0.1.0` (very old pin) + `click` for CLI wrapping.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default MCP transport implied).

### how selected

default

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

`uvx --from git+https://github.com/DiversioTeam/clickup-mcp clickup-mcp` — install from git URL.

### published package name(s)

no PyPI publication documented

### install commands shown in README

`uvx --from git+https://github.com/DiversioTeam/clickup-mcp clickup-mcp`; `uv run clickup-mcp`.

### pitfalls observed

- Install-from-git — `uvx --from git+...` as the primary install path, no PyPI
- `uvx --from git+...` as a distribution channel — bypasses PyPI entirely; the git URL becomes the effective package index
- Test-density vs popularity skew — low stars with high test count suggests an internal/team project published without a marketing push; star counts should not be read as a proxy for engineering quality

## 4. Entry point / launch

### command(s) users/hosts run

`uvx clickup-mcp` (after install-from-git); `uv run clickup-mcp`. Subcommands: `uvx clickup-mcp set-api-key YOUR_KEY`, `check-config`, `test-connection`, `--debug`.

### wrapper scripts, launchers, stubs

console script `clickup-mcp` → `clickup_mcp.__main__:main`.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Persistent config via `platformdirs` — API key stored via `set-api-key` subcommand. Env var alternative: `CLICKUP_MCP_API_KEY`.

### pitfalls observed

- `platformdirs`-based persistent config — API key stored in OS-appropriate config dir (`~/.config/` / `%APPDATA%` / etc.) via `set-api-key` subcommand; unlike the dominant "env var only" pattern
- OS-native config persistence via `platformdirs` — competes with `.env` files and env vars; reveals three distinct credential-storage conventions in the sample

## 6. Authentication

### flow

ClickUp personal API token (generated from Settings → Apps → API).

### where credentials come from

either `set-api-key` subcommand (persisted via `platformdirs`) or `CLICKUP_MCP_API_KEY` env var.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single workspace per API key; personal-token scope.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

28 tools covering task management, discovery, assignments, navigation, bulk operations, time tracking, analytics, user management.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`--debug` flag; `rich` used for formatted output.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Not captured per host in extract.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

62 pytest tests; pytest + pytest-asyncio + pytest-cov in dev deps.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions CI workflow present.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

not mentioned

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`set-api-key`, `check-config`, `test-connection` subcommands — strong CLI ergonomics for setup.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`clickup_mcp/` with `__main__.py`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- `platformdirs`-based persistent config — API key stored in OS-appropriate config dir (`~/.config/` / `%APPDATA%` / etc.) via `set-api-key` subcommand; unlike the dominant "env var only" pattern
- Management subcommands on the MCP binary (`set-api-key`, `check-config`, `test-connection`) — the MCP server command doubles as a config CLI, echoing patterns like `kubectl config`
- `__main__.py`-based entry — console script points at `clickup_mcp.__main__:main` rather than `clickup_mcp.server:main`
- `rich` for terminal output — the CLI-facing subcommands use rich formatting; reflects the dual-mode (server + management CLI) nature
- Install-from-git — `uvx --from git+...` as the primary install path, no PyPI
- 62 pytest tests on a 3-star repo — well above average test density for its popularity tier

## 18. Unanticipated axes observed

- MCP-server binary as a management CLI — the same console script handles both the server protocol and a separate CLI for configuration. A richer pattern than one-binary-one-purpose
- OS-native config persistence via `platformdirs` — competes with `.env` files and env vars; reveals three distinct credential-storage conventions in the sample
- `uvx --from git+...` as a distribution channel — bypasses PyPI entirely; the git URL becomes the effective package index
- Test-density vs popularity skew — low stars with high test count suggests an internal/team project published without a marketing push; star counts should not be read as a proxy for engineering quality

## 19. Python-specific

### SDK / framework variant

raw `mcp>=0.1.0` — extremely loose pin. Version pins from pyproject.toml: `mcp>=0.1.0`, `httpx>=0.27.0`, `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`, `platformdirs>=4.0.0`, `python-dotenv>=1.0.0`, `click>=8.1.0`, `rich>=13.0.0`. Import pattern likely `from mcp.server import Server` given raw SDK.

### Python version floor

`requires-python = ">=3.10"`

### Packaging

Build backend: hatchling. Lock file presence not captured. Version manager convention: `uv` / `uvx`.

### Entry point

`__main__.py` module entry: `clickup-mcp = clickup_mcp.__main__:main`. Console script name: `clickup-mcp`. Host-config snippet shape: `uvx clickup-mcp` (after git-install).

### Install workflow expected of end users

`uvx --from git+https://github.com/DiversioTeam/clickup-mcp clickup-mcp`

### Async and tool signatures

httpx + pytest-asyncio → async likely.

### Type / schema strategy

Pydantic v2 + pydantic-settings for typed config.

### Testing

pytest + pytest-asyncio + pytest-cov; 62 tests. Fixture style not captured.

### Dev ergonomics

ruff + mypy + subcommand CLI (`set-api-key`, `check-config`, `test-connection`).

### Notable Python-specific choices

- `pydantic-settings` for typed-config pattern (env + file loading)
- `platformdirs` for cross-platform config directory resolution
- `rich` + `click` for a polished CLI layer on top of the MCP server
- Very loose `mcp>=0.1.0` pin — unusual; most projects pin much tighter

## 20. Gaps

Docker presence, exact mcp SDK patterns, whether the server uses resources/prompts primitives, update cadence.
