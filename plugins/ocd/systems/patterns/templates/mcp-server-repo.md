# MCP Server Repository

Canonical shape for an open-source repository publishing one or more Model Context Protocol (MCP) servers intended to run across multiple hosts (Claude Desktop, Claude Code, Cursor, Windsurf, Cline, VS Code, Zed, Continue, Codex CLI, Gemini CLI, Warp, etc.), derived from 104 recently-maintained public repos spanning Python, TypeScript/JavaScript, Go, Rust, Clojure, Kotlin, C#, and one C++ DuckDB extension. Every decision below cites an adoption count across the sample so a reader can distinguish convention from outlier without inferring. Full repo list in *References*.

## When to use

- **This pattern** — a repository that ships one or more MCP servers for general (multi-host) consumption, with code, tests, and at least one published distribution channel (PyPI, npm, Docker, Homebrew, Cargo, GitHub release binary, or a hosted endpoint).
- **Adaptation: single-host focus (Claude-only)** — still valid; drop non-Claude host-integration sections in README but keep the rest of the shape. The `.claude-plugin/` wrapper becomes more compelling when it is the only advertised install path.
- **Adaptation: vendor-hosted remote service** — different discipline. The repo becomes config-only (OAuth flow, hosted endpoint URL, per-host config snippets). No local install artifacts, no `[project.scripts]`, no Dockerfile for end users. See `slackapi/slack-mcp-plugin`, `idosal/git-mcp`, `neondatabase/mcp-server-neon`.
- **Adaptation: internal / private MCP** — most of the layout still applies but distribution shifts to private registries, internal artifact stores, or worktree-mounted builds.
- **Not for Claude Code plugin marketplaces** — different manifest, different discipline; see the sibling `claude-marketplace.md`.
- **Not for MCP client / SDK repos** — a repo whose product is an SDK (`jlowin/fastmcp`, `modelcontextprotocol/kotlin-sdk`, `rust-mcp-stack/rust-mcp-sdk`) follows a library-publishing discipline where server-oriented concerns (transport choice, host integrations, entry-point script) do not apply symmetrically.
- **Not for tutorials or demo scaffolds** — those are instructional artifacts, not distributable servers.

## Canonical shape

```text
my-mcp-server/
├── src/ or <package-name>/       # Server implementation
│   └── server.py or index.ts     # main() or equivalent
├── tests/                        # Tests at repo root
├── scripts/                      # Dev helpers (optional)
├── .github/
│   └── workflows/
│       ├── ci.yml                # Push/PR pytest | vitest | go test
│       └── release.yml           # Tag-triggered publish (optional)
├── Dockerfile                    # Optional; common for DB/enterprise servers
├── pyproject.toml                # Python-primary repos
│   or package.json               # TS/JS-primary repos
│   or go.mod / Cargo.toml        # Go / Rust-primary repos
├── .claude-plugin/               # Optional Claude Code plugin wrapper (5/104)
│   └── plugin.json
├── .mcp.json                     # Optional embedded MCP config (2/104 standalone)
├── server.json                   # Optional capability manifest (4/104 — github, googleapis, redis, exa)
├── README.md                     # Host-integration snippets live here
├── LICENSE
├── CHANGELOG.md                  # Optional
└── CLAUDE.md                     # Optional agent-facing procedures
```

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

## Features

Independent yes/no features a repo may adopt in any combination. The **Docs** column marks features MCP or host documentation explicitly recommends.

### Universal features

Applicable to every installable server in the sample.

| Feature | Docs | Adoption |
|---|---|---|
| `README.md` at repo root | | 104/104 |
| At least one distribution channel advertised | ★ | 99/104 |
| `LICENSE` file declared | | 99/104 |
| Default branch `main` (not `master`) | | 104/104 — no repo in the sample is still on `master` |
| At least one test framework invoked in the repo | ★ | 37/104 |
| At least one CI workflow | | 82/104 |
| `CHANGELOG.md` or release notes section | | 34/104 |

### Conditional features

Applicability differs from the full sample. Each row names its applicability criterion and uses a matching denominator.

| Feature | Docs | Applicable to | Adoption where applicable |
|---|---|---|---|
| `Dockerfile` | ☆ | All installable servers (99) | 54/99 |
| `docker-compose.yml` for local dev | | Repos with a Dockerfile (54) | 6/54 |
| `Helm` chart | | Repos shipping k8s deployment (5) | 3/5 |
| `server.json` capability manifest at repo root | | All installable servers (99) | 4/99 (`exa-labs/exa-mcp-server`, `github/github-mcp-server`, `googleapis/mcp-toolbox`, `redis/mcp-redis`) |
| DXT manifest (`manifest-dxt.json` / `.dxt` bundle) | ★ (Desktop-specific) | Claude-Desktop-targeting repos (84) | 2/84 (`korotovsky/slack-mcp-server`, `sandraschi/email-mcp` MCPB bundle) |
| MCP Inspector launcher in README or scripts | ★ | All servers (104) | 2/104 (`getsentry/sentry-mcp`, `mukul975/cve-mcp-server`) |
| `fastmcp dev` launcher shipped | ★ | FastMCP-using Python repos (47) | 1/47 (`qdrant/mcp-server-qdrant`) |
| `CLAUDE.md` shipped in-repo (agent-facing procedures) | | All servers (104) | 3/104 |
| `llms.txt` (LLM-context doc alongside server) | | All servers (104) | 3/104 |
| `cursor_rules.md` / `.cursorrules` | | All servers (104) | 1/104 |
| Skills / commands directory co-located with server | | All servers (104) | 3/104 (`blazickjp/arxiv-mcp-server`, `neondatabase/mcp-server-neon`, `openags/paper-search-mcp`) |
| Audit logging as first-class capability | | Security-sensitive servers (~10) | 4/10 |
| Read-only safety flag | | Data / destructive-op servers (~30) | 12/30 |
| Orthogonal safety flags (read-only + enable-delete + per-verb) | | Data / destructive-op servers (~30) | 5/30 |
| Release automation (`release.yml` tag-triggered publish) | | Repos with a release cadence (~70) | 21/70 |
| Published to Smithery | | All installable servers (99) | 14/99 |
| Published to glama.ai or similar commercial registry | | All installable servers (99) | 6/99 |
| Published to `modelcontextprotocol/registry` (official) | ★ | All installable servers (99) | 3/99 |

**Python-specific features** (applicable to Python-primary repos, N=62):

| Feature | Docs | Adoption |
|---|---|---|
| `uv.lock` shipped in repo (not gitignored) | | 8/62 (verified Python-primary: `alexei-led/k8s-mcp-server`, `duolingo/slack-mcp`, `FuzzingLabs/mcp-security-hub`, `lanbaoshen/mcp-jenkins`, `pragmar/mcp-server-webcrawl`, `qdrant/mcp-server-qdrant`, `sandraschi/email-mcp`, `voska/hass-mcp`) |
| PEP 735 `[dependency-groups]` in `pyproject.toml` | | 1/62 (`redis/mcp-redis`) — too new to be meaningful adoption; watchlist item |

## Non-obvious gotchas

- **Raw `mcp` SDK vs FastMCP: which earns its place.** The raw SDK gives you hand-authored JSON Schemas, explicit server lifecycle, and full protocol control — the reference Python servers (git, fetch, time) use it deliberately for that reason. FastMCP gives you decorator-driven tool registration, automatic schema generation from type hints, and drop-in middleware. The packaging hint in `pyproject.toml` (`mcp[cli]` vs `fastmcp>=2`) tells you which line a repo is on. Mixing both in one `pyproject.toml` (as `awslabs`, `sooperset/mcp-atlassian`, `normaltusker/kotlin-mcp-server` do) usually means different sub-modules use different layers — audit before extending.

- **FastMCP 1.x vs 2.x/3.x API divergence.** FastMCP 1.x was absorbed into the official SDK as `mcp.server.fastmcp`. FastMCP 2.x and 3.x are the standalone `fastmcp` package by `jlowin`/PrefectHQ. The APIs diverged after the absorption — middleware, Providers, and Transforms in 2.9+ and 3.x have no equivalent in the absorbed 1.x layer. `from fastmcp import FastMCP` and `from mcp.server.fastmcp import FastMCP` import different classes with different capabilities despite the name collision.

- **`uvx` vs `pip install`.** `uvx <package>` runs a PyPI package in an ephemeral venv — no global state, no conflict with the user's Python. Every modern Python MCP host-config example uses `uvx`. Falling back to `pip install <package>` and `python -m <package>` works but forces the user into venv management. `uvx` is the default; everything else is a fallback.

- **`npx -y` vs `npx`.** Without `-y`, `npx` prompts "OK to proceed?" on first run. Hosts connecting via stdio hang waiting for stdin that never arrives. Always include `-y` in host-config snippets for TS servers.

- **Stdio env-var propagation.** Hosts spawn the server as a subprocess and populate `env` from the host-config JSON block. The user's shell env does not auto-flow. If your server reads `AWS_PROFILE` or `GITHUB_TOKEN` and the user didn't add it to the `env:` block, the server sees unset values. Document every env var your server reads and whether it needs to appear in the host's `env:` block.

- **Prompt injection in tool descriptions is a real threat.** Any string returned by a tool, resource, or prompt is interpreted by the client LLM. Malicious content in a fetched web page, a GitHub issue, or an email can issue instructions the LLM will follow. See `blog-simonw-mcp-prompt-injection.md` and `blog-elastic-mcp-attack-defense.md` for the canonical threat taxonomy. The agent reading tool output is the attack target; sanitize, scope, and require confirmation for destructive actions.

- **Multi-token Slack and Slack-family servers.** `korotovsky/slack-mcp-server` documents four token modes (user token, bot token, stealth mode, enterprise), and some are abusable — a stolen user token reads DMs across an entire workspace. When the server supports multiple auth modes, docs must state which mode maps to which capability surface and recommend the least-privilege option.

- **DXT is not cross-host.** DXT (Desktop Extensions) is a Claude Desktop packaging format. It does not install in Claude Code, Cursor, Windsurf, or VS Code. Ship DXT only as an optional additional channel.

- **Remote-hosted MCP means users don't self-host.** Sentry, Slack, Neon, Supabase, Cloudflare, Context7's HTTP endpoint, and `idosal/git-mcp` all run the server on the vendor's infrastructure. The user's repo contains config, not code. For anyone authoring a server meant to run on user hardware, this is a different discipline — no Dockerfile for end users, no `[project.scripts]`, no PyPI publish. Choose posture explicitly.

- **Config file formats differ per host.** Claude Desktop uses `~/.../claude_desktop_config.json`; Claude Code accepts `.mcp.json` in a project or `~/.claude/*` for user-scope; Cursor uses `.cursor/mcp.json`; VS Code uses `.vscode/mcp.json`; Windsurf uses `~/.codeium/windsurf/mcp_config.json`; Zed keys its config under `context_servers`, not `mcpServers`; Codex CLI uses TOML in `config.toml`, not JSON; Gemini CLI uses `~/.gemini/settings.json`. README snippets cannot be one snippet — each host wants its own shape.

- **Host `env:` blocks propagate to the subprocess; CLI args don't.** Claude Desktop and most hosts have no "args that need shell interpolation" feature. `"${HOME}/foo"` in an `args` array is passed literally. Use `env:` for anything the server reads from the environment; use `args:` only for fixed-shape flags.

- **SSE is deprecated; streamable HTTP replaces it.** Elasticsearch's Rust server and AWS servers document SSE removal explicitly. Ship streamable HTTP for new HTTP-capable servers, offer SSE only if you have legacy consumers.

- **Tool count has a budget.** Windsurf enforces a 100-tool cap. Claude Code's context window is finite; every tool description loads on every turn. Servers shipping 250+ tools (`kubectl-mcp-server`) force the user into tool-gating config. Minimalism — `utensils/mcp-nixos`'s two tools, `baryhuang`'s one — is a deliberate strategy, not a maturity gap.

- **Stars and last-commit snapshots go stale fast.** MCP moves weekly. Numbers captured at research time drift by the month. Cite metadata only when you've re-verified against GitHub.

- **Observability is the axis most often silently undocumented.** 73/104 repos in the sample have no logging/metrics/tracing content in their section 9 — `stderr` stream behavior is assumed but not stated, debug-flag env vars are only mentioned when used, health endpoints appear only on servers that ship HTTP. For a production MCP server, state your logging destination, log level env var, and whether the process writes to stdout (which will collide with stdio-protocol framing and break the host connection) or only stderr.

- **FastMCP's `fastmcp dev` launcher is almost never shipped.** 1/47 FastMCP repos document the Inspector launcher — even though it's first-class in FastMCP docs. For new servers, ship a `fastmcp dev <script>` command in your README or `scripts/dev.sh`; it costs nothing and adds a smoke-test path the host doesn't provide.

- **Claude Desktop's `env:` block vs subprocess inheritance.** Hosts spawn servers as subprocesses and set `env` from the JSON. The subprocess does not inherit the user's shell env. Servers relying on `$AWS_PROFILE` or `$HOME` without documenting that the user must add the var to `env:` fail silently with "unset value." State every env var your server reads and whether the host JSON needs to forward it.

- **Tool count has a budget — check your host.** Windsurf caps at 100 tools; Claude Code's context window loads every tool description on every turn; Cursor documents a recommended ceiling. A server shipping 253 tools (`kubectl-mcp-server`) or 342 (`samuelgursky/davinci-resolve-mcp` full mode) forces the user into tool-gating config. If you're authoring a server and the natural tool count exceeds ~50, plan a `--compact` or category-gated mode from the start.

- **Template label echo is not a capability claim.** A pitfall observed in earlier passes over this very research corpus: the per-repo template's label prompt (`tools / resources / prompts / sampling / roots / logging / other:`) was being matched even when the body said "tools only." Downstream tallies overstated resources/prompts/sampling adoption by 3–5×. When measuring an axis against schema'd data, parse the value after the field prompt, not the label itself.

## Claude integration shapes

The two places the README must show concrete config for Claude hosts. Both accompany whatever other host shapes the server supports.

### Claude Desktop — `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uvx",
      "args": ["my-mcp-server"],
      "env": {
        "MY_SERVER_API_KEY": "<value>"
      }
    }
  }
}
```

TypeScript equivalent:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "npx",
      "args": ["-y", "my-mcp-server"],
      "env": {
        "MY_SERVER_API_KEY": "<value>"
      }
    }
  }
}
```

Config file path: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%APPDATA%\Claude\claude_desktop_config.json` (Windows). Restart Claude Desktop to pick up changes.

### Claude Code — two options

**Option A: CLI invocation (no repo files required).**

```bash
claude mcp add my-mcp-server -- uvx my-mcp-server
claude mcp add my-mcp-server -s user -- uvx my-mcp-server        # user-global
claude mcp add my-mcp-server -s project -- uvx my-mcp-server     # project-scoped
```

Or drop an `.mcp.json` at the project root for the `project` scope:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uvx",
      "args": ["my-mcp-server"]
    }
  }
}
```

**Option B: Claude Code plugin wrapper (server ships as installable plugin).**

```text
my-mcp-server/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json
└── ...
```

`.claude-plugin/plugin.json`:

```json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "description": "One-line server description",
  "author": "your-handle"
}
```

`.mcp.json` (same shape as Desktop):

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uvx",
      "args": ["my-mcp-server"]
    }
  }
}
```

Users install via:

```bash
/plugin marketplace add <owner>/<repo>
/plugin install my-mcp-server@<marketplace-name>
```

This path turns the repo into a Claude Code plugin and lets the author ship skills, commands, and hooks alongside the MCP server. Adopted by 5/104 repos carrying a `.claude-plugin/` artifact of any shape (`getsentry/sentry-mcp`, `stripe/agent-toolkit`, `exa-labs/exa-mcp-server`, `motherduckdb/mcp-server-motherduck`, `upstash/context7` as `marketplace.json`) — rare today but increasingly advantageous for anyone who wants the server's tools paired with workflow guidance the host loads automatically.

## Known ecosystem patterns worth naming

Outlier shapes that occur in the sample but are too rare to be Decision rows.

- **Server-as-extension embedded in a SQL engine.** `teaguesterling/duckdb_mcp` implements MCP as a native DuckDB extension — tools are registered via `PRAGMA mcp_publish_tool`, the transport is SQL-driven, and the "runtime" is DuckDB itself.
- **Monorepo of micro-servers.** `FuzzingLabs/mcp-security-hub` ships 38 containerized security-tool MCP servers (one per CLI tool: Nmap, Nuclei, SQLMap, etc.). Each is a standalone binary reachable via Docker Compose.
- **Transport split across separate console scripts.** `echelon-ai-labs/servicenow-mcp` ships two binaries (`servicenow-mcp-stdio` and `servicenow-mcp-sse`) instead of one multi-mode binary. Cleaner but doubles the release surface.
- **Dual-protocol in same process.** `zongmin-yu/semantic-scholar-fastmcp-mcp-server` and `gis-mcp` run MCP stdio and REST HTTP simultaneously (HTTP is used for file transfer, which MCP stdio isn't suited for).
- **Server mode selection — compact vs full tool set.** `samuelgursky/davinci-resolve-mcp` offers a 27-tool mode and a 342-tool mode selectable at launch. Deliberate token-budget lever.
- **Code-as-tool with AST sandbox.** `baryhuang/mcp-server-aws-resources-python` ships one tool: `exec_boto3_code`. The server runs the boto3 code inside an AST-restricted sandbox. One tool covers thousands of AWS APIs.
- **Spec-driven tool generation.** `awslabs/openapi-mcp-server` reads an OpenAPI spec at startup and emits one MCP tool per endpoint. `apollographql/apollo-mcp-server` does the same for GraphQL operations. The tool catalog is config, not code.
- **Skills / prompt routines shipped alongside the MCP server.** Exa, Context7, SlackAPI's wrapper, `pragmar/mcp-server-webcrawl` ("prompt routines"), `getsentry/sentry-mcp` ("Skills"), and `blazickjp/arxiv-mcp-server` bundle client-side skills/commands with the server — the MCP server provides data access; the skills provide workflow guidance.
- **Bundled non-MCP LLM context files.** `gis-mcp` ships `llms.txt`, `jbeno/cursor-notebook-mcp` ships `cursor_rules.md`, `makenotion/notion-mcp-server` ships `CLAUDE.md`. The convention: ship LLM-context docs the host's auto-injection mechanisms recognize, so the model has structural guidance beyond tool descriptions.
- **Universal installer across many hosts.** `samuelgursky/davinci-resolve-mcp` (10 hosts), `alpacahq/alpaca-mcp-server` (extensive host matrix), `exa-labs/exa-mcp-server`, and `upstash/context7` enumerate 10+ hosts in their READMEs with per-host config templates. Raises the maintenance cost but reaches every user.
- **Dispatcher monorepo.** `pathintegral-institute/mcp.science` publishes one PyPI package whose console script routes to multiple internal servers via a subcommand (`uvx mcp-science <server-name>`). One install, many servers.
- **Custom `install.py` replacing pip/uv entirely.** `samuelgursky/davinci-resolve-mcp` and `normaltusker/kotlin-mcp-server` ship a custom Python installer that creates the venv and writes per-host JSON directly. Bypasses PyPI; works across hosts that don't agree on a package manager.
- **Vendor-slug drift.** Perplexity's MCP lives at `ppl-ai/modelcontextprotocol`, not `perplexityai/modelcontextprotocol`. HubSpot's MCP lived at a vendor slug that's since been reorganized. When linking vendor MCPs, verify the slug — the brand-obvious guess often fails.

## Checklist for a new MCP server repo

1. **Pick language + SDK.** Python + FastMCP 2.x for fastest author ergonomics (47/62 Python repos use FastMCP 2.x specifically; 54/62 use FastMCP at any major version); Python + raw `mcp` SDK when reference-level protocol control matters (8/62); TypeScript + `@modelcontextprotocol/sdk` for JS-ecosystem integration (22/26 TS repos); Go/Rust/Kotlin for systems that already live in those languages. No Java, Ruby, PHP, or Swift servers appeared in the sample despite SDKs existing — disclosed gap, not evidence of nonexistence.
2. **Pick transport.** `stdio` as default — every host supports it (92/104 repos). Add `streamable HTTP` only if the server is intended to run remote-hosted or behind a shared URL. Skip SSE; it's deprecated.
3. **Pick distribution mechanism.** `uvx`-launchable PyPI package for Python; `npx -y`-launchable npm package for TS. Add Docker when the server bundles system deps (browsers, ffmpeg, native tools). Publish to PyPI/npm on tag; optionally register with Smithery (14/104) or the official `modelcontextprotocol/registry` (3/104 — docs-prescribed, thin adoption).
4. **Declare the entry point.** Python: `[project.scripts]` → `package.server:main` (42/61). TS: `bin` field in `package.json` → `./dist/index.js`. Avoid bare scripts without a packaged entry point.
5. **Wire the configuration surface.** Environment variables for everything secret; CLI flags for operational mode (`--transport`, `--port`). Document every var and whether users must add it to the host `env:` block.
6. **Implement authentication if remote.** None for stdio (30/104). Static API key via env var for single-tenant stdio (39/104). OAuth 2.1 + PRM + DCR for remote-hosted multi-tenant (28/104; use `mcp-authorization-tutorial.md` as reference).
7. **Write host-integration snippets.** Minimum: Claude Desktop JSON, Claude Code `claude mcp add` invocation, Cursor. Add Windsurf, VS Code, Cline, Zed as bandwidth allows. Per-host config path and shape all differ — snippets are not copy-paste between hosts.
8. **Optionally ship a Claude Code plugin wrapper.** `.claude-plugin/plugin.json` + `.mcp.json` at repo root. Turns the repo into an installable plugin that bundles the server with skills/commands/hooks. Rare today — **5/104** repos ship any `.claude-plugin/` artifact, plus 2/104 ship `.mcp.json` standalone — but the highest-integration path for Claude Code users. Adding `.claude/skills/` or `skills/` without the plugin manifest is a lightweight alternative (3/104).
9. **Add tests and CI.** pytest (30/62 Python) + GitHub Actions (77/82 CI-present repos). For deterministic MCP tests, use the in-memory `Client` pattern from `blog-jlowin-stop-vibe-testing.md`. Separate unit tests from integration tests that need Docker Compose fixtures.
10. **Tag a release.** Semver tag (`v1.0.0`); bump `pyproject.toml` / `package.json` version; push tag; CI publishes. Release-automation workflows appear in 21/70 release-cadence repos.
11. **Publish to the ecosystem registry.** `twine upload` / `npm publish` / `cargo publish` / GitHub release for Go binaries. Language-specific; mandatory for any `uvx <pkg>` / `npx -y <pkg>` launch command to work.
12. **Optionally register in discovery channels.** `modelcontextprotocol/registry` is the official registry (API v0.1, docs-prescribed, community-governed). Smithery, glama.ai, mcpservers.org, and pulsemcp are commercial/community alternates with more inbound traffic today.
13. **Write the README as host-integration-first.** Users installing an MCP server are almost always trying to wire it into a specific host. Put the host config snippets at the top, then the configuration reference, then the capability list. Deprioritize implementation details.
14. **Pick a permissive license.** MIT (58/104) or Apache-2.0 (33/104) are the community defaults. Avoid non-commercial licenses unless deliberate — downstream hosts and integrators cannot redistribute.

## References

Two sources inform this pattern: 104 per-repo structured findings (primary sample) and 43 authoritative context resources (spec, SDK docs, framework docs, host integration pages, registries, best-practice writeups).

### Primary sample (104)

Full breakdown with per-repo annotation lives in `/home/dev/projects/claude-plugins/research/mcp/repos/_INDEX.md`. Categories:

**Official MCP org (2):** [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers), [modelcontextprotocol/kotlin-sdk](https://github.com/modelcontextprotocol/kotlin-sdk).

**Cloud / infrastructure vendors (5):** [awslabs/mcp](https://github.com/awslabs/mcp), [Azure/azure-mcp](https://github.com/Azure/azure-mcp), [cloudflare/mcp-server-cloudflare](https://github.com/cloudflare/mcp-server-cloudflare), [docker/hub-mcp](https://github.com/docker/hub-mcp), [googleapis/mcp-toolbox](https://github.com/googleapis/mcp-toolbox).

**awslabs sub-server drill-down (5):** [aws-api-mcp-server](https://github.com/awslabs/mcp/tree/main/src/aws-api-mcp-server), [aws-documentation-mcp-server](https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server), [bedrock-kb-retrieval-mcp-server](https://github.com/awslabs/mcp/tree/main/src/bedrock-kb-retrieval-mcp-server), [openapi-mcp-server](https://github.com/awslabs/mcp/tree/main/src/openapi-mcp-server), [mcp-lambda-handler](https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler).

**Developer platform vendors (11):** [github/github-mcp-server](https://github.com/github/github-mcp-server), [getsentry/sentry-mcp](https://github.com/getsentry/sentry-mcp), [stripe/agent-toolkit](https://github.com/stripe/agent-toolkit), [apollographql/apollo-mcp-server](https://github.com/apollographql/apollo-mcp-server), [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp), [makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server), [slackapi/slack-mcp-plugin](https://github.com/slackapi/slack-mcp-plugin), [supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp), [neondatabase/mcp-server-neon](https://github.com/neondatabase/mcp-server-neon), [mongodb-js/mongodb-mcp-server](https://github.com/mongodb-js/mongodb-mcp-server), [elastic/mcp-server-elasticsearch](https://github.com/elastic/mcp-server-elasticsearch).

**Additional vendor-owned (8):** [paypal/paypal-mcp-server](https://github.com/paypal/paypal-mcp-server), [redis/mcp-redis](https://github.com/redis/mcp-redis), [ClickHouse/mcp-clickhouse](https://github.com/ClickHouse/mcp-clickhouse), [ppl-ai/modelcontextprotocol](https://github.com/ppl-ai/modelcontextprotocol), [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server), [upstash/context7](https://github.com/upstash/context7), [alpacahq/alpaca-mcp-server](https://github.com/alpacahq/alpaca-mcp-server), [PagerDuty/pagerduty-mcp-server](https://github.com/PagerDuty/pagerduty-mcp-server).

**Frameworks / SDKs / language toolkits (7):** [jlowin/fastmcp](https://github.com/jlowin/fastmcp), [mark3labs/mcp-go](https://github.com/mark3labs/mcp-go), [metoro-io/mcp-golang](https://github.com/metoro-io/mcp-golang), [viant/mcp](https://github.com/viant/mcp), [conikeec/mcpr](https://github.com/conikeec/mcpr), [rust-mcp-stack/rust-mcp-filesystem](https://github.com/rust-mcp-stack/rust-mcp-filesystem), [hugoduncan/mcp-clj](https://github.com/hugoduncan/mcp-clj).

**Relational / document / KV databases (10):** [motherduckdb/mcp-server-motherduck](https://github.com/motherduckdb/mcp-server-motherduck), [jparkerweb/mcp-sqlite](https://github.com/jparkerweb/mcp-sqlite), [hannesrudolph/sqlite-explorer-fastmcp-mcp-server](https://github.com/hannesrudolph/sqlite-explorer-fastmcp-mcp-server), [ktanaka101/mcp-server-duckdb](https://github.com/ktanaka101/mcp-server-duckdb), [teaguesterling/duckdb_mcp](https://github.com/teaguesterling/duckdb_mcp), [HenkDz/postgresql-mcp-server](https://github.com/HenkDz/postgresql-mcp-server), [ahmedmustahid/postgres-mcp-server](https://github.com/ahmedmustahid/postgres-mcp-server), [crystaldba/postgres-mcp](https://github.com/crystaldba/postgres-mcp), [spences10/mcp-turso-cloud](https://github.com/spences10/mcp-turso-cloud), [designcomputer/mysql_mcp_server](https://github.com/designcomputer/mysql_mcp_server).

**Vector / embedding databases (4):** [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant), [chroma-core/chroma-mcp](https://github.com/chroma-core/chroma-mcp), [zilliztech/mcp-server-milvus](https://github.com/zilliztech/mcp-server-milvus), [sajal2692/mcp-weaviate](https://github.com/sajal2692/mcp-weaviate).

**Code / repos / dev tools (3):** [idosal/git-mcp](https://github.com/idosal/git-mcp), [cyanheads/git-mcp-server](https://github.com/cyanheads/git-mcp-server), [bhauman/clojure-mcp](https://github.com/bhauman/clojure-mcp).

**AI / search / RAG / web content (5):** [cyanheads/perplexity-mcp-server](https://github.com/cyanheads/perplexity-mcp-server), [DaInfernalCoder/perplexity-mcp](https://github.com/DaInfernalCoder/perplexity-mcp), [pragmar/mcp-server-webcrawl](https://github.com/pragmar/mcp-server-webcrawl), [shreyaskarnik/huggingface-mcp-server](https://github.com/shreyaskarnik/huggingface-mcp-server), [riza-io/riza-mcp](https://github.com/riza-io/riza-mcp).

**Academic / research data (4):** [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server), [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp), [JackKuo666/PubMed-MCP-Server](https://github.com/JackKuo666/PubMed-MCP-Server), [zongmin-yu/semantic-scholar-fastmcp-mcp-server](https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server).

**Notebooks / data science / ML (5):** [datalayer/jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server), [jbeno/cursor-notebook-mcp](https://github.com/jbeno/cursor-notebook-mcp), [marlonluo2018/pandas-mcp-server](https://github.com/marlonluo2018/pandas-mcp-server), [shibuiwilliam/mcp-server-scikit-learn](https://github.com/shibuiwilliam/mcp-server-scikit-learn), [pathintegral-institute/mcp.science](https://github.com/pathintegral-institute/mcp.science).

**GIS / geospatial / earth data (3):** [mahdin75/gis-mcp](https://github.com/mahdin75/gis-mcp), [isaaccorley/planetary-computer-mcp](https://github.com/isaaccorley/planetary-computer-mcp), [datalayer/earthdata-mcp-server](https://github.com/datalayer/earthdata-mcp-server).

**Kubernetes / container tooling (5):** [rohitg00/kubectl-mcp-server](https://github.com/rohitg00/kubectl-mcp-server), [alexei-led/k8s-mcp-server](https://github.com/alexei-led/k8s-mcp-server), [feiskyer/mcp-kubernetes-server](https://github.com/feiskyer/mcp-kubernetes-server), [ckreiling/mcp-server-docker](https://github.com/ckreiling/mcp-server-docker), [utensils/mcp-nixos](https://github.com/utensils/mcp-nixos).

**Infrastructure / IaC / cloud ops (2):** [severity1/terraform-cloud-mcp](https://github.com/severity1/terraform-cloud-mcp), [baryhuang/mcp-server-aws-resources-python](https://github.com/baryhuang/mcp-server-aws-resources-python).

**Observability / monitoring (2):** [tumf/grafana-loki-mcp](https://github.com/tumf/grafana-loki-mcp), [opensearch-project/opensearch-mcp-server-py](https://github.com/opensearch-project/opensearch-mcp-server-py).

**Security (2):** [mukul975/cve-mcp-server](https://github.com/mukul975/cve-mcp-server), [FuzzingLabs/mcp-security-hub](https://github.com/FuzzingLabs/mcp-security-hub).

**CI/CD (1):** [lanbaoshen/mcp-jenkins](https://github.com/lanbaoshen/mcp-jenkins).

**Enterprise ITSM / CRM (3):** [echelon-ai-labs/servicenow-mcp](https://github.com/echelon-ai-labs/servicenow-mcp), [reminia/zendesk-mcp-server](https://github.com/reminia/zendesk-mcp-server), [DiversioTeam/clickup-mcp](https://github.com/DiversioTeam/clickup-mcp).

**Communications / SaaS integrations (8):** [korotovsky/slack-mcp-server](https://github.com/korotovsky/slack-mcp-server), [duolingo/slack-mcp](https://github.com/duolingo/slack-mcp), [geropl/linear-mcp-go](https://github.com/geropl/linear-mcp-go), [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP), [sandraschi/email-mcp](https://github.com/sandraschi/email-mcp), [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian), [v-3/discordmcp](https://github.com/v-3/discordmcp), [normaltusker/kotlin-mcp-server](https://github.com/normaltusker/kotlin-mcp-server).

**Browsers / automation / media (5):** [executeautomation/mcp-playwright](https://github.com/executeautomation/mcp-playwright), [twolven/mcp-server-puppeteer-py](https://github.com/twolven/mcp-server-puppeteer-py), [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp), [misbahsy/video-audio-mcp](https://github.com/misbahsy/video-audio-mcp), [labeveryday/mcp_pdf_reader](https://github.com/labeveryday/mcp_pdf_reader).

**Home automation (1):** [voska/hass-mcp](https://github.com/voska/hass-mcp).

**Healthcare (1):** [the-momentum/fhir-mcp-server](https://github.com/the-momentum/fhir-mcp-server).

**CMS / content (1):** [thenets/ghost-mcp](https://github.com/thenets/ghost-mcp).

**Translation / localization (1):** [AlwaysSany/deepl-fastmcp-python-server](https://github.com/AlwaysSany/deepl-fastmcp-python-server).

### Authoritative context resources (43)

Full index at `/home/dev/projects/claude-plugins/research/mcp/context-resources/_INDEX.md`. Grouped by type:

**Spec and official docs:** `mcp-specification.md`, `modelcontextprotocol-io-home.md`, `mcp-build-server-tutorial.md`, `mcp-authorization-tutorial.md`.

**Official SDKs:** `python-sdk-readme.md`, `typescript-sdk-readme.md`, `go-sdk-readme.md`, `rust-sdk-readme.md`, `kotlin-sdk-readme.md`.

**Frameworks and reference code:** `fastmcp-readme.md`, `fastmcp-docs.md`, `mcp-servers-monorepo.md`, `mcp-inspector.md`.

**Claude Code plugin packaging:** `claude-code-plugins-reference.md`, `claude-code-plugin-marketplaces.md`, `claude-code-mcp-docs.md`.

**Host integration docs:** `claude-desktop-mcp-setup.md`, `cursor-mcp-docs.md`, `vscode-mcp-docs.md`, `windsurf-mcp-docs.md`, `zed-mcp-docs.md`, `continue-mcp-docs.md`, `cline-mcp-docs.md`, `codex-cli-mcp-docs.md`, `warp-mcp-docs.md`, `gemini-cli-mcp-docs.md`.

**Registries:** `registry-official.md`, `registry-smithery.md`, `registry-glama-ai.md`, `registry-pulsemcp.md`, `registry-mcpservers-org.md`, `registry-mcp-so.md`.

**Awesome lists:** `awesome-mcp-punkpeye.md`, `awesome-mcp-wong2.md`, `awesome-mcp-appcypher.md`.

**Community best-practice writeups:** `blog-15-best-practices-mcp-production.md`, `blog-mcpcat-production-guide.md`, `blog-jlowin-fastmcp-middleware.md`, `blog-jlowin-fastmcp-3.md`, `blog-jlowin-stop-vibe-testing.md`, `blog-mauro-canuto-mcp-ts-production.md`, `blog-simonw-mcp-prompt-injection.md`, `blog-elastic-mcp-attack-defense.md`.

### Sample caveats

- **Language coverage is uneven.** Python (61), TypeScript/JavaScript (26), Go (7), Rust (4), Clojure (2), Kotlin (1), C# (1), C++ as DuckDB extension (1), one remote-only no-primary-language repo. No Java, Ruby, PHP, or Swift servers appeared despite SDKs existing for most — that is a disclosed gap, not a claim of nonexistence.
- **Stars and last-commit dates captured during research may be stale.** MCP moves weekly. Re-verify against GitHub before citing a specific count.
- **Monorepo handling.** `awslabs/mcp` is counted once for repo-level axes (CI, license, default branch); its five drilled-down sub-servers count individually for per-server axes. Other monorepos (`cloudflare/mcp-server-cloudflare`, `modelcontextprotocol/servers`) were not drilled into sub-server depth, so their per-server adoption counts reflect the aggregate rather than each contained server.
- **Framework-vs-server distinction.** `jlowin/fastmcp`, `mark3labs/mcp-go`, `metoro-io/mcp-golang`, `viant/mcp`, `conikeec/mcpr`, `rust-mcp-stack/rust-mcp-filesystem`, `hugoduncan/mcp-clj`, and `modelcontextprotocol/kotlin-sdk` are framework/SDK repos, not standalone servers. `awslabs/mcp-lambda-handler` is a framework for building Lambda-hosted MCP servers. They are included to surface the layout conventions the framework author promotes, but per-server decision axes (entry point, auth, transport) apply less cleanly. Where a framework repo was excluded from a decision tally, the denominator note reflects that.
- **Discovery sampling.** Community-server discovery relied on GitHub search, awesome-list scraping, and cross-references from the context-resources sample. The 104 repos examined here are not claimed to be the full population — they are what surfaced within research budget, filtered for maintained status. Adoption rates here are valid for the sample; global MCP ecosystem rates may differ.
- **Template extraction limits.** Per-repo files were populated from README and surface-visible repo contents. Deep code inspection (source-level audit, actual version pins from `pyproject.toml`/`package.json`) was done for a subset but not uniformly. Claims like "uses FastMCP 2.x" rely on README phrasing or dependency-line quotes and may miss edge cases where the README disagrees with the actual source.
- **Perplexity vendor-slug drift.** `perplexityai/modelcontextprotocol` was the anticipated slug; the actual server lives at `ppl-ai/modelcontextprotocol`. `riza-io/mcp-server` (anticipated) is at `riza-io/riza-mcp`. When linking vendor MCPs, verify the slug.
