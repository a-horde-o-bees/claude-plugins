# Sample

Pass-1 Phase-1a partial for bin 11. Atomic knowledge chunks from rust-mcp-stack--rust-mcp-filesystem, sajal2692--mcp-weaviate, samuelgursky--davinci-resolve-mcp, sandraschi--email-mcp, severity1--terraform-cloud-mcp, shibuiwilliam--mcp-server-scikit-learn, shreyaskarnik--huggingface-mcp-server, slackapi--slack-mcp-plugin, organized by divergence axes. Phase-1b merger will unify with other partials.

## Language and runtime

### Implementation language

- Rust — `rust-mcp-sdk` + `rust-mcp-schema` libraries; version pinned via `rust-toolchain.toml` [`rust-mcp-stack--rust-mcp-filesystem`]
- Python — dominant choice in this bin; six of eight samples are Python servers [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Not applicable — remote HTTP service with no local code; the repo ships configs only [`slackapi--slack-mcp-plugin`]

### Python version floor

- 3.12+ explicitly — `requires-python = ">=3.12"` [`sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- 3.10–3.12 inclusive upper bound — driven by an external ABI dependency (DaVinci Resolve's Python scripting module is incompatible with 3.13+) [`samuelgursky--davinci-resolve-mcp`]
- Pinned via `.python-version` only — no explicit `requires-python` surfaced [`sajal2692--mcp-weaviate`, `shreyaskarnik--huggingface-mcp-server`]
- Not surfaced — README and packaging do not state a floor [`shibuiwilliam--mcp-server-scikit-learn`]

> Pitfall: a CI matrix that tests Python versions below `requires-python` is a self-inconsistency. `sandraschi--email-mcp` declares `requires-python = ">=3.12"` but tests 3.10/3.11/3.12 in CI.

### MCP framework / SDK variant

- FastMCP (Python) — Pydantic-backed auto-derivation of tool schemas [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`]
- FastMCP 3.x specifically — `fastmcp>=3.1.0,<4` is the highest FastMCP floor seen [`sandraschi--email-mcp`]
- Raw `mcp` Python SDK (not FastMCP) — `from mcp.server import Server` style [`samuelgursky--davinci-resolve-mcp` (presumed), `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Rust MCP libraries — `rust-mcp-sdk` + `rust-mcp-schema` [`rust-mcp-stack--rust-mcp-filesystem`]
- Remote MCP — no local SDK; protocol terminated server-side [`slackapi--slack-mcp-plugin`]

## Transport

### Transport set

- stdio only — by default or by explicit selection [`rust-mcp-stack--rust-mcp-filesystem` (inferred), `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- stdio + streamable-http — multi-transport server with CLI/env selection [`sajal2692--mcp-weaviate`]
- HTTP only — remote MCP endpoint at a fixed URL [`slackapi--slack-mcp-plugin`]

### How transport is selected

- CLI argument or env var [`sajal2692--mcp-weaviate`]
- Implicit (stdio-only build, no toggle) [most samples in this bin]
- HTTP URL configured at the client side [`slackapi--slack-mcp-plugin`]

### stdio hardening

- Explicit stdout/stderr isolation discipline — README emphasizes hardened stdout/stderr separation for JSON-RPC correctness; "zero-tolerance `print` policy" in core handlers to keep stdout clean [`sandraschi--email-mcp`]

## Distribution

### Distribution mechanism

- PyPI via `uvx` — primary one-liner install [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`]
- PyPI via `uv` (local install) [`severity1--terraform-cloud-mcp`]
- Source clone + editable install (`pip install -e ".[dev]"`) [`shibuiwilliam--mcp-server-scikit-learn`]
- Source clone + `uv sync` and run a script directly [`shreyaskarnik--huggingface-mcp-server`]
- Source-only with custom installer — no PyPI; bespoke `install.py` orchestrates venv and per-client config [`samuelgursky--davinci-resolve-mcp`]
- Smithery CLI — `npx -y @smithery/cli install <name> --client claude` [`shreyaskarnik--huggingface-mcp-server`]
- MCPB bundle (Claude Desktop drag-and-drop) [`sandraschi--email-mcp`]
- Zed extension [`sandraschi--email-mcp`]
- Docker image (Docker Hub MCP Registry / Dockerfile in repo) [`rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- Homebrew formula [`rust-mcp-stack--rust-mcp-filesystem`]
- Cargo crate — `cargo install rust-mcp-filesystem` [`rust-mcp-stack--rust-mcp-filesystem`]
- npm package — `@rustmcp/rust-mcp-filesystem` (Rust binary wrapped for npm distribution) [`rust-mcp-stack--rust-mcp-filesystem`]
- Shell installer / PowerShell installer [`rust-mcp-stack--rust-mcp-filesystem`]
- GitHub release binary downloads [`rust-mcp-stack--rust-mcp-filesystem`]
- Remote-hosted-only — no install at all; `git clone` is for config review only [`slackapi--slack-mcp-plugin`]

### Cross-ecosystem distribution

- A single Rust binary is shipped via Homebrew, Cargo, npm, Docker, GitHub releases, plus shell/PowerShell scripts — broadest distribution surface in this bin [`rust-mcp-stack--rust-mcp-filesystem`]

## Entry point / launch

### Launch shape

- Console script via `[project.scripts]` — `uvx <name>` or `uv run <name>` [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Bare script — `uv run <path>/<script>.py`, no console-script entry [`shreyaskarnik--huggingface-mcp-server`]
- Bare Python script with absolute paths — `python src/server.py` (no packaging entry point at all) [`samuelgursky--davinci-resolve-mcp`]
- Path-anchored `uv --directory=<path> run <name>` — implies the package isn't designed for pip-install-everywhere; designed for developer-installed local runs [`shibuiwilliam--mcp-server-scikit-learn`]
- Standalone binary — no interpreter; direct execution [`rust-mcp-stack--rust-mcp-filesystem`]
- No local entry point — remote HTTP only [`slackapi--slack-mcp-plugin`]

### Console script naming

- Matches package name — `mcp-weaviate`, `terraform-cloud-mcp`, `mcp-server-scikit-learn` [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Does NOT match package name — `[project.scripts]` entry is `schip-mcp-email` while the PyPI package is `email-mcp` [`sandraschi--email-mcp`]

> Pitfall: console-script name divergence from package name is unusual. Most pyproject entries match package name; mismatch surfaces in host-config snippets where users must know the script name not the install name.

### Host-config snippet shape

- `uvx <name>` — minimal, single argument [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`]
- `uv run <name>` — dev-style invocation surfaced in README [`sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- `uv --directory=<path> run <name>` — path-anchored [`shibuiwilliam--mcp-server-scikit-learn`]
- `uv run <path>/<script>.py` [`shreyaskarnik--huggingface-mcp-server`]
- Absolute venv-Python path + absolute script path — `"command": "/path/to/venv/bin/python", "args": ["/path/to/repo/src/server.py"]`. The cost of not publishing to PyPI: hosts must know both paths [`samuelgursky--davinci-resolve-mcp`]

## Configuration surface

### Config delivery channel

- Environment variables — credentials, endpoints, feature flags [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- CLI flags for mode selection (in addition to env) [`samuelgursky--davinci-resolve-mcp` (`--full` for tool-set choice)]
- MCP server JSON config (command/args) — no env config at all [`shibuiwilliam--mcp-server-scikit-learn`]
- Auto-generated per-client JSON config by an installer script [`samuelgursky--davinci-resolve-mcp`]
- Runtime reconfiguration via a tool call — `configure_service` switches backends without restart [`sandraschi--email-mcp`]
- Built-in feature toggles in the server itself — read-only by default; opt-in MCP Roots; CLI-driven tool disabling to reduce token usage [`rust-mcp-stack--rust-mcp-filesystem`]
- Client-side OAuth config — `clientId` / `callbackPort` shipped to consumers [`slackapi--slack-mcp-plugin`]

### Safety gating

- Single-axis read-only flag [`rust-mcp-stack--rust-mcp-filesystem`]
- Two-axis safety: `READ_ONLY_TOOLS` + separate `ENABLE_DELETE_TOOLS` (delete is treated as more dangerous than write and gets its own toggle) [`severity1--terraform-cloud-mcp`]
- Read-only-only stance — README explicitly scopes the entire server to read-only access [`shreyaskarnik--huggingface-mcp-server`]
- Tool disabling at the CLI to reduce surface area and prompt-token usage [`rust-mcp-stack--rust-mcp-filesystem`]
- Compound vs full tool-set as a launch flag — `--full` flips between 27 aggregate tools and 342 granular tools [`samuelgursky--davinci-resolve-mcp`]

## Authentication

### Auth flow

- API token via env var — single-tenant, single-token-per-process [`severity1--terraform-cloud-mcp` (`TFC_TOKEN`), `shreyaskarnik--huggingface-mcp-server` (optional `HF_TOKEN`)]
- Per-provider API keys — multi-backend dispatch (SendGrid, Mailgun, Resend, Postmark, SES, plus SMTP/IMAP app passwords, plus ProtonMail Bridge, plus webhooks) [`sandraschi--email-mcp`]
- Embedding-provider keys + cloud-service keys — OpenAI / Cohere / WCS [`sajal2692--mcp-weaviate`]
- OAuth 2.0 with workspace admin approval — callback-port flow [`slackapi--slack-mcp-plugin`]
- None — server talks to a local-only API or local-only data [`rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

### Optional vs required credentials

- Required — server cannot start without the credential [`severity1--terraform-cloud-mcp`]
- Optional bearer token for elevated capability — anonymous access works for public data; token unlocks rate limit and private data [`shreyaskarnik--huggingface-mcp-server`]

## Multi-tenancy

### Tenancy model

- Single-user — bound to one process / one credential [`rust-mcp-stack--rust-mcp-filesystem`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Per-workspace OAuth token — workspace admin scope; tenant boundary is the OAuth grant [`slackapi--slack-mcp-plugin`]
- Per-call tenancy as a tool argument — first-class multi-tenancy in tool signatures rather than server config [`sajal2692--mcp-weaviate`]

> Notable: `sajal2692--mcp-weaviate` calls out per-tenant search tools as a first-class MCP concept. Tenancy becomes an argument, not a server-config dimension. Rare across Python MCP servers in this bin.

## Capabilities exposed

### MCP surface coverage

- Tools only [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `slackapi--slack-mcp-plugin`]
- Tools + resources + prompts + sampling + skills — broadest surface in this bin (custom `email_compose_request` prompt, `email_agentic_assist` sampling tool) [`sandraschi--email-mcp`]
- Tools + resources + prompts — uses all three core MCP surfaces with a custom `hf://` URI scheme [`shreyaskarnik--huggingface-mcp-server`]
- Tools + MCP Roots (opt-in) [`rust-mcp-stack--rust-mcp-filesystem`]

> Notable: most Python servers in this bin stick to tools-only. Two samples (`sandraschi--email-mcp`, `shreyaskarnik--huggingface-mcp-server`) demonstrate prompts and resources, with the latter exposing a custom URI scheme via the resources surface.

### Tool count and design

- Small focused set — under 15 tools [`sajal2692--mcp-weaviate` (11), `sandraschi--email-mcp` (6 core)]
- Mid-range — 50+ tools [`severity1--terraform-cloud-mcp`]
- Two-mode design — compound (27 aggregate) vs full (342 granular); explicit context-window-vs-expressiveness trade [`samuelgursky--davinci-resolve-mcp`]
- 342 granular tools — among the largest tool surfaces seen; the dual-mode design exists specifically to counter context-window pressure [`samuelgursky--davinci-resolve-mcp`]

### Multi-backend unified surface

- One tool, many backends — `send_email` dispatches to SMTP or to an API provider based on configuration; backend heterogeneity is hidden from the LLM caller [`sandraschi--email-mcp`]

## Observability

### Logging / metrics

- Not documented [`rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Debug logging enabled by default; format/destination not surfaced [`severity1--terraform-cloud-mcp`]
- Separate monitoring directory + web dashboard (Vite + Uvicorn on ports 10812/10813) for health/metrics/control [`sandraschi--email-mcp`]
- Server-side only — telemetry lives on the hosted service, not in the repo [`slackapi--slack-mcp-plugin`]

## Host integrations

### Documented host integration count

- One host (Claude Desktop only) [`shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- A few hosts — Claude Desktop, Cursor, plus optionally Glama, Zed [`sandraschi--email-mcp`]
- Many hosts via universal installer — 10 MCP clients auto-configured in one pass [`samuelgursky--davinci-resolve-mcp`]
- Standard `claude mcp add` CLI registration alongside JSON `mcpServers` for desktop hosts [`severity1--terraform-cloud-mcp`]
- Two hosts shipped as configs — Claude Code + Cursor with separate plugin layouts [`slackapi--slack-mcp-plugin`]

### Host-specific config files

- `manifest.json` — MCPB / Claude Desktop bundle [`sandraschi--email-mcp`]
- `mcp.json` — Cursor [`sandraschi--email-mcp`]
- `glama.json` — Glama discovery [`sandraschi--email-mcp`]
- `.cursor-mcp.json` — Cursor (alternate location) [`slackapi--slack-mcp-plugin`]
- `.mcp.json` — Claude Code [`slackapi--slack-mcp-plugin`]
- `.claude-plugin/` directory — Claude Code plugin layout [`slackapi--slack-mcp-plugin`]
- `.cursor-plugin/` directory — Cursor plugin layout [`slackapi--slack-mcp-plugin`]

### Universal installer pattern

- Custom `install.py` walks every supported client and writes per-client JSON to that client's standard config location. Replaces both pip and uv roles. Flags `--clients`, `--dry-run`, `--no-venv`, `--full` [`samuelgursky--davinci-resolve-mcp`]

## Claude Code plugin wrapper

### Plugin presence

- None observed [most samples in this bin]
- Configs-only `.claude-plugin/` directory in a remote-hosted MCP — plugin layout used to ship configs, not server code [`slackapi--slack-mcp-plugin`]

## Tests

### Test framework

- pytest [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- pytest + pytest-asyncio + pytest-cov via a `test` extra [`sandraschi--email-mcp`]
- cargo-nextest [`rust-mcp-stack--rust-mcp-filesystem`]
- Custom 5-phase live suite — read-only / destructive / media / AI/ML / advanced; framework not surfaced; 319/324 methods live-tested with claimed 100% pass [`samuelgursky--davinci-resolve-mcp`]
- Not surfaced [`severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- Not applicable — config-only repo [`slackapi--slack-mcp-plugin`]

### Test layout

- `tests/` directory at repo root [`rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- `pytest.ini` at root alongside `pyproject.toml` — legacy dual-config [`sandraschi--email-mcp`]

## CI

### CI presence

- GitHub Actions [`rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Not evident [`shreyaskarnik--huggingface-mcp-server`]
- Not applicable [`slackapi--slack-mcp-plugin`]

### What CI runs

- fmt + clippy + test + check via Makefile.toml (cargo-make) [`rust-mcp-stack--rust-mcp-filesystem`]
- Multi-Python matrix (3.10/3.11/3.12) + Ruff + MyPy + Bandit; webapp linted with Biome [`sandraschi--email-mcp`]
- ruff + black + mypy [`severity1--terraform-cloud-mcp`]
- Details not surfaced beyond presence [`sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]

## Container / packaging artifacts

### Container artifacts

- Dockerfile in repo [`rust-mcp-stack--rust-mcp-filesystem`, `severity1--terraform-cloud-mcp`, `shreyaskarnik--huggingface-mcp-server`]
- Multi-stage Docker build with minimal final image — `clux/muslrust:stable` builder + `alpine:latest` final, static binary, non-root user [`rust-mcp-stack--rust-mcp-filesystem`]
- Docker Hub MCP Registry presence [`rust-mcp-stack--rust-mcp-filesystem`]
- MCPB bundle replaces Docker for distribution [`sandraschi--email-mcp`]
- Windows installer via WiX toolset (`wix/`) [`rust-mcp-stack--rust-mcp-filesystem`]
- No container — intentional when the server must run on the same host as a local app [`samuelgursky--davinci-resolve-mcp`]
- Not observed [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`]

## Example client / developer ergonomics

### Task runner

- Makefile [`shibuiwilliam--mcp-server-scikit-learn`]
- Makefile.toml (cargo-make) — Rust task runner [`rust-mcp-stack--rust-mcp-filesystem`]
- Justfile recipes — uncommon in MCP servers; Windows-first repo [`sandraschi--email-mcp`]
- PowerShell scripts (`build.ps1`, `start.ps1`, `build_mcpb.bat`) — Windows-first dev posture [`sandraschi--email-mcp`]
- Plain `uv run <tool>` invocations [`sajal2692--mcp-weaviate`]

### Sample configs

- Per-host JSON snippets in README — `mcpServers` blocks per host [`severity1--terraform-cloud-mcp`, `slackapi--slack-mcp-plugin`]
- `examples/` directory [`sandraschi--email-mcp`, `samuelgursky--davinci-resolve-mcp`]
- Glob-pattern usage examples — `*.rs`, `src/**/*.txt`, `logs/error-???.log` [`rust-mcp-stack--rust-mcp-filesystem`]

## Repo layout

### Layout shape

- Single-package — `src/<package>/` [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`]
- Single-package with support directories — `install.py`, `src/`, `tests/`, `docs/`, `examples/` [`samuelgursky--davinci-resolve-mcp`]
- Multi-directory single-repo — distinct concerns split: `src/<pkg>/` core, `mcp-server/` packaging, `webapp/` monitoring dashboard, `monitoring/` health/metrics, `tests/`, `examples/`, `scripts/`, `.github/workflows/` [`sandraschi--email-mcp`]
- Single-package Rust — `src/`, `tests/`, `docs/`, `wix/`, `Dockerfile`, `Makefile.toml`, `Cargo.toml/Cargo.lock` [`rust-mcp-stack--rust-mcp-filesystem`]
- Flat — main server file at repo root, `src/<pkg>/` for helpers [`shreyaskarnik--huggingface-mcp-server`]
- Config-only repository — no server implementation, just per-host configs [`slackapi--slack-mcp-plugin`]

### Domain-per-module decomposition

- One module per domain area for a REST-API-wrapping server (account, workspace, run, plan, apply, project, organization) [`severity1--terraform-cloud-mcp`]

## Python-specific

### Build backend

- `hatchling.build` [`sandraschi--email-mcp`]
- Not surfaced (uv-backed) [`sajal2692--mcp-weaviate`, `shibuiwilliam--mcp-server-scikit-learn`]
- Likely hatchling given uv convention [`shreyaskarnik--huggingface-mcp-server`]
- pyproject with uv [`severity1--terraform-cloud-mcp`]
- No `pyproject.toml` at all — installation is entirely orchestrated by a bespoke script [`samuelgursky--davinci-resolve-mcp`]

### Lock file

- `uv.lock` present [`sajal2692--mcp-weaviate` (likely), `sandraschi--email-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server` (likely)]
- None — venv managed by a bespoke installer [`samuelgursky--davinci-resolve-mcp`]

### Version manager convention

- uv [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Plain pip inside a venv managed by `install.py` [`samuelgursky--davinci-resolve-mcp`]

### Async vs sync tool signatures

- Async — FastMCP-driven; weaviate-client's async surface used; aiosmtplib-style connection pooling [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Sync — domain library is sync-only (sklearn) and wrapping it async would introduce thread complexity for no benefit [`shibuiwilliam--mcp-server-scikit-learn`]
- Mixed — MCP SDK accepts both [`shreyaskarnik--huggingface-mcp-server`]
- Sync inherited from a binary scripting module — DaVinci Resolve's Python bindings are Lua-derived synchronous [`samuelgursky--davinci-resolve-mcp`]

### Type / schema strategy

- Pydantic via FastMCP — auto-derived from signatures [`sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`]
- Pydantic via raw MCP SDK [`shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`]
- Hand-authored — likely given raw SDK + 324 method surface [`samuelgursky--davinci-resolve-mcp`]

### Dev toolchain

- ruff + mypy [`sajal2692--mcp-weaviate`, `severity1--terraform-cloud-mcp`]
- ruff + black + mypy [`severity1--terraform-cloud-mcp`]
- Ruff + MyPy + Bandit (security) + Biome (webapp) [`sandraschi--email-mcp`]

### Mixed-language packaging

- `Cargo.toml` alongside `pyproject.toml` — Rust artifacts for MCPB bundle signing [`sandraschi--email-mcp`]

## Notable structural choices

### Cross-cutting design observations

- Read-only by default — server starts in least-privilege mode; write access opt-in [`rust-mcp-stack--rust-mcp-filesystem`, `shreyaskarnik--huggingface-mcp-server`]
- Two-axis safety — read-only and delete-enabling are independent toggles, not collapsed into one write-mode flag [`severity1--terraform-cloud-mcp`]
- Dual-mode tool surface — context-efficient compound vs full granular, user-selectable at launch [`samuelgursky--davinci-resolve-mcp`]
- Tool disabling at the CLI to reduce token usage in narrow workflows [`rust-mcp-stack--rust-mcp-filesystem`]
- Lazy connection — auto-reconnect and auto-launch of the underlying app on first tool call, smoothing cold-start UX [`samuelgursky--davinci-resolve-mcp`]
- Path-traversal protection — file-op tools validate paths stay within expected directories [`samuelgursky--davinci-resolve-mcp`]
- Auto-cleanup of exports after response encoding to prevent disk bloat [`samuelgursky--davinci-resolve-mcp`]
- Cross-platform sandbox handling — temp paths redirected per-OS (macOS/Linux/Windows) [`samuelgursky--davinci-resolve-mcp`]
- Multi-stage Docker build to a non-root static-binary alpine final image [`rust-mcp-stack--rust-mcp-filesystem`]
- Runtime backend reconfiguration via a tool call rather than a restart [`sandraschi--email-mcp`]
- Multi-backend unified surface — one tool dispatches to many providers; heterogeneity hidden from the caller [`sandraschi--email-mcp`]
- Per-tenant search tools as a first-class MCP concept; tenancy is an argument, not server config [`sajal2692--mcp-weaviate`]
- All three MCP surfaces (tools + resources + prompts) plus a custom URI scheme — uncommon among Python servers [`shreyaskarnik--huggingface-mcp-server`]
- Configs-as-product — the GitHub repo ships only configs; the actual MCP server is a remote HTTP service [`slackapi--slack-mcp-plugin`]
- First-party vendor authoring vs third-party — Slack provides their own MCP; Blackmagic Design does not, so a third-party server (`samuelgursky--davinci-resolve-mcp`) is effectively canonical [`slackapi--slack-mcp-plugin`, `samuelgursky--davinci-resolve-mcp`]
- "Industrial Quality Stack" / "SOTA 14.1" framing — author self-labels quality tiers; idiosyncratic and may be marketing rather than engineering signal [`sandraschi--email-mcp`]
- Author-cross-language port — Rust rewrite of the official JavaScript `@modelcontextprotocol/server-filesystem` for performance [`rust-mcp-stack--rust-mcp-filesystem`]

## Server-as-product vs configs-as-product

> Cross-cutting axis surfaced by `slackapi--slack-mcp-plugin` and discriminating most other samples in the bin.

### Server-as-product

- Repo contains the implementation, packaging, tests, and distribution for a runnable server [most samples in this bin]

### Configs-as-product

- Repo contains only configs and skills/commands for client hosts; the MCP server itself is a remote HTTP endpoint operated separately. License may not be specified because the repo holds no implementation [`slackapi--slack-mcp-plugin`]

## Vendor relationship

### First-party (vendor publishes their own MCP)

- Slack-hosted remote MCP at `mcp.slack.com` published under `slackapi/` org [`slackapi--slack-mcp-plugin`]

### Third-party canonical (vendor has no MCP; community fills the gap)

- DaVinci Resolve has no first-party MCP from Blackmagic Design; this third-party server is effectively canonical for the 833-star community [`samuelgursky--davinci-resolve-mcp`]

## Domain-imposed constraints

### External ABI-driven version ceilings

- Python 3.10–3.12 inclusive — Resolve's binary scripting module is incompatible with 3.13+; the MCP inherits the application's ABI floor and ceiling [`samuelgursky--davinci-resolve-mcp`]

### Free-edition exclusion

- Resolve Studio 18.5+ required; the free edition has no scripting API and is unsupported. The MCP inherits the application's licensing constraint [`samuelgursky--davinci-resolve-mcp`]

### Local-app-required

- Server must run on the same host as the controlled application; Docker is intentionally absent because it would break the local-app contract [`samuelgursky--davinci-resolve-mcp`]

### Local-data-only

- Server operates on local filesystems / local datasets / local models — no remote auth or remote state [`rust-mcp-stack--rust-mcp-filesystem`, `shibuiwilliam--mcp-server-scikit-learn`]

## State lifecycle (ML-specific)

### Trained-model persistence as a tool surface

- Exposing an ML training pipeline over MCP raises a state-lifecycle question (where do trained models persist? who owns them?) that the tool surface implicitly answers via `model_persistence` tools [`shibuiwilliam--mcp-server-scikit-learn`]

## Gaps observed across this bin

- Python version floor and PyPI publication status frequently unconfirmed in extracted content
- Logging destination/format almost universally undocumented
- Last-commit date and CI trigger details often not surfaced
- Whether multi-backend servers share a common abstraction internally or use per-provider adapters typically not externally documented [`sandraschi--email-mcp`]
