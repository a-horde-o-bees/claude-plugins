# elastic/mcp-server-elasticsearch

## Identification
- url: https://github.com/elastic/mcp-server-elasticsearch
- stars: 646
- last-commit: April 18, 2026
- license: Apache-2.0
- default branch: main
- one-line purpose: Elasticsearch MCP server (deprecated) — Rust; Docker-only distribution.

## 1. Language and runtime
- language(s) + version constraints: Rust (94.3%); Rust 2024 edition
- framework/SDK in use: rmcp ^0.2.1 (Rust MCP SDK), tokio (async), axum (HTTP), elasticsearch ^9.0.0-alpha.1
- pitfalls observed:
  - exact Rust version not specified in Cargo.toml (only edition)

## 2. Transport
- supported transports: stdio, streamable-HTTP; SSE deprecated
- how selected: Docker environment or CLI args (`stdio` vs `http`)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Docker container (`docker.elastic.co/mcp/elasticsearch`)
- published package name(s): Docker image via AWS Marketplace and Elastic's container registry
- install commands shown in README: `docker run` with environment variables (`ES_URL`, `ES_API_KEY` or `ES_USERNAME`/`ES_PASSWORD`)
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `docker run ... stdio` or `docker run ... http`
- wrapper scripts: Docker entrypoint (implicit)
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: env vars — `ES_URL`, `ES_API_KEY` or `ES_USERNAME`+`ES_PASSWORD`, `ES_SSL_SKIP_VERIFY` (dev only)
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: `ES_API_KEY` or username/password for the Elasticsearch cluster
- where credentials come from: env vars passed to Docker container
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single Elasticsearch cluster connection; per-client MCP connection in HTTP mode
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools: `list_indices`, `get_mappings`, `search`, `esql` (ES|QL execution), `get_shards`
- resources: not explicitly documented (cluster metadata assumed)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging: container logs (stdout/stderr); health check at `/ping` (returns "pong")
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop (assumed MCP compatible), Cursor (assumed MCP compatible), Docker-based deployment (EC2, ECS, EKS)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- not present
- pitfalls observed: none noted in this repo

## 12. Tests
- present; `tests/` directory
- pitfalls observed: none noted in this repo

## 13. CI
- present; `.github/` (GitHub Actions) AND `.buildkite/` (Buildkite pipeline)
- pitfalls observed:
  - Buildkite + GitHub Actions CI (multi-platform testing)
  - Buildkite CI alongside GitHub Actions — axis: CI system diversity (not just GitHub)

## 14. Container / packaging artifacts
- Dockerfile (main), Dockerfile-8000 (alternative)
- `.dockerignore`
- multi-container deployment ready (EC2, ECS, EKS)
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- Docker Compose examples (implied)
- configuration examples via env vars
- pitfalls observed:
  - Makefile for build automation

## 16. Repo layout
- single-package Rust project
- dirs: `src/`, `tests/`, `docs/`, `scripts/`, `.buildkite/`, `.github/`
- config: `Cargo.toml`, `Cargo.lock`, `Makefile`, `rustfmt.toml`, `elastic-mcp.json5`
- additional: `catalog-info.yaml`, `renovate.json`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Rust implementation (performance, safety)
- container-first distribution (Docker only)
- Buildkite + GitHub Actions CI (multi-platform testing)
- Makefile for build automation
- explicit deprecation notice (superseded by Elastic Agent Builder in ES 9.2.0+)

## 18. Unanticipated axes observed
- Rust-native MCP server — rare axis value
- Buildkite CI alongside GitHub Actions — axis: CI system diversity (not just GitHub)
- explicit deprecation status in README (EOL, security updates only) — axis: declared lifecycle stage

## 20. Gaps
- exact Rust version not specified in Cargo.toml (only edition)
- test coverage and patterns not documented
- migration path to Elastic Agent Builder not detailed
