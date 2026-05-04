# Sample

Mirrors of `https://github.com/AlwaysSany/deepl-fastmcp-python-server`. DeepL translation MCP server — translates, rephrases, batch-translates documents; detects language; keeps translation history and usage analytics locally. 4 stars, MIT, default branch `main`.

## Server runtime

### Python with FastMCP

Python server (97.3% Python in repo) built on FastMCP — likely 2.x given standalone-package install via `uv sync`. Import pattern likely `from fastmcp import FastMCP`. Version pin from pyproject.toml not surfaced in extract. Async handlers likely given multi-transport support.

## Transport

### stdio

Default transport; selectable via `--transport stdio`.

### Streamable HTTP

Selectable via `--transport http`; takes `--host` and `--port` args.

### SSE (Server-Sent Events)

Selectable via `--transport sse`. Three-transport support (stdio, SSE, Streamable HTTP) all in one binary, CLI-flag selectable — among the most complete transport surfaces observed for a small community server.

### Selection mechanism

CLI flag at startup — `--transport stdio|sse|http`, with `--host`, `--port` args.

## Capability surface

### Tools-only, hand-curated narrow surface

7 primary tools: `translate_text`, `rephrase_text`, `batch_translate`, `translate_document`, `detect_language`, `get_translation_history`, `analyze_usage_patterns`. No resources, prompts, or other primitives surfaced.

### Self-reflective analytics tool

`analyze_usage_patterns` and `get_translation_history` expose aggregated observations of the server's own past calls back to the LLM. Implies local persistence of call history (DB or file) — atypical of the otherwise-stateless MCP server pattern.

## Configuration delivery

### Environment variables

`DEEPL_AUTH_KEY` (required), `DEEPL_SERVER_URL` (optional, defaults to `https://api-free.deepl.com`).

### CLI flags

Transport, host, and port via CLI args (`--transport`, `--host`, `--port`).

## Authentication

### Static API key / token via env var

DeepL API key supplied via `DEEPL_AUTH_KEY` environment variable.

## Multi-tenancy

### Single-user / single-tenant per process

Not explicitly addressed in README; single API key per deployment implies single-user single-tenant.

## Distribution channel

### Source clone with editable install

`git clone ... && cd ... && uv sync` is the documented install path. No PyPI publication observed.

### Docker / OCI image

Dockerfile and `docker-compose.yml` present — supports containerized multi-transport deployment.

## Entry point and launch

### Bare interpreter + script path

`uv run python main.py --transport stdio` — bare `main.py` script with CLI arg handling parsed inside the script. No installable console script.

## Build and packaging

### Hatchling + uv (Python)

`uv sync`-managed; `uv.lock` implied. Build backend not directly captured. Version manager convention: `uv`.

### Python version pinning

`.python-version` present; `runtime.txt` references Python 3.13.3 — finer-grained than typical `>=3.12` constraints, an aggressive modern-Python target.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-style auto-derived schema from Python signatures (inferred from FastMCP usage, not directly captured).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root.

### Docker Compose for local dev

`docker-compose.yml` present, supporting SSE/HTTP transports' multi-container orchestration for development.

## Test stack

### pytest with async + coverage

`/tests` directory present; pytest framework not directly verified in extract.

## Repository layout

### Single-package flat layout

`main.py` at repo root with no installable console script — "hackable" community server layout.

## Documentation surface

### README as the canonical surface

Single README.md; integration details per host not captured.
