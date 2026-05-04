# Sample

Mirrors of `https://github.com/awslabs/mcp/tree/main/src/openapi-mcp-server`. OpenAPI-driven MCP server — dynamically generates MCP tools, resources, and prompts from one or more OpenAPI specs at server start; multi-spec composition supported. Apache-2.0; default branch `main`; sub-package in awslabs/mcp monorepo (parent stars carry; per-server last-commit not captured individually).

## Server runtime

### Python with FastMCP

Python `>=3.10` server on FastMCP 2.x (`fastmcp>=3.2.2,<4`). Pinned with caret-style upper bound (`,<4`); analogous bounded pins (`,<1`) appear elsewhere — a stricter compatibility stance than typical Python projects. Import pattern not captured; likely `from fastmcp import FastMCP`.

## Transport

### stdio

stdio is the documented transport. Not configurable per README. (`uvicorn` appears as a runtime dep despite stdio transport — suggests an undocumented HTTP mode or internal HTTP client pool.)

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Dynamically generated tools + resources + prompts. Operation-specific prompts and API-doc prompts auto-generated alongside tools — uses MCP prompts primitive more deeply than most servers.

### Spec-driven dynamic tool generation

No hand-authored tool definitions; tools materialize at server start from parsed OpenAPI specs. GET-with-query-params is mapped to tools (not resources) — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search. Other GETs become resources; mutating operations become tools. Tool descriptions auto-enriched with response codes and parameter examples — claimed 70-75% token reduction vs naive rendering. A validation toggle accommodates non-compliant real-world specs.

### Tools plus toolset gating (dynamic)

Tag filtering via `--include-tags` / `--exclude-tags` reduces tool surface at mount time.

## Configuration delivery

### CLI flags

CLI flags drive composition: `--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags`. Per-spec auth configured via CLI or env.

### Environment variables

Env vars layered alongside CLI for the same surface; auth config supplied per spec.

## Authentication

### Per-spec authentication

Each upstream API mounted into the server can carry its own auth config — Basic, Bearer Token, API Key (header/query/cookie), or AWS Cognito — supplied via CLI args or env vars. Different APIs in a multi-spec composition can use different auth configs; `boto3` enters core deps to support Cognito.

## Multi-tenancy

### Multi-spec / multi-source composition

Single server fronts multiple OpenAPI specs concurrently via `--additional-specs`; each spec has its own HTTP client and auth context. The server is positioned as a gateway between one MCP host and many SaaS APIs declared in its manifest.

## Distribution channel

### PyPI via pip / pipx

Standard `pip install "awslabs.openapi-mcp-server"` with optional extras: `[yaml]`, `[prometheus]`, `[all]`. Published name: `awslabs.openapi-mcp-server`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `awslabs.openapi-mcp-server` mapped to `awslabs.openapi_mcp_server.server:main`. Hosts launch with required CLI args inline: `awslabs.openapi-mcp-server --api-name <name> --api-url <url> --spec-url <spec>`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. `requires-python = ">=3.10"`. Version manager convention: `uv` / pip. Lock file not captured.

### Optional-dependency fan-out

`[yaml]`, `[prometheus]`, `[all]` extras separate optional capability surfaces from core install.

### Pin discipline (Python)

Caret-pinned upper bounds (`,<4`, `,<1`) throughout — stricter compatibility stance than typical Python projects.

## Schema and types

### Pydantic v2 models

Pydantic v2 used throughout.

### Hand-authored tool schemas

Schemas auto-derived from external OpenAPI specs via `openapi-spec-validator` + `prance` — the most extreme "schema is data" design in the corpus, registering tools with hand-built schema dicts at runtime rather than from Python type hints.

### Async model (cross-cutting)

`httpx` + FastMCP 2 — async throughout is expected.

## Container artifacts

### No container artifacts

Not explicitly captured at sub-server level.

## Observability

### loguru (Python)

`loguru` for application logging.

### Prometheus metrics

Optional Prometheus metrics endpoint via the `[prometheus]` install extra.

## Caching and rate-limiting infrastructure

### SQLite TTL cache

`cachetools` for in-process caching of spec/responses. Cache is in-memory dict-based with TTL eviction (`cachetools` library), not the persistent SQLite-backed variant the path name suggests.

## CI

### Monorepo CI inheritance

CI inherited from parent monorepo.

## Repository layout

### Monorepo of namespace-prefixed packages

`src/openapi-mcp-server/` directory inside the parent multi-server monorepo, with its own `pyproject.toml`, console script, and PyPI release.

## Host integration

### Monorepo catalog

Host integration aggregated in parent monorepo catalog.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Automated-release sentinel version

Version field in pyproject.toml observed as `0.9223372036854775807.9223372036854775807` (int64 max) — automated-release sentinel rather than human-chosen number.

### Active development

Active via parent monorepo.
