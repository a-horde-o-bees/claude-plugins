# Sample

## Identification

### url

https://github.com/sandraschi/email-mcp

### stars

1

### last-commit

Not explicitly extracted within budget.

### license

MIT

### default branch

master

### one-line purpose

Email MCP server — SMTP/IMAP plus transactional-email APIs; FastMCP 3.x; Cargo.toml alongside pyproject.toml for MCPB signing.

## 1. Language and runtime

### language(s) + version constraints

Python (46.9%) + web assets; Python 3.12+.

### framework/SDK in use

FastMCP 3.1.0+ (Python MCP framework).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio.

### how selected

Stdio default; README emphasizes hardened stdout/stderr isolation for JSON-RPC correctness.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI package (`uvx email-mcp`), MCPB bundle for Claude Desktop, Zed extension, GitHub clone.

### published package name(s)

`email-mcp`.

### install commands shown in README

`uv run email-mcp` (dev); `uvx email-mcp` (ad-hoc).

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`uv run email-mcp` or `uvx email-mcp`.

### wrapper scripts, launchers, stubs

PowerShell scripts (`build.ps1`, `start.ps1`); Justfile recipes for operations; entry point is `email_mcp.server` module.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variables dominate — SMTP/IMAP servers/ports/credentials, per-provider API keys, local-testing flags, mailing-list files; `configure_service()` tool for runtime (re)configuration without restart.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Multi-backend — SMTP/IMAP with app passwords, per-provider API keys (SendGrid, Mailgun, Resend, Postmark, SES), ProtonMail Bridge, webhook integrations. Dynamic service switching via tool call.

### where credentials come from

Environment variables per service; runtime overrides via `configure_service`.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single-user — one set of mail credentials per process, though multiple providers can be configured simultaneously and selected per-send. Not designed for per-request tenancy.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools (6 core): `send_email`, `check_inbox`, `email_status`, `configure_service`, `list_services`, `email_help`. Optional: `suggest_email_subject`, `email_agentic_assist` (sampling), prompts (`email_compose_request`), skills. Supported backends: SMTP/IMAP (Gmail, Outlook, Yahoo, iCloud, ProtonMail), transactional APIs (SendGrid, Mailgun, Resend, SES, Postmark), local testing (MailHog, Mailpit, MailCatcher, Inbucket), webhooks (Slack, Discord, Telegram, GitHub).

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Separate monitoring/ directory with health + metrics; web dashboard (Vite + Uvicorn on ports 10812/10813) for monitoring and control; zero-tolerance `print` policy in core handlers to keep stdout clean.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

MCPB bundle, `manifest.json`.

### Cursor IDE

`mcp.json`.

### Glama discovery

`glama.json`.

### Zed

Extension supported.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not explicitly observed — MCPB bundle targets Claude Desktop, not Claude Code plugin layout.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest (`pytest.ini` at root); `tests/` directory; multi-Python CI matrix (3.10/3.11/3.12).

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions — test matrix across Python versions, linting (Ruff), type checking (MyPy), security scanning (Bandit); webapp uses Biome.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

No Dockerfile; MCPB is the packaging format used.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Justfile recipes; PowerShell scripts; per-host config samples (`manifest.json`, `mcp.json`, `glama.json`); `examples/` directory.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Multi-directory single-repo with distinct concerns — `src/email_mcp/` core, `mcp-server/` packaging, `webapp/` monitoring dashboard, `monitoring/` health/metrics, `tests/`, `examples/`, `scripts/`, `.github/workflows/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Author's "Industrial Quality Stack" / "SOTA 14.1" framing — heavy investment in test/lint/security tooling for a personal project. Separate web dashboard (Vite + Uvicorn) as a monitoring companion, not bundled into MCP server but shipped in the same repo. Dynamic service reconfiguration via `configure_service` tool — runtime flexibility instead of restart-to-reload. Mailing-list presets via JSON files — bulk-send use case pre-wired. Multi-backend unified surface — the same `send_email` tool dispatches to SMTP or API providers based on configuration, hiding backend heterogeneity from the LLM caller.

## 18. Unanticipated axes observed

One of the more backend-rich servers surveyed — 10+ transactional providers + 5 local test servers + 4 webhook integrations all behind a single tool interface. Reference case for "many backends, one interface" MCP design. Zed editor integration is rarely seen — most servers target Claude Desktop and Cursor only. Author self-labels quality tiers; may be idiosyncratic marketing rather than signal of deeper engineering.

## 19. Python-specific

### SDK / framework variant

FastMCP 3.x — `fastmcp>=3.1.0,<4` in pyproject.toml (highest FastMCP floor in the sample); import pattern: FastMCP 3.x (`from fastmcp import FastMCP` inferred).

### Python version floor

`requires-python = ">=3.12"` — tied with crystaldba for highest in the sample. CI matrix: 3.10 / 3.11 / 3.12 (README claims — note the matrix is looser than requires-python).

### Packaging

Build backend: `hatchling.build`. Lock file: `uv.lock` present. Version manager convention: `uv`. Additional: `Cargo.toml` present (Rust side for MCPB packaging presumably).

### Entry point

`[project.scripts]`: `schip-mcp-email = "email_mcp.server:main"` — note the non-obvious `schip-mcp-email` name (not `email-mcp`). README run commands: `uv run email-mcp` (dev), `uvx email-mcp` (ad-hoc); MCPB drag-and-drop for Claude Desktop.

### Install workflow expected of end users

`uvx email-mcp` (primary), `.mcpb` bundle drag-and-drop, manual `claude_desktop_config.json` edit. Requires `uv` installed.

### Async and tool signatures

Tools are async with connection pooling (per README). pytest-asyncio in test extras.

### Type / schema strategy

FastMCP 3.x auto-derives; Annotated patterns likely (not confirmed).

### Testing

pytest + pytest-asyncio + pytest-cov in `test` extra. Separate `test` and `dev` extras. `pytest.ini` at root (alongside pyproject — legacy dual-config).

### Dev ergonomics

Justfile recipes (one of the few in the sample). PowerShell scripts (`build.ps1`, `start.ps1`, `build_mcpb.bat`) — Windows-first dev posture. Separate web dashboard built with Vite + uvicorn.

### Notable Python-specific choices

Mixed Python + Rust packaging — `Cargo.toml` alongside `pyproject.toml`, likely for MCPB bundle signing. Console script name `schip-mcp-email` does not match the package name `email-mcp` — unusual (most pyproject entries match package name). Python 3.12 floor is among the highest; CI matrix tests 3.10+ which mismatches the requires-python floor. Justfile for task running — very uncommon in MCP-server sample. MCPB-first distribution (Claude Desktop drag-and-drop) with `manifest.json` in repo.

## 20. Gaps

Last commit date and release cadence not extracted. Whether backends share a common abstraction internally or are per-provider adapters is not documented externally. Only 1 star — adoption is nascent; community validation is limited.
