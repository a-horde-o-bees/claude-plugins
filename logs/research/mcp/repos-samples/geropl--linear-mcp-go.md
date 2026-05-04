# Sample

Mirrors of `https://github.com/geropl/linear-mcp-go`. Linear issue-tracker MCP server (Go) with read-only-by-default safety posture and a `setup` subcommand that automates host configuration. 11 stars, MIT, default branch `main`, v1.15.0 released Oct 8, 2025.

## Server runtime

### Go with mark3labs/mcp-go SDK

Go (98.6%) on `mark3labs/mcp-go` (canonical Go MCP SDK), Go 1.23+. Single-binary build artifact suiting cross-platform release-and-download distribution.

## Transport

### stdio

Default and only documented transport; selected via the `serve` subcommand.

### Selection mechanism

Subcommand verb — `./linear-mcp-go serve` selects stdio with no alternative transport offered.

## Capability surface

### Read/write tool split

Read-only tools (default): `linear_search_issues`, `linear_get_user_issues`, `linear_get_issue`, `linear_get_issue_comments`, `linear_get_teams`. Write tools (flag-gated behind `--write-access`): `linear_create_issue` (supports parent-child / sub-issues, labels), `linear_update_issue`, `linear_add_comment`, `linear_reply_to_comment`, `linear_update_issue_comment`. URL-aware operations — accepts Linear comment URLs directly without manual ID extraction.

### Domain-bundled tool set

10 tools total, organized by Linear's entity types (issues, comments, teams, users) with CRUD shape on each entity.

## Configuration delivery

### Environment variables

`LINEAR_API_KEY` (required) supplies the Linear credential.

### CLI flags

`--write-access` enables write tools; `--auto-approve` marks specific tools as safe to run without per-call confirmation; `--tool` selects the host the `setup` subcommand configures (e.g., `--tool=cline`).

## Authentication

### Static API key / token via env var

Linear API key supplied via `LINEAR_API_KEY` environment variable; user provisions it from Linear's API key management UI.

## Multi-tenancy

### Single-user / single-tenant per process

API key ties to one Linear workspace/user identity; one process serves one user.

## Distribution channel

### Pre-built binary release

GitHub Releases publishes pre-built binaries for Linux, macOS, and Windows; an automated download script in the README installs the binary.

### Go module via `go get` / `go install`

`go install` documented as an alternative install path.

### Docker / OCI image

Dockerfile present in repo for containerized deployment.

## Entry point and launch

### Subcommand verb

`./linear-mcp-go serve` (read-only default), `./linear-mcp-go serve --write-access` (with write), `./linear-mcp-go setup --tool=cline` (configures a target AI assistant), `./linear-mcp-go version`. The `setup` subcommand replaces manual JSON config editing — a rare ergonomic among MCP servers.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

### Devcontainer for contributors

`.devcontainer/` directory provides a dev environment.

## Test stack

### Recorded HTTP fixtures (cassettes)

go-vcr for recorded HTTP interactions; cassettes checked into `testdata/`. Live test workspace `linear.app/linear-mcp-go-test` for re-recording. Separate flags for re-record (`-record=true`) and write-op recording (`-recordWrites=true`) — full integration tests run offline against recorded fixtures, reproducible without Linear credentials.

### Go stdlib testing

Go's standard testing package drives the suite.

## CI

### GitHub Actions

GitHub Actions runs automated testing on pushes/PRs and automated releases on version tags.

## Host integration

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline (VSCode extension) is the primary integration with a dedicated `setup --tool=cline` subcommand.

### Smithery / Glama discovery

Reachable via MCP Registry; the `--tool` flag is a scoped extension point that signals planned automation for additional hosts.

## Repository layout

### Single-package source (language-conventional)

Single-package Go project — `cmd/` for command implementations, `pkg/` for core packages.

## Safety and security posture

### Read-only by default with explicit write flag

Read-only is the default; writes require explicit `--write-access`. More conservative than most MCPs, which ship full capabilities unconditionally.

### Per-tool auto-approve gating

`--auto-approve` flag lets users mark specific tools as safe to run without per-call confirmation, narrowing trust to declared tools.

## Release and lifecycle

### Tagged release with version in changelog

Versioning via constant with build-time injection (standard Go release pattern); v1.15.0 released Oct 8, 2025.

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Recent releases and active tagging cadence.

## Developer ergonomics

### Setup subcommands on the MCP binary

`setup` subcommand automates host configuration, replacing manual JSON config editing for the supported `--tool` targets.

### `scripts/` directory

`scripts/` directory holds build/utility scripts.

## Documentation surface

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`memory-bank/` directory holds context/memory files — author dogfoods Cline's memory-bank convention in their own workflow.
