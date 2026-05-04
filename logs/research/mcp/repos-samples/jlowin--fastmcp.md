# Sample

Mirrors of `https://github.com/jlowin/fastmcp`. FastMCP — Python MCP framework providing a decorator-driven API over the official MCP Python SDK; absorbed into the official MCP Python SDK in 2024 and de facto the canonical Python MCP authoring path. 24.7k stars, Apache-2.0, default branch `main`, v3.2.4 released Apr 14, 2026.

## Server runtime

### Python with FastMCP

This IS the FastMCP framework — version 3.x. Wraps the lower-level official `mcp` Python SDK; consumers import `from fastmcp import FastMCP`. Older `mcp.server.fastmcp` is the in-SDK incarnation. `requires-python = ">=3.10"`. Supports both `def` and `async def` tool signatures transparently; anyio/asyncio under the hood. Core deps include `authlib`, `python-multipart`, `uvicorn`, `websockets` — the framework ships the HTTP-transport stack so consumers don't need to add it. Self-claims to power "70% of MCP servers across all languages" — market self-assessment indicating ecosystem centrality. Absorbed into the official MCP Python SDK in 2024.

## Transport

### stdio

Framework supports stdio for consumer servers; selectable via `mcp.run()` call signature in the consuming server's code.

### Streamable HTTP

Framework supports HTTP for consumer servers; framework ships `uvicorn` and `python-multipart` in core deps so HTTP transport is built in. Selectable via `mcp.run()` call signature.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Framework exposes three core pillars: Servers (expose tools, resources, prompts), Clients (connect to MCP servers), and Apps (interactive UIs in conversations). Tool, resource, and prompt declarations all use decorators. Tool example:

```python
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

The "Apps" pillar extends MCP into UI territory — a structural choice beyond the standard tool/resource/prompt triad. Whether Apps requires host-side UI support and which hosts implement it is not confirmed.

## Configuration delivery

### Functional options at construction (code-level)

Framework configured programmatically via decorators and constructor args. Consumers wire their own config; FastMCP itself has no external config surface.

## Authentication

### None / implicit (local-resource gating)

Not applicable at framework level — consumers implement auth per server. Framework supports middleware patterns for auth layering.

## Multi-tenancy

### N/A (library, not a runtime)

Project ships scaffolding and primitives; tenancy is the consumer's concern. HTTP transport enables multi-client shared deployments; consumer decides the model.

## Distribution channel

### PyPI via pip / pipx

Published to PyPI as `fastmcp`. README install: `uv pip install fastmcp` (canonical); also `pip install fastmcp`.

## Entry point and launch

### Framework CLI run

`[project.scripts]` defines `fastmcp = "fastmcp.cli:app"` — the `fastmcp` CLI itself. `fastmcp dev` and `fastmcp run` serve consumer scripts; `fastmcp install` deploys to Claude Desktop. Substitutes for a project-level entry point when consumers commit to the framework's conventions.

### Programmatic embedding via library function

Consumers write entry points calling `mcp.run()`, embedding the framework directly into their own program.

## Build and packaging

### Hatchling + uv (Python)

Build backend `hatchling.build`; `uv.lock` present; src-layout `src/fastmcp/`.

### `uv.lock` committed

uv lockfile committed for reproducibility.

### Optional-dependency fan-out

Very broad optional-dependencies surface — `anthropic`, `azure`, `gemini`, `openai`, `apps`, `code-mode`, `tasks`. Each opt-in, avoiding bloat on core install.

## Schema and types

### FastMCP auto-derivation from type hints

Auto-derives JSON Schema from Python type hints and docstrings; `Annotated[type, Field(description=...)]` patterns supported. Pydantic for models; jsonschema-path + jsonref in core deps for schema traversal.

### Async model (cross-cutting)

Mixed — accepts both `def` and `async def` tool signatures transparently; the framework dispatches both.

## Test stack

### pytest with async + coverage

Extensive test tooling: pytest + pytest-asyncio + pytest-cov + pytest-env + pytest-flakefinder + pytest-httpx + pytest-report + pytest-retry + pytest-timeout + pytest-xdist + inline-snapshot + pytest-examples. Config: `asyncio_mode = "auto"`, `timeout = 5`, `testpaths = ["tests"]`. `pytest-flakefinder` + `pytest-retry` + `pytest-xdist` build flake hunting and parallelism into the test stack — heavier investment than any server in the sample. `pytest-examples` and `inline-snapshot` mean docs are test-verified.

## CI

### GitHub Actions

`run-tests.yml` workflow identified.

## Repository layout

### Single-package src-layout

`src/fastmcp/` source layout, `tests/`, `examples/`, `docs/`, `pyproject.toml` + `uv.lock`.

## Developer ergonomics

### Linter and type-checker stack

`ty` (Astral's new type checker) plus `pyright`-style strictness — adopting newer tooling ahead of the ecosystem. `ruff` for linting/formatting.

### `pre-commit` framework

`prek` (pre-commit replacement) in dev deps.

### Examples directory with many patterns

`/examples` directory; `/docs` directory.

## Documentation surface

### `llms.txt` / `llms-full.txt`

Framework ships `llms.txt` and `llms-full.txt` — design-for-AI-consumption surface. Docs at gofastmcp.com; community Discord.

### GitHub Pages / hosted docs site

Hosted docs at gofastmcp.com.

## Release and lifecycle

### Active development

v3.2.4 released Apr 14, 2026; ongoing development.

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
