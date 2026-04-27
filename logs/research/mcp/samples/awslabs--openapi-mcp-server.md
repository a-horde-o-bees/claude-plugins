# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/openapi-mcp-server

### stars

parent monorepo

### last-commit (date or relative)

not captured individually

### license

Apache-2.0

### default branch

main

### one-line purpose

OpenAPI-driven MCP server — dynamically generates MCP tools, resources, and prompts from one or more OpenAPI specs at server start; multi-spec composition supported.

## 1. Language and runtime

### language(s) + version constraints

Python `>=3.10`

### framework/SDK in use

FastMCP 2.x (`fastmcp>=3.2.2,<4`)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio

### how selected

not configurable per README

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI with optional extras (`[yaml]`, `[prometheus]`, `[all]`)

### published package name(s)

`awslabs.openapi-mcp-server`

### install commands shown in README

  - `pip install "awslabs.openapi-mcp-server"`
  - `pip install "awslabs.openapi-mcp-server[yaml]"`
  - `pip install "awslabs.openapi-mcp-server[prometheus]"`
  - `pip install "awslabs.openapi-mcp-server[all]"`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`awslabs.openapi-mcp-server --api-name <name> --api-url <url> --spec-url <spec>`

### wrapper scripts, launchers, stubs

console script → `awslabs.openapi_mcp_server.server:main`

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

CLI args (`--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags`) and env vars; auth configured per-spec via CLI or env

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

per-API auth — Basic, Bearer Token, API Key (header/query/cookie), AWS Cognito

### where credentials come from

CLI args or env vars; different APIs in a multi-spec composition can use different auth configs

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

**multi-spec composition** — one server can host tools from multiple OpenAPI specs via `--additional-specs`, each with its own HTTP client and auth

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

**dynamically generated tools + resources + prompts** — GET with query params becomes a tool (for LLM-friendly search); other GETs become resources; mutating operations become tools; operation-specific prompts and API doc prompts auto-generated

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`loguru`; optional Prometheus metrics via `[prometheus]` extra

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Aggregated in parent monorepo

- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

not captured

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

parent monorepo

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

not explicitly captured at sub-server level

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

CLI shape is itself the developer ergonomic — one command per spec to mount

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

sub-package in awslabs/mcp

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- **Dynamic tool generation from OpenAPI specs** — no hand-authored tool definitions; tools materialize at server start from the parsed spec
- **GET-with-query-params mapped to tools, not resources** — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search
- **Multi-spec composition** — a single server can front many APIs, each with independent auth and HTTP clients
- **Tag filtering via `--include-tags` / `--exclude-tags`** — reduces tool-surface at mount time
- **Auto-enriched tool descriptions** with response codes + parameter examples → claimed 70-75% token reduction vs naive rendering
- **Validation toggle** for non-compliant specs (many real-world OpenAPI specs fail strict validation)
- Depends on both `fastmcp` and `boto3` (for Cognito auth) — boto3 is used beyond pure AWS-API servers
- Version number in pyproject.toml was `0.9223372036854775807.9223372036854775807` — looks like an automated-release sentinel (int64 max), not a human-chosen version

## 18. Unanticipated axes observed

- **Spec-driven vs code-driven tool surface** — a major design axis. Most MCP servers hand-author tool functions; this one generates them. Implications for docs drift (spec is source of truth), testing (every spec change is a contract change), and LLM behavior (tool descriptions come from OpenAPI `description` fields, quality varies)
- **Multi-API composition as a core feature** — not a workaround; `--additional-specs` is first-class
- **Token-cost awareness as a pyproject-level concern** — README quantifies token reduction from description enrichment
- **Auth as per-spec, not per-server** — each mounted spec has its own credential context, supporting "one gateway to many SaaS APIs" use case
- **Prompts generated per-operation** alongside tools — uses MCP prompts primitive more deeply than most servers

## 19. Python-specific

### SDK / framework variant

- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: FastMCP 2.x (`fastmcp>=3.2.2,<4`)
- version pin from pyproject.toml: `fastmcp>=3.2.2,<4`
- import pattern observed: not captured; likely `from fastmcp import FastMCP`

### Python version floor

- `requires-python` value: `>=3.10`

### Packaging

- build backend: hatchling
- lock file present: not captured
- version manager convention: `uv` / pip

### Entry point

- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script
- actual console-script name(s): `awslabs.openapi-mcp-server`
- host-config snippet shape: `pip install` + direct CLI invocation with args

### Install workflow expected of end users

- install form + one-liner from README: `pip install awslabs.openapi-mcp-server[all]`

### Async and tool signatures

- sync `def` or `async def`: `httpx` + FastMCP 2 → async throughout is expected

### Type / schema strategy

- Pydantic / dataclasses / TypedDict / raw dict / Annotated: Pydantic v2; schemas derived from OpenAPI specs via `openapi-spec-validator` + `prance`
- schema auto-derived vs hand-authored: **auto-derived from external OpenAPI specs** — the most extreme "schema is data" design in the sample

### Testing

- pytest / pytest-asyncio / unittest / none: not captured

### Dev ergonomics

- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: CLI composition; `prance` for spec parsing

### Notable Python-specific choices

- `prance` + `openapi-spec-validator` for OpenAPI parsing — non-trivial dependencies rarely seen in MCP servers
- `tenacity` for retry logic on upstream HTTP calls
- `cachetools` for in-process caching of spec/responses
- `uvicorn` as a dependency despite stdio transport — suggests optional HTTP mode or internal HTTP client pool
- `bcrypt` as a runtime dep — likely for Basic Auth credential hashing/storage
- Caret-pinned upper bounds (`,<4`, `,<1`) throughout — stricter compatibility stance than typical Python projects

## 20. Gaps

### what couldn't be determined

whether the `uvicorn` dep indicates an undocumented HTTP transport, test coverage, actual runtime spec-caching strategy, how the "prompt generation" materializes (auto from OpenAPI tags?)
