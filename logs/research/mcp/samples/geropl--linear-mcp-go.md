# Sample

## Identification

### url

https://github.com/geropl/linear-mcp-go

### stars

11

### last-commit

v1.15.0 released Oct 8, 2025

### license

MIT

### default branch

main

### one-line purpose

Linear issue-tracker MCP server (Go) — pre-built binary releases on GitHub.

## Language and runtime

### language(s) + version constraints

Go 98.6%; Go 1.23+.

### framework/SDK in use

mcp-go (Model Context Protocol Go SDK, mark3labs/mcp-go canonical).

## Transport

### supported transports

stdio.

### how selected

Stdio default via `serve` subcommand.

## Distribution

### every mechanism observed

GitHub Releases pre-built binaries (Linux, macOS, Windows), automated download script, `go install`, Docker (Dockerfile present).

### published package name(s)

Binary `linear-mcp-go`.

### install commands shown in README

Binary download script; `go install`.

## Entry point / launch

### command(s) users/hosts run

`./linear-mcp-go serve` — read-only (default). `./linear-mcp-go serve --write-access` — with write. `./linear-mcp-go setup --tool=cline` — configures a target AI assistant. `./linear-mcp-go version`.

### wrapper scripts, launchers, stubs

`setup` subcommand automates host configuration; shell download script.

## Configuration surface

### how config reaches the server

`LINEAR_API_KEY` env var (required); CLI flags `--write-access`, `--auto-approve`, `--tool`.

## Authentication

### flow

Static API key via `LINEAR_API_KEY` env var.

### where credentials come from

User supplies from Linear's API key management UI.

## Multi-tenancy

### tenancy model

Single-user — API key ties to one Linear workspace/user identity.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Read-only (default): `linear_search_issues`, `linear_get_user_issues`, `linear_get_issue`, `linear_get_issue_comments`, `linear_get_teams`. Write (flag-gated): `linear_create_issue` (supports parent-child / sub-issues, labels), `linear_update_issue`, `linear_add_comment`, `linear_reply_to_comment`, `linear_update_issue_comment`. URL-aware operations — accepts Linear comment URLs directly without manual ID extraction.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not extracted within budget; Go stdio servers typically log to stderr.

### pitfalls observed

Logging destination and format not extracted.

## Host integrations shown in README or repo

### Cline

VSCode extension — primary, has dedicated `setup --tool=cline`.

### Other

reachable via MCP Registry; `--tool` flag extension point for more.

## Claude Code plugin wrapper

### presence and shape

Not observed.

## Tests

### presence, framework, location, notable patterns

go-vcr for recorded HTTP interactions; cassettes checked into `testdata/`; live test workspace `linear.app/linear-mcp-go-test` for re-recording; separate flags for re-record (`-record=true`) and write-op recording (`-recordWrites=true`).

## CI

### presence, system, triggers, what it runs

GitHub Actions — automated testing on pushes/PRs, automated releases on version tags.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; `.devcontainer/` for dev environment.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`setup` subcommand replaces manual JSON config editing; `scripts/` directory for build/utility; `memory-bank/` for context/memory files.

## Repo layout

### single-package / monorepo / vendored / other

Single-package Go project — `cmd/` for command implementations, `pkg/` for core packages.

## Notable structural choices

Read-only-by-default safety posture — writes gated behind explicit `--write-access` flag rather than being the default. `setup` subcommand as an official install ergonomic — rare among MCP servers; most expect users to hand-edit JSON. Auto-approve configurability — users can mark specific tools as safe to run without per-call confirmation. Rate-limited API calls respect Linear's limits. go-vcr cassette testing means full integration tests run offline against recorded fixtures — reproducible without Linear credentials. Versioning via constant with build-time injection — standard Go release pattern.

## Unanticipated axes observed

The `setup --tool` flag is a scoped extension point — currently only `cline`, but the flag's existence signals a plan to automate other host configurations. `memory-bank/` directory suggests author uses Cline's memory-bank convention in their own workflow — evidence of dogfooding. Read-only default + explicit write flag is a more conservative posture than most MCPs, which tend to ship full capabilities unconditionally.

## Gaps

Logging destination and format not extracted. Whether HTTP transport is planned or stdio is deliberate. Precise test coverage of write operations (recorded-writes flag suggests coverage exists but extent not extracted).
