# Sample

## Identification

### url

https://github.com/the-momentum/fhir-mcp-server

### stars

77

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

FHIR healthcare MCP server — embedded RAG stack (llama-index + huggingface + pinecone); in-server encrypted credential vault for PHI handling.

## Language and runtime

### language(s) + version constraints

Python 97%; `requires-python = ">=3.12"`.

### framework/SDK in use

FastMCP (standalone `fastmcp` package).

## Transport

### supported transports

stdio, http, https — selected via `TRANSPORT_MODE` env var.

### how selected

environment variable

## Distribution

### every mechanism observed

`make build` (Docker-based); `make uv` (uv-based install); clone required.

### published package name(s)

no PyPI publication documented

### install commands shown in README

`make build` or `make uv`

## Entry point / launch

### command(s) users/hosts run

`start.py` as entry; launched via Docker Compose or uv.

### wrapper scripts, launchers, stubs

console script `start` → `start:main` (via pyproject).

## Configuration surface

### how config reaches the server

`TRANSPORT_MODE` env var; FHIR backend URL + OAuth2 client ID/secret; optional encryption master key for sensitive fields.

## Authentication

### flow

OAuth2 client-credentials against the FHIR server; FHIR servers like Medplum mentioned as targets.

### where credentials come from

environment variables; the server also supports "encrypted credential storage with optional master key-based encryption for sensitive fields" — a server-internal credential vault.

## Multi-tenancy

### tenancy model

not addressed

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

14+ tools across FHIR resources (Patient, Observation, Condition, Medication, etc.), document management, LOINC terminology lookup.

## Observability

### logging destination + format, metrics, tracing, debug flags

not captured

## Host integrations shown in README or repo

### Claude Desktop

configured via `claude_desktop_config.json` example with Docker or uv launcher.

## Claude Code plugin wrapper

### presence and shape

none

## Tests

### presence, framework, location, notable patterns

pytest + pytest-asyncio + pytest-cov declared in dev deps; `.github` present.

## CI

### presence, system, triggers, what it runs

GitHub Actions present.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile + docker-compose.yml; volume mounting documented.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Makefile — `make build`, `make uv` as primary workflow entry. Uses `pre-commit`, `ruff`, `ty` for lint/type-check.

### pitfalls observed

Makefile-driven workflow — `make build`, `make uv`, `make test-connection`; common in data-ops projects but rare in MCP servers.

## Repo layout

### single-package / monorepo / vendored / other

single-package with `app/` module (build backend is `uv_build` with `module-name = "app"`).

## Notable structural choices

Three transport modes (stdio / http / https) selected via env var — among the richest transport surfaces in the sample.

FHIR-agnostic — not tied to a single FHIR server; connects to any FHIR-compliant backend (Medplum referenced as example).

Encrypted credential storage with master-key-based encryption — in-server credential vault, unusual among MCP servers; likely driven by HIPAA/PHI handling concerns.

`uv_build` backend with module name `app` — explicit non-standard module naming, matches `voska/hass-mcp` pattern.

LLM-assisted retrieval stack — depends on `llama-index` + `huggingface` embeddings + `pinecone` + `sentence-transformers` + `pymupdf`; the server embeds a full RAG pipeline for FHIR + document context.

Makefile-driven workflow — `make build`, `make uv`, `make test-connection`; common in data-ops projects but rare in MCP servers.

## Unanticipated axes observed

In-server RAG pipeline — the server embeds an embedding + vector-store + document-parsing stack inside an MCP server. Most MCP servers expose tools that call upstream RAG services; this one hosts the RAG itself. A server-boundary-blurring pattern.

Compliance-driven encryption features (master-key for sensitive credentials) — a distinct design axis emerging from regulated domains (healthcare, finance, legal).

Transport-mode env-var switch pattern for stdio/http/https — different from `awslabs.aws-api-mcp-server`'s CLI flag; env-var-driven transport selection is better suited to containerized deployments.

`uv_build` backend — less common than hatchling; shows the `uv` tool's build-backend integration is being adopted.

Healthcare-specific terminology service integration (LOINC) — the server bridges a domain-specific terminology ontology, a pattern that would reappear in legal (Westlaw taxonomies), education (curriculum standards), and finance (ticker/ISIN conventions).

## Python-specific

### SDK / framework variant

FastMCP standalone (2.x); `fastmcp` core dep, version not captured precisely; import pattern likely `from fastmcp import FastMCP`.

### Python version floor

`requires-python` value: `>=3.12`.

### Packaging

build backend: `uv_build` with `module-name = "app"` — unusual; shows adoption of `uv`'s native build backend. `.python-version` present; `uv.lock` implied. Version manager convention: `uv`.

### Entry point

console script `start = start:main` (entry at `start:main` — bare-module-name `start` rather than `app.start`). Host-config snippet shape: likely direct `uv run start` or script path inside Docker.

### Install workflow expected of end users

`make uv` or `make build`.

### Async and tool signatures

likely async (FastMCP 2.x + httpx + FastAPI).

### Type / schema strategy

Pydantic v2 (explicit dep) with pydantic-settings for config.

### Testing

pytest + pytest-asyncio + pytest-cov; fixture style not captured.

### Dev ergonomics

Makefile + pre-commit + ruff + ty (type checker alternative to mypy).

### Notable Python-specific choices

Heavy RAG stack: `llama-index`, `huggingface` embeddings, `pinecone`, `sentence-transformers`, `pymupdf`. `cryptography` + `passlib` for credential encryption. `fastapi` pulled in alongside `fastmcp` — likely for the HTTP transport surface. `greenlet` as a dep hints at sync/async bridging (SQLAlchemy-style patterns). `ty` type-checker (a newer alternative to `mypy`) — a small leading-edge signal.

## Gaps

what couldn't be determined: exact stars update time, complete tool surface, how the encryption master key is provisioned in practice, whether RAG components are optional or always active, LOINC terminology source.
