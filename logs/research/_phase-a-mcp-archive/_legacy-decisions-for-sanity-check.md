# Legacy Decisions Block (held for sanity check)

Extracted from `logs/research/mcp/consolidated.md` during the 2026-04-30 structural migration to `RESEARCH.md` / `ANALYSIS.md` / `<subtopic>-samples/_CONSOLIDATED.md`. Held here as a reference to compare against the from-scratch `repos-samples/_CONSOLIDATED.md` synthesis (Task #10).

After the new `_CONSOLIDATED.md` lands, diff this against it. Divergences classify as either:

- **(a) Findings the new synthesis missed** — re-run that section's synthesis
- **(b) Claims in the old block the corpus does not actually support** — drop them

Delete this file after the sanity check completes.

---

## Decisions

Each subsection describes a design component a repo author chooses among mutually-exclusive implementation paths. The **Docs** column marks paths explicitly prescribed or shown-as-valid by authoritative MCP documentation — the [spec](https://modelcontextprotocol.io/specification), [Python SDK README](https://github.com/modelcontextprotocol/python-sdk), [TypeScript SDK README](https://github.com/modelcontextprotocol/typescript-sdk), [Go SDK README](https://github.com/modelcontextprotocol/go-sdk), [Rust SDK README](https://github.com/modelcontextprotocol/rust-sdk), [Kotlin SDK README](https://github.com/modelcontextprotocol/kotlin-sdk), [FastMCP docs](https://gofastmcp.com), the [build-server tutorial](https://modelcontextprotocol.io/quickstart/server), and the per-host [integration docs](https://code.claude.com/docs/en/mcp). The **Adoption** column shows how many of the 104 sample repos use each path.

**Legend.** ★ — path explicitly prescribed or recommended in MCP or host docs. ☆ — docs shown as valid but without endorsement. (blank) — docs silent; adoption is the only available signal.

When ★ and highest-adoption rows disagree, the conflict is flagged explicitly in the decision's narrative.

**Denominator rule.** Each table's denominator is the applicable subset for that decision, not the full sample. Python-specific decisions (packaging backend, launch command) use Python-primary denominators. TS-specific decisions use TS/JS-primary denominators. The narrative names the applicability criterion so the reader sees why rows don't sum to 104.

**Monorepo handling.** `awslabs/mcp` is a monorepo containing dozens of sub-servers; five sub-servers were drilled into individually (`aws-api-mcp-server`, `aws-documentation-mcp-server`, `bedrock-kb-retrieval-mcp-server`, `openapi-mcp-server`, `mcp-lambda-handler`). For repo-level axes (monorepo vs single package, license, CI system) the monorepo counts once. For per-server axes (entry point shape, auth, transport) the drill-downs count individually.

### Language and runtime

The primary language defines most downstream choices (packaging backend, launch command, distribution registry, test framework).

| Implementation path | Docs | Adoption |
|---|---|---|
| Python (primary) | ★ | 58/104 |
| TypeScript / JavaScript (primary) | ★ | 26/104 |
| Go | ★ | 7/104 |
| Python + TS (mixed) | ★ | 4/104 |
| Rust | ★ | 4/104 |
| Clojure | | 2/104 |
| Kotlin | ★ (via Kotlin SDK) | 1/104 |
| C# / .NET | ★ (via C# SDK) | 1/104 |
| No primary language / configs-only | | 1/104 (`slackapi/slack-mcp-plugin`) |

The 58 Python-primary + 4 Python+TS-mixed = **62 Python-carrying repos** — the denominator used for Python-specific tables below. The C++ / DuckDB extension (`teaguesterling/duckdb_mcp`) is counted under Python above because its Python wrapper is secondary — a pitfall called out in sample caveats.

Python is the de-facto majority, but the official SDK family (Python, TypeScript, Go, Rust, Kotlin, C#, Java, Ruby, Swift) supports any mainstream language; Java, Ruby, PHP, and Swift did not appear in the sample despite SDKs existing — a disclosed gap, not evidence of nonexistence.

### Python SDK / framework

Applicable to Python-primary repos (62/104). Five subcategories emerged from framework/SDK-in-use lines.

| Implementation path | Docs | Adoption (Python-primary) |
|---|---|---|
| FastMCP (any version) — decorator-based, Pythonic | ★ | 54/62 |
| Raw `mcp` SDK only (explicit low-level) | ★ | 8/62 |
| Both `mcp` and `fastmcp` in same repo | | 3/62 (subset of above counts — `awslabs/mcp` sub-servers, `sooperset/mcp-atlassian`, `normaltusker/kotlin-mcp-server`) |
| Custom or pre-FastMCP-absorption implementation | | 2/62 |
| No recognizable Python MCP package pinned (bespoke) | | 2/62 (`samuelgursky/davinci-resolve-mcp`, `twolven/mcp-server-puppeteer-py`) |

> FastMCP 2.x was originally a separate project by `jlowin` that got absorbed into the official `mcp` Python SDK as `mcp.server.fastmcp` in 2024. FastMCP 2.x and 3.x now live in the standalone `fastmcp` package from PrefectHQ. This means "FastMCP" ambiguously refers to (a) the FastMCP layer inside the official SDK (`from mcp.server.fastmcp import FastMCP`) or (b) the standalone package (`from fastmcp import FastMCP`). Community repos use the standalone package almost universally; the reference `modelcontextprotocol/servers` Python servers (git, fetch, time) deliberately use the raw low-level SDK with hand-authored schemas to illustrate coverage of the protocol.

Within the FastMCP cohort (54 repos mentioning any FastMCP variant):

| FastMCP major version | Adoption |
|---|---|
| FastMCP 1.x (pre-absorption line) | 1/54 |
| FastMCP 2.x | 47/54 |
| FastMCP 3.x | 5/54 |
| Version not specified | 1/54 |

**Docs-vs-adoption note.** The official Python SDK README now documents FastMCP as its high-level API and recommends it for new servers. Community adoption of the standalone `fastmcp` package predates the absorption and remains dominant; that split means `pyproject.toml` pins tell you which line the repo uses (`mcp[cli]` vs `fastmcp>=2` vs `fastmcp>=3`).

### TypeScript SDK

Applicable to TS/JS-primary repos (26/104).

| Implementation path | Docs | Adoption (TS/JS-primary) |
|---|---|---|
| Official `@modelcontextprotocol/sdk` | ★ | 22/26 |
| Custom protocol implementation | | 2/26 |
| Framework-provided (Cloudflare Workers, Next.js App Router) | | 2/26 |

TS repos usually also pull `zod` for tool-input validation and one HTTP framework (`hono`, `express`) when HTTP transport is offered.

### Transport

MCP currently supports three transports: `stdio` (local, line-delimited JSON-RPC over process stdin/stdout), `HTTP+SSE` (being phased out — explicitly deprecated by Elasticsearch, AWS, and the Cloudflare servers in the sample), and `streamable HTTP` (single-endpoint, replaces SSE).

| Implementation path | Docs | Adoption |
|---|---|---|
| stdio only | ★ | 38/104 |
| stdio + HTTP (streamable or SSE) | ★ | 54/104 |
| HTTP only (remote-hosted or HTTP-first) | ★ | 10/104 |
| Other (REPL-as-transport, SQL PRAGMAs, SFTP) | | 2/104 |

`stdio` is near-universal as the local-first default (92/104 mention it) because every host supports it. HTTP transports appear in ~60% of repos, usually as a secondary mode selectable via environment variable or CLI flag. Remote-hosted services are HTTP-only by nature (Sentry, Slack, Neon, Supabase, Cloudflare, idosal/git-mcp).

**Docs-vs-adoption note.** The spec and all SDK READMEs treat streamable HTTP as the successor to SSE. Several repos in the sample still ship SSE as a first-class option (32/104 mention SSE); treat SSE as a legacy export path, not a green-field choice.

### Transport selection mechanism

How users pick between the transports the server supports. Applicable to repos shipping more than one transport (66/104).

| Implementation path | Docs | Adoption |
|---|---|---|
| Environment variable (e.g. `MCP_NIXOS_TRANSPORT`, `TRANSPORT_MODE`) | | 38/66 |
| CLI flag (`--transport stdio`, `--port`) | | 21/66 |
| Separate console scripts — one binary per transport | | 2/66 (`echelon-ai-labs/servicenow-mcp`, `utensils/mcp-nixos` partially) |
| Auto-detect from launch context | | 1/66 |
| Other (PRAGMA, SQL config) | | 1/66 (`teaguesterling/duckdb_mcp`) |
| Dual-protocol in same process (MCP + REST) | | 3/66 (`zongmin-yu/semantic-scholar`, `gis-mcp`, `datalayer/jupyter-mcp-server`) |

Env var is the community majority; docs are silent on which mechanism to use.

### Distribution mechanism

How users install and run the server. Multiple mechanisms per repo are common; the table counts a repo once per mechanism it ships.

| Implementation path | Docs | Adoption |
|---|---|---|
| PyPI + `uvx`-launchable (Python-primary) | ★ | 52/62 Python-primary |
| npm + `npx`-launchable (TS/JS-primary) | ★ | 23/26 TS/JS-primary |
| Docker image (Docker Hub or `ghcr.io`) | ☆ | 57/104 |
| Homebrew formula | | 12/104 |
| Cargo crate (Rust) | ★ | 4/4 Rust-primary |
| Go binary via GitHub release / `go install` | ★ | 6/7 Go-primary |
| Nix flake (`nix run github:...`) | | 1/104 (`utensils/mcp-nixos`) |
| Cloudflare Workers deployment | | 2/104 (`cloudflare/mcp-server-cloudflare`, `idosal/git-mcp`) |
| Remote-hosted URL (no local install) | | 5/104 |
| Smithery registry | ☆ | 14/104 |
| Custom `install.py` / installer script | | 2/104 (`samuelgursky/davinci-resolve-mcp`, `normaltusker/kotlin-mcp-server`) |
| `modelcontextprotocol/registry` (official registry) | ★ | 3/104 |

**Docs-vs-adoption conflict.** The `modelcontextprotocol/registry` is the official, community-governed registry (API v0.1 frozen). Only 3/104 repos explicitly advertise an entry there. Smithery (14/104), glama.ai, mcpservers.org, and pulsemcp remain the discovery channels community servers actually surface in READMEs. For portfolio signal, publishing to the official registry is the docs-prescribed choice; for real-world discoverability, commercial registries currently carry more traffic.

### Python packaging backend

Applicable to Python-primary repos with a `pyproject.toml` (≈43/62; rest have no backend, legacy `setup.py`, or the content wasn't extracted).

| Implementation path | Docs | Adoption (Python-primary w/ pyproject) |
|---|---|---|
| `hatchling.build` | | 31/62 |
| `poetry-core` | | 9/62 (`JackKuo666/PubMed-MCP-Server`, `PagerDuty/pagerduty-mcp-server`, `blazickjp/arxiv-mcp-server`, `isaaccorley/planetary-computer-mcp`, `jbeno/cursor-notebook-mcp`, +4 more) |
| `setuptools.build_meta` | | 2/62 (`rohitg00/kubectl-mcp-server`, `twolven/mcp-server-puppeteer-py`) |
| `uv_build` (uv's native backend) | | 1/62 (`redis/mcp-redis`) |
| No `pyproject.toml` / custom installer | | 2/62 (`hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `samuelgursky/davinci-resolve-mcp`) |
| Not declared in sampled content | | 17/62 |

`hatchling` is the unambiguous community default. `poetry-core` (9/62) is a meaningful secondary — mostly older Python MCP servers whose `pyproject.toml` predates hatchling's community rise. No `flit`, no `pdm`, and only one `uv_build` adopter in the sample — `uv_build` is newer than most repos in the set.

See `_INDEX.md` Purpose 19 — Python-specific → Packaging backend for representative repos.

### Python host-config launch command

Applicable to Python-primary repos that document a host-config snippet (≈58/62).

| Implementation path | Docs | Adoption (Python-primary) |
|---|---|---|
| `uvx <package>` or `uvx <package>@latest` | ★ | 52/62 |
| `uv run --with <package>` | ☆ | 8/62 |
| `python -m <module>` / `python <script>` | ☆ | 5/62 |
| `fastmcp install <script>` | ☆ | 1/62 |
| Absolute venv-Python path | | 2/62 |
| Docker-primary (`docker run ...`) | ☆ | 8/62 |
| Custom installer-driven (`install.py` writes config) | | 2/62 |

`uvx <package>` is the de-facto Python convention. Combined with `[project.scripts]` → `server:main`, it gives users a zero-install, single-command launch. Docker-primary appears when the server bundles system dependencies the user shouldn't be asked to install (Playwright browsers, ffmpeg, security CLIs).

### TS/JS host-config launch command

Applicable to TS/JS-primary repos (26/104).

| Implementation path | Docs | Adoption (TS/JS-primary) |
|---|---|---|
| `npx -y <package>` | ★ | 23/26 |
| `node <path>` (absolute path or from checkout) | ☆ | 3/26 |
| Docker-primary | ☆ | 4/26 |
| Bun-first launch | | 1/26 (`cyanheads/git-mcp-server`) |

`npx -y <pkg>` is the equivalent of `uvx <pkg>` for TS. The `-y` flag auto-confirms the install prompt — without it, hosts hang waiting for stdin.

### Entry point tier (Python)

Applicable to Python-primary repos (62/62).

| Implementation path | Docs | Adoption |
|---|---|---|
| `[project.scripts]` console script → `pkg.server:main` | ★ | 42/62 |
| `__main__.py` in package root (`python -m <pkg>`) | ☆ | 8/62 |
| Bare script in repo root (no installable package) | | 3/62 |
| CLI wrapper with subcommands (`<tool> serve`, `<tool> init`, ...) | | 2/62 (`DiversioTeam/clickup-mcp`, `utensils/mcp-nixos`) |
| Custom installer writes host config; no `[project.scripts]` | | 2/62 |
| Dispatcher (one console script routes to sub-servers) | | 1/62 (`pathintegral-institute/mcp.science` — `uvx mcp-science <server>`) |
| Not declared in sampled content | | 4/62 |

Console script is the canonical path. CLI wrappers are emerging for servers that also ship operational commands (auth init, migration, session-token rotation).

### Configuration surface

How configuration reaches the server at startup.

Multi-label — a repo may ship env vars + CLI + a config file; counts sum to more than 104.

| Implementation path | Docs | Adoption |
|---|---|---|
| Environment variables (exclusive) | ☆ | 44/104 |
| Env vars + CLI flags (both accepted) | ☆ | 37/104 |
| Config file (YAML / TOML / `fastmcp.json` / `.env` file) | ☆ | 23/104 |
| CLI flags (exclusive) | ☆ | 7/104 |
| OAuth callback flow (cloud-hosted) | ☆ | 7/104 |
| OS keyring for secrets | | 1/104 (`DiversioTeam/clickup-mcp` — `platformdirs` + keyring) |
| In-server encrypted vault | | 1/104 (`the-momentum/fhir-mcp-server`) |
| Stdin prompt on first run | | 0/104 |

Env vars dominate because host-config JSON files can populate them via an `env` block and they flow cleanly across stdio. Mixed env+CLI is the common superset. Config files (23/104) appear when the tool catalog itself is config (`apollographql/apollo-mcp-server`, `googleapis/mcp-toolbox`'s `tools.yaml`, `awslabs/openapi-mcp-server`) or when FastMCP's `fastmcp.json` is in use.

See `_INDEX.md` Purpose 5 for representative repos per path.

### Authentication

How the server verifies the caller. Not mutually exclusive — servers supporting multiple auth modes (stdio: none, HTTP: token) are counted for each mode they offer.

| Implementation path | Docs | Adoption |
|---|---|---|
| None (stdio-only, trusted local) | ★ | 30/104 |
| Static API key / bearer token | ☆ | 39/104 |
| OAuth 2.x (2.0 or 2.1) | ★ | 28/104 |
| Per-request header (multi-tenant by caller) | | 13/104 |
| In-server credential vault | | 2/104 |
| Platform-delegated (boto3 default chain, GCP ADC) | ☆ | 6/104 |

The 2025 MCP authorization spec introduced OAuth 2.1 + Protected Resource Metadata + Dynamic Client Registration + PKCE as the formal remote-server pattern. Community adoption is led by vendor-hosted services (Supabase, Sentry, Neon, Slack, Context7) and a handful of k8s/infra servers. Static API keys remain the community majority because they fit the env-var-into-stdio model.

### Multi-tenancy

How the server handles simultaneous users.

| Implementation path | Docs | Adoption |
|---|---|---|
| Single-user — one server process per user/workspace | ★ (implicit in stdio) | 94/104 |
| Per-request tenant via middleware | | 1/104 (`ClickHouse/mcp-clickhouse`) |
| Per-request tenancy via HTTP headers | | 1/104 (`lanbaoshen/mcp-jenkins`) |
| OAuth-scoped remote hosting | | 3/104 (`supabase`, `neondatabase`, `getsentry`) |
| Base-directory sandboxing (one server, many project roots) | | 1/104 (`cyanheads/git-mcp-server`) |
| Tenancy-as-tool-argument | | 1/104 (`sajal2692/mcp-weaviate`) |
| Workspace-keyed (one server, multiple workspaces) | | 3/104 |

Single-user is the overwhelming default because stdio transport is one-process-per-client. Multi-tenant designs appear exclusively alongside HTTP transport or hosted-service models.

### Tool-surface philosophy

How many tools a server exposes and how they're organized. Influences token budget, discoverability, and prompt-injection surface.

| Implementation path | Docs | Adoption |
|---|---|---|
| Enumerate-every-API (one tool per endpoint) | ☆ | 71/104 |
| Category-gated tool sets (flags disable groups) | | 8/104 |
| Workflow-oriented (tools correspond to user intents, not API verbs) | ☆ (recommended by community best-practices) | 15/104 |
| Spec-driven generation (tool catalog from OpenAPI / GraphQL) | ☆ | 3/104 (`awslabs/openapi-mcp-server`, `apollographql/apollo-mcp-server`, `makenotion/notion-mcp-server`) |
| Code-as-tool (one `exec` tool with AST sandbox) | | 2/104 (`baryhuang/mcp-server-aws-resources-python`, `teaguesterling/duckdb_mcp`) |
| Minimalist-by-design (token-budget strategy) | | 2/104 (`utensils/mcp-nixos` — 2 tools, `samuelgursky/davinci-resolve-mcp` has a compact mode with 27 vs 342 tools) |

The range is extreme: `rohitg00/kubectl-mcp-server` ships 253 tools; `utensils/mcp-nixos` ships 2; `baryhuang` ships 1. Community best-practice writeups (MCPcat production guide, 15-best-practices-mcp-production) increasingly advocate workflow-oriented or minimalist designs — token budget and prompt-injection surface are design costs, not free.

### Claude Desktop config surface

How the README instructs users to wire the server into Claude Desktop (`claude_desktop_config.json`).

| Implementation path | Docs | Adoption |
|---|---|---|
| README JSON snippet with `mcpServers` block | ★ | 74/104 |
| DXT manifest (`manifest-dxt.json` / `.dxt` bundle) | ★ (Desktop-specific) | 1/104 (`korotovsky/slack-mcp-server`) |
| No Claude Desktop snippet (remote-only, CLI-only, or host-neutral README) | | 30/104 |

**Gotcha.** DXT (Desktop Extensions) is a Claude Desktop-specific packaging format — it does not work in Claude Code, Cursor, Windsurf, VS Code, or other hosts. Ship DXT only as an additional channel, never as the sole distribution path.

### Claude Code integration surface

How the README and repo layout support Claude Code specifically. Independent of Claude Desktop.

| Implementation path | Docs | Adoption |
|---|---|---|
| README shows `claude mcp add` CLI invocation | ★ | 32/104 |
| `.claude-plugin/plugin.json` shipped (no `.mcp.json`) | ★ | 3/104 (`exa-labs/exa-mcp-server`, `motherduckdb/mcp-server-motherduck`, `stripe/agent-toolkit`) |
| `.claude-plugin/plugin.json` + `.mcp.json` both shipped | ★ | 1/104 (`getsentry/sentry-mcp`) |
| `.claude-plugin/marketplace.json` only (marketplace metadata, no plugin.json) | ★ | 1/104 (`upstash/context7`) |
| `.mcp.json` only at repo root (no `.claude-plugin/`) | ★ | 2/104 (`FuzzingLabs/mcp-security-hub`, `modelcontextprotocol/servers`) |
| `.claude/skills/` or `skills/` directory (no plugin manifest) | | 3/104 (`blazickjp/arxiv-mcp-server`, `neondatabase/mcp-server-neon`, `openags/paper-search-mcp`) |
| `.codex-plugin/` (Codex CLI's plugin format) | | 1/104 (`blazickjp/arxiv-mcp-server`) |
| `.cursor-plugin/` directory | | 2/104 (`slackapi/slack-mcp-plugin`, `stripe/agent-toolkit`) |
| No Claude-Code-specific surface | | 94/104 |

Claude Code accepts generic `.mcp.json` in project root or user-global registration via `claude mcp add <name> -- <command>`. A full `.claude-plugin/` wrapper is the highest-integration path: it turns the repo into an installable Claude Code plugin (skills, hooks, commands, and MCP config ship together). Most community servers still expect the user to hand-assemble config, but shipping `.claude-plugin/` unlocks one-line install via `/plugin marketplace add`.

**Verification note.** An earlier pass reported 6/104 for `.claude-plugin/plugin.json` because the per-repo template's label prompt `(.claude-plugin/plugin.json, .mcp.json at repo root, ...)` was being matched even on repos whose body read "not observed." The verified counts in the table above parse only the value after the `presence and shape:` prompt.

See the *Claude integration shapes* appendix below for concrete templates.

### Other host integrations documented in README

Independent yes/no per host. A single repo often targets several.

| Host | Docs (has integration page) | Adoption |
|---|---|---|
| Claude Desktop | ★ | 84/104 |
| Cursor | ★ | 42/104 |
| VS Code / GitHub Copilot | ★ | 33/104 |
| Claude Code | ★ | 32/104 |
| Windsurf | ★ | 21/104 |
| Cline | ★ | 20/104 |
| Zed | ★ | 15/104 |
| Continue | ★ | 11/104 |
| Smithery auto-detect | ☆ | 7/104 |
| Codex CLI | ★ | 5/104 |
| Gemini CLI | ★ | 5/104 |
| Kiro | | 4/104 |
| OpenAI / Codex (hosted) | | 3/104 |
| Warp | ★ | 2/104 |

Distribution of host counts per repo: 14 repos document 0 hosts (framework/configs-only), 22 document 1 host (usually Claude Desktop), 44 document 2–3, 10 document 4–5, 12 document 6–9, and 2 document 10+ (`samuelgursky/davinci-resolve-mcp`, `exa-labs/exa-mcp-server`). Most repos (66/104) land in the 1–3 host band.

See `_INDEX.md` Purpose 10 for representative repos per host.

### Repo layout

Dominant structural shape of the repo. Each repo counted in its primary layout bucket.

| Implementation path | Docs | Adoption |
|---|---|---|
| Single package, flat layout (no `src/`) | ☆ | 54/104 |
| Single package, `src/<pkg>/` layout | ★ (Python packaging guide) | 15/104 |
| Monorepo (per-server sub-packages, unspecified flavor) | | 10/104 |
| Monorepo (pnpm / Turbo workspaces) | | 4/104 (`cloudflare/mcp-server-cloudflare`, `getsentry/sentry-mcp`, `supabase-community/supabase-mcp`, `upstash/context7`) |
| Monorepo (Cargo crates) | | 2/104 (`apollographql/apollo-mcp-server`, `rust-mcp-stack/rust-mcp-filesystem`) |
| Bare script / single file (no packaging) | | 4/104 |
| Extension of host product (DuckDB, Jupyter, VS Code) | | 3/104 (`datalayer/jupyter-mcp-server`, `isaaccorley/planetary-computer-mcp`, `teaguesterling/duckdb_mcp`) |
| Dispatcher monorepo (one package → many servers) | | 1/104 (`pathintegral-institute/mcp.science`) |
| Configs-only (no server code) | | 1/104 (`slackapi/slack-mcp-plugin`) |
| Other / unclassified | | 10/104 |

Flat single-package (54/104) outweighs `src/`-layout (15/104) despite `src/` being the packaging-community recommendation. The imbalance reflects the MCP server community's origins in single-file FastMCP scripts that grew into packages without refactoring to `src/`.

See `_INDEX.md` Purpose 16 for representative repos.

### CI system

Applicable to repos with any CI (82/104).

| Implementation path | Docs | Adoption (CI-present) |
|---|---|---|
| GitHub Actions | | 77/82 |
| Buildkite | | 1/82 |
| Other (CircleCI, GitLab, Jenkins, none) | | 4/82 |

### License

| Implementation path | Docs | Adoption |
|---|---|---|
| MIT | | 58/104 |
| Apache-2.0 | | 33/104 |
| BSD-3-Clause / ISC / Zlib | | 4/104 |
| GPL-family | | 3/104 |
| CC BY-NC-SA (non-commercial) | | 1/104 (`jbeno/cursor-notebook-mcp`) |
| No license declared in sampled content | | 5/104 |

CC BY-NC-SA is unusually restrictive for a developer-tool MCP server — most hosts and downstream integrators cannot redistribute a non-commercially-licensed server inside their products. Declare a permissive license unless deliberate.
