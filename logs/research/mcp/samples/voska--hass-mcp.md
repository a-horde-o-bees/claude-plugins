# Sample

## Identification

### url

https://github.com/voska/hass-mcp

### stars

287

### last-commit

August 5, 2025 (v0.1.1 release)

### license

MIT (per README badges; pyproject.toml did not declare)

### default branch

master

### one-line purpose

Home Assistant MCP server — Docker-first distribution; long-lived access token auth; Python 3.13 floor.

## 1. Language and runtime

### language(s) + version constraints

Python 99.6% — `requires-python = ">=3.13"`.

### framework/SDK in use

raw `mcp[cli]>=1.4.1`.

### pitfalls observed

Python 3.13 floor — aggressive version requirement; most Python MCP servers target 3.10+. Python 3.13 requirement on a relatively popular (287 stars) production server — uncommon floor.

## 2. Transport

### supported transports

stdio (wrapped in Docker or uvx).

### how selected

default stdio; Docker container runs the stdio server inside.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Docker Hub (`voska/hass-mcp:latest`); `uvx hass-mcp`.

### published package name(s)

`hass-mcp` on PyPI (inferred from `uvx hass-mcp` install one-liner).

### install commands shown in README

`docker pull voska/hass-mcp:latest`; `uvx hass-mcp`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`docker run -i --rm -e HA_URL -e HA_TOKEN voska/hass-mcp`; `uvx hass-mcp`.

### wrapper scripts, launchers, stubs

console script `hass-mcp` → `app.run:main`.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

environment variables `HA_URL`, `HA_TOKEN`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Home Assistant long-lived access token.

### where credentials come from

`HA_TOKEN` env var injected into the container or uvx process.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per Home Assistant instance.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools for controlling HA entities, querying states, executing services, managing automations — parent `homeassistant-ai/ha-mcp` advertises 80+ tools; this variant is more focused.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not captured

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON snippet shown with Docker `command`/`args`; `HA_URL` + `HA_TOKEN` env.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none shown

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest mentioned; GitHub Actions workflow directory present.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions — details not extracted.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile; official image `voska/hass-mcp:latest` on Docker Hub — Docker as the primary distribution channel.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON example embedded in README.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`app/` module).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Python 3.13 floor — aggressive version requirement; most Python MCP servers target 3.10+.

Docker as the primary distribution channel — README leads with `docker pull` and shows the Claude Desktop config using Docker as the `command`.

Two-dep server (`mcp[cli]` + `httpx`) — REST client over HA's REST API, minimal abstraction.

Non-`awslabs.` namespace but similar top-level module name pattern: `hass-mcp` binary → `app.run:main` (module is just `app`, not `hass_mcp`).

## 18. Unanticipated axes observed

Docker-first distribution for home-automation servers — many users run HA in Docker already; bundling the MCP server in the same paradigm matches operator mental models.

Python 3.13 requirement on a relatively popular (287 stars) production server — uncommon floor.

Bare `app` module name rather than `hass_mcp` package — unusual naming; suggests template-derived structure.

## 19. Python-specific

### SDK / framework variant

raw `mcp[cli]>=1.4.1` — older pin than awslabs sub-servers (>=1.23.0). Version pin from pyproject.toml: `mcp[cli]>=1.4.1`, `httpx>=0.27.0`. Import pattern observed: `from mcp.server.fastmcp import FastMCP` is likely given `[cli]` extra; not confirmed.

### Python version floor

`requires-python` value: `>=3.13`.

### Packaging

build backend: hatchling. Lock file present: `.python-version` file referenced. Version manager convention: `uv` / `uvx`.

### Entry point

console script. Actual console-script name: `hass-mcp`. Host-config snippet shape: Docker-first (`"command": "docker"`); uvx as alternative.

### Install workflow expected of end users

`docker pull voska/hass-mcp:latest` (primary); `uvx hass-mcp` (secondary).

### Async and tool signatures

httpx + MCP SDK — likely async.

### Type / schema strategy

not captured — Pydantic arrives via `mcp[cli]` extra.

### Testing

pytest (per README mention).

### Dev ergonomics

not captured.

### Notable Python-specific choices

Very small dep set (2 runtime deps). Requires Python 3.13 — tracks modern Python features or standard library additions. Module name `app` (bare) vs conventional `hass_mcp` package.

## 20. Gaps

what couldn't be determined: exact CI workflow, tool count, whether resources or prompts are used, pyproject license field (README shows MIT badge).
