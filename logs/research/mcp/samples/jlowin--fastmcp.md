# Sample

## Identification

### url

https://github.com/jlowin/fastmcp

### stars

24.7k

### last-commit

v3.2.4 released Apr 14, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

FastMCP Python framework (not a server) — decorator-driven SDK absorbed into the official MCP Python SDK; anchors Python MCP repo-layout defaults.

## Language and runtime

### language(s) + version constraints

Python 100%; specific Python minimum not extracted within budget (3.10+ is typical for modern FastMCP)

### framework/SDK in use

This IS the framework — wraps the official MCP Python SDK with a decorator-based API. Incorporated into the official MCP Python SDK in 2024.

## Transport

### supported transports

stdio and HTTP (the framework supports both; servers built on FastMCP choose per-deployment)

### how selected

Via `mcp.run()` call signature in the consuming server's code

## Distribution

### every mechanism observed

PyPI

### published package name(s)

fastmcp

### install commands shown in README

`uv pip install fastmcp`

## Entry point / launch

### command(s) users/hosts run

Not applicable — consumers write their own servers; FastMCP provides the runtime. Consumer script calls `mcp.run()` as entry.

### wrapper scripts, launchers, stubs

Framework-level; consumers write entry points.

## Configuration surface

### how config reaches the server

Framework API — consumers wire their own config. FastMCP itself is configured programmatically via decorators and constructor args.

## Authentication

### flow

Not applicable at framework level — consumers implement auth per server. Framework supports middleware patterns for auth layering.

### where credentials come from

Consumer-defined

## Multi-tenancy

### tenancy model

Framework supports arbitrary tenancy patterns — consumer decides. HTTP transport enables multi-client shared deployments.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Three core pillars: Servers (expose tools, resources, prompts), Clients (connect to MCP servers), Apps (interactive UIs in conversations). Tool definition via `@mcp.tool` decorator:

```python
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

Resources and prompts similarly declared via decorators.

## Observability

### logging destination + format, metrics, tracing, debug flags

Framework-level logging utilities; consumers configure destinations.

## Host integrations shown in README or repo

Not applicable — framework is host-agnostic; the servers built on it target Claude Desktop, Cursor, Windsurf, etc.

## Claude Code plugin wrapper

### presence and shape

Not applicable — framework level

## Tests

### presence, framework, location, notable patterns

pytest; tests in `/tests` directory.

## CI

### presence, system, triggers, what it runs

GitHub Actions — `run-tests.yml` workflow identified.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not observed at framework level; consumers containerize their own servers.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`/examples` directory; `/docs` directory; `llms.txt` format for LLM-consumable docs; community Discord; docs at gofastmcp.com.

## Repo layout

### single-package / monorepo / vendored / other

Single-package Python project with `src/fastmcp/` layout (src-layout, uses uv); separate `/examples`, `/docs`, `/tests`; `pyproject.toml` + `uv.lock`.

## Notable structural choices

Framework status — not a server; this file is present to anchor the reference layout that many Python MCP servers adopt. Decorator-based API for tools/resources/prompts is the "Pythonic" framing compared to raw SDK boilerplate. Three-pillar model (Servers, Clients, Apps) — Apps is distinctive; it positions FastMCP beyond just server-side framing into interactive UI territory. Claims to power "70% of MCP servers across all languages" — market self-assessment, worth noting as a signal of ecosystem centrality. Absorbed into the official MCP Python SDK in 2024 — the framework is de facto the canonical Python MCP authoring path. Src-layout (`src/fastmcp/`) with uv lockfile is the modern Python packaging default — reference pattern for other Python MCP servers in this research.

## Unanticipated axes observed

`llms.txt` documentation format signals design-for-AI-consumption — docs meant to be read by LLMs building on the framework, not just humans. The "Apps" pillar extends MCP into UI territory — a structural choice beyond the standard tool/resource/prompt triad. Framework is a consumer of itself — many FastMCP-built servers surveyed elsewhere in this research (motherduckdb, etc.) import it.

## Python-specific

### SDK / framework variant

THIS IS the framework — FastMCP 3.x. As of the inspected pyproject, depends on `mcp` (lower-level SDK), so FastMCP wraps/extends the official Python SDK. Import pattern for consumers: `from fastmcp import FastMCP` (2.x+ line); the older `mcp.server.fastmcp` is the in-SDK incarnation.

### Python version floor

`requires-python = ">=3.10"`. CI matrix: `run-tests.yml` exists; exact versions not extracted.

### Packaging

Build backend: `hatchling.build`. Lock file: `uv.lock` present. Version manager convention: `uv` (src-layout, `src/fastmcp/`).

### Entry point

`[project.scripts]`: `fastmcp = "fastmcp.cli:app"` — the `fastmcp` CLI itself (not an MCP server launcher; drives server dev/run workflow). Typical consumer entry: own `[project.scripts]` calling `mcp.run()` or `fastmcp run <script.py>`.

### Install workflow expected of end users

`uv pip install fastmcp` (canonical); also `pip install fastmcp`; framework consumers distribute their own servers via uvx/pip/Docker.

### Async and tool signatures

Supports both `def` and `async def` tool signatures transparently — the framework dispatches both. anyio/asyncio under the hood.

### Type / schema strategy

Auto-derives JSON Schema from Python type hints and docstrings; `Annotated[type, Field(description=...)]` patterns supported. pydantic for models; jsonschema-path + jsonref in core deps for schema traversal.

### Testing

pytest + pytest-asyncio + pytest-cov + pytest-env + pytest-flakefinder + pytest-httpx + pytest-report + pytest-retry + pytest-timeout + pytest-xdist + inline-snapshot + pytest-examples — extremely extensive test tooling. `asyncio_mode = "auto"`, `timeout = 5`, `testpaths = ["tests"]`.

### Dev ergonomics

`fastmcp dev` and `fastmcp run` CLI commands for serving scripts; `fastmcp install` deploys to Claude Desktop. `prek` (pre-commit replacement) in dev deps; ruff + `ty` (new Astral type checker) for typing. `llms.txt` and `llms-full.txt` for AI-consumable docs.

### Notable Python-specific choices

Very broad optional-dependencies surface: `anthropic`, `azure`, `gemini`, `openai`, `apps`, `code-mode`, `tasks` — each opt-in, avoiding bloat on core install. `ty` (Astral's type checker) + `pyright`-style strictness, adopting newer tooling ahead of the ecosystem. `pytest-flakefinder` + `pytest-retry` + `pytest-xdist` — test flake hunting and parallelism built in; heavier investment than any server in the sample. Core deps include `authlib`, `python-multipart`, `uvicorn`, `websockets` — the framework ships the HTTP-transport stack, consumers do not add it. `griffelib`, `inline-snapshot`, `pytest-examples` — docs are test-verified.

## Gaps

Specific CI matrix (versions, OS) not extracted. Whether FastMCP's "Apps" pillar requires host-side UI support and which hosts implement it is not confirmed.
