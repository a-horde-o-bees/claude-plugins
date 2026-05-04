# Sample

Mirrors of `https://github.com/sandraschi/email-mcp`. Email MCP server — SMTP/IMAP plus 10+ transactional-email APIs and 5 local-test servers and 4 webhook integrations behind a single tool surface; FastMCP 3.x; ships a separate Vite + Uvicorn web dashboard for monitoring; mixed Python + Rust packaging with `Cargo.toml` for MCPB signing. 1 star, MIT, default branch `master`. Last commit not extracted.

## Server runtime

### Python with FastMCP

Python on FastMCP 3.x — `fastmcp>=3.1.0,<4` in `pyproject.toml`, pinning to the 3.x major. Import pattern: `from fastmcp import FastMCP` (inferred). Tools are async with connection pooling per README; pytest-asyncio in test extras.

## Transport

### stdio

Stdio default; README emphasizes hardened stdout/stderr isolation for JSON-RPC correctness.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

6 core tools: `send_email`, `check_inbox`, `email_status`, `configure_service`, `list_services`, `email_help`. Optional tools include `suggest_email_subject` and `email_agentic_assist` (sampling). Many backends behind one interface — SMTP/IMAP (Gmail, Outlook, Yahoo, iCloud, ProtonMail), transactional APIs (SendGrid, Mailgun, Resend, Postmark, SES), local testing (MailHog, Mailpit, MailCatcher, Inbucket), webhooks (Slack, Discord, Telegram, GitHub).

### Tools plus prompts (no resources)

Ships at least one prompt (`email_compose_request`) alongside tools; no resources observed.

### Sampling and elicitation as client primitives

`email_agentic_assist` invokes MCP sampling.

## Configuration delivery

### Environment variables

Environment variables dominate — SMTP/IMAP servers/ports/credentials, per-provider API keys (SendGrid, Mailgun, Resend, Postmark, SES), local-testing flags, mailing-list file paths.

### Runtime reconfiguration tool

`configure_service()` tool reconfigures the active backend at runtime without process restart — runtime flexibility instead of restart-to-reload.

## Authentication

### Multi-provider credential bundles

Multi-backend credential bundle: SMTP/IMAP with app passwords; per-provider API keys for SendGrid, Mailgun, Resend, Postmark, SES; ProtonMail Bridge integration; webhook tokens. All credentials supplied via env vars per service; runtime overrides via `configure_service`. Dynamic service switching via tool call.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user — one set of mail credentials per process; multiple providers can be configured simultaneously and selected per send. Not designed for per-request tenancy.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published on PyPI as `email-mcp`; primary install command `uvx email-mcp`.

### MCPB bundle / Desktop Extension manifest

`.mcpb` bundle for Claude Desktop drag-and-drop install; `manifest.json` in repo. MCPB-first distribution stance.

### Zed extension

Zed editor extension supported.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `schip-mcp-email = "email_mcp.server:main"` — the `schip-mcp-email` console-script name does not match the package/distribution name `email-mcp`. README invocations: `uv run email-mcp` (dev), `uvx email-mcp` (ad-hoc).

### `uvx <package>`

Primary user invocation `uvx email-mcp`.

## Build and packaging

### Hatchling + uv (Python)

Build backend `hatchling.build`; lock file `uv.lock` present; version manager convention `uv`.

### `uv.lock` committed

`uv.lock` present in repo.

### Python version pinning

`requires-python = ">=3.12"`. CI matrix tests 3.10/3.11/3.12, looser than the requires-python floor (mismatch between declared floor and tested matrix).

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP 3.x auto-derives schemas from type hints; Annotated patterns likely (not directly verified).

### Async model (cross-cutting)

Async tools with connection pooling per README; pytest-asyncio in test extras.

## Container artifacts

### `.mcpbignore` for bundle packaging

MCPB is the packaging format; no Dockerfile present. `.mcpbignore`-style bundle packaging implied by MCPB layout.

### No container artifacts

No Dockerfile.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov in `test` extra. Separate `test` and `dev` extras. `pytest.ini` at root coexists with `pyproject.toml` (legacy dual-config pattern). `tests/` directory.

### MyPy strict + Bandit security scans alongside tests

CI runs Ruff (lint), MyPy (type), Bandit (security) alongside pytest; webapp uses Biome for the JS side.

## CI

### GitHub Actions

GitHub Actions configured.

### Build + test + supply-chain scan

CI runs the test matrix across Python versions plus linting (Ruff), type checking (MyPy), and security scanning (Bandit). Webapp side uses Biome.

## Host integration

### Claude Desktop

MCPB bundle with `manifest.json`.

### Cursor

`mcp.json` config file.

### Smithery / Glama discovery

`glama.json` for Glama discovery.

### Zed

Zed extension ships in repo.

### MCPB / DXT bundle manifest

`manifest.json` for the MCPB / Desktop Extension bundle.

## Observability

### Companion monitoring dashboard

Separate `monitoring/` directory with health + metrics; web dashboard built with Vite + Uvicorn on ports 10812/10813 for monitoring and control. Shipped in the same repo but not bundled into the MCP server itself.

### Suppressed stdout / discipline-only

Zero-tolerance `print` policy in core handlers to keep stdout clean for JSON-RPC.

## Repository layout

### Multi-directory single-repo (ancillary services)

Multi-directory single-repo with distinct concerns — `src/email_mcp/` (core), `mcp-server/` (packaging), `webapp/` (monitoring dashboard, Vite + Uvicorn), `monitoring/` (health/metrics), `tests/`, `examples/`, `scripts/`, `.github/workflows/`.

## Safety and security posture

### None / not surfaced

Author's "Industrial Quality Stack" / "SOTA 14.1" framing markets quality discipline but no specific safety posture is enforced beyond standard env-var credential handling.

## Developer ergonomics

### Justfile recipes

Justfile recipes for build/start operations.

### PowerShell + batch scripts

`build.ps1`, `start.ps1`, `build_mcpb.bat` — Windows-first dev posture.

### Linter and type-checker stack

Ruff + MyPy + Bandit (Python); Biome (webapp).

### Sample MCP client configs in repo

Per-host config samples shipped: `manifest.json`, `mcp.json`, `glama.json`.

### Examples directory with many patterns

`examples/` directory present.

## Documentation surface

### README as the canonical surface

README is the main documentation surface; per-host integration sections embed JSON snippets.

### Per-host README integration sections

README shows per-host config blocks for Claude Desktop, Cursor, Glama, Zed.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` directory; MCPB bundle targets Claude Desktop, not Claude Code plugin layout.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### MCPB bundle signing

`Cargo.toml` alongside `pyproject.toml` is attributed to MCPB bundle signing tooling.

### Active development

Heavy dev tooling investment; release cadence not extracted.
