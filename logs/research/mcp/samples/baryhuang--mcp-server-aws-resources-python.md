# Sample

## Identification

### url

https://github.com/baryhuang/mcp-server-aws-resources-python

### stars

24

### last-commit

active on main (specific date not surfaced)

### license

MIT

### default branch

main

### one-line purpose

AWS resources MCP server — exposes a single AST-sandboxed `exec boto3` tool (code-as-tool) rather than enumerating each AWS API.

## 1. Language and runtime

### language(s) + version constraints

Python 95.7%; Python version not explicitly surfaced.

### framework/SDK in use

raw MCP Python SDK (boto3-based).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio.

### how selected

default MCP transport.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Docker Hub (`buryhuang/mcp-server-aws-resources:latest`), git clone + uv, Smithery.

### published package name(s)

mcp-server-aws-resources (Docker); smithery registry entry.

### install commands shown in README

`docker pull buryhuang/mcp-server-aws-resources:latest`; `npx -y @smithery/cli install mcp-server-aws-resources-python --client claude`; uv-based source build.

### pitfalls observed

multi-arch Docker images (including arm/v7) for broader platform coverage.

## 4. Entry point / launch

### command(s) users/hosts run

`src/mcp_server_aws_resources/server.py` or containerized equivalent.

### wrapper scripts, launchers, stubs

Dockerfile; Smithery CLI.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

environment variables injected into the Docker command in Claude Desktop config; or AWS profile path mounted into container.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

AWS credentials via `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` (+ optional `AWS_SESSION_TOKEN`), `AWS_DEFAULT_REGION`, or `AWS_PROFILE` mount.

### where credentials come from

host env / mounted AWS credentials file.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per process (one AWS credential set).

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

single "run boto3 code" tool with AST validation sandboxing; exposes a dynamic AWS-resources resource.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not explicitly documented.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` Docker command with env injection or AWS profile mount.

### Smithery

CLI-installable via `@smithery/cli install`.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

not detailed in README excerpt.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions directory present.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile; multi-arch images published (linux/amd64, arm64, arm/v7).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Smithery install path; Docker one-liner.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single package under `src/mcp_server_aws_resources/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Exposes a single "execute arbitrary boto3 Python" tool rather than enumerating AWS APIs — AST validator + allowlist of imports (boto3, operator, json, datetime, pytz, dateutil, re, time) is the sandboxing mechanism. Multi-arch Docker images (including arm/v7) for broader platform coverage.

## 18. Unanticipated axes observed

"Code-as-tool" architecture: one flexible code-execution tool with AST sandbox versus N hand-enumerated per-API tools. Smithery CLI as a distribution vector alongside Docker and source.

## 19. Python-specific

### SDK / framework variant

raw `mcp` Python SDK; version pin not surfaced; import pattern not surfaced.

### Python version floor

`requires-python` value not explicitly surfaced.

### Packaging

build backend: pyproject.toml present; lock file presence not surfaced; version manager convention: uv.

### Entry point

bare script at `src/mcp_server_aws_resources/server.py`; actual console-script name(s) not surfaced; host-config snippet shape: Docker-first config in Claude Desktop.

### Install workflow expected of end users

Docker pull; Smithery install.

### Async and tool signatures

synchronous code execution; asyncio/anyio usage not surfaced.

### Type / schema strategy

not surfaced; tool input is a Python code string; hand-authored single-tool schema.

### Testing

not detailed; fixture style not surfaced.

### Dev ergonomics

not surfaced.

### Notable Python-specific choices

AST validation for user-supplied Python is rare among MCP servers; treats AWS API as "run this Python snippet" rather than "call this named tool". Allowed-imports allowlist baked into the sandbox.

## 20. Gaps

Python version floor, test presence, last-commit date, console script name, schema strategy details could not be determined.
