# sooperset/mcp-atlassian

## Identification
- url: https://github.com/sooperset/mcp-atlassian
- stars: 5,000
- last-commit (date or relative): v0.21.1 released April 10, 2026; 560+ commits, 70 releases
- license: MIT
- default branch: main
- one-line purpose: Atlassian Jira/Confluence MCP server — community-canonical server carrying both `mcp` and `fastmcp` packages simultaneously.

## 1. Language and runtime
- language(s) + version constraints: Python (99.3%); specific min Python not extracted within budget
- framework/SDK in use: Model Context Protocol Python SDK; Anthropic Claude Agent SDK conventions referenced
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: SSE (Server-Sent Events) primary; HTTP support mentioned
- how selected (flag, env, separate entry, auto-detect, etc.): Not extracted in detail — likely env-var or subcommand driven given Python+uvx pattern
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (`mcp-atlassian`), Docker (Dockerfile present), source install, `uvx` execution
- published package name(s): mcp-atlassian
- install commands shown in README: `uvx mcp-atlassian`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `uvx mcp-atlassian` or containerized via Docker
- wrapper scripts, launchers, stubs: PyPI entry point; docker image
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Environment variables for Atlassian connection —
  - Cloud: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`
  - Server/Data Center: `JIRA_PERSONAL_TOKEN`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Cloud uses email + API token; Server/Data Center uses Personal Access Token; OAuth 2.0 supported per docs
- where credentials come from: Atlassian-managed API tokens; PATs for on-prem
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Instance-keyed — one Atlassian site (URL + credentials) per process. No per-request tenant switching observed
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 72 tools spanning Jira (search, issue CRUD, transitions, comments) and Confluence (search, page CRUD, comments). Supports both Cloud and on-prem (Confluence v6.0+, Jira v8.14+)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not extracted within budget
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop
- Cursor IDE
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not explicitly observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Comprehensive test suite in `tests/` directory
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions tests workflow present
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `.devcontainer/` for dev environment; pre-commit hooks; `llms.txt` docs
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python project with test + devcontainer + docs
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Dual-deployment support (Cloud + Server/Data Center) with explicit version floors — Confluence v6.0+, Jira v8.14+ — signals deliberate enterprise-compatibility work
- 72-tool surface is large; no explicit tool-group selector flag surfaced in this research window (contrast with PayPal's `--tools=all` or Supabase's `features`)
- Community-owned canonical — 5k stars on a non-vendor repo for Atlassian suggests Atlassian has not shipped a first-party MCP and this is the de facto standard
- 171 open issues + 91 PRs indicates active maintenance but also backlog pressure at scale

## 18. Unanticipated axes observed
- Enterprise-scale support (on-prem Data Center plus Cloud) in a community MCP — a level of deployment-mode coverage uncommon outside first-party vendors
- `llms.txt` presence signals design-for-AI-consumption documentation pattern

## 19. Python-specific

### SDK / framework variant
- Both `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` pinned — uses FastMCP 2.x but also pins raw mcp for compatibility
- Import pattern: FastMCP-based (inferred)

### Python version floor
- `requires-python = ">=3.10"`

### Packaging
- build backend: `hatchling.build`
- lock file: present (uv project)
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `mcp-atlassian = "mcp_atlassian:main"`
- README host-config snippet: `"command": "uvx"`, `"args": ["mcp-atlassian"]` — clean uvx invocation

### Install workflow expected of end users
- `uvx mcp-atlassian` (primary), Docker, `pip`, or from source

### Async and tool signatures
- pytest-asyncio + pytest-anyio both present in dev — likely mix of asyncio and anyio async styles
- Source-level sync/async not inspected

### Type / schema strategy
- FastMCP-based schema auto-derivation likely; also uses raw mcp for lower-level needs

### Testing
- pytest + pytest-cov + pytest-asyncio + pytest-anyio
- Custom pytest markers: `integration`, `dc_e2e` (Data Center e2e), `cloud_e2e` (Cloud e2e) — separates deployment-mode test scopes
- ruff + black + mypy in dev group (double formatter — unusual)

### Dev ergonomics
- `.devcontainer/` for dev environment
- pre-commit hooks configured
- `llms.txt` — AI-consumption docs format

### Notable Python-specific choices
- Dual SDK (raw `mcp` + `fastmcp`) — likely historical: project predates FastMCP and migrated partially
- Test markers split by deployment topology (`dc_e2e` vs `cloud_e2e`) — encodes the on-prem/cloud matrix into the test suite rather than just CI config
- Both `black` and `ruff` in dev — redundant; `ruff format` typically replaces black in modern Python projects

## 20. Gaps
- Tool-scoping mechanism (if any) — how users reduce 72 tools to a working subset not extracted
- Exact OAuth 2.0 flow mechanics for Cloud
- Whether the server supports simultaneously Jira + Confluence or requires separate launches
- Transport selection mechanism details
