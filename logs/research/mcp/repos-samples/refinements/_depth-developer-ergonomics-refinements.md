# Depth Pass Refinements — Sample > Developer ergonomics

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > Developer ergonomics > Linter and type-checker stack` — current description names runtime-typical linters (ruff, ESLint+Prettier, mypy/pyright, biome, clippy) but the corpus shows the lint perimeter routinely extends beyond code. `datalayer--earthdata-mcp-server` adds `mdformat`+`mdformat-gfm` (markdown linting), `sandraschi--email-mcp` adds `Bandit` (security linting), and `awslabs--mcp` adds secret-scan hooks via pre-commit. Several samples (`crystaldba--postgres-mcp`, `modelcontextprotocol--servers`) pin exact tool versions, signalling lockstep dev-tool discipline. Suggested addition: "Lint perimeter often extends to markdown (`mdformat`), security (`Bandit`), and secret-scanning hooks; some projects pin exact linter versions (`ruff==0.14.13`, `pyright==1.1.408`) to prevent dev-environment drift across contributors."

`Sample > Developer ergonomics > Sample MCP client configs in repo` — current description scopes to "ready-to-paste configs for various hosts, plus inline JSON snippets in README" but the bucket has absorbed two adjacent artifact types: (1) `.env.example` files which are server-side environment templates not host-client configs, and (2) auto-generated host-config files emitted by an installer (normaltusker's `mcp_config_claude.json`/`mcp_config_vscode.json`). Suggested sharpening: scope description to "host-side JSON snippets (Claude Desktop, Cursor, Windsurf, `.vscode/mcp.json`) shipped as copy-paste onboarding aids in `examples/` or README." Move `.env.example` exemplars out (see Mis-placed samples). Note auto-generated host configs as a related but distinct sub-pattern.

`Sample > Developer ergonomics > \`pre-commit\` framework` — heading and description bias toward the `pre-commit` package, but 2 of 9 samples use alternatives (`GLips--Figma-Context-MCP`: lefthook; `jlowin--fastmcp`: `prek`, a pre-commit replacement). The current description acknowledges this in a trailing aside ("Git hooks via lefthook or similar are an alternative") but the path name reinforces a single framework. Suggested rename + sharpening: "Git-hook orchestration framework — `pre-commit` is dominant, with `lefthook` and `prek` (a pre-commit replacement) as alternatives. Standardizes lint, format, secret-scan, and commit-message checks at commit time."

`Sample > Developer ergonomics > Inspector/debug tooling references` — current description ("README points to MCP Inspector or similar debuggers") understates. Cross-corpus shows three distinct invocation patterns: (a) external launch via `npx @modelcontextprotocol/inspector` (mukul975, ktanaka101), (b) framework-integrated launch via `fastmcp dev <server.py>` (qdrant) or `mcp[cli]` (openags, shreyaskarnik), (c) Inspector wired as the test driver (jparkerweb: `npm test`). One sample (`pragmar--mcp-server-webcrawl`) explicitly substitutes an in-process `--interactive` REPL for Inspector. Suggested sharpening: "MCP Inspector references span external launch (`npx @modelcontextprotocol/inspector`), framework-integrated launch (`fastmcp dev`, `mcp[cli]`), and Inspector-as-test-driver (`npm test`). A few projects bypass Inspector with an in-repo interactive REPL."

`Sample > Developer ergonomics > Setup subcommands on the MCP binary` — current description focuses on host-config setup (`set-api-key`, `check-config`, `setup --tool=cline`) but `conikeec--mcpr` exhibits a distinct sub-pattern: project scaffolding (`mcpr generate-project`) for new MCP server stubs. Same mechanism (subcommands on the binary), different intent (operator setup vs developer scaffolding). Suggested sharpening: split description into two related sub-patterns — operator-setup subcommands (`set-api-key`, `setup --tool=...`, `check-config`, `test-connection`) and developer-scaffolding subcommands (`generate-project`, server/client stub generation).

`Sample > Developer ergonomics > Examples directory with many patterns` — current description ("`examples/` with 20+ runnable patterns covering the full surface") fits SDK-shaped repos like `mark3labs--mcp-go` and `viant--mcp` but overstates for samples like `redis--mcp-redis` ("`examples/` directory for usage demos") and `sandraschi--email-mcp` ("`examples/` directory present") which are minimal. The "many patterns" qualifier doesn't survive cross-corpus inspection. Suggested sharpening: drop the "20+" framing from the path-level description; describe the range — "from a single illustrative example up to 20+ runnable patterns covering client, server, transports, OAuth, roots, sampling, and structured tools. Larger collections appear in SDK repos where adoption hinges on showing each primitive in real code."

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > Developer ergonomics > Programmatic embedding API` — two distinct sub-patterns: (a) server-in-host embedding via `createConnection()` / `NewMCPServer()` where the MCP server runs inside a host process (microsoft--playwright-mcp, viant--mcp, 2 samples), and (b) tool-schema export bypassing MCP transport entirely (supabase-community: `createToolSchemas()` for Vercel AI SDK consumers, 1 sample). Different audiences (host-app developers vs AI-SDK consumers). With only 3 samples total, fold into description rather than split: "Two flavors — embed-server-in-host (`createConnection()`, `NewMCPServer()`) for processes that want MCP server functionality without subprocess; or tool-schema re-export (`createToolSchemas()`) for AI-SDK consumers who want the tool definitions without the MCP transport."

`Sample > Developer ergonomics > Custom installer-orchestrator` — both samples (normaltusker, samuelgursky) center on `install.py` that handles env setup + dependency install + per-host config generation. The pattern is consistent: bespoke Python installer replacing pip/uv with `--dry-run`/`--no-venv`/`--full`/`--clients` flags and emits host-side configs as a side effect. Fold into description: "Bespoke `install.py` replacing pip/uv — typically combines venv creation, dependency install, and per-host config emission (Claude Desktop, VS Code, Cursor, generic) in a single guided flow. Flags often include `--dry-run`, `--no-venv`, `--full`, `--clients <list>`."

`Sample > Developer ergonomics > Sample MCP client configs in repo` — auto-generated configs (normaltusker's `mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json`) are produced by the installer rather than written by hand. Same artifact shape but different provenance. 1 sample only — fold into description as a sub-note that some configs ship hand-curated in `examples/` while others are emitted by a `Custom installer-orchestrator`.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

`Sample implementations directory` + `Examples directory with many patterns` — the only sample under `Sample implementations directory` (modelcontextprotocol--kotlin-sdk: "`samples/` directory with end-to-end mini-apps covering various transports/configurations") is structurally indistinguishable from large-scale `examples/` collections (mark3labs--mcp-go: "20+ runnable patterns covering the full surface"). Both are "directory of runnable patterns demonstrating SDK surface." The naming difference (`samples/` vs `examples/`) is the only delta and is incidental. Canonical name: keep `Examples directory with many patterns` (more inclusive); fold the kotlin-sdk sample under it as a `samples/`-named variant. Net effect: one path goes from 1 sample to 9, eliminates a low-value singleton bucket.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

(none proposed — sub-axes flagged above are folded into descriptions rather than split, given small supporting counts)

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

`mukul975--cve-mcp-server.md` currently under `Sample MCP client configs in repo` better fits `Configuration delivery > Dotenv file` because the supporting evidence is "`.env.example` for key configuration shipped alongside the server" — a dotenv template for server env vars, not a host-side MCP client config snippet.

`openags--paper-search-mcp.md` currently under `Sample MCP client configs in repo` better fits `Configuration delivery > Dotenv file` because the supporting evidence is "`.env.example` shipped alongside the server" — same dotenv-template pattern. The same sample's separate Inspector reference is fine; the client-configs placement is the issue.

`reminia--zendesk-mcp-server.md` currently under `Sample MCP client configs in repo` better fits `Configuration delivery > Dotenv file` because the supporting evidence is "`.env.example` as dev-config template" — explicitly framed as a dotenv template, not a client config.

`rust-mcp-stack--rust-mcp-filesystem.md` currently under `PowerShell + batch scripts` better fits `Distribution channel` (or a related installer-script sub-axis) because the supporting evidence describes "PowerShell installer for Windows; POSIX shell installer for Unix — paired platform-native installers" — a user-facing install-script delivery mechanism rather than dev-build automation. The other two samples under `PowerShell + batch scripts` (jbeno: `run_tests.sh`/`run_tests.ps1`; sandraschi: `build.ps1`/`start.ps1`/`build_mcpb.bat`) are clearly developer-facing build/test scripts. Reconciler may want to verify whether `Distribution channel` already has an "installer scripts" path or whether this needs a new home.

`chroma-core--chroma-mcp.md` currently under `MCP framework dev config` weakly fits the path. Supporting evidence is "`mcp` CLI via `mcp[cli]` extra; `.env` example committed" — `mcp[cli]` is an installer extra (closer to `Inspector/debug tooling references` since `mcp[cli]` is the canonical Inspector launcher) and `.env example committed` belongs in `Configuration delivery > Dotenv file`. Neither is a framework dev-config file like `fastmcp.json`. Reconciler should consider moving this sample to one of those paths and leaving the `MCP framework dev config` path with the two cleaner exemplars (ClickHouse, hannesrudolph).

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

Aggregator/monorepo repos (`awslabs--mcp`, `modelcontextprotocol--servers`, `mongodb-js--mongodb-mcp-server`) cluster on multiple ergonomics paths simultaneously — pre-commit + linter stack + custom eslint rules + per-server READMEs with client snippets. Single-server repos rarely take all of these. The corpus shows aggregators effectively pay a higher fixed cost in dev tooling because they're absorbing many subprojects' conventions.

There is a visible split between SDK-shaped repos (`fastmcp`, `mark3labs/mcp-go`, `metoro-io/mcp-golang`, `viant/mcp`, `kotlin-sdk`, `mcpr`) and server-shaped repos in this role: SDK repos disproportionately ship `examples/`, `samples/`, and programmatic embedding APIs; server repos disproportionately ship sample MCP client configs. This is intuitive but not surfaced in the role-level description — the role currently treats every ergonomics affordance as available to any project, when in fact the consumer base shapes which affordances appear. Could be framed in the role-level prose: "Specific ergonomics affordances split along SDK-vs-server lines — SDK repos lean into examples and embedding APIs; server repos lean into ready-to-paste host configs and Inspector references."

The dev-iteration entry point varies — Makefile (9), Justfile (1), `uv run` (4), MCP framework dev config (3), custom installer (2), setup subcommands (3) — but no single dominant convention. This contrasts with linter and pre-commit, which converge tightly on a few canonical tools. A potential reading: dev-orchestration is still finding its conventions in the MCP corpus while lint/format have already converged industry-wide.

`pre-commit` and `Linter and type-checker stack` co-occur in many samples (awslabs--mcp, the-momentum--fhir-mcp-server, tumf--grafana-loki-mcp, qdrant--mcp-server-qdrant, awslabs--aws-api-mcp-server). The pairing is so consistent it suggests they're effectively a single "lint discipline" cluster operationally even though they're distinct affordances.

`In-repo docs site` is the only path with zero supporting samples after Pass 1/2/3 convergence. Reconciler may want to verify whether this path should be removed (no evidence) or kept as a known-empty bucket because it's an obvious affordance that the sampled corpus happens not to exhibit.
