# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/openapi-mcp-server

### stars

parent monorepo

### last-commit

not captured individually

### license

Apache-2.0

### default branch

main

### one-line purpose

OpenAPI-driven MCP server — dynamically generates MCP tools, resources, and prompts from one or more OpenAPI specs at server start; multi-spec composition supported.

## 1. Language and runtime

### language(s) + version constraints

Python `>=3.10`.

### framework/SDK in use

FastMCP 2.x (`fastmcp>=3.2.2,<4`).

## 2. Transport

### supported transports

stdio.

### how selected

Not configurable per README.

## 3. Distribution

### every mechanism observed

PyPI with optional extras (`[yaml]`, `[prometheus]`, `[all]`).

### published package name(s)

`awslabs.openapi-mcp-server`.

### install commands shown in README

- `pip install "awslabs.openapi-mcp-server"`
- `pip install "awslabs.openapi-mcp-server[yaml]"`
- `pip install "awslabs.openapi-mcp-server[prometheus]"`
- `pip install "awslabs.openapi-mcp-server[all]"`

## 4. Entry point / launch

### command(s) users/hosts run

`awslabs.openapi-mcp-server --api-name <name> --api-url <url> --spec-url <spec>`.

### wrapper scripts, launchers, stubs

Console script → `awslabs.openapi_mcp_server.server:main`.

## 5. Configuration surface

### how config reaches the server

CLI args (`--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags`) and env vars; auth configured per-spec via CLI or env.

## 6. Authentication

### flow

Per-API auth — Basic, Bearer Token, API Key (header/query/cookie), AWS Cognito.

### where credentials come from

CLI args or env vars; different APIs in a multi-spec composition can use different auth configs.

## 7. Multi-tenancy

### tenancy model

Multi-spec composition — one server can host tools from multiple OpenAPI specs via `--additional-specs`, each with its own HTTP client and auth.

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Dynamically generated tools + resources + prompts — GET with query params becomes a tool (for LLM-friendly search); other GETs become resources; mutating operations become tools; operation-specific prompts and API doc prompts auto-generated.

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`loguru`; optional Prometheus metrics via `[prometheus]` extra.

## 10. Host integrations shown in README or repo

Aggregated in parent monorepo.

## 11. Claude Code plugin wrapper

### presence and shape

None.

## 12. Tests

### presence, framework, location, notable patterns

Not captured.

## 13. CI

### presence, system, triggers, what it runs

Parent monorepo.

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not explicitly captured at sub-server level.

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

CLI shape is itself the developer ergonomic — one command per spec to mount.

## 16. Repo layout

### single-package / monorepo / vendored / other

Sub-package in awslabs/mcp.

## 17. Notable structural choices

Dynamic tool generation from OpenAPI specs — no hand-authored tool definitions; tools materialize at server start from the parsed spec.

GET-with-query-params mapped to tools, not resources — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search.

Multi-spec composition — a single server can front many APIs, each with independent auth and HTTP clients.

Tag filtering via `--include-tags` / `--exclude-tags` — reduces tool-surface at mount time.

Auto-enriched tool descriptions with response codes + parameter examples → claimed 70-75% token reduction vs naive rendering.

Validation toggle for non-compliant specs (many real-world OpenAPI specs fail strict validation).

Depends on both `fastmcp` and `boto3` (for Cognito auth) — boto3 is used beyond pure AWS-API servers.

Version number in pyproject.toml was `0.9223372036854775807.9223372036854775807` — looks like an automated-release sentinel (int64 max), not a human-chosen version.

## 18. Unanticipated axes observed

Spec-driven vs code-driven tool surface — a major design axis. Most MCP servers hand-author tool functions; this one generates them. Implications for docs drift (spec is source of truth), testing (every spec change is a contract change), and LLM behavior (tool descriptions come from OpenAPI `description` fields, quality varies).

Multi-API composition as a core feature — not a workaround; `--additional-specs` is first-class.

Token-cost awareness as a pyproject-level concern — README quantifies token reduction from description enrichment.

Auth as per-spec, not per-server — each mounted spec has its own credential context, supporting "one gateway to many SaaS APIs" use case.

Prompts generated per-operation alongside tools — uses MCP prompts primitive more deeply than most servers.

## 19. Python-specific

### SDK / framework variant

FastMCP 2.x (`fastmcp>=3.2.2,<4`). Import pattern not captured; likely `from fastmcp import FastMCP`.

### Python version floor

`requires-python = ">=3.10"`.

### Packaging

Build backend: hatchling. Lock file not captured. Version manager convention: `uv` / pip.

### Entry point

Console script `awslabs.openapi-mcp-server`. Host-config snippet shape: `pip install` + direct CLI invocation with args.

### Install workflow expected of end users

`pip install awslabs.openapi-mcp-server[all]`.

### Async and tool signatures

`httpx` + FastMCP 2 → async throughout is expected.

### Type / schema strategy

Pydantic v2; schemas derived from OpenAPI specs via `openapi-spec-validator` + `prance`. Schema auto-derived from external OpenAPI specs — the most extreme "schema is data" design in the sample.

### Testing

Not captured.

### Dev ergonomics

CLI composition; `prance` for spec parsing.

### Notable Python-specific choices

`prance` + `openapi-spec-validator` for OpenAPI parsing — non-trivial dependencies rarely seen in MCP servers.

`tenacity` for retry logic on upstream HTTP calls.

`cachetools` for in-process caching of spec/responses.

`uvicorn` as a dependency despite stdio transport — suggests optional HTTP mode or internal HTTP client pool.

`bcrypt` as a runtime dep — likely for Basic Auth credential hashing/storage.

Caret-pinned upper bounds (`,<4`, `,<1`) throughout — stricter compatibility stance than typical Python projects.

## 20. Gaps

Whether the `uvicorn` dep indicates an undocumented HTTP transport, test coverage, actual runtime spec-caching strategy, how the "prompt generation" materializes (auto from OpenAPI tags?).
