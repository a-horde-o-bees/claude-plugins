# Sample

Mirrors of `https://github.com/FuzzingLabs/mcp-security-hub`. Security toolchain MCP monorepo — 38 containerized MCP servers each wrapping one security tool (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, etc.). 527 stars, MIT, default branch `master`, active.

## Server runtime

### Python with hand-rolled MCP

Python 80.0% — custom hand-rolled MCP implementations per server (not FastMCP, not the official Python SDK wrappers), wrapping external security CLI tools (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, etc.) as subprocesses. Schema hand-authored (custom MCP impl). Async signatures not surfaced; likely sync given CLI subprocess wrapping. Per-Dockerfile Python environments (Alpine/Debian slim bases); no unified pyproject. Python version floor not unified (set per Dockerfile base image).

## Transport

### stdio

Docker container-based stdio transport — each container is launched by the host with `docker run -i`.

## Capability surface

### Tools-only, hand-curated narrow surface

Each of the 38 separate MCP servers wraps one security tool — Nmap (port scanning), Shodan (device search), Nuclei (vulnerability templates), SQLMap (SQLi detection), Hashcat (cracking), Ghidra (reverse engineering), etc.

## Configuration delivery

### Environment variables

Environment variables injected via container env for credentials and tool config.

### Mounted credentials

Volume mounts (read-only by default) deliver tool-specific data and credentials to containers. Container args also used.

## Authentication

### Per-tool varied (monorepo)

Authentication varies per server in the monorepo — some need API keys (vulnerability databases like Nuclei templates), others need none (local CLI wrappers like Nmap). The container env injection mechanism is uniform; the credentials inside it are tool-specific.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per container; one container per tool.

## Distribution channel

### Docker / OCI image

Docker images per tool — Docker-only distribution with no PyPI publishing. Per-tool Docker images launched via `docker run` or orchestrated via Docker Compose, including a multi-server bundle compose file. Exact registry not surfaced.

## Entry point and launch

### Docker container entrypoint

Per-tool Docker container entrypoints; `.mcp.json` or `claude_desktop_config.json` points at `docker run ...` invocations.

## Build and packaging

### System-level dependencies

Each server wraps a system binary (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, etc.) so Docker is the only self-contained distribution path. Python packaging concerns deferred entirely to the Docker layer; no unified pyproject or lockfile.

## Container artifacts

### Per-server Dockerfile in monorepo

Each server in the monorepo has its own Dockerfile.

### Dockerfile.template as scaffold

A template Dockerfile parameterized for "new tool added to the monorepo" — enforces the security baseline (non-root, capability-drop, read-only mounts, resource limits) and base-image conventions across all per-tool servers. Contribution-surface artifact.

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits — security-by-default rigor unusual for MCP servers.

### Docker Compose for multi-server orchestration

Docker Compose orchestrates many MCP server containers together so users can bring up the full security toolchain at once.

## Test stack

### pytest with async + coverage

pytest (pytest.ini present); `tests/test_mcp_servers.py`. Fixture style not surfaced.

## CI

### Build + test + supply-chain scan

GitHub Actions pipeline that builds container images, runs tests, and runs Trivy supply-chain scanning. The scan step is treated as a build gate rather than a separate concern.

## Deployment topology

### Containerized local process

Each server runs as a Docker container; host launches `docker run` as the server command.

## Host integration

### Claude Desktop

JSON `mcpServers` entry per security tool.

### Claude Code

Project-level `.mcp.json` with per-tool entries.

### `.mcp.json` in project root

`.mcp.json` is the project-level MCP config consumed by Claude Code; per-tool entries documented.

## Repository layout

### Monorepo of independent servers

38 tool subdirectories, each a standalone MCP server with its own Dockerfile, Python script(s), and tests. `Dockerfile.template` at root acts as scaffolding for adding new servers. Composability at the deployment layer instead of the tool layer.

## Safety and security posture

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits. Surfaces in this security-focused project where the wrapped CLI tools are themselves attack surface.

## Developer ergonomics

### Health-check scripts

Per-container health-check scripts so Docker can verify each server is responsive — tied to container deployment patterns.
