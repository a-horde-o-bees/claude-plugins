# Sample

## Identification

### url

https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server

### stars

parent monorepo (awslabs/mcp)

### last-commit

not captured individually

### license

Apache-2.0

### default branch

main

### one-line purpose

AWS documentation MCP server — fetches and converts AWS docs to markdown; partition-scoped tools differ between global AWS and China partitions.

## 1. Language and runtime

### language(s) + version constraints

Python `>=3.10`.

### framework/SDK in use

raw `mcp[cli]>=1.23.0` — no fastmcp dependency.

## 2. Transport

### supported transports

stdio primary; Docker runs stdio inside a container.

### how selected

Default stdio; Docker wrapping is a distribution choice, not a transport change.

## 3. Distribution

### every mechanism observed

PyPI (`awslabs.aws-documentation-mcp-server`); `uvx`; Windows `.exe` via `uv tool run`; Docker image.

### published package name(s)

`awslabs.aws-documentation-mcp-server`.

### install commands shown in README

- `uvx awslabs.aws-documentation-mcp-server@latest`
- `uv tool run --from awslabs.aws-documentation-mcp-server@latest awslabs.aws-documentation-mcp-server.exe` (Windows)
- `docker build -t mcp/aws-documentation .`

## 4. Entry point / launch

### command(s) users/hosts run

`awslabs.aws-documentation-mcp-server` (console script).

### wrapper scripts, launchers, stubs

`awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main`; Windows `.exe` variant.

## 5. Configuration surface

### how config reaches the server

Minimal — User-Agent via env var for corporate proxies; partition selection (global vs China) likely env-configured.

## 6. Authentication

### flow

None required — fetches public AWS documentation.

### where credentials come from

N/A.

## 7. Multi-tenancy

### tenancy model

Not applicable — stateless read-only fetching of public docs; any number of instances can run without conflict.

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools — `read_documentation` (URL → markdown), `search_documentation` (global partition only), `read_sections`, `recommend`, `get_available_services` (China partition only).

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`loguru` for structured logging.

## 10. Host integrations shown in README or repo

Host-specific configs covered in parent monorepo catalog, not sub-server README.

## 11. Claude Code plugin wrapper

### presence and shape

None at sub-server level.

## 12. Tests

### presence, framework, location, notable patterns

pytest with `--cov --cov-branch`; live integration test flag `--run-live` gates tests that hit real AWS docs.

## 13. CI

### presence, system, triggers, what it runs

Parent monorepo CI; details not extracted per sub-server.

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; no compose.

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`--run-live` pytest flag for integration; no Inspector launcher.

## 16. Repo layout

### single-package / monorepo / vendored / other

Sub-package in awslabs/mcp monorepo.

## 17. Notable structural choices

Pure read-only documentation bridge — no AWS credentials, no mutation.

Splits tools by AWS partition: global has search/recommend; China has service discovery — partition-specific tool gating.

HTML-to-markdown conversion as a core value-add — uses `markdownify` + `beautifulsoup4`.

Uses `httpx` (async HTTP) + User-Agent handling for corporate firewalls that block browser UAs.

No framework above raw `mcp` SDK — the server is deliberately minimal.

## 18. Unanticipated axes observed

Partition-scoped tool surface — same binary exposes different tools depending on which AWS partition is targeted (global vs cn-*); most servers expose a single fixed tool set.

No-auth MCP servers as a design category — documentation/search servers form a distinct "credential-free" family.

Corporate proxy support as a first-class concern — User-Agent override baked in; reveals an operational constraint specific to enterprise Python deployments.

Partition-variant Windows `.exe` entry via `uv tool run` — Windows distribution pattern documented explicitly.

## 19. Python-specific

### SDK / framework variant

raw `mcp[cli]>=1.23.0`. Import pattern not captured; raw `mcp` suggests `from mcp.server import Server` pattern.

### Python version floor

`requires-python = ">=3.10"`.

### Packaging

Build backend: hatchling. Lock file not captured. Version manager convention: `uv` / `uvx`.

### Entry point

Console script `awslabs.aws-documentation-mcp-server`. Host-config snippet shape: `uvx awslabs.aws-documentation-mcp-server@latest`.

### Install workflow expected of end users

`uvx awslabs.aws-documentation-mcp-server@latest`.

### Async and tool signatures

`httpx` is sync-or-async; likely async given network-bound work.

### Type / schema strategy

`pydantic>=2.10.6`. Schema likely hand-authored tool handlers given raw `mcp` SDK.

### Testing

pytest with coverage and branch coverage; custom `--run-live` flag.

### Dev ergonomics

Not extracted.

### Notable Python-specific choices

Minimalist dependency set (6 runtime deps) compared to AWS-API sibling's 13+ — reflects narrower surface.

`markdownify` for HTML→markdown conversion is an unusual dependency in MCP servers and a reusable building block.

`beautifulsoup4` for selective HTML parsing.

## 20. Gaps

Exact tool handler signatures, whether async is used throughout, specifics of the corporate-proxy User-Agent logic, partition-switching mechanism.
