# Sample

Mirrors of `https://github.com/teaguesterling/duckdb_mcp`. DuckDB-embedded MCP server — implemented as a native DuckDB extension invoked from SQL rather than as a standalone process. 47 stars, MIT, default branch `main`. v2.1.0 released March 28, 2026. Blurs database and tool-registry roles: SQL PRAGMAs control the server, SQL templates become first-class published tools, and `ATTACH` semantics let queries span multiple MCP-exposed data sources.

## Server runtime

### DuckDB extension (C++) embedding MCP

Native DuckDB extension built with CMake. C++ (73.7%), Shell (13.1%), Python (10.6%), small TS/JS/HTML. The "server" is the user's DuckDB session; tool calls and configuration originate from SQL statements (`PRAGMA mcp_server_start(...)`, `PRAGMA mcp_publish_tool(...)`). Custom hand-rolled MCP implementation; no third-party MCP SDK.

## Transport

### stdio

Stdio transport supported — selectable via `PRAGMA mcp_server_start(...)` parameters from SQL.

### Streamable HTTP

HTTP server mode with bearer-token auth; `/health` and `/mcp` endpoints surface remote access.

### MCP-client mode (server connects out)

Inverted role — the same artifact connects out to other MCP servers via SQL `ATTACH`, federating other MCP-exposed data sources into a unified SQL plane. Lets queries span the local server's tools plus attached upstream MCP servers' tools.

### Selection mechanism

SQL PRAGMA — server mode and transport parameters chosen from SQL inside the embedded extension. User issues `PRAGMA mcp_server_start(...)` with transport options as arguments.

## Capability surface

### Domain-bundled tool set

Built-in tools for query execution, table/schema description, listing, database introspection, export, DDL.

### User-publishable tools meta-tool

`PRAGMA mcp_publish_tool` registers a custom parameterized SQL query as a discoverable MCP tool with name, description, properties, required fields, and output format. SQL templates become first-class MCP tools at runtime.

## Configuration delivery

### SQL PRAGMA parameters

SQL PRAGMA calls with parameters (name, description, SQL template, properties, required fields, output format) are the primary config mechanism. JSON config file for HTTP/token settings.

### HTTP request headers

Bearer token in HTTP server mode read via Authorization headers.

## Authentication

### Bearer token via JSON config file

Bearer-token authentication in HTTP server mode; the bearer token is read from a JSON configuration file rather than env var or CLI flag — used because the embedded-extension model means env vars are awkward to thread through the host process.

## Multi-tenancy

### Single connection per server instance

Single-instance server keyed to the DuckDB database; no per-request tenant handling documented.

## Distribution channel

### Source build with make / CMake

`make` (build from source) is the only documented install. CMake-driven; no package-registry distribution observed (extension not yet in DuckDB community extensions per content fetched).

## Entry point and launch

### SQL PRAGMA invocation

User starts the server from inside a DuckDB session via `PRAGMA mcp_server_start()`. Tool publication via `PRAGMA mcp_publish_tool(...)`. The host process is the DuckDB CLI/library; the MCP server is a behavior toggled within it.

## Build and packaging

### Native build system (CMake / make)

CMake-based build invoked through `make`. Native C++ extension build pipeline.

## Test stack

### Native build-system test target

Tests under `/test`; `make test` invokes the CMake-based test target.

## CI

### GitHub Actions

`.github/workflows/` present; specifics not extracted within budget.

## Repository layout

### Single-package source (language-conventional)

Single-package DuckDB extension — `src/`, `examples/`, `test/`, CMake-based, with separate security audit docs.

## Observability

### Health endpoint

HTTP `/health` endpoint provides liveness probe.

## Host integration

### `.mcp.json` in project root

Claude Desktop integration via `.mcp.json` in project root.

## Developer ergonomics

### Examples directory with many patterns

6+ ready-to-use configs under `/examples`.

### Makefile / Makefile.toml

`make test` target plus other make-driven workflows.

## Documentation surface

### GitHub Pages / hosted docs site

ReadTheDocs documentation hosted alongside the repo.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Tagged release with version in changelog

v2.1.0 released March 28, 2026.

### Active development

Active project with v2.x line.
