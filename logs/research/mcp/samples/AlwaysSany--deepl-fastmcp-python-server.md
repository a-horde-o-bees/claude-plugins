# Sample

## Identification

### url

https://github.com/AlwaysSany/deepl-fastmcp-python-server

### stars

4

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

DeepL translation MCP server — translate, rephrase, batch-translate documents; detect language; keep translation history and usage analytics locally.

## 1. Language and runtime

### language(s) + version constraints

Python 97.3%; `.python-version` present, `runtime.txt` references Python 3.13.3.

### framework/SDK in use

FastMCP (likely 2.x given standalone-package install).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default); SSE (Server-Sent Events); Streamable HTTP — all three selectable at launch.

### how selected

`--transport stdio|sse|http` CLI flag; `--host`, `--port` args.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

clone + `uv sync`; Docker (Dockerfile + docker-compose.yml).

### published package name(s)

no PyPI publication documented

### install commands shown in README

`git clone ... && cd ... && uv sync`; Docker / compose (compose file present).

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`uv run python main.py --transport stdio`

### wrapper scripts, launchers, stubs

bare `main.py` script with CLI arg handling

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

env vars — `DEEPL_AUTH_KEY` (required), `DEEPL_SERVER_URL` (optional, defaults to `https://api-free.deepl.com`); transport + host/port via CLI args.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

DeepL API key

### where credentials come from

`DEEPL_AUTH_KEY` env var

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

not addressed — likely single-user (single API key per deployment).

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools — 7 primary: `translate_text`, `rephrase_text`, `batch_translate`, `translate_document`, `detect_language`, `get_translation_history`, `analyze_usage_patterns`.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not captured

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

Not captured per host in extract.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`/tests` directory present; CI details not captured.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

not captured

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile + docker-compose.yml — supports containerized multi-transport deployment.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

CLI arg design for transport/host/port selection.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`main.py` at root); no installable console script.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- Three-transport support (stdio, SSE, Streamable HTTP) all in one binary, CLI-flag selectable — one of the most complete transport surfaces observed among small community servers
- Bare-script entry like `labeveryday/mcp_pdf_reader`, but with CLI arg handling built in — a middle tier between "script + no args" and "console-script + click"
- `docker-compose.yml` present — SSE/HTTP transports motivate multi-container orchestration patterns
- Python 3.13.3 floor in `runtime.txt` — aggressive modern-Python target
- History and analytics tools — `get_translation_history`, `analyze_usage_patterns` suggest local persistence of past calls, unusual for a translation server

## 18. Unanticipated axes observed

- Transport polyglot — stdio + SSE + streamable-http in one binary reveals a design axis where a small community server exceeds the transport breadth of some vendor-authored servers
- History persistence inside an MCP server — most MCP servers are stateless; a translation history implies a local store (DB? file?) not typical of the sample
- Analytics-as-tool — `analyze_usage_patterns` exposes aggregated self-observations back to the LLM, suggesting a reflection-style capability

## 19. Python-specific

### SDK / framework variant

FastMCP (standalone package, likely 2.x). Version pin from pyproject.toml not captured precisely. Import pattern likely `from fastmcp import FastMCP`.

### Python version floor

`requires-python` not extracted from pyproject; `runtime.txt` pins 3.13.3.

### Packaging

Build backend not extracted. Lock file `uv.lock` implied (`uv sync`). Version manager convention: `uv`.

### Entry point

Bare script (`main.py`) with CLI args parsed inside the script. No console script. Host-config snippet: `uv run python main.py --transport stdio`.

### Install workflow expected of end users

`git clone ... && uv sync`

### Async and tool signatures

likely async given multi-transport support

### Type / schema strategy

FastMCP-auto-derived (not captured directly)

### Testing

`/tests/` directory present

### Dev ergonomics

docker-compose for multi-transport dev

### Notable Python-specific choices

- Python 3.13.3 specific pin in `runtime.txt` — finer-grained than typical `>=3.12` constraints
- Script-only server + Docker — a "dev-tier" distribution for a library with a lot of transport flexibility

## 20. Gaps

pyproject details, license placement, test framework specifics, whether Streamable HTTP uses MCP's new transport spec or a local variant, how translation history is persisted.
