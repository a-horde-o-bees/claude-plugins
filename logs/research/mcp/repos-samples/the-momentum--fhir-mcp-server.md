# Sample

Mirrors of `https://github.com/the-momentum/fhir-mcp-server`. FHIR healthcare MCP server — embedded RAG stack (llama-index + huggingface + pinecone) inside the server; in-server encrypted credential vault for PHI handling. 77 stars, MIT, default branch `main`. FHIR-agnostic (Medplum referenced as example backend). The server embeds a full RAG pipeline rather than calling out to an external retrieval service — a server-boundary-blurring pattern driven by regulated-domain (HIPAA/PHI) requirements.

## Server runtime

### Python with FastMCP

Python 97% (`requires-python = ">=3.12"`); FastMCP standalone (2.x), `fastmcp` core dep. Import pattern likely `from fastmcp import FastMCP`. Async handlers likely (FastMCP 2.x + httpx + FastAPI). `fastapi` pulled in alongside `fastmcp` — likely for the HTTP transport surface. `greenlet` as a dep hints at sync/async bridging (SQLAlchemy-style patterns).

## Transport

### stdio

Stdio transport — selected via `TRANSPORT_MODE` env var.

### Streamable HTTP

HTTP transport — selected via `TRANSPORT_MODE` env var.

### HTTP with JSON response mode

HTTPS variant — selected via `TRANSPORT_MODE` env var. Three transport modes (stdio / http / https) selected via env var.

### Selection mechanism

Environment variable — `TRANSPORT_MODE` selects stdio/http/https. Container-friendly because env vars are the natural Docker/Kubernetes config surface.

## Capability surface

### Domain-bundled tool set

14+ tools across FHIR resources (Patient, Observation, Condition, Medication, etc.), document management, LOINC terminology lookup.

### Embedded RAG / retrieval pipeline

Server bundles `llama-index` + `huggingface` embeddings + `pinecone` + `sentence-transformers` + `pymupdf` for in-process embedding, vector storage, and document parsing. Tool calls run inference and similarity search inside the server rather than delegating to an external RAG service. Provides domain-aware retrieval for FHIR + document context the upstream doesn't pre-index.

## Configuration delivery

### Environment variables

`TRANSPORT_MODE` env var; FHIR backend URL + OAuth2 client ID/secret; optional encryption master key for sensitive fields.

## Authentication

### OAuth 2.0 client credentials

OAuth2 client-credentials flow against the FHIR server; no browser/user consent step. FHIR servers like Medplum mentioned as targets. Credentials supplied via env vars.

### In-server encrypted credential vault

Server supports encrypted credential storage with optional master-key-based encryption for sensitive fields — an in-server credential vault driven by HIPAA/PHI handling concerns. Master-key provisioning mechanics not documented in detail.

## Multi-tenancy

### Single-user / single-tenant per process

Tenancy not addressed; single OAuth2 client-credentials pair per process implies single-tenant.

## Distribution channel

### Source clone with editable install

Clone required; `make uv` is the uv-based install path.

### Docker / OCI image

`make build` (Docker-based) install path. Dockerfile + docker-compose.yml shipped.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `start = start:main` declared in pyproject — bare-module-name `start` rather than `app.start`. Host-config snippet shape: likely direct `uv run start` or script path inside Docker.

### Make targets in repo

`make build` and `make uv` are the documented install/launch entry points; `make test-connection` for upstream-reachability check.

## Build and packaging

### uv_build backend (Python)

Build backend: `uv_build` with `module-name = "app"` — non-standard module-name. Adoption of uv's native build backend rather than hatchling.

### Python version pinning

`requires-python = ">=3.12"`. `.python-version` present; `uv.lock` implied.

### `uv.lock` committed

uv-managed lockfile; uv is the version manager convention.

## Schema and types

### Pydantic v2 models

Pydantic v2 (explicit dep) with `pydantic-settings` for config.

### Async model (cross-cutting)

Async throughout — FastMCP 2.x with httpx + FastAPI; `greenlet` dep hints at sync/async bridging for SQLAlchemy-style upstream patterns.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

### Docker Compose for local dev

`docker-compose.yml` present; volume mounting documented.

## Test stack

### pytest with async + coverage

`pytest` + `pytest-asyncio` + `pytest-cov` declared in dev deps.

### Linter/formatter test gate

`ruff` + `ty` (type checker alternative to mypy) for lint/type-check — `ty` is a newer alternative to `mypy`, a small leading-edge signal.

## CI

### GitHub Actions

GitHub Actions present.

## Repository layout

### Single-package src-layout

Single-package with `app/` module — build backend is `uv_build` with `module-name = "app"`.

## Domain logic and embedded intelligence

### Embedded RAG / retrieval pipeline

The server hosts the RAG pipeline rather than exposing tools that call an upstream RAG service — `llama-index` + `huggingface` + `pinecone` + `sentence-transformers` + `pymupdf` all in-process.

### Domain-specific terminology service integration

Healthcare-specific terminology service integration (LOINC) — the server bridges a domain-specific terminology ontology alongside the primary FHIR API.

## Host integration

### Claude Desktop

`claude_desktop_config.json` example with Docker or uv launcher.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile-driven workflow — `make build`, `make uv`, `make test-connection` as primary entry points.

### `pre-commit` framework

`pre-commit` configured.

### Linter and type-checker stack

`ruff` + `ty` — `ty` is a newer type-checker alternative to mypy.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Active development

Active project; last-commit date not captured.
