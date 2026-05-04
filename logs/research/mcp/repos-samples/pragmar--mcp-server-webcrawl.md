# Sample

Mirrors of `https://github.com/pragmar/mcp-server-webcrawl`. Web crawler MCP server — content extraction over pre-captured crawler archives (ArchiveBox/HTTrack/InterroBot/Katana/SiteOne/WARC/wget); ships "prompt routines" as Markdown templates alongside tools. 39 stars, default branch `master`, v0.15.0 released Dec 7, 2025.

## Server runtime

### Python with raw MCP SDK

Python (95.2%); Python 3.10+; raw `mcp` Python SDK at `mcp>=1.3.0` (no fastmcp). Low-level MCP server API (inferred). README references Anthropic Claude Agent SDK conventions.

## Transport

### stdio

stdio is the standard transport for Claude Desktop integration.

### Selection mechanism

stdio default; `--interactive` flag selects a terminal REPL mode rather than a transport.

## Capability surface

### Tools-only, hand-curated narrow surface

Boolean fulltext search with field-specific queries (url, content, headers, type, status, id, size). Content filtering by type (html, img, pdf, video, etc.) and HTTP status. Extraction modes: markdown, snippet, regex, XPath. Thumbnail generation for image content. Multi-crawler format compatibility: ArchiveBox, HTTrack, InterroBot, Katana, SiteOne, WARC, wget.

### Tools + prompt routines (out-of-band)

"Prompt routines" — pre-authored Markdown prompts for autonomous tasks (SEO audits, 404 detection, performance analysis) shipped in the `prompts/` directory. A concept adjacent to skills but shipped as plain Markdown rather than as MCP prompts protocol resources. Encodes "how to use the server for SEO audits" as reusable content rather than forcing users to rediscover prompting patterns.

## Configuration delivery

### CLI flags

`--crawler`, `--datasrc`, `--interactive` are the CLI surface — no env vars or sidecar config observed.

## Authentication

### None / implicit (local-resource gating)

Reads local crawler archives on disk; no service auth required. Operates entirely on local archives — the server has no external service dependency, so authentication is implicit local-resource gating.

## Multi-tenancy

### Single-user / single-tenant per process

One data source per launch. Multiple crawler data sources would require multiple launches.

## Distribution channel

### PyPI via pip / pipx

`pip install mcp-server-webcrawl` is the only install path shown; package name `mcp-server-webcrawl` on PyPI. No uv/uvx/pipx/Docker mentioned — positioned for plain Python users rather than uv-native ecosystem.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `mcp-server-webcrawl = "mcp_server_webcrawl:main"`. Standard MCP mode: `mcp-server-webcrawl` (integrated with Claude Desktop). Interactive REPL: `mcp-server-webcrawl --interactive`. With crawler + data source: `mcp-server-webcrawl --crawler wget --datasrc /path/to/datasrc --interactive`.

## Build and packaging

### Setuptools (with `setup.py` or `setup.cfg`)

Build backend: `setuptools.build_meta`. Lock file: not observed (no `uv.lock` mentioned). Version manager convention: plain pip — no uv tooling.

## Schema and types

### Hand-authored tool schemas

Low-level MCP SDK — hand-authored schemas likely.

## Host integration

### Claude Desktop

Primary; documentation lists it as a requirement.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not observed.

## Documentation surface

### README plus docs directory

`sphinx/` for documentation build; `docs/` for guides.

## Developer ergonomics

### Inspector/debug tooling references

`--interactive` terminal REPL doubles as a debug surface — interactive querying available without running an MCP host or MCP Inspector.

## Repository layout

### Single-package, organized subdirectories

Single-package Python project — `docs/`, `prompts/`, `sphinx/`.

## Release and lifecycle

### Tagged release with version in changelog

v0.15.0 released Dec 7, 2025; specific license name not extracted (license file present in repo).
