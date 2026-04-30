# Sample

## Identification

### url

https://github.com/jparkerweb/mcp-sqlite

### stars

99

### last-commit

Not explicitly shown in GitHub UI

### license

MIT

### default branch

main

### one-line purpose

SQLite MCP server — schema exploration and SQL execution.

## Language and runtime

### language(s) + version constraints

TypeScript/JavaScript, Node.js 14.0.0+

### framework/SDK in use

MCP SDK (@modelcontextprotocol/sdk ^1.12.1), sqlite3

## Transport

### supported transports

stdio

### how selected

Default, no transport selection mechanism documented

## Distribution

### every mechanism observed

npm package (mcp-sqlite)

### published package name(s)

mcp-sqlite

### install commands shown in README

`npx -y mcp-sqlite <database-path>`

### pitfalls observed

Direct npx invocation without intermediate config

## Entry point / launch

### command(s) users/hosts run

`npx -y mcp-sqlite <database-path>`

### wrapper scripts, launchers, stubs

mcp-sqlite-server (CommonJS in package.json bin field)

## Configuration surface

### how config reaches the server

Database path as CLI argument, IDE configuration via JSON

## Authentication

### flow

None specified

### where credentials come from

Not applicable

## Multi-tenancy

### tenancy model

Single-user per database instance

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Database introspection, CRUD operations, SQL query execution with parameterized queries

## Observability

### logging destination + format, metrics, tracing, debug flags

MCP Inspector test script via npm test

## Host integrations shown in README or repo

### Cursor

npx command

### VSCode

npx command

## Claude Code plugin wrapper

### presence and shape

Not present in documentation

## Tests

### presence, framework, location, notable patterns

Present; MCP Inspector framework; npm test script

## CI

### presence, system, triggers, what it runs

Not documented

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not observed

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

MCP Inspector integrated as test; postinstall instructions

## Repo layout

### single-package / monorepo / vendored / other

Single npm package with package.json, README, bin entry

## Notable structural choices

Minimal dependencies (sqlite3 + MCP SDK only). Direct npx invocation without intermediate config. Parameterized query support for security.

## Unanticipated axes observed

CRUD-first design rather than query-focused like some competitors.

## Gaps

Last commit date not displayed in GitHub UI. CI/CD system not documented. HTTP transport alternative not documented.
