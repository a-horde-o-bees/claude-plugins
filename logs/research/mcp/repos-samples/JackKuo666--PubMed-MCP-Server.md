# Sample

Mirrors of `https://github.com/JackKuo666/PubMed-MCP-Server`. PubMed research-paper MCP server — keyword and advanced search, metadata retrieval, PDF download, and deep paper analysis. ~108 stars, MIT, default branch `main`, 13 commits at capture.

## Server runtime

### Python with FastMCP

Python server explicitly named as FastMCP in README. Python 3.10+ floor declared via a `.python-version` dotfile. Exact FastMCP version pin not surfaced in README. `asyncio` mentioned, suggesting async tool handlers. Bare-script style — `pubmed_server.py` and `pubmed_web_search.py` at repo root rather than `src/<package>/`.

## Transport

### stdio

stdio-only; implicit (no transport selection mechanism documented). README only shows Claude Desktop integration.

## Capability surface

### Tools-only, hand-curated narrow surface

5 tools — `search_pubmed_key_words`, `search_pubmed_advanced`, `get_pubmed_article_metadata`, `download_pubmed_pdf`, `deep_paper_analysis`. No resources, prompts, or other primitives.

## Configuration delivery

### Host-side JSON config snippet

Configuration via Claude Desktop `claude_desktop_config.json` — absolute path to `pubmed_server.py` passed via `python` command. No env vars or CLI flags surfaced (PubMed access is anonymous).

## Authentication

### None / implicit (local-resource gating)

No auth at the MCP layer. Anonymous PubMed web access — server fronts a public unauthenticated upstream.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user.

## Distribution channel

### Source clone with editable install

`git clone ... && cd PubMed-MCP-Server && pip install -r requirements.txt`. No PyPI publication at time of research (no `pip install pubmed-mcp-server` shown).

### Smithery registry

`smithery.yaml` in repo root for Smithery install — server distributed via Smithery without ever being published to PyPI.

### Docker / OCI image

Dockerfile present as a third install path.

## Entry point and launch

### Bare interpreter + script path

`python pubmed_server.py` (absolute path passed via Claude Desktop's `command`/`args`). No console-script entry registered; `pyproject.toml` script declarations not confirmed.

### Module invocation / `python -m <module>` fallback

`python -m pubmed-mcp-server` also surfaced as a launch form.

## Build and packaging

### Requirements-driven (legacy Python)

`requirements.txt` is the install contract; `pyproject.toml` also present. The redundant manifest pair (both `requirements.txt` and `pyproject.toml` co-located) suggests the repo was bootstrapped from a requirements-driven template.

### No lock file

Lock file absent — `requirements.txt` plays the pin role.

### Python version pinning

`.python-version` (pyenv-style) at repo root pins Python 3.10+.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-derived schemas from type hints (per README's framework declaration).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root.

## Test stack

### No tests / not surfaced

No tests observed.

## CI

### GitHub Actions

`.github/` directory present; specific workflow content not surfaced in README.

## Host integration

### Claude Desktop

JSON config snippets shown for macOS and Windows.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline-specific integration example provided.

### Smithery / Glama discovery

`smithery.yaml` in repo root.

## Observability

### Standard library `logging` (Python)

Standard `logging` module.

## Repository layout

### Bare-script layout

`pubmed_server.py` and `pubmed_web_search.py` at repo root with `pyproject.toml` and `requirements.txt` side by side. Lightweight but harder to package for PyPI.

## Safety and security posture

### MseeP.ai security badge

"MseeP.ai Security Assessment Badge" displayed on README.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.
