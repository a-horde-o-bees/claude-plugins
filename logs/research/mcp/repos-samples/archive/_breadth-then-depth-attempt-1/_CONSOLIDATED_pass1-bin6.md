# Sample

Pass-1 Phase-1a partial for bin 6. Atomic knowledge chunks from `geropl--linear-mcp-go`, `getsentry--sentry-mcp`, `github--github-mcp-server`, `googleapis--mcp-toolbox`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `hugoduncan--mcp-clj`, `idosal--git-mcp`, `isaaccorley--planetary-computer-mcp`, organized by divergence axes. Phase-1b merger will unify with other partials.

## Language and runtime

### Go

Custom Go MCP implementations dominate this bin's Go corner. `github--github-mcp-server` ships a custom Go MCP implementation rooted at `cmd/github-mcp-server` with `server.json` declaring MCP capability. `googleapis--mcp-toolbox` likewise uses a custom Go implementation with `server.json`. `geropl--linear-mcp-go` uses the `mcp-go` SDK (`mark3labs/mcp-go` canonical) — Go 1.23+; Go module versioning typical.

### TypeScript / JavaScript

`getsentry--sentry-mcp` runs on Node with TypeScript 98.3% under a pnpm workspace + Turbo monorepo, MCP TypeScript SDK inferred. `idosal--git-mcp` runs TypeScript/JavaScript on Node.js (npx, pnpm, npm) using React Router 7, Vite, MCP SDK, and Cloudflare Workers (Wrangler) — atypical TS stack centered on edge-runtime deployment.

### Python

`hannesrudolph--sqlite-explorer-fastmcp-mcp-server` is 100% Python on FastMCP 0.4.1 (1.x era), Python 3.6+ floor. `isaaccorley--planetary-computer-mcp` runs Python 87.5% (with TS 11.3% co-located VS Code extension) on raw `mcp` SDK (Anthropic MCP Python implementation), Python version pinned via `.python-version`.

### Clojure

`hugoduncan--mcp-clj` runs Clojure 99.7% on Java runtime against MCP version `2024-11-05` using only Clojure standard library — specific Java version constraints not stated.

### SDK / framework variants

Span includes raw MCP Python SDK, FastMCP 1.x (pre-2.x), MCP TypeScript SDK, mcp-go (mark3labs), custom Go MCP implementations, and a hand-rolled Clojure stack on `org.clojure/data.json` only. [`isaaccorley--planetary-computer-mcp`] notes raw MCP SDK in 2026 as a holdout — many newer servers have migrated to FastMCP. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] anchors the FastMCP 1.x reference case for "how the FastMCP ecosystem looked before the 2.0 split".

## Transport

### stdio

Default for many local-install servers. [`geropl--linear-mcp-go`] selects via `serve` subcommand. [`github--github-mcp-server`] selects via `github-mcp-server stdio` subcommand. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] is implicit — FastMCP CLI installer wires stdio with no explicit flag. [`isaaccorley--planetary-computer-mcp`] is stdio-only implicit. [`hugoduncan--mcp-clj`] selects via `clj -M:stdio-server` profile, recommended for Claude Desktop. [`getsentry--sentry-mcp`] supports stdio for local self-hosted Sentry deployments.

### HTTP / SSE

[`googleapis--mcp-toolbox`] is HTTP-first on port 5000 at `/mcp` endpoint — diverges from the stdio-first convention. [`hugoduncan--mcp-clj`] supports SSE/HTTP via `clj -M:sse-server` (default port 3001, customizable via `--port`). [`idosal--git-mcp`] is HTTP/HTTPS only via cloud endpoint `gitmcp.io`, plus SSE; auto-detected by IDE via direct HTTP URL specification. [`getsentry--sentry-mcp`] supports HTTP via remote service `https://mcp.sentry.dev`. [`github--github-mcp-server`] offers a separately-hosted remote service at `api.githubcopilot.com`.

### In-memory

[`hugoduncan--mcp-clj`] supports in-memory transport explicitly for testing — unusual; flagged as a notable axis.

### Selection mechanism

CLI subcommand or profile is the most common pattern: `serve`, `stdio`, `:stdio-server`, `:sse-server`. [`googleapis--mcp-toolbox`] makes HTTP the default mode of the binary with no per-mode subcommand. [`idosal--git-mcp`] relies on IDE auto-detection from a URL string. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] never exposes selection — FastMCP CLI installer hardcodes stdio.

## Distribution

### Channels observed

| Channel | Samples |
|---------|---------|
| GitHub Releases pre-built binaries | [`geropl--linear-mcp-go`], [`github--github-mcp-server`] (58 releases), [`googleapis--mcp-toolbox`] (Linux AMD64, macOS ARM64/Intel, Windows AMD64) |
| `go install` | [`geropl--linear-mcp-go`], [`googleapis--mcp-toolbox`] |
| Docker image (GHCR / Artifact Registry) | [`github--github-mcp-server`] (`ghcr.io/github/github-mcp-server`), [`googleapis--mcp-toolbox`] (`us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION`), [`geropl--linear-mcp-go`] (Dockerfile present) |
| npm / npx | [`getsentry--sentry-mcp`] (`@sentry/mcp-server`), [`googleapis--mcp-toolbox`] (`@toolbox-sdk/server` shim) |
| Homebrew | [`googleapis--mcp-toolbox`] (`brew install mcp-toolbox`) |
| Source clone + build | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (`fastmcp install`), [`isaaccorley--planetary-computer-mcp`] (`uv sync`), [`idosal--git-mcp`] (`pnpm install`), [`hugoduncan--mcp-clj`] (Git dependency in `deps.edn`) |
| Cloud-hosted SaaS endpoint | [`idosal--git-mcp`] (`gitmcp.io/{owner}/{repo}`), [`getsentry--sentry-mcp`] (`mcp.sentry.dev`), [`github--github-mcp-server`] (`api.githubcopilot.com`) |
| Marketplace plugin (Claude Desktop) | [`getsentry--sentry-mcp`] |
| Shell download script | [`geropl--linear-mcp-go`] (automated download) |

### Multi-channel breadth

[`googleapis--mcp-toolbox`] surfaces 5 distribution channels (binary, Docker, go install, Homebrew, npm shim) — cross-ecosystem discoverability as a deliberate goal. [`getsentry--sentry-mcp`] vends both an npm package and a Claude marketplace plugin distinct from the raw JSON snippet.

### Cross-ecosystem glue

NPM shim wrapping a Go binary — [`googleapis--mcp-toolbox`] ships `@toolbox-sdk/server` (npm) which wraps the Go binary so node-oriented hosts can run a Go server by name.

### Hosted vs local

A clear axis. [`idosal--git-mcp`] is hosted-only (no local install, zero-auth cloud service). [`getsentry--sentry-mcp`] and [`github--github-mcp-server`] are dual-mode: official remote endpoint operated by the vendor alongside a self-run stdio binary. [`geropl--linear-mcp-go`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`] are local-only.

### Pre-`pyproject.toml` packaging

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses pre-`pyproject.toml`-era layout: `requirements.txt` + single `sqlite_explorer.py` script + no packaging. No `[project.scripts]`, no PyPI publish.

## Entry point / launch

### Subcommand-based binary

[`geropl--linear-mcp-go`] uses `serve`, `setup --tool=cline`, `version` subcommands. [`github--github-mcp-server`] uses `stdio` subcommand at `cmd/github-mcp-server/`.

### Profile-based (Clojure deps)

[`hugoduncan--mcp-clj`] launches via `clj -M:stdio-server` / `clj -M:sse-server` / `clj -M:sse-server --port 8080`.

### npx / npm one-liners

[`getsentry--sentry-mcp`] uses `npx @sentry/mcp-server@latest --access-token=...`.

### Python module invocation

[`isaaccorley--planetary-computer-mcp`] launches via `python -m planetary_computer_mcp.server` — module-level invocation rather than console script. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses `fastmcp install sqlite_explorer.py` then host launches via configured MCP command, or direct run via `uv run --with fastmcp --with uvicorn fastmcp run /path/to/sqlite_explorer.py`.

### Wrapper scripts and setup ergonomics

[`geropl--linear-mcp-go`]'s `setup --tool=cline` subcommand automates host configuration — rare among MCP servers, most expect users to hand-edit JSON. [`googleapis--mcp-toolbox`] uses `--config "tools.yaml"` flag with the same binary across Docker / npm shim / native invocations. [`getsentry--sentry-mcp`] surfaces monorepo workspace scripts (`pnpm -w run cli`).

## Configuration surface

### Env vars

Common pattern. [`geropl--linear-mcp-go`]: `LINEAR_API_KEY` (required). [`github--github-mcp-server`]: `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_HOST`, `GITHUB_TOOLSETS`, `GITHUB_TOOLS`, `GITHUB_READ_ONLY`, `GITHUB_INSIDERS`. [`getsentry--sentry-mcp`]: `SENTRY_ACCESS_TOKEN`, `EMBEDDED_AGENT_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_HOST`, `MCP_DISABLE_SKILLS`. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `SQLITE_DB_PATH` (required; only config knob).

### CLI flags

[`geropl--linear-mcp-go`]: `--write-access`, `--auto-approve`, `--tool`. [`github--github-mcp-server`]: `--toolsets`, `--tools`, `--read-only`, `--lockdown-mode`, `--dynamic-toolsets`. [`googleapis--mcp-toolbox`]: `--config`, `--disable-reload`. [`hugoduncan--mcp-clj`]: `--port`.

### YAML manifest

[`googleapis--mcp-toolbox`] uses `tools.yaml` as primary configuration surface — declares sources, tools, toolsets, and prompts. Admins configure by editing YAML rather than writing code.

### Host JSON config

[`hugoduncan--mcp-clj`] integrates via `claude_desktop_config.json` with bash interpreter, project path, and env vars in config. [`idosal--git-mcp`] documents JSON `mcp.json` for 8 IDEs (Claude Desktop, Cursor, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI). [`isaaccorley--planetary-computer-mcp`] uses function-call parameters + environment.

### Hot reload

[`googleapis--mcp-toolbox`] dynamic reloading on by default; `--disable-reload` opts out — implies state survives across configuration changes; unusual for MCP servers (most re-exec).

## Authentication

### Static API key / token (env-supplied)

[`geropl--linear-mcp-go`] (`LINEAR_API_KEY`), [`github--github-mcp-server`] (`GITHUB_PERSONAL_ACCESS_TOKEN`), [`getsentry--sentry-mcp`] (Sentry user tokens with scopes `org:read project:read project:write team:read team:write event:write`).

### OAuth (hosted-only)

[`github--github-mcp-server`] supports OAuth for the remote hosted server (VS Code 1.101+ has native support). [`getsentry--sentry-mcp`] supports OAuth App for the hosted `mcp.sentry.dev` endpoint.

### Delegated to underlying source auth

[`googleapis--mcp-toolbox`] delegates to database auth schemes — IAM for Google Cloud (ambient/ADC credentials), plus standard credentials for PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Elasticsearch, others.

### None / public

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (local SQLite, no credentials), [`isaaccorley--planetary-computer-mcp`] (Planetary Computer STAC API publicly accessible), [`idosal--git-mcp`] (zero-auth public-repo cloud service), [`hugoduncan--mcp-clj`] (no explicit mechanism documented; assumes transport-layer security).

## Multi-tenancy

### Single-user per process

[`geropl--linear-mcp-go`] (API key ties to one Linear workspace), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (one SQLite file per server instance pinned via env var), [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`].

### Single-user stdio + per-user OAuth on hosted

[`getsentry--sentry-mcp`] (single-user per stdio process, per-user OAuth on hosted), [`github--github-mcp-server`] (one PAT one identity for stdio, per-user OAuth in hosted mode).

### Per-process / multi-source

[`googleapis--mcp-toolbox`] is per-process; manifest can declare multiple sources (multi-database but not multi-user); HTTP endpoint serves any connected MCP client.

### Per-repo parameterized tenant

[`idosal--git-mcp`] uses per-repository tenant parameterized by owner/repo via URL — cloud-hosted single service with multi-repo support.

## Capabilities exposed

### Tools-only

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (3 tools: `read_query`, `list_tables`, `describe_table`; no resources/prompts/sampling/roots). [`isaaccorley--planetary-computer-mcp`] (2 tools: `download_data`, `download_geometries`). [`idosal--git-mcp`] (4 tools: `fetch_<repo>_documentation`, `search_<repo>_documentation`, `search_<repo>_code`, `fetch_url_content`). [`geropl--linear-mcp-go`] (read-only default `linear_search_issues`, `linear_get_user_issues`, `linear_get_issue`, `linear_get_issue_comments`, `linear_get_teams`; write-gated `linear_create_issue`, `linear_update_issue`, `linear_add_comment`, `linear_reply_to_comment`, `linear_update_issue_comment`).

### Tools + first-class prompts

[`googleapis--mcp-toolbox`] surfaces tools, toolsets, AND prompts via YAML manifest — most MCP servers concentrate on tools; this one surfaces the prompts capability too.

### Tools + "Skills" abstraction

[`getsentry--sentry-mcp`] makes "Skills" first-class — `MCP_DISABLE_SKILLS` env var toggles skill subsets (skills live under `.agents/skills/`). README positions the project as "primarily designed for human-in-the-loop coding agents." A higher-level behavioral primitive distinct from tools.

### Embedded LLM invocation

[`getsentry--sentry-mcp`] supports an embedded agent provider — `EMBEDDED_AGENT_PROVIDER` ('openai' | 'anthropic') with provider-specific API keys lets the MCP server invoke an LLM internally. Unusual; most MCP servers are pure tool-callers.

### Built-in REPL evaluation

[`hugoduncan--mcp-clj`] ships `clj-eval` (evaluate Clojure expressions) and `ls` (list files with gitignore support, depth/limit options); custom tools can be added dynamically via API.

### Toolset gating

[`github--github-mcp-server`] ships ~100+ tools across 20+ toolsets (repos, issues, pull_requests, actions, etc.) with granular toolset/tool gating via flags. Read-only mode, lockdown mode (filters public repo content), dynamic toolsets allowing runtime discovery.

### URL-aware operations

[`geropl--linear-mcp-go`] accepts Linear comment URLs directly without manual ID extraction — a UX choice rather than capability.

### Read-only-by-default

[`geropl--linear-mcp-go`] writes gated behind explicit `--write-access` flag. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] enforces read-only at the tool layer (query validation + row caps), not DB-level. [`github--github-mcp-server`] surfaces `--read-only` flag.

### LLM-targeted output synthesis

[`isaaccorley--planetary-computer-mcp`] generates visualizations for LLM analysis — server synthesizes images for the model to interpret. Multi-format outputs (GeoTIFF, GeoParquet, Zarr) — uncommon in MCP servers; implies large-file handling.

## Observability

### Conventions and gaps

Most samples in this bin do not document logging destination/format. [`geropl--linear-mcp-go`]: not extracted; Go stdio servers typically log to stderr. [`github--github-mcp-server`]: likely stderr per Go-binary convention. [`googleapis--mcp-toolbox`]: standard Go stderr logging likely. [`isaaccorley--planetary-computer-mcp`]: not documented. [`hugoduncan--mcp-clj`]: no explicit observability documented. [`idosal--git-mcp`]: not documented; presumed server-side. [`getsentry--sentry-mcp`]: not explicitly extracted.

### Stdio cleanliness pressure

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] explicitly notes "progress output suppression for clean JSON responses" as a deliberate behavior — reflects stdio-protocol cleanliness pressure where any stray stdout corrupts the JSON-RPC stream.

## Host integrations

### Claude Desktop

Documented as a host config target by [`geropl--linear-mcp-go`] (Cline emphasis, not Desktop directly), [`github--github-mcp-server`] (JSON snippet using Docker or local binary), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (via FastMCP CLI install), [`hugoduncan--mcp-clj`] (sample `claude_desktop_config.json`), [`idosal--git-mcp`], [`getsentry--sentry-mcp`] (as marketplace plugin).

### Claude Code

[`getsentry--sentry-mcp`] integration documented. [`googleapis--mcp-toolbox`] listed as compatible client. [`hugoduncan--mcp-clj`] not explicitly documented.

### VS Code / VS Code MCP

[`github--github-mcp-server`] VS Code 1.101+ native MCP support with OAuth or PAT auth. [`isaaccorley--planetary-computer-mcp`] ships a parallel TypeScript VS Code extension under `vscode-extension/`. [`idosal--git-mcp`] documents JSON `mcp.json` for VSCode.

### Cursor

[`getsentry--sentry-mcp`], [`github--github-mcp-server`] (Docker-based config with PAT env injection), [`idosal--git-mcp`].

### Windsurf

[`github--github-mcp-server`] (Docker-based with PAT env injection), [`idosal--git-mcp`].

### JetBrains IDEs

[`github--github-mcp-server`] (Docker-based with PAT env injection).

### Cline

[`geropl--linear-mcp-go`] (primary; dedicated `setup --tool=cline`), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (manual MCP configuration example with `"command": "uv"`, `"args": ["run", "--with", "fastmcp", ...]`), [`idosal--git-mcp`].

### Gemini CLI / Google Antigravity / Codex

[`googleapis--mcp-toolbox`] ships in-repo `gemini-extension.json` and lists Google Antigravity, Claude Code, Codex as compatible clients.

### Highlight AI / Augment Code / Msty AI

[`idosal--git-mcp`] documents JSON `mcp.json` configs for these clients alongside the more common ones.

### Other extension points

[`geropl--linear-mcp-go`] reachable via MCP Registry; `--tool` flag is a scoped extension point (currently only `cline`, but signals plan to automate other host configurations).

## Claude Code plugin wrapper

### Present in-repo

[`getsentry--sentry-mcp`] ships both `.claude-plugin/` directory and `.mcp.json` at repo root — full Claude plugin wrapper in-repo. The server vends itself as a Claude plugin, not just a raw MCP binary. Rare; most servers leave host integration to external config.

### Absent

[`geropl--linear-mcp-go`], [`github--github-mcp-server`] (host integration via external `claude_desktop_config.json`), [`googleapis--mcp-toolbox`] (only `gemini-extension.json` shipped), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`idosal--git-mcp`], [`isaaccorley--planetary-computer-mcp`].

## Tests

### Frameworks

| Framework | Samples |
|-----------|---------|
| go-vcr (recorded HTTP cassettes) | [`geropl--linear-mcp-go`] (cassettes in `testdata/`; live test workspace `linear.app/linear-mcp-go-test` for re-recording; flags `-record=true`, `-recordWrites=true`) |
| Go stdlib testing | [`github--github-mcp-server`] (E2E in `e2e/`), [`googleapis--mcp-toolbox`] (`/tests`) |
| pytest | [`isaaccorley--planetary-computer-mcp`] (`uv run pytest`, `tests/`) |
| Vitest + Playwright | [`idosal--git-mcp`] (`vitest.config.ts` units, `playwright.config.ts` E2E, `npm run test`) |
| pnpm test + eval harness | [`getsentry--sentry-mcp`] (`pnpm test` units, `pnpm eval` evaluations/scenario tests; MCP Inspector for local testing) |
| Clojure tests.edn + clj-kondo | [`hugoduncan--mcp-clj`] (testing investigation notes; clj-kondo lint) |
| None observed | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] |

### Notable patterns

[`geropl--linear-mcp-go`] go-vcr cassette testing: full integration tests run offline against recorded fixtures — reproducible without Linear credentials. [`getsentry--sentry-mcp`] evaluation harness alongside unit tests — distinguishes behavioral regression from code regression.

## CI

### GitHub Actions

[`geropl--linear-mcp-go`] (automated testing on pushes/PRs, automated releases on version tags), [`github--github-mcp-server`] (workflows present, contents not enumerated), [`googleapis--mcp-toolbox`] (`.ci/` plus `.github/workflows/`, `.golangci.yaml` lint), [`idosal--git-mcp`] (`e2e-tests.yml`, `run-tests.yml`), [`isaaccorley--planetary-computer-mcp`] (configured), [`hugoduncan--mcp-clj`] (likely; `cliff.toml` for release notes), [`getsentry--sentry-mcp`] (implied by monorepo standard).

### None

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (no `.github/workflows`).

## Container / packaging artifacts

### Dockerfile present

[`geropl--linear-mcp-go`] (Dockerfile + `.devcontainer/` for dev), [`github--github-mcp-server`] (multi-platform Dockerfile, no compose/Helm/brew), [`googleapis--mcp-toolbox`] (Dockerfile + Homebrew formula, external tap inferred).

### Cloud-native deployment

[`idosal--git-mcp`] no Dockerfile; Cloudflare Workers cloud-native deployment.

### None observed

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`], [`getsentry--sentry-mcp`] (not explicitly documented).

## Repo layout

### Single-package

[`geropl--linear-mcp-go`] (Go: `cmd/` + `pkg/`), [`github--github-mcp-server`] (single Go module rooted at `cmd/github-mcp-server` with supporting packages, `server.json` at root), [`googleapis--mcp-toolbox`] (single Go module: `/cmd`, `/docs`, `/internal`, `/tests`, `/.ci`, `/.github`, `/.hugo`, `/.gemini`; `.gitmodules` present), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (single-file script `sqlite_explorer.py` with requirements + docs), [`idosal--git-mcp`] (single-package React/TS with Cloudflare integration: `app/`, `src/`, `static/`, `tests/`, `dist/`, `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts`).

### Monorepo

[`getsentry--sentry-mcp`] (pnpm workspaces + Turbo; multiple packages under `/packages`; `.agents/skills/` for skill definitions; `.claude-plugin/` and `.mcp.json` at root).

### Polylith-style modular (Clojure)

[`hugoduncan--mcp-clj`] (`bases/`, `components/`, `projects/` + supporting `design/`, `dev/`, `development/`, `doc/`, `spec/`, `scripts/`; `deps.edn`, `tests.edn`, `cliff.toml`, `.cljstyle`; `.clj-kondo/`, `.github/`, `.claude/`, `.mcp-vector-search/`).

### Mixed-language monorepo

[`isaaccorley--planetary-computer-mcp`] (monorepo-ish: Python `src/` with `core/`, `tools/`, `server.py`, plus parallel `vscode-extension/` TypeScript subproject).

## Notable structural choices

### Read-only-by-default safety posture

[`geropl--linear-mcp-go`] gates writes behind `--write-access` flag rather than being default. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] enforces read-only at the tool layer (query validation + row caps). [`github--github-mcp-server`] offers `--read-only` flag. More conservative than most MCPs which ship full capabilities unconditionally.

### Auto-approve configurability

[`geropl--linear-mcp-go`] users can mark specific tools safe to run without per-call confirmation.

### Setup ergonomics

[`geropl--linear-mcp-go`]'s `setup` subcommand replaces manual JSON config editing — rare; most expect users to hand-edit JSON.

### Dynamic reloading

[`googleapis--mcp-toolbox`] dynamic reloading on by default; `--disable-reload` opts out — implies state survives across configuration changes.

### Toolset gating + behavior modes

[`github--github-mcp-server`] surfaces `--read-only`, `--lockdown-mode`, `--insiders` as behavior envelopes rather than capability toggles, separating policy from toolset selection. `--dynamic-toolsets` exposes runtime-discoverable tools, affecting how hosts cache tool listings.

### Cloud-hosted SaaS endpoint

[`idosal--git-mcp`] removes installation friction. Zero-auth model for public repos. React Router 7 + Vite frontend, Biome unified lint/format. Parameterized repository endpoints — one deployment serves every GitHub repo.

### Hosted + local hybrid

[`getsentry--sentry-mcp`], [`github--github-mcp-server`] — official remote MCP endpoint operated by vendor alongside self-run stdio binary.

### Embedded LLM invocation

[`getsentry--sentry-mcp`] server-internal LLM invocation as architecture pattern — shifts some "agent" responsibility inside the MCP boundary.

### Skills as bundled capability layer

[`getsentry--sentry-mcp`] Skills toggleable per-deployment via `MCP_DISABLE_SKILLS`. A higher-level behavioral primitive distinct from tools. Skills live in `.agents/skills/`.

### Co-located non-MCP integration

[`isaaccorley--planetary-computer-mcp`] ships a VS Code extension alongside the MCP server — parallel non-MCP integration path in the same repo.

### LLM-targeted output synthesis

[`isaaccorley--planetary-computer-mcp`] generates visualizations for LLM analysis — server synthesizes images for the model to interpret.

### Polylith-style modular architecture

[`hugoduncan--mcp-clj`] bases/components/projects — advanced modular organization. Vector search integration (`.mcp-vector-search/`).

### Minimal dependencies

[`hugoduncan--mcp-clj`] only `org.clojure/data.json` for full MCP implementation. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] FastMCP only. Self-contained Clojure REPL evaluation without external deps.

### Single-file server script

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] keeps surface tiny.

### Two-tool minimal interface

[`hugoduncan--mcp-clj`] — `clj-eval` + `ls` only, contrasted with 50+ tools in clojure-mcp.

### Declarative tool authoring

[`googleapis--mcp-toolbox`] YAML manifest as primary configuration surface — admins define tools without writing code, distinct from code-defined MCP servers.

### Multi-database via sources abstraction

[`googleapis--mcp-toolbox`] same binary speaks to 8+ databases via `sources` abstraction; tool authoring is declarative on top of that.

### HTTP-first transport diverging from stdio convention

[`googleapis--mcp-toolbox`] HTTP at `:5000/mcp` — explicit divergence from stdio-first convention.

### Gemini-first integration shape

[`googleapis--mcp-toolbox`] in-repo `gemini-extension.json` and `.gemini/` directory reflect project's origin at Google; other hosts consume the generic HTTP endpoint.

## Example client / developer ergonomics

### MCP Inspector usage

[`getsentry--sentry-mcp`] called out in README with `pnpm -w run cli` for manual CLI testing. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] does not; FastMCP CLI install is the primary dev ergonomic.

### Sample host configs in-repo

[`geropl--linear-mcp-go`] `setup --tool` automates JSON config editing. [`github--github-mcp-server`] ships `.vscode/`. [`googleapis--mcp-toolbox`] `gemini-extension.json` + `server.json`. [`hugoduncan--mcp-clj`] sample `claude_desktop_config.json` in README. [`idosal--git-mcp`] dev scripts + Playwright E2E + README examples.

### Pre-commit / lint

[`isaaccorley--planetary-computer-mcp`] `uv run pre-commit run --all-files`. [`googleapis--mcp-toolbox`] `.golangci.yaml`. [`github--github-mcp-server`] `.golangci.yml`. [`idosal--git-mcp`] Biome unified linting/formatting. [`hugoduncan--mcp-clj`] clj-kondo + `.cljstyle`.

### Embedded LLM-context docs

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses `fastmcp-documentation.txt` + `mcp-documentation.txt` in repo — embedded LLM-context docs.

### Eval harness

[`getsentry--sentry-mcp`] `pnpm eval` for regression testing against model outputs.

### Memory-bank convention

[`geropl--linear-mcp-go`] `memory-bank/` directory suggests author uses Cline's memory-bank convention — evidence of dogfooding.

## Python-specific

### SDK / framework variant

| Variant | Samples |
|---------|---------|
| FastMCP 1.x (pre-2.x) — `fastmcp==0.4.1` pinned | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] |
| Raw `mcp` SDK (Anthropic Python implementation) | [`isaaccorley--planetary-computer-mcp`] |

### Packaging

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: NO pyproject.toml — only `requirements.txt` + single `sqlite_explorer.py`. No build backend, no lock file, pip/venv convention. [`isaaccorley--planetary-computer-mcp`]: uv-based workflow, `uv.lock` likely (uv sync convention), version manager via uv + `.python-version`.

### Entry point

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: no `[project.scripts]`; run via `fastmcp install sqlite_explorer.py` or `fastmcp run`. Cline config: `"command": "uv"`, `"args": ["run", "--with", "fastmcp", "--with", "uvicorn", "fastmcp", "run", "/path/to/sqlite_explorer.py"]`. [`isaaccorley--planetary-computer-mcp`]: `__main__.py` (module invoked with `python -m`), no console-script names surfaced.

### Install workflow expected of end users

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `fastmcp install sqlite_explorer.py --name "..." -e SQLITE_DB_PATH=...` — uses FastMCP CLI installer; no pip-install path. [`isaaccorley--planetary-computer-mcp`]: source clone + `uv sync`.

### Async and tool signatures

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: FastMCP-decorated functions (sync and async supported in 0.4.1). [`isaaccorley--planetary-computer-mcp`]: likely async (STAC clients tend to be async).

### Type / schema strategy

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: FastMCP auto-derived from type hints. [`isaaccorley--planetary-computer-mcp`]: Pydantic via MCP SDK; schema auto-derived.

### Notable Python-specific choices

[`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `fastmcp install` registers server with Claude Desktop directly — distinct from `uvx` or manual config editing. Pre-`pyproject.toml`-era reference case for "how the FastMCP ecosystem looked before the 2.0 split".

[`isaaccorley--planetary-computer-mcp`]: `python -m module.server` launch pattern — module-level invocation rather than console script. Raw MCP SDK in 2026 — many newer servers have migrated to FastMCP; this one stays on the lower-level SDK.

## Unanticipated axes observed

- **Tool-catalog mutability** — [`github--github-mcp-server`]'s `--dynamic-toolsets` exposes runtime-discoverable tools rather than fixed catalog at startup; affects how hosts cache tool listings
- **Per-feature behavior modes** — [`github--github-mcp-server`] `--read-only`, `--lockdown-mode`, `--insiders` act as behavior envelopes rather than capability toggles, separating policy from toolset selection
- **Hosted + local hybrid as distribution strategy** — [`github--github-mcp-server`], [`getsentry--sentry-mcp`]
- **Cloud-hosted SaaS endpoint** — [`idosal--git-mcp`] axis: hosted vs local installation; parameterized repository endpoints (one deployment serves every GitHub repo)
- **Server-internal LLM invocation** — [`getsentry--sentry-mcp`] shifts "agent" responsibility inside the MCP boundary; unusual
- **Skills as bundled capability layer** — [`getsentry--sentry-mcp`] higher-level behavioral primitive distinct from tools
- **In-repo Claude plugin wrapper** — [`getsentry--sentry-mcp`] rare; most servers leave host integration to external config
- **Evaluation discipline alongside unit tests** — [`getsentry--sentry-mcp`] `pnpm eval` as peer of `pnpm test`
- **Declarative tool authoring via YAML manifest** — [`googleapis--mcp-toolbox`] different authoring surface from code-defined servers
- **Prompts as first-class manifest concept** — [`googleapis--mcp-toolbox`] alongside tools
- **Hot reloading as built-in** — [`googleapis--mcp-toolbox`] state survives across configuration changes
- **NPM shim wrapping a Go binary** — [`googleapis--mcp-toolbox`] `@toolbox-sdk/server` as cross-ecosystem glue
- **Co-located VS Code extension with MCP server** — [`isaaccorley--planetary-computer-mcp`] mixed-language repo for editor integration outside MCP
- **LLM-targeted visualization generation** — [`isaaccorley--planetary-computer-mcp`] not just data retrieval; deliberate design choice
- **Vector search integration** — [`hugoduncan--mcp-clj`] `.mcp-vector-search/` suggests semantic/similarity search capabilities
- **Polylith architecture** — [`hugoduncan--mcp-clj`] bases/components/projects modular organization
- **In-memory transport for testing** — [`hugoduncan--mcp-clj`] unusual
- **Two-tool minimal interface vs. 50+ tools** — [`hugoduncan--mcp-clj`] outlier among Clojure MCP options
- **Setup subcommand as scoped extension point** — [`geropl--linear-mcp-go`] `--tool=cline` flag signals plan to automate other host configurations
- **go-vcr cassette testing for offline integration** — [`geropl--linear-mcp-go`] full integration tests run without live credentials
- **Memory-bank dogfooding** — [`geropl--linear-mcp-go`] `memory-bank/` evidence author uses Cline's convention themselves
- **Stdio cleanliness pressure** — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] explicit "progress output suppression" as design concern
- **GHCR as primary distribution channel** — [`github--github-mcp-server`] `docker run` is canonical install path, not `go install`

## Gaps observed across bin

- License content frequently not surfaced (LICENSE file not fetched in [`getsentry--sentry-mcp`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`])
- Logging destination/format rarely documented; most samples assume stderr by language convention
- Specific Go / Java / Node version constraints often unspecified
- CI workflow contents typically not enumerated within budget
- Whether `server.json` is consumed by MCP clients beyond identifying capability vs purely metadata — unclear ([`github--github-mcp-server`], [`googleapis--mcp-toolbox`])
- Custom tool registration API patterns documented as "via API" but not detailed ([`hugoduncan--mcp-clj`])
