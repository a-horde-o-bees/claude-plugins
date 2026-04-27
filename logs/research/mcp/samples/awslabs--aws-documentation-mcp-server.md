# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server

### stars

parent monorepo (awslabs/mcp)

### last-commit (date or relative)

not captured individually

### license

Apache-2.0

### default branch

main

### one-line purpose

AWS documentation MCP server — fetches and converts AWS docs to markdown; partition-scoped tools differ between global AWS and China partitions.

## 1. Language and runtime

### language(s) + version constraints

Python `>=3.10`

### framework/SDK in use

raw `mcp[cli]>=1.23.0` — no fastmcp dependency

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio primary; Docker runs stdio inside a container

### how selected

default stdio; Docker wrapping is a distribution choice, not a transport change

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (`awslabs.aws-documentation-mcp-server`); `uvx`; Windows `.exe` via `uv tool run`; Docker image

### published package name(s)

`awslabs.aws-documentation-mcp-server`

### install commands shown in README

  - `uvx awslabs.aws-documentation-mcp-server@latest`
  - `uv tool run --from awslabs.aws-documentation-mcp-server@latest awslabs.aws-documentation-mcp-server.exe` (Windows)
  - `docker build -t mcp/aws-documentation .`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`awslabs.aws-documentation-mcp-server` (console script)

### wrapper scripts, launchers, stubs

`awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main`; Windows `.exe` variant

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

minimal — User-Agent via env var for corporate proxies; partition selection (global vs China) likely env-configured

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

**none required** — fetches public AWS documentation

### where credentials come from

N/A

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

**not applicable** — stateless read-only fetching of public docs; any number of instances can run without conflict

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools — `read_documentation` (URL → markdown), `search_documentation` (global partition only), `read_sections`, `recommend`, `get_available_services` (China partition only)

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`loguru` for structured logging

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Host-specific configs covered in parent monorepo catalog, not sub-server README

- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none at sub-server level

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest with `--cov --cov-branch`; live integration test flag `--run-live` gates tests that hit real AWS docs

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

parent monorepo CI; details not extracted per sub-server

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; no compose

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`--run-live` pytest flag for integration; no Inspector launcher

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

sub-package in awslabs/mcp monorepo

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- Pure read-only documentation bridge — no AWS credentials, no mutation
- Splits tools by AWS partition: global has search/recommend; China has service discovery — partition-specific tool gating
- HTML-to-markdown conversion as a core value-add — uses `markdownify` + `beautifulsoup4`
- Uses `httpx` (async HTTP) + User-Agent handling for corporate firewalls that block browser UAs
- No framework above raw `mcp` SDK — the server is deliberately minimal

## 18. Unanticipated axes observed

- **Partition-scoped tool surface** — same binary exposes different tools depending on which AWS partition is targeted (global vs cn-*); most servers expose a single fixed tool set
- **No-auth MCP servers as a design category** — documentation/search servers form a distinct "credential-free" family
- **Corporate proxy support as a first-class concern** — User-Agent override baked in; reveals an operational constraint specific to enterprise Python deployments
- **Partition-variant Windows `.exe` entry** via `uv tool run` — Windows distribution pattern documented explicitly

## 19. Python-specific

### SDK / framework variant

- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: raw `mcp[cli]>=1.23.0`
- version pin from pyproject.toml: `mcp[cli]>=1.23.0`
- import pattern observed: not captured; raw `mcp` suggests `from mcp.server import Server` pattern

### Python version floor

- `requires-python` value: `>=3.10`

### Packaging

- build backend: hatchling
- lock file present: not captured
- version manager convention: `uv` / `uvx`

### Entry point

- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script
- actual console-script name(s): `awslabs.aws-documentation-mcp-server`
- host-config snippet shape: `uvx awslabs.aws-documentation-mcp-server@latest`

### Install workflow expected of end users

- install form + one-liner from README: `uvx awslabs.aws-documentation-mcp-server@latest`

### Async and tool signatures

- sync `def` or `async def`: `httpx` is sync-or-async; likely async given network-bound work

### Type / schema strategy

- Pydantic / dataclasses / TypedDict / raw dict / Annotated: `pydantic>=2.10.6`
- schema auto-derived vs hand-authored: likely hand-authored tool handlers given raw `mcp` SDK

### Testing

- pytest / pytest-asyncio / unittest / none: pytest with coverage and branch coverage; custom `--run-live` flag

### Dev ergonomics

- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: not extracted

### Notable Python-specific choices

- Minimalist dependency set (6 runtime deps) compared to AWS-API sibling's 13+ — reflects narrower surface
- `markdownify` for HTML→markdown conversion is an unusual dependency in MCP servers and a reusable building block
- `beautifulsoup4` for selective HTML parsing

## 20. Gaps

### what couldn't be determined

exact tool handler signatures, whether async is used throughout, specifics of the corporate-proxy User-Agent logic, partition-switching mechanism
