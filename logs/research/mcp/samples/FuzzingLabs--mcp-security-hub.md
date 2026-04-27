# Sample

## Identification

### url

https://github.com/FuzzingLabs/mcp-security-hub

### stars

527

### last-commit (date or relative)

active on master (specific date not surfaced)

### license

MIT

### default branch

master

### one-line purpose

Security toolchain MCP monorepo — 38 containerized MCP servers each wrapping one security tool (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, etc.).

## 1. Language and runtime

### language(s) + version constraints

Python 80.0%; version not explicitly surfaced

### framework/SDK in use

custom Python MCP implementations (not FastMCP, not the official Python SDK wrappers) wrapping external security CLI tools (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, etc.)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (Docker container-based)

### how selected

default

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Docker images per tool; Docker Compose for orchestration; direct image execution

### published package name(s)

per-tool Docker images (exact registry not surfaced)

### install commands shown in README

Docker Compose + volume mounts; individual `docker run` invocations

### pitfalls observed

  - Docker-only distribution; no PyPI publishing
  - what couldn't be determined: exact MCP JSON-RPC implementation approach per server, whether any servers share code, published registry for the Docker images, last-commit date

## 4. Entry point / launch

### command(s) users/hosts run

Docker container entrypoints per-tool; `.mcp.json` or `claude_desktop_config.json` pointing at `docker run ...`

### wrapper scripts, launchers, stubs

`Dockerfile.template` as scaffold for new tools

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

volume mounts (read-only by default), environment variables, container args

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

depends per tool (API keys for Nuclei templates, none for Nmap, etc.)

### where credentials come from

environment variables injected via container env

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

single-user per container; one container per tool

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

38 separate MCP servers, each wrapping one security tool (Nmap port scanning, Shodan device search, Nuclei vulnerability templates, SQLMap SQLi detection, Hashcat cracking, Ghidra reverse engineering, etc.)

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

health-check scripts per container; Trivy vulnerability scanning in CI pipeline

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location

### Claude Desktop

JSON `mcpServers` entry per security tool

### Claude Code

project-level `.mcp.json` with per-tool entries

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed (though `.mcp.json` is the project-level MCP config consumed by Claude Code)

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest (pytest.ini present); `tests/test_mcp_servers.py`

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions — builds + security scanning (Trivy) + tests

### pitfalls observed

  - Trivy scanning in CI as part of the build pipeline
  - decision dimensions this repo reveals: - "monorepo of micro-MCP-servers" as an architectural pattern — each server is one container, one tool, one security boundary - hardened-b...

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile per tool + `Dockerfile.template`; docker-compose for orchestration

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`Dockerfile.template` + sample claude_desktop_config.json entries; health-check scripts

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

monorepo — 38 tool subdirectories, each a standalone MCP server with its own Dockerfile, Python script(s), and tests

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- monorepo-of-servers rather than one server with many tools: each security tool gets its own MCP server, own Dockerfile, own container — composability at the deployment layer instead of the tool layer
- Docker-only distribution; no PyPI publishing
- security-by-default containers: non-root, capability-drop, resource limits, read-only mounts — unusual rigor for MCP servers
- Trivy scanning in CI as part of the build pipeline

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - "monorepo of micro-MCP-servers" as an architectural pattern — each server is one container, one tool, one security boundary
    - hardened-by-default container posture (capability-drop, non-root, read-only, resource limits) baked into Dockerfile.template
    - Trivy supply-chain scanning as part of CI, not an afterthought
    - Dockerfile.template as a first-class contribution surface for adding new security tool servers

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: custom — hand-rolled MCP implementations per server wrapping security CLI tools
- version pin from pyproject.toml: pyproject.toml/uv not explicitly used at repo root
- import pattern observed: not surfaced

### Python version floor
- `requires-python` value: not explicitly surfaced (set per Dockerfile base image)

### Packaging
- build backend: per-Dockerfile Python environments (Alpine/Debian slim bases); no unified pyproject
- lock file present: not unified
- version manager convention: Docker image as the unit of packaging

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: bare Python scripts executed via Docker entrypoint
- actual console-script name(s): N/A
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `docker run ...` as the command in Claude host config

### Install workflow expected of end users
- install form + one-liner from README: Docker Compose orchestration or per-tool `docker run`

### Async and tool signatures
- sync `def` or `async def`: not surfaced; likely sync given CLI subprocess wrapping
- asyncio/anyio usage: not surfaced

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not surfaced
- schema auto-derived vs hand-authored: hand-authored (custom MCP impl)

### Testing
- pytest / pytest-asyncio / unittest / none: pytest (pytest.ini present)
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: health-check scripts; `Dockerfile.template`; docker-compose

### Notable Python-specific choices
- open bullets:
    - opting out of FastMCP / official Python SDK in favor of hand-rolled MCP wrappers — suggests simplicity (stdin/stdout JSON-RPC) sufficed
    - Python packaging concerns deferred entirely to Docker layer

## 20. Gaps

### what couldn't be determined

exact MCP JSON-RPC implementation approach per server, whether any servers share code, published registry for the Docker images, last-commit date
