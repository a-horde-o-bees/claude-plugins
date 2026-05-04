# Sample

Mirrors of `https://github.com/modelcontextprotocol/servers`. Official MCP reference-servers monorepo — TypeScript and Python reference servers (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time) deliberately use raw `mcp` SDK rather than FastMCP. 84.2k stars, MIT (existing) / Apache-2.0 (new contributions), default branch `main`, last commit 2026-01-27 (release tag 2026.1.26).

## Server runtime

### Python with raw MCP SDK

Python reference servers (git, fetch, time) deliberately use raw `mcp` SDK exclusively — no FastMCP. git pins `mcp>=1.0.0`; fetch pins `mcp>=1.1.3`. Import pattern uses the low-level `Server` class from `mcp` package. Python 3.10+ across the three sampled Python servers. Demonstrates the "pre-FastMCP" authoring style and prioritizes low-level SDK coverage over developer convenience.

### Node.js / TypeScript with official MCP SDK

TypeScript reference servers (Everything, Filesystem, Memory, Sequential Thinking) use the official `@modelcontextprotocol/sdk`; ~69% TypeScript across the repo. Distributed via npm.

## Transport

### stdio

stdio across all reference servers; individual servers do not document non-stdio modes. Each reference server starts in stdio mode when launched by its entry command.

### Selection mechanism

Implicit single mode — stdio only; no transport flag.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools-focused across the reference set. Filesystem: 13 tools (9 read + 4 write). Git: 12 tools. Fetch: 1 `fetch` tool. Resources and prompts not prominent in the individual READMEs consulted.

### MCP Roots participation

Filesystem reference server implements the MCP Roots protocol — receives directory boundaries from the host and adapts file access accordingly. The only reference server consulted that interacts with the protocol's client-provided root-directory mechanism.

### Read/write tool split

Filesystem split into 9 read tools and 4 write tools.

## Configuration delivery

### CLI flags

Filesystem takes positional directory paths; git takes `--repository`; fetch takes `--user-agent`, `--ignore-robots-txt`, `--proxy-url`.

### Environment variables

Small number used (e.g., `PYTHONIOENCODING=utf-8` noted for Windows in fetch).

### Host-supplied protocol-level config (MCP Roots)

Filesystem additionally supports MCP Roots for dynamic directory updates from the host.

### Host-side JSON config snippet

Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code.

## Authentication

### None / implicit (local-resource gating)

No auth across the reference servers. Filesystem gates access via directory allowlist; git via repo path; fetch respects robots.txt by default.

### Domain-level access gate (not auth)

Filesystem allowlist, repo path, robots.txt — what can be accessed without identifying the caller.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user local process per host session.

## Distribution channel

### npm via npx / bunx

`npx -y @modelcontextprotocol/server-memory` — packages: `@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-memory`, `@modelcontextprotocol/server-everything`, `@modelcontextprotocol/server-sequentialthinking`.

### PyPI via uvx (zero-install runner)

`uvx mcp-server-git` — Python packages `mcp-server-git`, `mcp-server-fetch`, `mcp-server-time`.

### PyPI via pip / pipx

`pip install mcp-server-git` as alternative install path for Python servers.

### Docker / OCI image

Per-server Dockerfiles; images published to Docker Hub as `mcp/<server-name>` (`mcp/filesystem`, `mcp/git`, `mcp/fetch`). `docker run -i --rm --mount type=bind,src=/path,dst=/projects mcp/filesystem /projects`.

### Multi-channel publication

TypeScript servers via npm; Python servers via PyPI; both via Docker — each reference server multi-published.

## Entry point and launch

### `npx -y <package>` / `bunx`

TS — `npx -y @modelcontextprotocol/server-<name>` with positional args (filesystem takes directory paths).

### `uvx <package>`

`uvx mcp-server-<name>` — canonical uvx pattern with args like `--repository` for git.

### Module invocation / `python -m <module>` fallback

`python -m mcp_server_<name>` — alternative documented path.

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `mcp-server-git = "mcp_server_git:main"`, `mcp-server-fetch = "mcp_server_fetch:main"`. README host-config snippet uses `"command": "uvx"`, `"args": ["mcp-server-git", "--repository", "/path"]`.

### Docker container entrypoint

`docker run -i --rm --mount type=bind,src=/path,dst=/projects mcp/<name> ...`.

## Build and packaging

### Hatchling + uv (Python)

`build-backend = "hatchling.build"` across sampled Python servers; each is a standalone uv package (per-subdir pyproject); `uv` as the version manager convention.

### npm/Node toolchain

TypeScript servers ship via npm; centralized `package.json`/`package-lock.json` at root for shared lint/build tooling; individual servers buildable in isolation.

### Python version pinning

`requires-python = ">=3.10"` across the three Python servers sampled.

## Schema and types

### Hand-authored tool schemas

Low-level `mcp` SDK — hand-authored JSON schemas for tools. pyright for typing.

### Async model (cross-cutting)

Mixed — fetch is fully async (`pytest-asyncio>=0.21.0` + `asyncio_mode = "auto"`); git uses pytest only with no asyncio declared.

## Container artifacts

### Per-server Dockerfile in monorepo

Each server in the monorepo has its own Dockerfile (e.g., `src/filesystem/Dockerfile`, `src/git/Dockerfile`, `src/fetch/Dockerfile`); images publish to Docker Hub under `mcp/<name>`.

### Published Docker image

Pre-built images at `mcp/<server-name>` on Docker Hub.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio (fetch); pytest only (git). `testpaths = ["tests"]`, `python_files = "test_*.py"`. Each Python server has its own `tests/` directory.

## CI

### GitHub Actions

`.github/workflows/` present; specific workflows not fully enumerated within budget.

## Observability

### Stderr logging (convention / SDK default)

Each server logs to stderr per SDK default; not documented further at the reference-server level.

## Host integration

### Per-host README JSON snippets

Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code.

### Claude Desktop

Top README + each server README ship JSON for `claude_desktop_config.json` under `mcpServers.<name>` with `command`/`args`.

### VS Code / VS Code Insiders / Visual Studio family

`mcp.json` workspace/user config snippets in per-server READMEs (git).

### Zed

`settings.json` snippet in per-server README (git).

### Generic / host-agnostic snippet

Generic listing of "clients that support MCP" in top-level README without per-tool snippets. Mentions Zencoder.

## Repository layout

### Cross-language monorepo / mixed-language layout

Cross-language monorepo with TypeScript and Python as first-class peers in one repo. `src/<server>/` per reference server (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time). Archived servers physically moved out to a sibling `servers-archived` repo. Root has shared `package.json`, `tsconfig.json`, `.npmrc`; Python servers are self-contained Python packages inside the same directory tree. Each server has its own distribution channel (npm vs PyPI) and its own Docker image.

### Per-subserver README in monorepo

Each server has its own README documenting install path (npx vs uvx vs pip vs Docker).

## Developer ergonomics

### Linter and type-checker stack

pyright>=1.1.389, ruff>=0.7.3 pinned across Python servers.

### Sample MCP client configs in repo

Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code.

## Documentation surface

### Per-host README integration sections

Each server README has labeled sections per supported host showing canonical config snippets.

### README as the canonical surface

Top-level README plus per-server READMEs.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

`.mcp.json` present at repo root; no `.claude-plugin/` directory.

## Release and lifecycle

### Dual-license relicensing gate

Existing code stays MIT; new contributions land under Apache-2.0 — a deliberate relicensing-forward strategy.

### Tagged release with version in changelog

Release tag 2026.1.26.

### Active development

Active reference set; ongoing maintenance with active vs archived split (archived servers physically moved out rather than flagged in-place).

### Archived

`servers-archived` sibling repo holds excised reference servers — the repository keeps its demonstration set sharp by physically moving archived content out.
