# Sample

Mirrors of `https://github.com/jparkerweb/mcp-sqlite`. SQLite MCP server — schema exploration and parameterized SQL execution against a local SQLite file. 99 stars, MIT, default branch `main`.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript/JavaScript on Node.js 14.0.0+ using `@modelcontextprotocol/sdk ^1.12.1`. Uses `sqlite3` as the database driver.

## Transport

### stdio

Default and only transport documented; no transport selection mechanism surfaced in README.

## Capability surface

### Tools-only, hand-curated narrow surface

Hand-curated tool surface for database introspection, CRUD operations, and parameterized SQL query execution. Parameterized queries protect against SQL injection.

## Configuration delivery

### CLI flags

Database path passed as a positional CLI argument: `npx -y mcp-sqlite <database-path>`.

### Host-side JSON config snippet

IDE configuration via JSON (Cursor / VSCode `mcp.json`-style entries showing the npx command).

## Authentication

### None / implicit (local-resource gating)

No authentication; relies on local-file access semantics for the SQLite database.

## Multi-tenancy

### Single-user / single-tenant per process

One server instance per database file; single-user model.

## Distribution channel

### npm via npx / bunx

Published as `mcp-sqlite` on npm. README install command: `npx -y mcp-sqlite <database-path>` — direct npx invocation without intermediate config.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y mcp-sqlite <database-path>` is the canonical launch form. The package's `bin` field registers `mcp-sqlite-server` (CommonJS).

## Test stack

### MCP Inspector as test driver

`@modelcontextprotocol/inspector` invoked via `npm test` script — protocol-level end-to-end exercise rather than unit tests.

## Repository layout

### Single-package source (language-conventional)

Single npm package — `package.json`, README, `bin` entry. Conventional npm layout.

## Host integration

### Cursor

Documented integration via npx command in MCP config.

### VS Code / VS Code Insiders / Visual Studio family

Documented integration via npx command in MCP config.

## Developer ergonomics

### Inspector/debug tooling references

MCP Inspector integrated as the `npm test` driver; postinstall instructions reference Inspector for debugging.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
