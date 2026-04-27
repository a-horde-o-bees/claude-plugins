# Sample

## Identification

### url

https://github.com/modelcontextprotocol/servers

### stars

84.2k

### last-commit

2026-01-27 (release tag 2026.1.26)

### license

MIT for existing code; Apache-2.0 for new contributions.

### default branch

main

### one-line purpose

Official MCP reference-servers monorepo — Python (git, fetch, time) deliberately use raw `mcp` SDK rather than FastMCP; TypeScript reference servers alongside.

## Language and runtime

### language(s) + version constraints

TypeScript ~69%, Python ~19%, JavaScript ~10%. Per-server: TS servers ship via npm; Python servers target Python 3.x via uv/uvx.

### framework/SDK in use

Official `@modelcontextprotocol/sdk` (TypeScript) and `mcp` Python SDK (server-fetch, server-git use the Python SDK exposed as `mcp-server-*` modules).

## Transport

### supported transports

stdio across all reference servers; individual servers do not document non-stdio modes (fetch, git, filesystem READMEs describe stdio integration only via host config).

### how selected

Not exposed — each reference server starts in stdio mode when launched by its entry command; no transport flag.

## Distribution

### every mechanism observed

npm + npx (TS servers), PyPI + pip + uvx (Python servers), Docker images under `mcp/*` tag (per-server Dockerfiles). No Homebrew, no binary releases.

### published package name(s)

`@modelcontextprotocol/server-filesystem`, `@modelcontextprotocol/server-memory`, `@modelcontextprotocol/server-everything`, `@modelcontextprotocol/server-sequentialthinking` (npm); `mcp-server-git`, `mcp-server-fetch`, `mcp-server-time` (PyPI). Docker tags `mcp/filesystem`, `mcp/git`, `mcp/fetch`.

### install commands shown in README

`npx -y @modelcontextprotocol/server-memory`, `uvx mcp-server-git`, `pip install mcp-server-git`, `docker run -i --rm --mount type=bind,src=/path,dst=/projects mcp/filesystem /projects`.

## Entry point / launch

### command(s) users/hosts run

TS — `npx -y @modelcontextprotocol/server-<name>` with positional args (filesystem takes directory paths). Python — `uvx mcp-server-<name>` or `python -m mcp_server_<name>` (e.g., `--repository` flag for git).

### wrapper scripts, launchers, stubs

None — package entry points are the launcher. Dockerfile per server provides alt launch.

## Configuration surface

### how config reaches the server

Mix of positional CLI args (filesystem paths), flag CLI args (`--repository`, `--user-agent`, `--ignore-robots-txt`, `--proxy-url`), and a small number of env vars (e.g. `PYTHONIOENCODING=utf-8` noted for Windows in fetch). Filesystem additionally supports MCP Roots protocol for dynamic directory updates from the host.

## Authentication

### flow

None across the reference servers. Filesystem gates access via directory allowlist; git via repo path; fetch respects robots.txt by default.

### where credentials come from

N/A.

## Multi-tenancy

### tenancy model

Single-user local process per host session.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools across the board. Filesystem: 13 tools (9 read + 4 write). Git: 12 tools. Fetch: 1 `fetch` tool. Filesystem additionally implements MCP Roots protocol. Resources and prompts not prominent in the individual READMEs consulted.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not documented at the reference-server level. Each server logs to stderr per SDK default.

## Host integrations shown in README or repo

### Claude Desktop

JSON snippet for `claude_desktop_config.json` under `mcpServers.<name>` with `command`/`args` — top README + each server README.

### VS Code

`mcp.json` workspace/user config snippets in per-server READMEs (git).

### Zed

`settings.json` snippet in per-server README (git).

### Zencoder

Mentioned (git README).

### Other

Generic listing of "clients that support MCP" in top-level README without per-tool snippets.

## Claude Code plugin wrapper

### presence and shape

`.mcp.json` present at repo root (mentioned by repo listing). No `.claude-plugin/` directory.

## Tests

### presence, framework, location, notable patterns

`.github/` workflows present but per-server test infrastructure not prominent in individual READMEs; each server is small enough that test infrastructure is minimal/per-package.

## CI

### presence, system, triggers, what it runs

GitHub Actions present under `.github/workflows`. Specific workflows not fully enumerated within budget.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Per-server Dockerfile (e.g. `src/filesystem/Dockerfile`, `src/git/Dockerfile`, `src/fetch/Dockerfile`). Images published to Docker Hub as `mcp/<server-name>`. No Helm, compose, or brew formula observed.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code. Top-level `package.json`/`package-lock.json` suggests centralized lint/build tooling; individual servers buildable in isolation.

## Repo layout

### single-package / monorepo / vendored / other

Monorepo. `src/<server>/` per reference server (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time). Archived servers moved out to a sibling `servers-archived` repo. Root has shared `package.json`, `tsconfig.json`, `.npmrc`; Python servers are self-contained Python packages inside the same directory tree.

## Notable structural choices

Heterogeneous per-server implementations: TS and Python live side-by-side with independent package manifests. No forced uniformity — each server README documents its own install path (npx vs uvx vs pip vs Docker). Per-server Dockerfile with published `mcp/<name>` image — a consistent convention across servers even though language stack differs. Filesystem takes the unusual step of implementing MCP Roots — the only reference server consulted that interacts with the protocol's client-provided root-directory mechanism. Active vs archived split enforced by repository: archived servers physically moved out rather than flagged in-place, keeping the monorepo reference-set curated. License mixed: existing code stays MIT; new contributions land under Apache-2.0 — a deliberate relicensing-forward strategy rather than a relicense of existing material.

## Unanticipated axes observed

Cross-language monorepo convention: TS and Python as first-class peers in one repo, each with its own distribution channel (npm vs PyPI) and its own Docker image, rather than a single-language monorepo. Forces readers/hosts to handle multiple runtime stacks. Relicensing via contribution gate: dual-license strategy (MIT existing / Apache-2.0 new) as a migration mechanism without touching prior commits. Reference vs hosted split: repo is positioned as a showcase/reference set, not a product; archived content is physically excised to keep the demonstration sharp.

## Python-specific

### SDK / framework variant

Python reference servers (git, fetch, time) use raw `mcp` SDK exclusively — no fastmcp. git: `mcp>=1.0.0`; fetch: `mcp>=1.1.3`. Import pattern: low-level `Server` class from `mcp` package.

### Python version floor

All three Python servers sampled: `requires-python = ">=3.10"`.

### Packaging

Build backend: `hatchling.build` across sampled Python servers. Lock file: each Python server is a standalone uv package (per-subdir pyproject). Version manager convention: `uv`.

### Entry point

`[project.scripts]`: `mcp-server-git = "mcp_server_git:main"`, `mcp-server-fetch = "mcp_server_fetch:main"`. README host-config snippet: `"command": "uvx"`, `"args": ["mcp-server-git", "--repository", "/path"]` — canonical uvx pattern. Alternative: `python -m mcp_server_<name>` also documented.

### Install workflow expected of end users

`uvx mcp-server-<name>` (primary), `pip install mcp-server-<name>` (alternative), Docker `mcp/<name>`. Separate PyPI and npm distribution paths for the monorepo's two language stacks.

### Async and tool signatures

fetch: `pytest-asyncio>=0.21.0` + `asyncio_mode = "auto"` — fully async. git: pytest only (no asyncio declared).

### Type / schema strategy

Low-level `mcp` SDK — hand-authored JSON schemas for tools. pyright for typing.

### Testing

pytest + pytest-asyncio (fetch); pytest only (git). `testpaths = ["tests"]`, `python_files = "test_*.py"`. Each Python server has its own `tests/` directory.

### Dev ergonomics

pyright + ruff pinned across servers (pyright>=1.1.389, ruff>=0.7.3). Each Python server has its own Dockerfile published as `mcp/<name>`.

### Notable Python-specific choices

These are canonical reference Python MCP servers using the raw `mcp` SDK — demonstrate the "pre-FastMCP" authoring style. Consistent per-server pyproject.toml layout — hatchling + uv + raw mcp SDK + pyright + ruff + pytest. Python and TypeScript peers in one monorepo, each using its own distribution (PyPI vs npm) and its own Docker image. Reference-quality Python servers deliberately NOT using FastMCP — suggests the reference set prioritizes low-level SDK coverage over developer convenience.

## Gaps

Exact last-commit date (only the release tag 2026.1.26 was visible). Specific CI workflow contents (what tests/lints run per server) — would need `.github/workflows/*.yml` fetches. Whether any server supports non-stdio transports — not called out in the three READMEs (filesystem, git, fetch) checked. Full enumeration of published npm and PyPI packages for all seven servers — budget covered three in depth.
