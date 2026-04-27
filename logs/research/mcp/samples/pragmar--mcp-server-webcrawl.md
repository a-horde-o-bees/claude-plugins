# Sample

## Identification
- url: https://github.com/pragmar/mcp-server-webcrawl
- stars: 39
- last-commit (date or relative): v0.15.0 released Dec 7, 2025
- license: Present in repo (specific license not extracted within budget)
- default branch: master
- one-line purpose: Web crawler MCP server — content extraction with 'prompt routines' as a shipped capability alongside tools.

## 1. Language and runtime
- language(s) + version constraints: Python (95.2%); Python 3.10+
- framework/SDK in use: Model Context Protocol Python SDK; Anthropic Claude Agent SDK conventions
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected (flag, env, separate entry, auto-detect, etc.): Stdio default for Claude Desktop integration; `--interactive` flag for terminal REPL mode
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI
- published package name(s): mcp-server-webcrawl
- install commands shown in README: `pip install mcp-server-webcrawl`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run:
  - Standard MCP mode: `mcp-server-webcrawl` (integrated with Claude Desktop)
  - Interactive REPL: `mcp-server-webcrawl --interactive`
  - With crawler + data source: `mcp-server-webcrawl --crawler wget --datasrc /path/to/datasrc --interactive`
- wrapper scripts, launchers, stubs: PyPI console entry point
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI flags — `--crawler`, `--datasrc`, `--interactive`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Not applicable — reads local crawler archives on disk, no service auth
- where credentials come from: Not applicable
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user — one data source per launch. Multiple crawler data sources would require multiple launches
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other:
  - Boolean fulltext search with field-specific queries (url, content, headers, type, status, id, size)
  - Content filtering by type (html, img, pdf, video, etc.) and HTTP status
  - Extraction modes: markdown, snippet, regex, XPath
  - Thumbnail generation for image content
  - Multi-crawler format compatibility: ArchiveBox, HTTrack, InterroBot, Katana, SiteOne, WARC, wget
  - "Prompt routines" — pre-authored Markdown prompts for autonomous tasks (SEO audits, 404 detection, performance analysis)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: `--interactive` terminal mode doubles as a debug surface; explicit logging destination not extracted
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop (primary; documentation lists it as a requirement)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Not extracted — specific test config not visible in content
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: Not extracted
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not observed
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `--interactive` REPL; `prompts/` directory with reusable prompt routines; `sphinx/` for documentation; `docs/` for guides
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python project — `docs/`, `prompts/`, `sphinx/`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Reads existing crawler archives rather than crawling live — the server operates on pre-captured data, which sidesteps rate-limit, politeness, and JS-rendering concerns. Reference case for "don't crawl inside MCP, index what the user crawled"
- Seven-crawler format compatibility is unusually broad — most crawler tools target one format; this server abstracts across the ecosystem
- "Prompt routines" as a distribution surface — ships Markdown prompt templates alongside the tool surface. Encodes "how to use the server for SEO audits" as reusable content rather than forcing users to rediscover prompting patterns
- `--interactive` terminal mode for debugging is rare; most MCP servers assume stdio-only operation and expect MCP Inspector for interactive debugging

## 18. Unanticipated axes observed
- "Prompt routines" — a concept adjacent to skills but shipped as plain Markdown rather than as MCP prompts protocol resources. Structural reference for "how to package guided prompts with an MCP server"
- Non-OAuth, non-API-key auth posture — operates entirely on local archives — unusual among MCPs surveyed and demonstrates that valid MCP servers need not talk to external services at all
- Small star count (39) but focused niche; canonical for multi-crawler archive search

## 19. Python-specific

### SDK / framework variant
- Raw `mcp` Python SDK — `mcp>=1.3.0`; no fastmcp
- Import pattern: low-level MCP server API (inferred)

### Python version floor
- `requires-python = ">=3.10"`

### Packaging
- build backend: `setuptools.build_meta` — setuptools, not hatchling
- lock file: not observed (no uv.lock mentioned)
- version manager convention: plain pip

### Entry point
- `[project.scripts]`: `mcp-server-webcrawl = "mcp_server_webcrawl:main"`
- README install command: `pip install mcp-server-webcrawl`; interactive REPL via `mcp-server-webcrawl --interactive`

### Install workflow expected of end users
- `pip install mcp-server-webcrawl` (only install path shown)
- No uv/uvx/pipx/Docker mentioned

### Async and tool signatures
- Not inspected at source level; `mcp>=1.3.0` low-level SDK usually async
- No pytest-asyncio observed

### Type / schema strategy
- Low-level MCP SDK — hand-authored schemas likely

### Testing
- No pytest config or dev extras declared in pyproject.toml
- Test framework and CI details not extracted

### Dev ergonomics
- `sphinx/` directory for documentation build
- `--interactive` REPL mode is a custom debug surface — unusual among MCP servers that typically rely on MCP Inspector

### Notable Python-specific choices
- Setuptools backend — contrarian vs the hatchling-dominated sample
- No dev/test extras in pyproject.toml — minimal packaging posture
- pip-only install instructions (no uv/uvx) — positioned for plain Python users rather than uv-native ecosystem

## 20. Gaps
- Test framework and CI details not extracted
- License specific name (MIT/Apache/etc.) not extracted
- Whether the archive data format is auto-detected or user must specify `--crawler` each time
