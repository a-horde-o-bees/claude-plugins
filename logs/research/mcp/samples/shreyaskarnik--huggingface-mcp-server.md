# Sample

## Identification
- url: https://github.com/shreyaskarnik/huggingface-mcp-server
- stars: ~70
- last-commit (date or relative): not explicitly surfaced
- license: MIT
- default branch: main
- one-line purpose: Hugging Face Hub MCP server — all three MCP surfaces (tools + resources + prompts) with a custom `hf://` URI scheme.

## 1. Language and runtime
- language(s) + version constraints: Python; version via `.python-version` file
- framework/SDK in use: raw `mcp` Python SDK (not FastMCP)
- pitfalls observed:
  - Exact `.python-version` content not read

## 2. Transport
- supported transports: stdio (MCP default)
- how selected: stdio-only
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Smithery CLI (`@shreyaskarnik/huggingface-mcp-server`); source clone + `uv sync`
- published package name(s): not confirmed on PyPI; Smithery as primary distribution
- install commands shown in README: `npx -y @smithery/cli install @shreyaskarnik/huggingface-mcp-server --client claude`; `uv sync && uv run huggingface_mcp_server.py`
- pitfalls observed:
  - Whether PyPI publication exists not confirmed

## 4. Entry point / launch
- command(s) users/hosts run: `uv run huggingface_mcp_server.py`
- wrapper scripts, launchers, stubs: single script `huggingface_mcp_server.py`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables — `HF_TOKEN` optional
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: optional bearer token
- where credentials come from: `HF_TOKEN` env var (for higher rate limits and private-repo access)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tools — search/info on models, datasets, spaces, papers, collections; **prompts** — `compare-models`, `summarize-paper`; **resources** — custom `hf://` URI scheme
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not documented
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: macOS/Windows config paths
- Smithery: registered
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: not mentioned in README
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: not evident
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Claude Desktop JSON snippet
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: flat — main server file at root; `src/huggingface/` for helpers
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Read-only-only stance: README explicitly scopes to read-only access
- Custom `hf://` URI scheme exposed via MCP resources — one of few Python servers that use MCP's resource surface *and* prompts, not just tools
- Two MCP **prompts** shipped (`compare-models`, `summarize-paper`) — demonstrates MCP prompt feature rather than tool-only

## 18. Unanticipated axes observed
- decision dimensions this repo reveals: using all three MCP surfaces (tools + resources + prompts) in a single server, when most Python servers stick to tools only; explicit read-only contract as a security surface

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — raw `mcp` SDK
- version pin from pyproject.toml — not surfaced
- import pattern observed — `from mcp.server import Server` style

### Python version floor
- `requires-python` value — via `.python-version`; exact value not surfaced

### Packaging
- build backend — not surfaced (likely hatchling given uv convention)
- lock file present — uv-based (uv.lock likely)
- version manager convention — uv + `.python-version`

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — bare script (`huggingface_mcp_server.py`)
- actual console-script name(s) — none
- host-config snippet shape — `uv run <path>/huggingface_mcp_server.py`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — Smithery-first, then uv source clone; Docker
- one-liner the README recommends — Smithery install via `npx`

### Async and tool signatures
- sync `def` or `async def` — mix (MCP SDK accepts both)

### Type / schema strategy
- Pydantic via MCP SDK
- schema auto-derived from signatures

### Testing
- pytest / pytest-asyncio / unittest / none — none observed

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — MCP CLI via `mcp[cli]` implied

### Notable Python-specific choices
- Single-file server kept at repo root rather than packaged — common "hackable" pattern for community MCP servers
- Exposes MCP prompts — an underused MCP capability across the Python ecosystem

## 20. Gaps
- Whether PyPI publication exists not confirmed
- Exact `.python-version` content not read
- CI presence not verified
