# Sample

Mirrors of `https://github.com/elastic/mcp-server-elasticsearch`. Elasticsearch MCP server (deprecated, superseded by Elastic Agent Builder in ES 9.2.0+) — Rust on rmcp; Docker-only distribution; CI split across Buildkite and GitHub Actions. 646 stars, Apache-2.0, default branch `main`, last commit April 18, 2026.

## Server runtime

### Rust with rmcp / rust-mcp-sdk

Rust (94.3%) on `rmcp ^0.2.1` (Rust MCP SDK), `tokio` async runtime, `axum` for HTTP, `elasticsearch ^9.0.0-alpha.1`. Rust 2024 edition; exact Rust version not specified in `Cargo.toml` (only edition).

## Transport

### stdio

`docker run ... stdio` selectable.

### Streamable HTTP

`docker run ... http` selectable.

### SSE (Server-Sent Events)

SSE supported but deprecated.

### Selection mechanism

Container ARG/CMD — Docker entrypoint takes `stdio` or `http` as a positional argument so the user picks at `docker run` time. Natural since the server is container-only.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools — `list_indices`, `get_mappings`, `search`, `esql` (ES|QL execution), `get_shards`. Resources not explicitly documented (cluster metadata assumed).

## Configuration delivery

### Environment variables

`ES_URL`, `ES_API_KEY` or `ES_USERNAME` + `ES_PASSWORD`, `ES_SSL_SKIP_VERIFY` (dev only) — passed into the Docker container.

### Sidecar config files (JSON / YAML / TOML / EDN)

`elastic-mcp.json5` sidecar config file at repo root — JSON5 variant (allows comments and trailing commas) consumed by the server alongside env-var-driven configuration.

## Authentication

### Static API key / token via env var

`ES_API_KEY` against the Elasticsearch cluster — typical static-key path.

### Database connection string

Username/password authentication against the Elasticsearch cluster via `ES_USERNAME` + `ES_PASSWORD`.

## Multi-tenancy

### Multi-client sharing one process via session multiplexing

Single Elasticsearch cluster connection; per-client MCP connection in HTTP mode.

## Distribution channel

### Docker / OCI image

Container-first distribution — Docker is the only shipping channel. Image at `docker.elastic.co/mcp/elasticsearch`. Distributed via AWS Marketplace and Elastic's container registry.

## Entry point and launch

### Docker container entrypoint

`docker run ... stdio` or `docker run ... http`. Implicit Docker entrypoint.

## Build and packaging

### Cargo (Rust)

Standard Rust build via `Cargo.toml`/`Cargo.lock`. `Makefile` for build automation; `rustfmt.toml` for formatting.

## Test stack

### Cargo test / cargo-nextest (Rust)

`tests/` directory present. Framework and patterns not documented beyond directory presence.

### `make test` targets

Build automation routed through a `Makefile`.

## CI

### GitHub Actions

`.github/` (GitHub Actions) workflows present.

### Multi-system CI

CI is split across Buildkite (`.buildkite/`) and GitHub Actions for multi-platform coverage.

### Renovate / Changeset tooling

`renovate.json` for dependency automation.

## Container artifacts

### Multi-Dockerfile (prod / dev split)

`Dockerfile` (main), `Dockerfile-8000` (alternative tuned for specific port conventions), `.dockerignore`. Multi-container deployment ready (EC2, ECS, EKS).

### Vendor-namespaced image

Image lives at `docker.elastic.co/mcp/elasticsearch` rather than the public `mcp/*` namespace.

## Deployment topology

### Published container image (artifact = image)

EC2, ECS, EKS deployment targets called out in README; the unit of deployment is the published container image at Elastic's vendor registry.

## Observability

### Container logs (stdout/stderr)

Container logs from stdout/stderr.

### Health endpoint

`/ping` health check returning "pong".

## Host integration

### Claude Desktop

Listed as MCP-compatible (assumed).

### Cursor

Listed as MCP-compatible (assumed).

## Repository layout

### Single Rust crate

Single-package Rust project. Directories: `src/`, `tests/`, `docs/`, `scripts/`, `.buildkite/`, `.github/`. Config: `Cargo.toml`, `Cargo.lock`, `Makefile`, `rustfmt.toml`, `elastic-mcp.json5`. Additional: `catalog-info.yaml`, `renovate.json`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Dated deprecation in repo

README carries an explicit deprecation notice — the project is superseded by Elastic Agent Builder in ES 9.2.0+. Lifecycle stage explicitly declared (EOL, security updates only).
