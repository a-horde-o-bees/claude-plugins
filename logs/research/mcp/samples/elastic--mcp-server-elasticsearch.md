# Sample

## Identification

### url

https://github.com/elastic/mcp-server-elasticsearch

### stars

646

### last-commit

April 18, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

Elasticsearch MCP server (deprecated) — Rust; Docker-only distribution.

## Language and runtime

### language(s) + version constraints

Rust (94.3%); Rust 2024 edition. Exact Rust version not specified in `Cargo.toml` (only edition).

### framework/SDK in use

`rmcp ^0.2.1` (Rust MCP SDK), `tokio` (async), `axum` (HTTP), `elasticsearch ^9.0.0-alpha.1`.

## Transport

### supported transports

stdio and streamable-HTTP. SSE is deprecated.

### how selected

Docker environment or CLI args (`stdio` vs `http`).

## Distribution

### every mechanism observed

Docker container only — `docker.elastic.co/mcp/elasticsearch`.

### published package name(s)

Docker image distributed via AWS Marketplace and Elastic's container registry.

### install commands shown in README

`docker run` with environment variables (`ES_URL`, `ES_API_KEY` or `ES_USERNAME` / `ES_PASSWORD`).

## Entry point / launch

### command(s) users/hosts run

`docker run ... stdio` or `docker run ... http`.

### wrapper scripts, launchers, stubs

Docker entrypoint (implicit).

## Configuration surface

### how config reaches the server

Environment variables — `ES_URL`, `ES_API_KEY` or `ES_USERNAME` + `ES_PASSWORD`, `ES_SSL_SKIP_VERIFY` (dev only).

## Authentication

### flow

`ES_API_KEY` or username/password against the Elasticsearch cluster.

### where credentials come from

Environment variables passed into the Docker container.

## Multi-tenancy

### tenancy model

Single Elasticsearch cluster connection; per-client MCP connection in HTTP mode.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools — `list_indices`, `get_mappings`, `search`, `esql` (ES|QL execution), `get_shards`. Resources not explicitly documented (cluster metadata assumed).

## Observability

### logging destination + format, metrics, tracing, debug flags

Container logs (stdout/stderr); health check at `/ping` (returns "pong").

## Host integrations shown in README or repo

### Claude Desktop

Listed as MCP-compatible (assumed).

### Cursor

Listed as MCP-compatible (assumed).

### Docker-based deployment

EC2, ECS, EKS deployment targets called out.

## Claude Code plugin wrapper

### presence and shape

Not present.

## Tests

### presence, framework, location, notable patterns

Present; `tests/` directory. Framework and patterns not documented.

## CI

### presence, system, triggers, what it runs

Present; both `.github/` (GitHub Actions) and `.buildkite/` (Buildkite pipeline) — multi-platform testing across two CI systems.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

`Dockerfile` (main), `Dockerfile-8000` (alternative), `.dockerignore`. Multi-container deployment ready (EC2, ECS, EKS).

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Docker Compose examples (implied), configuration examples via env vars, `Makefile` for build automation.

## Repo layout

### single-package / monorepo / vendored / other

Single-package Rust project. Directories: `src/`, `tests/`, `docs/`, `scripts/`, `.buildkite/`, `.github/`. Config: `Cargo.toml`, `Cargo.lock`, `Makefile`, `rustfmt.toml`, `elastic-mcp.json5`. Additional: `catalog-info.yaml`, `renovate.json`.

## Notable structural choices

Rust implementation chosen for performance and safety. Container-first distribution — Docker is the only shipping channel. CI is split across Buildkite and GitHub Actions for multi-platform coverage. Build automation routed through a `Makefile`. README carries an explicit deprecation notice — the project is superseded by Elastic Agent Builder in ES 9.2.0+.

## Unanticipated axes observed

Rust-native MCP server — a rare axis value across the corpus. Buildkite CI alongside GitHub Actions — CI system diversity beyond the GitHub-only assumption. Explicit declared lifecycle stage in README (EOL, security updates only) — a deprecation-status axis most repos don't surface.

## Gaps

Exact Rust version is not specified in `Cargo.toml` (only edition). Test coverage and patterns are not documented. Migration path to Elastic Agent Builder is not detailed.
