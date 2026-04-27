# Sample

## Identification

### url

https://github.com/shreyaskarnik/huggingface-mcp-server

### stars

~70

### last-commit

not explicitly surfaced

### license

MIT

### default branch

main

### one-line purpose

Hugging Face Hub MCP server — all three MCP surfaces (tools + resources + prompts) with a custom `hf://` URI scheme.

## Language and runtime

### language(s) + version constraints

Python; version via `.python-version` file.

### framework/SDK in use

raw `mcp` Python SDK (not FastMCP).

### pitfalls observed

Exact `.python-version` content not read.

## Transport

### supported transports

stdio (MCP default).

### how selected

stdio-only

## Distribution

### every mechanism observed

Smithery CLI (`@shreyaskarnik/huggingface-mcp-server`); source clone + `uv sync`.

### published package name(s)

not confirmed on PyPI; Smithery as primary distribution.

### install commands shown in README

`npx -y @smithery/cli install @shreyaskarnik/huggingface-mcp-server --client claude`; `uv sync && uv run huggingface_mcp_server.py`.

### pitfalls observed

Whether PyPI publication exists not confirmed.

## Entry point / launch

### command(s) users/hosts run

`uv run huggingface_mcp_server.py`.

### wrapper scripts, launchers, stubs

single script `huggingface_mcp_server.py`.

## Configuration surface

### how config reaches the server

environment variables — `HF_TOKEN` optional.

## Authentication

### flow

optional bearer token.

### where credentials come from

`HF_TOKEN` env var (for higher rate limits and private-repo access).

## Multi-tenancy

### tenancy model

single-user

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools — search/info on models, datasets, spaces, papers, collections; prompts — `compare-models`, `summarize-paper`; resources — custom `hf://` URI scheme.

## Observability

### logging destination + format, metrics, tracing, debug flags

not documented

## Host integrations shown in README or repo

### Claude Desktop

macOS/Windows config paths.

### Smithery

registered

## Claude Code plugin wrapper

### presence and shape

none observed

## Tests

### presence, framework, location, notable patterns

not mentioned in README.

## CI

### presence, system, triggers, what it runs

not evident

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON snippet.

## Repo layout

### single-package / monorepo / vendored / other

flat — main server file at root; `src/huggingface/` for helpers.

## Notable structural choices

Read-only-only stance: README explicitly scopes to read-only access. Custom `hf://` URI scheme exposed via MCP resources — one of few Python servers that use MCP's resource surface and prompts, not just tools. Two MCP prompts shipped (`compare-models`, `summarize-paper`) — demonstrates MCP prompt feature rather than tool-only.

## Unanticipated axes observed

Using all three MCP surfaces (tools + resources + prompts) in a single server, when most Python servers stick to tools only; explicit read-only contract as a security surface.

## Python-specific

### SDK / framework variant

raw `mcp` SDK; version pin not surfaced; import pattern `from mcp.server import Server` style.

### Python version floor

`requires-python` value via `.python-version`; exact value not surfaced.

### Packaging

Build backend not surfaced (likely hatchling given uv convention). Lock file: uv-based (uv.lock likely). Version manager convention: uv + `.python-version`.

### Entry point

bare script (`huggingface_mcp_server.py`); no console-script; host-config snippet shape `uv run <path>/huggingface_mcp_server.py`.

### Install workflow expected of end users

Smithery-first, then uv source clone; Docker. One-liner: Smithery install via `npx`.

### Async and tool signatures

mix (MCP SDK accepts both).

### Type / schema strategy

Pydantic via MCP SDK; schema auto-derived from signatures.

### Testing

none observed

### Dev ergonomics

MCP CLI via `mcp[cli]` implied.

### Notable Python-specific choices

Single-file server kept at repo root rather than packaged — common "hackable" pattern for community MCP servers. Exposes MCP prompts — an underused MCP capability across the Python ecosystem.

## Gaps

Whether PyPI publication exists not confirmed. Exact `.python-version` content not read. CI presence not verified.
