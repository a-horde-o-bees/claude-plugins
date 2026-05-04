# Depth Pass Refinements — Sample > Entry point and launch

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role. 27 paths total; 25 with at least one supporting sample (one — `Setup ergonomics (cross-cutting)` — is a synthesis bucket with 0 supporting sample sections; another — `Aggregator/installer registry` — does not appear under this role and was not double-counted). Total sample evidence consumed: ~24 KB across ~152 sample sections.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### Sample > Entry point and launch > Console script via `[project.scripts]` / npm bin

Existing description anchors on "PyPI-distributed Python servers and the standard local-install entry point." Cross-corpus evidence shows the bucket is broader than that framing — it captures every package-declared script entry, but several samples use the path *not* as the host's launch command:

- The console script is declared but the actual host-config invocation is `uvx <package>`, `uv run <script>`, or Docker (`duolingo--slack-mcp` declares `slack-mcp = "main:main"` but the Dockerfile uses `uv run python main.py`; `severity1--terraform-cloud-mcp` declares `terraform-cloud-mcp` but the README launches with `uv run terraform-cloud-mcp`; `sajal2692--mcp-weaviate` declares `mcp-weaviate` and documents `uvx mcp-weaviate`). The script is the *entry-point declaration*; the actual launch command is uvx-mediated.
- Console-script-name vs distribution-name mismatch is a recurring oddity: `reminia--zendesk-mcp-server` ships `zendesk` (not `zendesk-mcp-server`); `sandraschi--email-mcp` ships `schip-mcp-email` while the package is `email-mcp`; `the-momentum--fhir-mcp-server` ships `start = start:main` (bare-module name).
- Quoted-dotted-name pattern is concentrated in awslabs samples (`"awslabs.aws-api-mcp-server" = "..."`) — a deliberate naming choice that lets dotted PyPI names match dotted console-script names; observed across 4+ awslabs samples. Worth keeping as a noted technique.
- Dual-script declarations — server + companion CLI — appear in `openags--paper-search-mcp` (`paper-search-mcp` server + `paper-search` CLI) and `redis--mcp-redis` (`redis-mcp-server`).
- Stale console-script signal: `twolven--mcp-server-puppeteer-py` declares `mcp-server-puppeteer = mcp_server_puppeteer.server:main` in `setup.py` but the README invokes `python puppeteer.py` — entry-point path and working entry-point diverge, signaling the package was never installed/tested as a console script.

The path therefore captures two distinct things readers should see distinguished:

1. *The declaration mechanism* — `[project.scripts]` / `package.json#bin` registers a name on PATH after install. Always present here regardless of whether the host config uses it.
2. *The launch shape it enables* — invoking the registered name directly (after `pip install` / `uv tool install` / `npm install -g`) or indirectly (via `uvx`, `uv run`, Docker entrypoint).

Sharpened text suggestion: "A package-declared entry — `pyproject.toml`'s `[project.scripts]` (Python) or `package.json`'s `"bin"` field (Node) maps a name to a `module:function` callable. The script becomes available on PATH after install (`pip install`, `uv tool install`, `npm install -g`) and serves as the named target invoked directly by `uvx <name>`, `uv run <name>`, or by host config when the binary is on PATH. The same declaration sometimes ships *without* being the actual launch path — e.g., when the README documents `python -m <package>`, `python <script.py>`, or a Dockerfile that bypasses the registered name. Read this path as 'the declared entry mechanism,' not 'the host-config command' — many samples appear here *and* under `uvx`/`Docker container entrypoint` because the registered script is what those launchers invoke. Common patterns: console-script name == package name (`mcp-clickhouse`, `arxiv-mcp-server`, `chroma-mcp`); awslabs-style quoted dotted names (`"awslabs.aws-api-mcp-server" = "..."`) so the dotted PyPI name matches the dotted script name; dual-script declarations (server + companion config CLI); console-script name unrelated to package name (`zendesk`, `schip-mcp-email`, bare `start`) — reduces typing but loses package↔binary correspondence. Required CLI args inline are common (`grafana-loki-mcp -u ... -k ...`); host wrapper config quoting must be careful."

### Sample > Entry point and launch > `uvx <package>`

Existing description is concise but misses three cross-corpus details:

- Two sub-shapes exist within this bucket: the simple `uvx <package>` form (most common) and the `uvx --from <package>[@version]` form, which is used when the console-script name differs from the PyPI package name (`uvx --from mysql-mcp-server` for `designcomputer`, `uvx --from redis-mcp-server@latest redis-mcp-server --url "..."` for redis). The `--from` form is the workaround when name divergence makes the simple form ambiguous.
- `@latest` and `@<version>` qualifiers appear in 5+ samples (`uvx awslabs.aws-api-mcp-server@latest`, `uvx jupyter-mcp-server@latest`, `uvx awslabs.aws-documentation-mcp-server@latest`). awslabs samples consistently pin `@latest` — author-level preference for always-fresh.
- The `uv tool install <package>` persistent-binary form vs ephemeral `uvx` form is mentioned in the existing description (under Distribution channel, not here). Worth a one-line note here too — `uv tool install` produces the same binary on PATH that `[project.scripts]` declares; `uvx` fetches per-invocation.
- Inline flags are common (`uvx mcp-server-duckdb --db-path <path> [--readonly]`, `uvx chroma-mcp --client-type persistent --data-dir ...`, `uvx mcp-server-motherduck --db-path :memory: --read-write`); host-config snippets carry the args verbatim.

Cross-role note: every uvx entry-point sample also surfaces under `Distribution channel > PyPI via uvx (zero-install runner)` (or `Install-from-git via uvx`). The two roles' descriptions should cross-reference each other but stay separate — distribution channel describes the publication target; entry point describes the host-config command shape. Counts diverge: distribution-channel uvx = 34 samples, entry-point uvx = 26. The 8-sample gap is samples that *publish* to PyPI but document a different host-config shape (e.g., `uv run <script>`, console script directly, `python -m <module>`).

Sharpened text suggestion: "Host config uses `"command": "uvx"` and passes the package name as an arg; uv fetches and runs in an ephemeral environment. Sub-shapes: simple `uvx <package>` (most common); `uvx --from <package>[@version] <console-script-name>` when the package name differs from the script name (`uvx --from mysql-mcp-server`, `uvx --from redis-mcp-server@latest redis-mcp-server`); `@latest` or `@<version>` qualifiers when authors want explicit version pinning at the host level (awslabs samples consistently pin `@latest`). Inline flags are routine (`uvx mcp-server-duckdb --db-path <path>`, `uvx mcp-server-motherduck --db-path :memory:`); host-config snippets carry the args verbatim. The cleanest stdio launcher for Python servers and the common host-config shape for modern Python servers — eliminates pre-install or venv management. Cross-role: see *Distribution channel — PyPI via uvx*; entry-point counts are lower than distribution-channel counts because some uvx-published servers document `uv run <script>`, console-script-direct, or Docker as the host-config shape rather than `uvx <package>`."

### Sample > Entry point and launch > Docker container entrypoint

Existing description correctly identifies `docker run -i --rm <image>` as the shape. Two cross-corpus refinements:

- The "primary launch surface" framing applies in some samples (`alexei-led--k8s-mcp-server` "Docker container is the primary launch surface", `github--github-mcp-server` "Docker is the canonical launch path", `voska--hass-mcp` "the primary documented launch shape") but is one launch mode among several in others (`crystaldba--postgres-mcp` "documented launch mode" alongside uvx, `aws-api-mcp-server` "alternative launch form", `sooperset--mcp-atlassian` "alternative to uvx", `ckreiling`, `datalayer--earthdata-mcp-server`, `mongodb-js`). Two postures cluster here:
    - **Docker-only / Docker-canonical** — ~6-8 samples where the host config invokes Docker because there is no other (or the author steers users toward Docker first). Often correlates with system-tool dependencies (browsers via Playwright, kubectl, slack-cli) or vendor preference (`mcr.microsoft.com/playwright/mcp`, `mcp/notion`).
    - **Docker-as-alternative** — ~12-14 samples where Docker is one mode among uvx/npx/console-script. Often paired with `Multi-channel publication` distribution.
- Some samples use `-i --rm --init --pull=always` — `microsoft--playwright-mcp` uses `--init` (PID 1) and `--pull=always` (always fetch latest). Worth noting these as observed flags beyond `-i` and `-e`/`-v`.

Cross-role note: every Docker-entrypoint sample also surfaces under `Distribution channel > Docker / OCI image`. Counts diverge sharply: distribution-channel Docker = 51, entry-point Docker = 22. The 29-sample gap is samples that *publish* a Docker image but the README's host-config shape is uvx/npx/console-script with Docker as a deployment-only option (deployed elsewhere, e.g., as a long-running service via compose or Kubernetes, not as the local host-config launch path).

Sharpened text suggestion: "`docker run -i --rm <image>` (with `-e` env vars and `-v` mounts) replaces the local console script with a containerized one. The container's `ENTRYPOINT`/`CMD` runs the server; MCP transport is stdio inside the container, with `-i` wiring host stdin/stdout to the container. The host config invokes Docker as the command; the entire `docker run ...` line is what the host calls, so host-side complexity grows with mount and env requirements. Observed flags beyond `-i`: `--rm` (auto-cleanup), `--init` (PID 1 for clean signal handling, `microsoft--playwright-mcp`), `--pull=always` (force re-fetch). Two postures within this bucket: **Docker-canonical** — Docker is the primary documented launch (often correlates with system-tool dependencies the package manager can't install — browsers, kubectl, slack-cli — or with vendor preference for image-only distribution: `mcr.microsoft.com/playwright/mcp`, `github-mcp-server`, `mcp/notion`); **Docker-as-alternative** — Docker is one of several documented launches alongside uvx/npx/console-script (the larger group; correlates with `Multi-channel publication`). Cross-role: see *Distribution channel — Docker / OCI image*. Entry-point count (~22) is much smaller than distribution-channel count (~51) — many samples publish a Docker image without making it the host-config launch shape."

### Sample > Entry point and launch > `npx -y <package>` / `bunx`

Existing description covers the basics well. Cross-corpus refinements:

- Subcommand-after-package pattern is a strong sub-axis: `npx <package> stdio` vs. `npx <package>` (HTTP default) — observed in `ahmedmustahid--postgres-mcp-server`, `executeautomation--mcp-playwright`, `microsoft--playwright-mcp` (`npx @playwright/mcp@latest --port 8931` for SSE), `makenotion--notion-mcp-server` (`--transport http`). When transport is selectable, npm-distributed servers prefer subcommands or `--port` flags over env vars.
- Inline `--api-key=...` / `--access-token=...` pattern is more prevalent in npx samples than in uvx samples — observed in `getsentry--sentry-mcp` (`--access-token=...`), `stripe--agent-toolkit` (`--api-key=...`), `paypal--paypal-mcp-server` (`--tools=all`, `--access-token`), `GLips--Figma-Context-MCP` (`--figma-api-key=YOUR-KEY --stdio`). May reflect TypeScript-server convention preference for inline args over env vars; uvx-served Python servers more often use env vars. Worth flagging as a sub-axis.
- One-shot bootstrap usage is documented: `upstash--context7` (`npx ctx7 setup`), `paypal--paypal-mcp-server` (OAuth bootstrap). The entry-point bucket captures both server-launch and CLI-bootstrap uses of the same npx invocation.
- `@latest` qualifier ubiquity: 5+ samples use `npx -y <package>@latest` (cyanheads, mongodb-js, ppl-ai, microsoft, sentry).

Sharpened text suggestion: "Bare `npx -y <package>` (or `bunx`) for Node servers. The `-y` accepts the install prompt automatically. Universal launch idiom for npm-distributed servers — host's JSON config lists `npx` as the command and the package name (with `-y` for auto-confirm) as the first arg. `@latest` qualifier appears in many samples for always-fresh ergonomics. Inline `--api-key=...`/`--access-token=...` flag patterns are more common in npx samples than in uvx samples — TypeScript servers favor inline args; Python servers more often gate credentials via env vars. Subcommand-after-package selects mode (`npx <pkg> stdio` for stdio; bare `npx <pkg>` defaults to HTTP) — observed across several Node servers when transport is selectable. Also used for one-shot bootstrap commands (`npx ctx7 setup`, OAuth-init scripts). Windows variant wraps in `cmd /c npx ...`. Cross-role: see *Distribution channel — npm via npx / bunx*."

### Sample > Entry point and launch > Module invocation / `python -m <module>` fallback

Existing description correctly captures the role as fallback / parallel mode. Cross-corpus refinements:

- "Parallel-to-console-script" is the dominant pattern (8 of 12 samples have a console script *and* a `python -m` form documented). Pure-fallback (no console script declared) is the minority (`mukul975--cve-mcp-server` "No console script defined; `python -m cve_mcp.server` is the documented launch command", `feiskyer--mcp-kubernetes-server` per its content `python -m src.mcp_kubernetes_server.main`).
- The `__main__.py` packaging convention is the explicit substrate: `isaaccorley--planetary-computer-mcp` "module-level invocation rather than console script. `__main__.py` packaging convention," `DiversioTeam--clickup-mcp` console script points to `clickup_mcp.__main__:main`, `PagerDuty` "via `__main__.py`."
- Module-style spelling sometimes uses package-only (`python -m gis_mcp`), sometimes module-path (`python -m servicenow_mcp.cli`, `python -m awslabs.aws_api_mcp_server.server`). The deeper path explicitly targets the module file rather than relying on `__main__.py`.
- The "alternative for advanced users" framing in the existing description matches `JackKuo666`, `mahdin75`, `awslabs--aws-api-mcp-server`, `modelcontextprotocol--servers`, `jbeno`. The "doubles as a management CLI" framing matches `DiversioTeam` (subcommands like `set-api-key`) and `echelon-ai-labs--servicenow-mcp` (transport-mode-selecting CLI).

Existing description holds — minor sharpening only.

Sharpened text suggestion: "Server invoked by running the package as a module via `python -m <package>` (dispatched through `__main__.py`) or `python -m <package>.<module>` (dispatched directly to a named module). Pure-fallback usage (no console script declared) is rare; far more common is parallel-to-console-script — a console script *and* `python -m` are both documented, with module-form positioned for advanced users invoking from a known interpreter, sometimes paired with management subcommands (`set-api-key`, `check-config`, transport-mode selection). Common substrate: `__main__.py` in the package. Common in source-distributed Python servers using uv."

### Sample > Entry point and launch > Bare interpreter + script path

Existing description is comprehensive. Cross-corpus refinements:

- Two distinct sub-postures within the bucket:
    - **`uv run` wrapping bare script** (most common, 6+ samples): `AlwaysSany` (`uv run python main.py --transport stdio`), `labeveryday` (`uv run python pdf_reader_server.py`), `misbahsy` (`uv run server.py`), `shreyaskarnik` (`uv run <path>/huggingface_mcp_server.py`). These are `python <script.py>` *via uv* — uv resolves the venv and dependencies but the entry point is still a bare script, not a console-script.
    - **Bare `python` on system PATH** (3+ samples): `JackKuo666` (`python pubmed_server.py`), `twolven` (`python puppeteer.py`), `marlonluo2018` (`python server.py`), `samuelgursky--davinci-resolve-mcp` uses absolute venv path `"command": "/path/to/venv/bin/python"` to avoid the fragile system-PATH problem.
- The "no installable package wrapping the entry point at all" claim is the primary signal — these are samples that explicitly *don't* declare console scripts and ship a `script.py` at root or under `src/` as the runtime contract.
- Single-file vs multi-script split: `marlonluo2018` ships both `server.py` (server) and `cli.py` (CLI) at repo root — a deliberate split rather than a single-file. `samuelgursky` documents two modes by flag (`python src/server.py` vs `python src/server.py --full`).

Sharpened text suggestion: existing description is good; suggest adding "Two sub-shapes: bare `python <script.py>` directly (fragile — depends on which interpreter is first found; mitigated by absolute venv paths in host config: `samuelgursky` uses `"command": "/path/to/venv/bin/python"`); and `uv run python <script.py>` or `uv run <script.py>` (uv resolves the venv but the script is still bare, not a console-script). Multi-script splits also occur (`server.py` + `cli.py` at repo root rather than one file with subcommands)."

### Sample > Entry point and launch > Built JS file (`node build/index.js`)

Existing description is brief; samples reveal a tiny detail worth surfacing:

- Output directory naming varies — `build/` (`v-3--discordmcp`), `dist/` (`cyanheads--perplexity-mcp-server`, `docker--hub-mcp`, `spences10--mcp-turso-cloud`), with `dist/` being more common in modern TypeScript projects (tsup, esbuild). The current path-name `Built JS file (\`node build/index.js\`)` may suggest `build/` is canonical — the cross-corpus sample is more often `dist/`.
- The sample evidence is small (5 samples). Some samples that match this category prefer `npm start` to `node build/index.js` directly (the npm-scripts path); discrimination between the two is whether host config invokes `node` or `npm`.

Sharpened text suggestion: "TypeScript projects compile to a JS output directory (`dist/` is more common in modern toolchains; `build/` appears in older or hand-rolled setups) and host config invokes Node against the built file. Requires the consumer to have run `npm install && npm run build` first. Distinct from `npm scripts` (which dispatches via `npm run start`/`npm start`) — this path is `node <built-file.js>` directly. Host-config snippet shape: `"command": "node"`, `"args": ["<absolute-path>/dist/index.js"]`."

### Sample > Entry point and launch > `uv --directory` from source

Existing description is accurate. One refinement — `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`'s sample shows a degenerate variant: `uv run --with fastmcp --with uvicorn fastmcp run /path/to/sqlite_explorer.py` — the host config is `"command": "uv"` with `"run"` as the arg-prefix, not `--directory`. This is closer to `Source-tree \`uv run\`` than to `uv --directory`. Possible mis-placement (see Mis-placed samples).

The remaining 3 samples (`designcomputer`, `reminia`, `shibuiwilliam`) all use the path-anchored `uv --directory <path> run <script>` form.

### Sample > Entry point and launch > Source-tree `uv run`

Existing description is accurate. Cross-corpus pattern: the bucket fits `crystaldba--postgres-mcp` ("`uv run postgres-mcp` from source tree"), `shreyaskarnik--huggingface-mcp-server` ("`uv sync && uv run huggingface_mcp_server.py`"), `zilliztech--mcp-server-milvus` ("`"command": "uv"` with `run src/mcp_server_milvus/server.py --milvus-uri ...` as args").

The boundary between this and `Bare interpreter + script path` (where the bare script is wrapped in `uv run`) is fuzzy: when the script is a `.py` at a known path *and* uv is the runtime, the choice between buckets depends on whether the framing is "uv launches my script" (here) or "script-with-no-installable-wrapper" (Bare interpreter). Worth a cross-reference.

Sharpened text suggestion: "Server launched against a checked-out source tree via `uv run <script>` (without `--directory`). Variants: `uv run <console-script-name>` (when a console script is declared and accessible from the source tree's installed venv); `uv run <script.py>` (when the entry point is a bare script). Unusual but documented in some projects' canonical configs. Fuzzy boundary with `Bare interpreter + script path` — that bucket also covers `uv run <script.py>`-shaped invocations; the discriminator is whether the framing positions uv as the runtime selector (here) or whether the script is the primary artifact and uv is incidental."

### Sample > Entry point and launch > SDK constructor + transport-method launch

Existing description correctly identifies the SDK-as-library pattern. Cross-corpus refinements:

- The "The launcher is the consumer's `main`" framing fits all 4 samples but should be more explicit that this is *the* defining property: there is no project-level entry point in the SDK repo that end-users invoke; the entry point is whatever consumer code wraps the SDK.
- Across samples: Go (`mark3labs--mcp-go`: `server.NewMCPServer()` + `ServeStdio()`/`ServeSSE()`/`ServeHTTP()`; `metoro-io--mcp-golang`: `RegisterTool()` + Gin/HTTP; `viant--mcp`: `server.NewMCPServer()` + `stdioSrv.ListenAndServe()` / `srv.HTTP(...)`); Kotlin (`modelcontextprotocol--kotlin-sdk`: Ktor + STDIO transport). The pattern recurs across both Go and Kotlin SDKs but the API surface differs by ecosystem.
- This is the canonical shape for *SDK-style* artifacts (versus server-style artifacts that ship a runnable binary). Worth tagging in the description.

Sharpened text suggestion: "The repo ships an SDK, not a runnable server — the consumer writes `main.go`/`Application.kt`/etc. that imports the SDK and orchestrates startup. Pattern: `server.NewMCPServer()` (or analog) returns a server value, then a transport-method call (`ServeStdio()`, `ServeSSE()`, `ServeHTTP()`, `stdioSrv.ListenAndServe()`, `srv.HTTP(...).ListenAndServe()`, Ktor `embeddedServer().start()`) runs the server. There is no project-level entry point in the SDK repo end-users invoke; the entry point is whatever consumer code wraps the SDK. API surfaces differ by ecosystem (Go's mcp-go vs mcp-golang vs viant; Kotlin SDK with Ktor) but the structural shape is the same. Appropriate for Go/Kotlin SDK consumers building bespoke servers — the SDK is infrastructure, not a finished product."

### Sample > Entry point and launch > Subcommand verb

Existing description ("Mode is an explicit verb rather than a flag, separating 'run the server' from 'configure a host' cleanly") matches the 4 samples but understates how varied the subcommand surfaces are:

- `DiversioTeam--clickup-mcp`: management subcommands (`set-api-key`, `check-config`, `test-connection`) on top of the server protocol — the binary doubles as configuration tooling.
- `geropl--linear-mcp-go`: server modes + setup verb (`serve` / `serve --write-access`, `setup --tool=cline`, `version`) — the `setup` verb writes host config files for a target host.
- `github--github-mcp-server`: transport mode selection (`stdio`).
- `ahmedmustahid--postgres-mcp-server`: transport mode (`stdio` positional, default HTTP).

Three sub-roles for the subcommand:

1. **Transport mode selector** (`stdio` vs default HTTP) — `ahmedmustahid`, `github`.
2. **Server-mode selector** (read-only vs write, dev vs prod) — `geropl`'s `serve` vs `serve --write-access`.
3. **Config / management surface** (set-api-key, check-config, test-connection, setup) — `DiversioTeam`, `geropl`'s `setup`.

The `setup --tool=<host>` form in `geropl` is also called out in the cross-cutting `Setup ergonomics` synthesis bucket (which has 0 supporting sample sections because it's a synthesis). Worth cross-referencing.

Sharpened text suggestion: "The binary takes a subcommand selecting mode. Three sub-roles observed: transport-mode selector (`stdio` positional vs default HTTP — `ahmedmustahid`, `github`); server-mode selector (`serve` / `serve --write-access`, read-only vs write — `geropl--linear-mcp-go`); config / management surface (`set-api-key`, `check-config`, `test-connection` — `DiversioTeam`; `setup --tool=cline` writes host config — `geropl`). Mode is an explicit verb rather than a flag, separating 'run the server' from 'configure a host' cleanly. Appropriate when the binary has multiple roles beyond running the server. The `setup --tool=<host>` variant is one of the rare ergonomic surfaces — see also *Setup ergonomics (cross-cutting)*."

### Sample > Entry point and launch > Setup ergonomics (cross-cutting)

This path has 0 supporting sample sections (it's a synthesis bucket). The current description enumerates 6 setup-ergonomic patterns. Cross-corpus check:

- `setup` subcommand: `geropl--linear-mcp-go` (`server setup --tool=cline`); also referenced in `Subcommand verb`.
- Framework CLI installer (`fastmcp install`): `jlowin--fastmcp` — also under `Framework CLI run`.
- Marketplace plugin (Claude Desktop plugin, gemini-extension, MCPB): referenced in `Distribution channel > MCPB bundle / Desktop Extension manifest`, `Distribution channel > .claude-plugin/marketplace.json`, `Distribution channel > Pre-built host installer / one-click install URL`.
- README JSON snippets: pervasive — implicit in nearly every Python/Node sample.
- Universal installer covering many hosts (`install.py` to 10+ MCP client locations): `sandraschi--email-mcp` and a Custom Python installer script reference under `Distribution channel > Custom Python installer script`.
- Setup-wizard CLI as bootstrap (`npx ctx7 setup`, OAuth-bootstrap): `upstash--context7`, `paypal--paypal-mcp-server`.

The synthesis is accurate but lives in awkward space — every pattern it lists *also* lives in another path. Reconciler should consider whether to keep it as a synthesis cross-reference or fold each item back into its primary path with cross-role notes.

Sharpened text suggestion: keep the synthesis but tag it explicitly as a cross-reference cluster: "*This bucket has no primary samples — every pattern listed also surfaces under another path; this section catalogs the cross-cutting setup-ergonomic surface.* Patterns: `setup` subcommand on the server binary (see *Subcommand verb*: `geropl--linear-mcp-go` `server setup --tool=cline`); framework CLI installer (see *Framework CLI run*: `fastmcp install`); marketplace plugin (see *Distribution channel — MCPB bundle*, `.claude-plugin/marketplace.json`, *Pre-built host installer*); README JSON snippets (default for every server without a setup verb); universal installer covering many hosts (see *Distribution channel — Custom Python installer script*: `install.py` writing to 10+ MCP client locations); setup-wizard CLI as bootstrap (`npx ctx7 setup`, OAuth-bootstrap; see *Distribution channel — npm via npx / bunx* one-shot bootstrap notes)."

### Sample > Entry point and launch > URL configuration (no local launch)

Existing description is concise and accurate. Cross-corpus pattern within the bucket:

- Pure URL-only paste: `idosal--git-mcp` (`https://gitmcp.io/{owner}/{repo}`), `neondatabase` (`mcp.neon.tech/mcp` with OAuth), `slackapi--slack-mcp-plugin`, `stripe--agent-toolkit` (`https://mcp.stripe.com`), `supabase-community` (`https://mcp.supabase.com/mcp?project_ref=...`), `upstash--context7`, `getsentry`, `github` (`api.githubcopilot.com`), `exa-labs`.
- Bridge-shim variant: `cloudflare--mcp-server-cloudflare` uses `npx mcp-remote <cloudflare-mcp-url>` — a shim bridges stdio (host) to Streamable HTTP (Cloudflare). Distinct from pure URL paste; the host's command is `npx`, not the URL.

The `mcp-remote` shim is functionally a stdio→HTTP bridge that lets stdio-only host configs talk to a remote streamable-HTTP endpoint. Worth surfacing in the description as a sub-pattern.

Sharpened text suggestion: "For managed-endpoint / vendor-hosted deployments, the user's MCP client points at an HTTPS URL — no local launch step. Two sub-patterns: **pure URL paste** (host config carries the URL directly: `idosal--git-mcp`, `neondatabase`, `stripe`, `supabase` cloud, `getsentry`, `github` Copilot path) — most common; **stdio-to-HTTP bridge shim** (`cloudflare--mcp-server-cloudflare`: host runs `npx mcp-remote <url>`, the shim translates stdio host I/O to streamable-HTTP requests against the remote endpoint) — used when the host supports stdio only and the server is HTTP-only. Cross-role: see *Distribution channel — Hosted endpoint (no install)*."

### Sample > Entry point and launch > Native binary

Existing description is brief. Cross-corpus refinements:

- Three distinct provenance paths within the bucket:
    - Pre-built binary release fetched by installer script: `rust-mcp-stack--rust-mcp-filesystem` ("Wrapper installer scripts (POSIX shell + PowerShell) fetch the pre-built binary release").
    - Self-built Go binary: `korotovsky--slack-mcp-server` ("Self-built Go executable; users `go run` or run the compiled binary directly").
    - Single binary doubling for npm/Docker variants: `googleapis--mcp-toolbox` (`./toolbox --config "tools.yaml"` — Docker and npm shim variants run the same binary).
- The "no runtime deps" framing fits all 3.

Sharpened text suggestion: "Pre-built standalone executable from a release artifact (Cargo, Homebrew, npm shim, GitHub release download); users run the binary path directly. Three provenance paths: installer-script-fetched (`rust-mcp-stack--rust-mcp-filesystem` POSIX-shell + PowerShell wrappers); self-built and run from `target/release/<name>` (`korotovsky` `go run` or compiled binary); single binary that doubles for npm/Docker variants by being wrapped in a thin shim (`googleapis--mcp-toolbox` `./toolbox --config <yaml>`). Appropriate for Rust/Go-style compiled servers with no runtime deps. Cross-role: see *Distribution channel — Pre-built binary release*, *Standalone bridge binary*, *npm package wrapping native binary*."

### Sample > Entry point and launch > Library import inside a user's handler

Existing description correctly identifies "no standalone command." Cross-corpus refinement: this path has 3 samples but they cluster into two distinct shapes:

- Lambda handler delegation: `awslabs--mcp-lambda-handler` — `mcp.handle_request(event, context)` inside a Lambda handler. The "no command" applies to runtime invocation; the package *does* declare a console script (`awslabs.mcp-lambda-handler` mapped to `awslabs.mcp_lambda_handler.server:main`) but it's not the primary use.
- Generic library/SDK use: `modelcontextprotocol--kotlin-sdk` ("library; consumers import it into their own Kotlin/JVM applications") and `viant--mcp` ("Consumers embed the library; for non-Go consumers, the bridge binary substitutes").

Significant overlap with `SDK constructor + transport-method launch` — both describe SDK-as-library use. Discriminator: this bucket is about delegation patterns where a consumer's *handler* (Lambda, web framework) calls into the SDK, while `SDK constructor + transport-method launch` is about consumer code that *constructs* the server and runs it.

Possible mis-placement — `modelcontextprotocol--kotlin-sdk` and `viant--mcp` both surface under *both* paths. Reconciler should review whether one of them should be the canonical home and the other a cross-reference.

Sharpened text suggestion: "No standalone command — the package is imported into consumer code, but with a *delegation pattern* (consumer's handler calls into the SDK) rather than an *orchestration pattern* (consumer's `main` constructs and runs the server — see *SDK constructor + transport-method launch*). Examples: Lambda handler that delegates request handling (`mcp.handle_request(event, context)` — `awslabs--mcp-lambda-handler`); generic library use where the consumer's framework owns the lifecycle (`modelcontextprotocol--kotlin-sdk`, `viant--mcp` non-Go embedding). Appropriate when the artifact is infrastructure for building servers rather than a server itself, and when the consumer's runtime (Lambda, Ktor, Spring, etc.) owns the request loop. Distinct from *Programmatic embedding via library function* — that path is about explicit programmatic-API entry points (`createConnection()`); this path is about handler delegation."

### Sample > Entry point and launch > Programmatic embedding via library function

Existing description is concise. Cross-corpus check confirms 2 samples fit:

- `jlowin--fastmcp`: "Consumers write entry points calling `mcp.run()`, embedding the framework directly into their own program."
- `microsoft--playwright-mcp`: "`createConnection()` programmatic API for embedding inside a Node process as a library, blurring server/client lines."

The description correctly captures the "in-process MCP endpoint a host process can consume directly without subprocess IPC" property. Worth clarifying boundary with `Library import inside a user's handler` — that's delegation; this is explicit programmatic-API construction (`createConnection()` returns an in-process endpoint object).

Sharpened text suggestion: "The SDK exposes a programmatic API (`createConnection()`, `mcp.run()`, or analog) that returns an in-process MCP endpoint a host process can consume directly without subprocess IPC. Distinct from *Library import inside a user's handler* — that path is delegation (handler calls into SDK); this path is explicit construction (consumer obtains an in-process endpoint object and wires it into the host). Appropriate when the host is itself a Node/Python app and wants to embed the server's tool surface as a library, blurring the server/client boundary."

### Sample > Entry point and launch > Framework CLI run

Existing description matches `jlowin--fastmcp` (`fastmcp run`/`fastmcp install`/`fastmcp dev`). Cross-corpus refinement:

- `neondatabase--mcp-server-neon`'s sample says "Local development runs `pnpm dev` (Next.js dev server) for contributors" — that's a Next.js framework dev path, not an MCP-framework CLI. Possible mis-placement (see Mis-placed samples).
- The pure cohort is just `jlowin--fastmcp` with `fastmcp dev`/`fastmcp run`/`fastmcp install`. With one sample remaining, the bucket may be effectively single-sample.

### Sample > Entry point and launch > npm scripts (start/start:stdio/start:http)

Existing description matches well. Cross-corpus refinement:

- Two sub-patterns: transport-mode-named scripts (`start:stdio`, `start:http` — `cyanheads--git-mcp-server`) vs single `npm start` with arg-passthrough (`npm start -- ...` — `docker--hub-mcp`, `cyanheads--perplexity-mcp-server`).
- Dev-vs-prod posture: the existing description notes "production users typically prefer the console-script form" — confirmed by `v-3--discordmcp` where `npm run dev` is dev and host config invokes `node build/index.js` for production, and by `cyanheads--perplexity-mcp-server` where `npm start` runs the built artifact and `npm run build` compiles.

Existing description holds.

### Sample > Entry point and launch > Multiple entry points per transport

Existing description is accurate. Cross-corpus refinement:

- `echelon-ai-labs--servicenow-mcp`: clearly fits — `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE), architecturally split.
- `normaltusker--kotlin-mcp-server`: described as "Three invocation modes selectable by installation type; HTTP REST bridge via `vscode_bridge.py` runs as a separate launch path" — this is closer to "transport-mode-aware launch paths" than "separately-installed binaries per transport." The bucket may be a slightly looser fit for normaltusker than for echelon.

The description's "Lets each transport carry its own dependency closure" claim is supported by `echelon` (the SSE binary pulls Starlette; stdio doesn't) but not explicitly stated in `normaltusker`.

Sharpened text suggestion: "Two or more separately-installed binaries, one per transport (`<server>` for stdio, `<server>-sse` for SSE), letting each transport carry its own dependency closure (the SSE binary pulls in Starlette; the stdio binary doesn't). Higher install ceremony in exchange for lighter runtime footprint per mode. Distinguish from samples that ship one binary with transport selectable by subcommand or env var — that's *Subcommand verb* / inline-flag launch."

### Sample > Entry point and launch > Profile-driven launcher

Existing description matches both samples (`bhauman--clojure-mcp`, `hugoduncan--mcp-clj`) well — both use `clj -M:<profile>` with `:stdio-server`/`:sse-server` aliases in `deps.edn`. Description holds.

### Sample > Entry point and launch > Language-tool launcher

Existing description ("Language-native command (e.g., `clojure -Tmcp start`, `clojure-mcp-light` profile)") matches both samples (`bhauman`, `hugoduncan`). Both samples *also* surface under `Profile-driven launcher` — this and `Profile-driven launcher` may be the same shape with slightly different framing (the `-T` is a deps.edn tool alias, the `-M` is a deps.edn main alias; both are profile mechanisms). Possible bucket merge candidate (see Proposed bucket merges).

### Sample > Entry point and launch > CLI dispatcher subcommand

Single-sample bucket (`pathintegral-institute--mcp.science`: `uvx mcp-science <server-name>`). Description is accurate for that sample. Worth keeping the bucket distinct because it's structurally different from `Subcommand verb` (the subcommand selects which *server* runs, not which *mode*; the dispatcher is one PyPI package containing many servers).

### Sample > Entry point and launch > Mounted into another runtime as an extension

Single-sample bucket (`datalayer--jupyter-mcp-server`). Description correctly identifies the dual role (standalone or in-process Jupyter extension). Holds.

### Sample > Entry point and launch > SQL PRAGMA invocation

Single-sample bucket (`teaguesterling--duckdb_mcp`: `PRAGMA mcp_server_start()`). Description correctly identifies the host process as DuckDB. Holds.

### Sample > Entry point and launch > Make targets in repo

Two-sample bucket (`the-momentum--fhir-mcp-server`, `thenets--ghost-mcp`). Existing description ("Local-dev launch via `make run`, `make dev`, `make build`, etc. … not the end-user launch path but the developer-iteration path") is accurate. Worth noting the role: Make is a *developer* entry point in both samples, not the user-facing launch. The two samples both also surface under other paths (`thenets` under `uvx`, `the-momentum` under `Console script`). The Make-targets bucket captures a development-affordance dimension orthogonal to user-facing launch.

Sharpened text suggestion: "Local-dev launch via `make run`, `make dev`, `make build`, `make test`, `make test-connection` etc. Common in projects with substantial dev tooling — orthogonal to the user-facing launch path; samples in this bucket also surface under the user-facing entry-point bucket they ship (uvx, console script, Docker). Worth tagging as the *developer-iteration affordance* rather than the *end-user launch shape*."

### Sample > Entry point and launch > Click-based CLI wrapper (Python)

Two samples (`alpacahq--alpaca-mcp-server`, `zilliztech--mcp-server-milvus`). Both wrap a FastMCP runner with `click`. Description holds — concise and accurate.

### Sample > Entry point and launch > Generated binary from scaffolded project

Single-sample bucket (`conikeec--mcpr`). Description holds.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### Sample > Entry point and launch > Console script via `[project.scripts]` / npm bin — declaration-vs-launch sub-axis

The bucket conflates the *declaration mechanism* (script registered on PATH after install) with the *launch mechanism* (host config invokes it). 12+ samples have a console script declared *but* the documented launch is `uvx <package>`, `uv run`, Docker, or `python -m <module>`. Fold into description (sharpening above) rather than splitting — the bucket is correctly named "Console script via `[project.scripts]` / npm bin"; the sharpening clarifies that this captures the declaration even when it's not the host's invocation shape.

### Sample > Entry point and launch > Docker container entrypoint — primary-vs-alternative sub-axis

Within the 22 Docker-entry-point samples, the split is:

- Docker-canonical (~6-8 samples): Docker is the documented launch shape. Often correlates with system-tool dependencies (Playwright browsers, kubectl, slack-cli, GitHub PAT-managed) or with vendor-image-only distribution.
- Docker-as-alternative (~12-14 samples): Docker is one of several. Pairs with `Multi-channel publication`.

Fold into description (sharpening above) — the two postures are observable but don't justify a bucket split (same launch-command shape; the difference is positional in the README, not structural).

### Sample > Entry point and launch > `npx -y <package>` / `bunx` — inline-args vs env-vars sub-axis

5+ npx samples document inline `--api-key=`/`--access-token=`/`--figma-api-key=` flags (`getsentry`, `stripe`, `paypal`, `GLips`); npx-distributed servers favor inline args more than uvx-distributed Python servers (which more often gate via env vars). Fold into description (sharpening above).

### Sample > Entry point and launch > Bare interpreter + script path — uv-wrapped vs system-Python sub-axis

6+ samples wrap a bare script in `uv run`; 3+ run `python <script.py>` directly with system Python (some mitigated by absolute venv paths). Fold into description.

### Sample > Entry point and launch > URL configuration (no local launch) — pure-paste vs bridge-shim sub-axis

9 samples use pure URL paste; 1 sample (`cloudflare--mcp-server-cloudflare`) uses `npx mcp-remote <url>` as a stdio→HTTP bridge. Sample count for the bridge-shim sub-pattern is too small for a bucket split; fold into description.

### Sample > Entry point and launch > Subcommand verb — three sub-roles

Three sub-roles (transport-mode selector, server-mode selector, config / management surface) across 4 samples. Sample count too small for a bucket split; fold into description (sharpening above).

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

### Profile-driven launcher + Language-tool launcher

Both buckets contain `bhauman--clojure-mcp` and `hugoduncan--mcp-clj` (i.e., the same 2 Clojure samples). The current split is by which deps.edn alias mechanism (`-M:profile` for main aliases, `-T<tool> <verb>` for tool aliases). Both are Clojure-toolchain launch idioms. The split adds analytic granularity but each bucket is single-substrate (Clojure-only) and the same samples populate both.

Consider:

- **Merge** into a single `Clojure deps.edn launcher (profiles and tool aliases)` bucket — captures both `-M:stdio-server` profiles and `-Tmcp start` tool aliases as one Clojure-ecosystem launch idiom.
- **Or keep split** — the underlying mechanisms are genuinely different (profile vs tool alias) and Clojure-aware readers would distinguish them. The cost is that any Clojure sample populates both.

Reconciler call. If kept split, descriptions should cross-reference each other and mention that samples may appear in both.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

No bucket splits proposed. Sub-axes within `Console script`, `Docker container entrypoint`, `npx`, `Bare interpreter`, `Subcommand verb`, and `URL configuration` are observable but the sample-count per side is too uneven to justify a structural split — fold into description sharpenings instead.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` currently under `uv --directory` from source — better fits `Source-tree \`uv run\``

The sample's content shows host config `"command": "uv"`, `"args": ["run", "--with", "fastmcp", "--with", "uvicorn", "fastmcp", "run", "/path/to/sqlite_explorer.py"]`. The `--directory` flag is *not* present; `--with` adds dependencies and `run` runs against the source tree path. This is structurally `Source-tree \`uv run\`` (which currently has 3 samples). Reconciler: consider moving from `uv --directory` to `Source-tree \`uv run\``.

### `neondatabase--mcp-server-neon` currently under `Framework CLI run` — possibly better fits a developer-iteration bucket or `Make targets in repo`

The sample's content for this path is "Local development runs `pnpm dev` (Next.js dev server) for contributors." This is a Next.js dev-mode path, not an MCP-framework CLI (which is what the bucket otherwise captures via `jlowin--fastmcp`'s `fastmcp dev`/`fastmcp run`). Closer to `Make targets in repo` semantically (developer-iteration affordance) but the substrate is `pnpm`. Reconciler: consider whether this sample's section should be removed from `Framework CLI run` (leaving the bucket effectively single-sample around fastmcp's CLI), and whether the dev-iteration content belongs in a different role entirely.

### `normaltusker--kotlin-mcp-server` currently under `Multiple entry points per transport` — partial fit

The sample describes "Three invocation modes selectable by installation type; HTTP REST bridge via `vscode_bridge.py` runs as a separate launch path" which is closer to "multiple installation modes" than "separately-installed binaries per transport." The bucket's framing assumes `<server>` for stdio and `<server>-sse` for SSE as parallel binaries; normaltusker's pattern is different (HTTP REST bridge as separate launch path). Reconciler: consider whether this is genuinely a multiple-entry-points-per-transport sample or whether it surfaces a separate sub-pattern (multiple-launch-paths-by-installation-type) that doesn't have its own bucket and should fold elsewhere.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Entry point ↔ Distribution channel role pairing

The cross-role coupling between Entry point and Distribution channel surfaces clearly when both roles are inspected together:

| Distribution-channel path | Entry-point path it implies | Sample count alignment |
|---|---|---|
| PyPI via uvx | `uvx <package>` | 34 vs 26 (8-sample gap) |
| npm via npx / bunx | `npx -y <package>` / `bunx` | 23 vs 20 (close) |
| Docker / OCI image | Docker container entrypoint | 51 vs 22 (29-sample gap) |
| Source clone with editable install | Bare interpreter / Source-tree `uv run` / `uv --directory` | 41 vs ~19 combined |
| Hosted endpoint (no install) | URL configuration | 11 vs 10 (close) |
| Pre-built binary release | Native binary | 6 vs 3 (close) |

The sample-count gaps are diagnostic:

- **Docker gap (51 vs 22)**: most Docker-published servers also publish to uvx/npx; the Docker entry-point bucket only captures samples where the *host config* uses `docker run` as the launch command. Many Docker-published servers document `uvx <package>` or `npx -y <package>` as the host-config snippet, with Docker as a separate deployment artifact — not the host-launch shape. The Docker entry-point bucket is therefore a more selective filter than the Docker distribution bucket.
- **PyPI uvx gap (34 vs 26)**: 8-sample gap suggests several uvx-published servers document something other than `uvx <package>` as the host-config shape — `uv run <script>`, console-script direct, `python -m <module>`, or Docker.
- **Source clone gap (41 vs ~19)**: source-clone distribution is a fallback channel; the actual launch shape varies widely.

The two roles are legitimately separate and should remain so — the same artifact can be distributed via channel X but launched via mechanism Y. But descriptions in both roles should cross-reference the relationship, and the consolidated should call out the count gaps as evidence that "distribution channel" and "entry point" are independent decisions even when the named substrates (uvx, npx, docker) are identical.

### Author-level posture signals visible across all paths

Inspecting the role across all samples surfaces author-level posture signals that aren't visible per-bin:

- **Convergence on `uvx`/`npx -y`** — the two top zero-install entry points dominate the modern (post-2024) Python and Node sample subsets. Older or legacy projects fall back to bare interpreter, console-script-direct, or `python -m`.
- **Inline credentials vs env-var credentials** — a clear ecosystem split: npx samples favor inline `--api-key=`/`--access-token=` flags; uvx samples favor env vars (`AWS_PROFILE`, `HA_URL`, `HA_TOKEN`). Reflects TypeScript-server convention (Stripe, PayPal, Sentry, GitHub) vs Python-server convention.
- **`@latest` ubiquity** — `uvx <pkg>@latest` and `npx -y <pkg>@latest` both appear in many samples; authors use the qualifier as ergonomic-shorthand for "always pull the freshest." This is an ergonomic preference, not a technical requirement, and surfaces consistently across the corpus.
- **README JSON-snippet vs setup-verb gap** — virtually every sample has README JSON snippets; only `geropl--linear-mcp-go` has a `setup --tool=<host>` verb. The setup-verb path is structurally available but rarely adopted (`Setup ergonomics (cross-cutting)` is a synthesis bucket because real adoption is thin).
- **Framework-CLI launch is rare** — only `jlowin--fastmcp` ships `fastmcp dev`/`fastmcp run`/`fastmcp install` as primary launch, and consumer projects don't propagate that as their host-config shape (FastMCP-using projects ship console scripts, uvx-launchable, etc.). The framework-CLI launch shape is the framework author's affordance, not a consumer-adopted convention.

### Path proliferation vs. corpus weight

The role has 27 paths but the top 6 (`Console script`, `uvx`, `Docker entrypoint`, `npx`, `Bare interpreter`, `Module invocation`) cover 116 of the 102 sample-attestations (samples appear in multiple paths). The long tail (`SQL PRAGMA invocation`, `Mounted into another runtime`, `Generated binary`, `CLI dispatcher`, etc.) is largely single-sample. Reconciler may want to consider whether the long-tail buckets are useful as cataloged-but-rare patterns or whether some could fold into a "Niche language-toolchain launchers" parent — but the current arrangement honors single-sample evidence cleanly.
