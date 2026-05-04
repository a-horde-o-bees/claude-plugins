# Sample

Mirrors of `https://github.com/PagerDuty/pagerduty-mcp-server`. PagerDuty incident-management MCP server — 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, and change events. 62 stars, Apache-2.0, default branch `main`, 288 commits, vendor-authored (PagerDuty).

## Server runtime

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK (raw, not FastMCP per README). Module-level entry pattern (`python -m pagerduty_mcp` via `__main__.py`). Async-vs-sync tool patterns not surfaced; type-hint and schema-derivation specifics not surfaced.

## Transport

### stdio

stdio default; Dockerfile exposes stdio transport.

### Selection mechanism

Implicit single mode — stdio only.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events — comprehensive vendor-authored wrapper of the PagerDuty domain.

### Capability gating flags (per-tool, per-category, write-mode)

`--enable-write-tools` CLI flag gates mutating tools. Read-only by default; write surface opt-in.

## Configuration delivery

### Environment variables

`PAGERDUTY_USER_API_KEY`, `PAGERDUTY_API_HOST`.

### CLI flags

`--enable-write-tools` boolean flag.

### Host-side JSON config snippet

Claude Desktop and generic MCP-host JSON `mcpServers` entries with `env` block injecting the API key + host.

## Authentication

### Static API key / token via env var

PagerDuty User API Token via `PAGERDUTY_USER_API_KEY` env var. Token obtained from PagerDuty account settings → API Access.

## Multi-tenancy

### Single-user / single-tenant per process

One user token per process.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published to PyPI as `pagerduty-mcp`; canonical install command `uvx pagerduty-mcp`.

### Source clone with editable install

`uv sync` for local development from a clone.

### Docker / OCI image

Dockerfile published; Docker is one of the documented distribution forms.

## Entry point and launch

### Module invocation / `python -m <module>` fallback

`python -m pagerduty_mcp` via `__main__.py`. Console-script registrations in `pyproject.toml` not surfaced.

### `uvx <package>`

Host-config snippet shape: `uvx pagerduty-mcp`.

## Build and packaging

### Poetry (Python)

Poetry as build backend — `poetry.lock` present.

### Hatchling + uv (Python)

`pyproject.toml` also supports the uv workflow alongside Poetry — dual packaging tools coexist in one repo.

### Python version pinning

`.tool-versions` (asdf) is the version-pin convention here. Specific Python value not surfaced. asdf-based pinning is rarer than uv-native or `.python-version`.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present, configured to expose stdio transport.

## Test stack

### pytest with async + coverage

`tests/` directory present; specific framework details and fixtures not surfaced. Bedrock test result files referenced (suggesting validation against Amazon Bedrock agents).

### External agent validation artifacts

Bedrock test result files committed to repo as evidence of cross-platform agent compatibility (validated against Amazon Bedrock agents).

## CI

### GitHub Actions

`.github/` directory with GitHub Actions workflows.

## Host integration

### Claude Desktop

JSON `mcpServers` entry with `env` block for API key + API host.

### Generic / host-agnostic snippet

JSON `mcpServers` entry generically labelled "Other MCP-enabled clients."

## Documentation surface

### GitHub Pages / hosted docs site

`website/` directory in repo, likely a docs site shipped alongside the server.

## Safety and security posture

### Read-only by default with explicit write flag

Mutation tools registered but hidden behind `--enable-write-tools` CLI flag — author's default posture is "no surprise mutations."

## Repository layout

### Single-package src-layout

Single package under `pagerduty_mcp/` with `tests/`, `scripts/`, `website/`, `.github/` as siblings.

## Developer ergonomics

### `scripts/` directory

`scripts/` directory at repo root.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0; vendor-authored (official PagerDuty repo) gives long-term maintenance signal.
