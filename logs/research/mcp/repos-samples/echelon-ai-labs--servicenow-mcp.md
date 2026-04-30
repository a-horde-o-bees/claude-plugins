# Sample

## Identification

### url

https://github.com/echelon-ai-labs/servicenow-mcp

### stars

241

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

ServiceNow MCP server — 60+ tools across incidents, service catalog, change requests, agile, workflows, knowledge bases; stdio and SSE ship as separate console scripts.

## Language and runtime

### language(s) + version constraints

Python 99.4%; requires Python 3.11 or higher.

### framework/SDK in use

raw `mcp` Python SDK; Starlette for SSE transport.

### pitfalls observed

Python 3.11 floor — a touch more modern than awslabs' 3.10.

## Transport

### supported transports

stdio (standard mode) and Server-Sent Events (SSE) via a web server.

### how selected

separate console script (`servicenow-mcp-sse`) vs stdio CLI module (`python -m servicenow_mcp.cli`).

## Distribution

### every mechanism observed

clone + `pip install -e .`; Docker (Dockerfile present).

### published package name(s)

not captured from README

### install commands shown in README

`git clone ... && python -m venv .venv && pip install -e .`

## Entry point / launch

### command(s) users/hosts run

stdio: `python -m servicenow_mcp.cli`. SSE: `servicenow-mcp-sse --instance-url=... --username=... --password=...`.

### wrapper scripts, launchers, stubs

separate console script for SSE mode with CLI args.

## Configuration surface

### how config reaches the server

CLI args (SSE mode) or env vars (both modes) — `SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`, `SERVICENOW_AUTH_TYPE`.

## Authentication

### flow

three methods — Basic Auth (username/password), OAuth (client credentials), API Key.

### where credentials come from

CLI args or env vars; `SERVICENOW_AUTH_TYPE` selects mechanism.

## Multi-tenancy

### tenancy model

single ServiceNow instance per deployment (via env/URL).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

60+ tools across: Incident management, Service catalog, Change requests, Agile management, Workflows, Script includes, Changesets, Knowledge bases, User management.

## Observability

### logging destination + format, metrics, tracing, debug flags

not captured

## Host integrations shown in README or repo

Not captured per host.

## Claude Code plugin wrapper

### presence and shape

none

## Tests

### presence, framework, location, notable patterns

`tests/` directory present.

## CI

### presence, system, triggers, what it runs

not captured — no mention.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

CLI arg shape for SSE mode.

## Repo layout

### single-package / monorepo / vendored / other

single-package (`servicenow_mcp/`).

## Notable structural choices

Two separate entry points for different transports — `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE); architecturally split rather than env-var-switched. Starlette as the SSE web framework — an explicit choice; many other servers use FastAPI + uvicorn. Three auth mechanisms in one server (Basic, OAuth, API Key) — selector is `SERVICENOW_AUTH_TYPE` env var. 60+ tools across 9 functional areas — very broad enterprise-ITSM surface. Python 3.11 floor — a touch more modern than awslabs' 3.10.

## Unanticipated axes observed

Transport split across separate console scripts — unlike servers that switch transport via env var/CLI flag, this one ships two distinct binaries. A cleaner separation but more install-time ceremony. Multi-auth support as a first-class feature — enterprise SaaS servers often need it because different customer deployments mandate different auth; most community servers pick one. ServiceNow MCP leans enterprise here. Starlette standalone for SSE rather than FastAPI — reveals Starlette as a viable sub-FastAPI layer for MCP servers that want HTTP transport without full REST framework overhead. Enterprise-tool density — 60+ tools in 9 functional areas; enterprise platforms generate more surface area than consumer SaaS does.

## Python-specific

### SDK / framework variant

raw `mcp` Python SDK. Version pin from pyproject.toml: not captured (pyproject not read directly). Import pattern observed: likely `from mcp.server import Server`.

### Python version floor

`requires-python` value: `>=3.11`.

### Packaging

Build backend: not captured. Lock file present: not captured. Version manager convention: pip (`pip install -e .`).

### Entry point

Both — `__main__`-style module invocation (`python -m servicenow_mcp.cli`) and a console script (`servicenow-mcp-sse`). Actual console-script name(s): `servicenow-mcp-sse`. Host-config snippet shape: stdio — `python -m servicenow_mcp.cli`; SSE — `servicenow-mcp-sse` with CLI args.

### Install workflow expected of end users

`pip install -e .` after clone.

### Async and tool signatures

not captured; Starlette suggests async for SSE path.

### Type / schema strategy

not captured

### Testing

tests/ directory present.

### Dev ergonomics

not captured

### Notable Python-specific choices

Plain `pip install -e .` installation workflow — more conservative than the uv/uvx-heavy trend among newer servers. Separate CLI entry for each transport — the opposite of `AlwaysSany/deepl-fastmcp-python-server`'s one-binary multi-transport model.

## Gaps

Exact pyproject dependencies, console-script vs entry-point details, CI presence, test framework specifics, Docker image publication, OAuth specifics.
