# Sample

## Identification

### url

https://github.com/JackKuo666/PubMed-MCP-Server

### stars

~108

### last-commit

13 commits (relatively small history, active at time of capture).

### license

MIT

### default branch

main

### one-line purpose

PubMed research-paper MCP server — keyword and advanced search, metadata retrieval, PDF download, and deep paper analysis.

## 1. Language and runtime

### language(s) + version constraints

Python, 3.10+ (`.python-version` file).

### framework/SDK in use

FastMCP (explicitly named in README).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (standard MCP server default).

### how selected

stdio-only implicit; README only shows Claude Desktop integration.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Source clone + `pip install -r requirements.txt`; Smithery CLI.

### published package name(s)

Not published to PyPI at time of research (no `pip install pubmed-mcp-server` shown).

### install commands shown in README

`git clone ... && pip install -r requirements.txt`; Smithery.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`python pubmed_server.py` or `python -m pubmed-mcp-server`.

### wrapper scripts, launchers, stubs

`smithery.yaml` for Smithery install.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Claude Desktop `claude_desktop_config.json` command/args — absolute path to `pubmed_server.py`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

None.

### where credentials come from

N/A — anonymous PubMed web access.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

5 tools — `search_pubmed_key_words`, `search_pubmed_advanced`, `get_pubmed_article_metadata`, `download_pubmed_pdf`, `deep_paper_analysis`.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Standard `logging` module.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON config snippets for macOS, Windows.

### Cline

Dedicated example.

### Smithery

`smithery.yaml` in repo root.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

None observed (despite "MseeP.ai Security Assessment Badge" shown on README).

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

No tests observed.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

`.github/` directory present; no workflow details surfaced.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop / Cline snippets; `smithery.yaml`.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Bare-script style — `pubmed_server.py` and `pubmed_web_search.py` at repo root; `pyproject.toml` and `requirements.txt` side by side.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Keeps both `pyproject.toml` and `requirements.txt` — redundant manifest; suggests the repo was bootstrapped from a requirements-driven template. Bare-script top-level layout rather than `src/<pkg>/` — lightweight but harder to package for PyPI.

## 18. Unanticipated axes observed

MCP server distributed via Smithery without ever being published to PyPI — the package manager path is optional when Smithery handles install.

## 19. Python-specific

### SDK / framework variant

FastMCP (not pinned explicitly in README). Version pin from pyproject.toml not surfaced. Import pattern: FastMCP per README.

### Python version floor

3.10+ (`.python-version` file).

### Packaging

Build backend unknown; no PyPI publication. Lock file: none (uses `requirements.txt`). Version manager convention: `.python-version` + `requirements.txt` (pyenv-style).

### Entry point

Bare script (`pubmed_server.py`). No console-script names. Host-config snippet shape: absolute path to `pubmed_server.py` via `python` command.

### Install workflow expected of end users

Source clone + `pip install -r requirements.txt`, or Smithery, or Docker. README one-liner: `git clone ... && cd PubMed-MCP-Server && pip install -r requirements.txt`.

### Async and tool signatures

Mentions `asyncio`; likely async.

### Type / schema strategy

FastMCP-derived (auto from type hints).

### Testing

None observed.

### Dev ergonomics

None explicit.

### Notable Python-specific choices

No PyPI publication, no console script — repository is distributed as code to clone, not as a package. Duplicate manifest files (`pyproject.toml` + `requirements.txt`) — unusual split.

## 20. Gaps

Exact FastMCP version pin not surfaced. Whether `pyproject.toml` defines any console scripts not confirmed. CI workflow content not read.
