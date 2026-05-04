# Depth Pass Refinements — Sample > Configuration delivery

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Configuration delivery > Environment variables`

**What the existing description misses.** Two cross-corpus patterns visible only when all 72 supporting samples are stacked: (1) the `<TOOL>_<SETTING>` vendor-prefix convention is near-universal — `MDB_MCP_*`, `PAPER_SEARCH_MCP_*`, `OPENSEARCH_*`, `MCP_NIXOS_*`, `SLACK_MCP_*`, `SEMANTIC_SCHOLAR_*`, `MCP_REDIS_*`, `MCP_AUTH_*`, `CHROMA_<PROVIDER>_*` — agreement is so strong that the absence of the prefix (raw `PORT`, `HOST`, generic `KUBECONFIG`, `DOCKER_HOST`, `JUPYTER_TOKEN`) marks a settings as inherited from upstream library convention rather than authored for the MCP server; (2) env-var surface size correlates with role of env in the configuration story — single-secret servers (`PERPLEXITY_API_KEY`, `EXA_API_KEY`, `RIZA_API_KEY`, `LINEAR_API_KEY`, `HF_TOKEN`, `DISCORD_TOKEN`) versus comprehensive env-only configuration (qdrant `CLI args deprecated; env-var-only`, mcp-atlassian `Env-var-driven with no documented CLI flag surface`, mcp-turso-cloud `Env-only configuration surface`, utensils-mcp-nixos `Env-var-only configuration surface`). The current description treats env vars as a single dominant path; the corpus shows two distinct uses — credential carrier (the common "token in env" case) versus full configuration substrate (the "env-var-only" subset).

**Sharpened text suggestion.** Add to existing description:

> Vendor-prefixed conventions appear at near-universal adoption: a single tool prefix (e.g., `MDB_MCP_*`, `PAPER_SEARCH_MCP_*`, `MCP_NIXOS_*`, `SLACK_MCP_*`, `SEMANTIC_SCHOLAR_*`) namespaces every setting the server itself authors. Exceptions trace to settings inherited from an upstream library's idiom (`KUBECONFIG`, `DOCKER_HOST`, `JUPYTER_TOKEN`, raw `PORT`/`HOST`) — the absence of the project prefix signals "this name is owned by the upstream client, not by this server". A subset of servers explicitly mark CLI as deprecated and treat env as the *only* configuration substrate (qdrant, mcp-atlassian, mcp-turso-cloud, mcp-nixos), distinct from the more common pattern of env carrying credentials while CLI carries operational switches.

### `Sample > Configuration delivery > CLI flags`

**What the existing description misses.** Two clusters within the supporting samples that aren't surfaced: (1) **capability-gating CLI flags** — `--read-only`, `--write-access`, `--enable-write-tools`, `--disable-destructive`, `--toolsets`, `--tools`, `--lockdown-mode`, `--access-mode`, `--readOnly`, `--read-write`, `--allow-root`, `--full`, `--allow-switch-databases`, `--auto-approve`, `--access-mode` — flags that meaningfully change what tools the server exposes or what they're allowed to do; (2) **connection/transport CLI flags** — `--host`, `--port`, `--transport`, `--api-key`, `--connection-string`, `--db-path`, `--url`, `--config`. The current description lists examples but doesn't surface that these are two functionally distinct uses of CLI: capability gating (operationally meaningful, user-visible in `ps`) vs. connection plumbing (what env vars often carry instead). The "capability-gating" cluster is the more deliberate authorial choice — using flags rather than env explicitly for visibility in process listings and host config snippets.

**Sharpened text suggestion.** Tighten the existing rationale block to:

> Flags cluster into two distinct uses across the corpus: (1) capability gating — `--read-only`, `--write-access`, `--enable-write-tools`, `--toolsets`, `--tools`, `--lockdown-mode`, `--allow-root`, `--access-mode`, `--full`, `--auto-approve` — flags that change what surface the server presents and that authors deliberately surface in process listings and host-config snippets; (2) connection/transport plumbing — `--host`, `--port`, `--transport`, `--db-path`, `--connection-string`, `--config <path>` — settings that are intrinsically per-launch. Authors lean on flags when (a) the value is per-launch and structurally identifies the running instance (transport choice, port, which spec to mount), (b) the operationally-meaningful switch should be visible in process lists and shell history (capability gating), or (c) the host-config snippet should be self-documenting at a glance.

### `Sample > Configuration delivery > Host-side JSON config snippet`

**What the existing description misses.** The corpus is highly redundant under this path (33 samples, mostly enumerating the same target hosts) and the description already captures the universal mechanism. Cross-corpus visibility surfaces three sub-patterns the description could note: (1) **scope levels** — global `~/.cursor/mcp.json` versus project-scoped `.cursor/mcp.json` (jbeno, slackapi); (2) **uvx package-reference idioms** — `uvx --from <pkg>@latest`, `uvx <pkg>`, `uv --directory <abs> run <name>` — these appear repeatedly but they're a host-config snippet detail; (3) **per-host snippet target inventory** — Claude Desktop is universal, Cursor is near-universal, VS Code, Windsurf, Cline, Zed, Kiro, GitHub Copilot CLI, Goose, Qodo Gen, Highlight AI, Augment Code, Msty AI all appear; the surface "host inventory" expands well beyond the original Claude Desktop case. The description's enumeration of host paths is already representative; adding more host names doesn't help.

**Sharpened text suggestion.** Add at end of existing description:

> Scope levels matter — both global (`~/.cursor/mcp.json`) and project-scoped (`.cursor/mcp.json`) variants are documented across hosts that support both. The host inventory observed in the corpus reaches well past Claude Desktop and Cursor — VS Code, Windsurf, Cline, Zed, Kiro, GitHub Copilot CLI, Goose, Qodo Gen, Highlight AI, Augment Code, Msty AI all show up — though Claude Desktop's `claude_desktop_config.json` remains the most-documented target.

### `Sample > Configuration delivery > Dotenv file`

**What the existing description misses.** The description correctly notes the priority-inversion case (zilliztech) as one observed exception. Cross-corpus visibility shows the dotenv path almost always co-occurs with explicit env-var support — it's never the *only* surface; it's a developer-convenience layer that ships an `.env.example` template (openags, marlonluo2018, reminia explicitly, others implicitly). One sample (chroma-core) routes dotenv through a `--dotenv-path` CLI flag, making the dotenv layer itself controllable per-launch. Description is accurate; no sharpening needed beyond what's there.

### `Sample > Configuration delivery > Sidecar config files (JSON / YAML / TOML / EDN)`

**What the existing description misses.** Two cross-corpus patterns: (1) **sidecar usage bifurcates** between configs that are checked into the consuming repository (apollographql operations, googleapis `tools.yaml`, bhauman `.clojure-mcp/config.edn`, opensearch `example_config.yml`) versus configs that are operator-edited per deployment (mongodb `MDB_MCP_CONFIG`, executeautomation `mcp-config.json`, microsoft `--config`). The repo-checked-in case ties strongly to the *Capability surface — Capability authoring style* role (the YAML manifest IS the tool definition), while the operator-edited case is just structured config that env vars handle awkwardly; (2) Among the 7 supporting samples, the tool-authoring use accounts for at least apollographql, bhauman, googleapis, opensearch — close to half — suggesting the path collapses two distinct intents.

**Sharpened text suggestion.** Existing description states the rationale; sharpen by inserting after "JSON5 (allows comments…) appears…":

> The sidecar surface bifurcates by who writes the file: (a) authored-and-versioned (apollographql operations, googleapis `tools.yaml`, bhauman `.clojure-mcp/config.edn`, opensearch `example_config.yml`) where the file IS the tool surface and ships in the repo, versus (b) operator-edited (mongodb `MDB_MCP_CONFIG`, microsoft `--config`, executeautomation `mcp-config.json`) where the file is local deployment state. The first cluster overlaps strongly with the *Capability authoring style* role; the second is purely a richer-than-env config surface.

### `Sample > Configuration delivery > Functional options at construction (code-level)`

**What the existing description misses.** All 6 supporting samples are SDK/library projects (jlowin/fastmcp, mark3labs/mcp-go, metoro-io/mcp-golang, viant/mcp, modelcontextprotocol/kotlin-sdk, conikeec/mcpr) — the path is essentially a marker for "this is an SDK, not a server". The description acknowledges this ("Appropriate when the consumer is writing the server program themselves") but the corpus signal is stronger: this path identifies an SDK rather than describing an alternate config-delivery mechanism. Cross-role reference to *Server runtime — \*-SDK rows* would help readers see the connection.

**Sharpened text suggestion.** Add at end:

> All 6 supporting samples in this corpus are SDKs/libraries (FastMCP, mcp-go, mcp-golang, viant, kotlin-sdk, mcpr), not servers. The path is in practice a "this is an SDK" marker on the configuration-delivery axis — for SDK consumers building servers, this is the only configuration surface; for end users running pre-built servers, the configuration surfaces of *that* server apply. Cross-role: *Server runtime* rows tagged as SDKs (e.g., `Python with raw MCP SDK`, `Go with mark3labs/mcp-go SDK`).

### `Sample > Configuration delivery > Connection URI scheme`

**What the existing description misses.** All 4 samples are database/cache servers (postgres x3, redis x1) where the URI is the upstream-library idiom, not a deliberate MCP author choice. Description notes "Often accepted alongside discrete CLI flags" — the corpus shows this is essentially universal: postgres servers accept both `POSTGRES_URL` and `POSTGRES_HOST`/`POSTGRES_USERNAME`/etc.; redis-mcp accepts `--url` alongside discrete flags. The URI scheme path is not standalone — it's always layered.

**Sharpened text suggestion.** Append:

> All 4 supporting samples (3 postgres, 1 redis) accept the URI alongside discrete connection flags rather than as the sole connection surface — this path is in every observed case a layer over discrete env/flag config, not a replacement.

### `Sample > Configuration delivery > Hosted endpoint as primary delivery`

**What the existing description misses.** The 4 supporting samples diverge meaningfully: (1) cloudflare carries Wrangler config + `mcp-remote` shim; (2) idosal/git-mcp encodes per-repo config in the URL path itself (`gitmcp.io/{owner}/{repo}`); (3) slackapi runs at a fixed enterprise URL; (4) upstash/context7 runs at a fixed URL with API key in headers. Three sub-patterns are visible: (a) Wrangler-based deploys (cloudflare, slackapi-style infra), (b) URL-path-as-config (idosal), (c) fixed-URL + header auth (upstash, slackapi for end users). The "near-zero local config" framing is accurate but misses that "near-zero" varies — Cloudflare has Wrangler, idosal encodes config in the path itself.

**Sharpened text suggestion.** Replace existing description with:

> For hosted-endpoint distributions, "configuration" reduces to the JSON snippet pointing at a URL — the server has near-zero per-tenant local config. Three observed shapes: (a) fixed URL with header-supplied credentials (`https://mcp.context7.com/mcp` + `CONTEXT7_API_KEY`); (b) URL-path-as-config (`gitmcp.io/{owner}/{repo}` — the path itself names the repository the server should expose); (c) Wrangler-deployed Worker fronted by an `mcp-remote` shim (Cloudflare). The end-user-facing config-delivery surface in all three cases is the host's `mcpServers` JSON entry; per-tenant scoping happens through URL or headers, not through env or CLI.

### `Sample > Configuration delivery > HTTP request headers`

**What the existing description misses.** Two distinct uses across the 6 supporting samples: (1) **per-request credential carrier** — neondatabase, makenotion, teaguesterling, lanbaoshen — bearer tokens or per-tenant credentials supplied per request; (2) **observability/source identification** — exa-labs (`x-exa-source: claude-code-plugin`) — not configuration in any meaningful sense, more like a User-Agent. mongodb-js's `--allowRequestOverrides` flag is a meta-position: it controls whether headers are *allowed* to override server-wide config, suggesting the per-request header surface is sometimes opt-in for security. The "exa-labs" placement under HTTP request headers feels like a stretch — `x-exa-source` is metadata, not configuration delivery.

**Sharpened text suggestion.** Append:

> Two functional uses observed: (a) per-request credential or scope carrier (neondatabase, makenotion, lanbaoshen, teaguesterling) where each MCP request authenticates or scopes itself via headers — required for HTTP multi-tenancy; (b) observability/source identification (exa-labs `x-exa-source`, mongodb-js when `--allowRequestOverrides=true`) where headers identify the calling client rather than configure server behavior. The credential-carrier use is the substantive case; the observability use is closer to a User-Agent.

### `Sample > Configuration delivery > Auto-generated host-config JSON files`

**What the existing description misses.** Both supporting samples (normaltusker, samuelgursky/davinci-resolve) pair this path with an installer script that walks the user through per-host setup. davinci-resolve writes into 10 different host config locations. Description already captures this. No sharpening needed.

### `Sample > Configuration delivery > Framework-native config file`

**What the existing description misses.** The two supporting samples are heterogeneous to the point that grouping is questionable: (1) ClickHouse-mcp ships `fastmcp.json` for FastMCP framework settings (legitimately framework-native); (2) teaguesterling/duckdb_mcp is placed here but its content actually describes SQL PRAGMA calls as the primary config mechanism — the JSON config file mentioned is a secondary path for HTTP/token settings. **The duckdb_mcp content is a mis-placement** — it should sit under "SQL PRAGMA parameters" (currently 0 supporting samples). After moving duckdb_mcp out, this path has only 1 supporting sample (ClickHouse fastmcp.json) and arguably becomes a single-instance idiom. See *Mis-placed samples* below.

### `Sample > Configuration delivery > Runtime reconfiguration tool`

**What the existing description misses.** The two supporting samples represent two distinct "runtime reconfiguration" patterns: (1) googleapis/mcp-toolbox auto-reloads the YAML manifest when the file changes — operator edits a file and the running process picks it up; (2) sandraschi/email-mcp exposes a `configure_service` MCP tool that the LLM/host can call to swap providers mid-session. These are very different mechanisms — file-watched hot reload vs. tool-driven reconfiguration. The current description only mentions the tool-driven case.

**Sharpened text suggestion.** Replace with:

> Two distinct patterns share this path: (a) tool-driven reconfiguration (sandraschi/email-mcp's `configure_service`) where the host/LLM invokes an MCP tool to swap providers mid-session; (b) file-watched hot reload (googleapis/mcp-toolbox where `tools.yaml` edits propagate without restart, with `--disable-reload` as the opt-out). Both let configuration change without process churn but the trigger differs — host-initiated tool call versus filesystem event. Each implies state surviving across configuration changes, a different lifecycle assumption from the typical re-exec pattern.

### `Sample > Configuration delivery > URL query parameters on HTTP connection`

**What the existing description misses.** Three supporting samples represent three distinct intents: (1) supabase-community is the canonical three-axis case (scope + mode + features); (2) neondatabase carries similar tenant-scoping (readonly, category, projectId); (3) exa-labs uses `?client=claude-code-plugin` purely for source identification, not configuration. Same observation as HTTP headers — observability use cases get conflated with substantive configuration carriers. The description correctly emphasizes the multi-tenancy case; the exa-labs placement is the outlier.

### `Sample > Configuration delivery > Mounted credentials`

**What the existing description misses.** All 4 supporting samples are container-or-CLI-tool wrappers (k8s, docker daemon, AWS, kubectl) where the credential file format is an upstream-tool standard (kubeconfig, AWS credentials file). Description captures this accurately.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### `Sample > Configuration delivery > Environment variables` — credential-carrier vs. full-configuration-substrate

Sub-pattern: env as credential carrier with CLI/file carrying everything else (most samples) vs. env as the *only* configuration substrate (qdrant `CLI args deprecated`, mcp-atlassian `no documented CLI flag surface`, mcp-turso-cloud `Env-only configuration surface`, mcp-nixos `Env-var-only configuration surface`). 4 samples explicitly mark env as the sole surface, ~68 use env in the dominant-but-not-sole role. Below the 3-sample threshold-per-mode if we're strict, but folded into description sharpening above.

**Recommendation.** Fold into description (already proposed above), don't split — the underlying mechanism is the same; the difference is "does CLI exist alongside" which a reader can look up.

### `Sample > Configuration delivery > CLI flags` — capability-gating vs. connection-plumbing

Sub-pattern: capability-gating flags (~14 samples) vs. connection/transport flags (~20 samples). Many samples use both. This is an authorial-intent split rather than a mechanism split.

**Recommendation.** Fold into description (already proposed above), don't split — same underlying mechanism (argv parsing); a reader benefits from knowing the two purposes coexist within "CLI flags" rather than from a separate path.

### `Sample > Configuration delivery > HTTP request headers` — credential-carrier vs. observability-marker

Sub-pattern: per-request credential/scope (4 samples) vs. observability/source-id (1-2 samples).

**Recommendation.** Fold into description (already proposed above), don't split — single observability sample doesn't justify a path; better to flag the placement as a stretch in description.

### `Sample > Configuration delivery > Sidecar config files (JSON / YAML / TOML / EDN)` — repo-versioned-tool-authoring vs. operator-edited-deployment-config

Sub-pattern: 3-4 samples are tool-authoring artifacts (YAML manifest IS the surface) — strong overlap with `YAML manifest (declarative tool authoring)` path. Other 3-4 are operator-edited deployment config.

**Recommendation.** Possible bucket merge (see proposed merges below): `YAML manifest (declarative tool authoring)` may already be a separation of the same intent. The split is principled; the mechanism overlaps.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

### Candidate: `Sidecar config files (JSON / YAML / TOML / EDN)` + `YAML manifest (declarative tool authoring)`

**Why considered.** The YAML-manifest path's two supporting samples (googleapis/mcp-toolbox, opensearch/example_config.yml) are also sidecar config files; the differentiator is "the sidecar IS the tool surface" (declarative tool authoring) vs. "the sidecar is structured deployment config". Cross-corpus visibility shows several samples currently under "Sidecar config" are also tool-authoring (apollographql operations, bhauman `.clojure-mcp/config.edn`).

**Why NOT to merge.** The "declarative tool authoring" path describes a meaningful authorial intent — the file replaces the code where tool definitions normally live. That semantic distinction is worth preserving. Better to keep the bucket and re-classify samples currently under sidecar that fit the manifest pattern.

**Recommendation.** Don't merge. Instead, surface in *Mis-placed samples* below: apollographql and bhauman might better fit `YAML manifest (declarative tool authoring)` since their sidecars carry tool definitions.

### Candidate: `Hosted endpoint as primary delivery` + `Wrangler config (Cloudflare Workers)`

**Why considered.** Wrangler config has 0 direct supporting samples; cloudflare's content discusses Wrangler under "Hosted endpoint as primary delivery". The two paths describe the same Cloudflare-Workers deployment story split across two tree positions.

**Recommendation.** Merge — fold Wrangler into Hosted-endpoint description. The standalone Wrangler path adds nothing; it's deployment-time machinery that already lives within the hosted-endpoint story. After merge, the Wrangler path can be removed from the tree as zero-supporting-sample.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed at this stage. Sub-axes identified above (env credential vs. substrate; CLI capability vs. connection; sidecar authoring vs. deployment) are best handled as description sharpening rather than splits — the underlying mechanism is the same and forcing readers to navigate twice as many paths slows comprehension without payoff.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `teaguesterling--duckdb_mcp.md` — currently under `Framework-native config file` better fits `SQL PRAGMA parameters`

**Evidence.** The sample's content under "Framework-native config file" reads: "SQL PRAGMA calls with parameters (name, description, SQL template, properties, required fields, output format) are the primary config mechanism. JSON config file for HTTP/token settings." The substantive content is PRAGMA-driven runtime configuration. The "SQL PRAGMA parameters" path currently has 0 supporting samples — moving duckdb_mcp there gives that path its natural exemplar and aligns the placement with what the sample actually does. After the move, "Framework-native config file" loses its second sample, leaving only ClickHouse-mcp's `fastmcp.json` — which is the cleaner case for "framework-native".

### `exa-labs--exa-mcp-server.md` (HTTP request headers + URL query parameters) — placement is a stretch

**Evidence.** The exa-labs content under both `HTTP request headers` (`x-exa-source: claude-code-plugin`) and `URL query parameters on HTTP connection` (`?client=claude-code-plugin`) is observability/source-identification metadata, not configuration. There's no path on the tree that fits this better, but its presence inflates both bucket counts misleadingly. Either:

- Drop the exa-labs entries from these paths (the substantive config lives in env/host-config-snippet entries which exa-labs also has)
- Add a description note in both paths flagging that "observability/source-id metadata uses the same surface but is not configuration"

Reconciler decision needed; my recommendation is to drop the exa-labs entries — the sample is well-supported elsewhere and these two entries don't represent configuration delivery.

### `cloudflare--mcp-server-cloudflare.md` — also exemplifies `Wrangler config` (currently 0 supporting)

**Evidence.** Cloudflare's `Hosted endpoint as primary delivery` content explicitly says "Server-side configuration is Wrangler config per Worker (`wrangler.toml`/`wrangler.jsonc`) controlling deployment". If `Wrangler config` is kept as a path, cloudflare belongs under it. Per the merge proposal above, the cleaner action is to drop the Wrangler path and absorb its content into the hosted-endpoint description.

### `apollographql--apollo-mcp-server.md`, `bhauman--clojure-mcp.md` — currently under `Sidecar config files` may fit `YAML manifest (declarative tool authoring)` better

**Evidence.** Both samples describe sidecar configs that carry tool/operation definitions, not just deployment settings. Apollographql: "operation definitions for MCP tools". Bhauman: ".clojure-mcp/config.edn with a Clojure-map structure carries tool filtering, profile selection". The "Sidecar" path collapses these into the deployment-config cluster; the "YAML manifest" path captures the "config file IS the tool surface" intent more accurately. Caveat: the manifest path's name says "YAML" while these are JSON5/EDN — a mismatch. Reconciler may prefer to broaden the manifest path's name (e.g., "Declarative tool-authoring manifest") or accept the misnomer.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Configuration-delivery axes are layered, not mutually exclusive

Most samples populate 2-4 paths under this role. The corpus shows configuration delivery is a *stack*, not a choice — env vars dominate (70%) but rarely as the sole surface; CLI flags (36%) and host-config snippets (32%) layer on top; dotenv (11%), sidecar files (7%), and connection URIs (4%) appear as niche additions. The role's role-level description treats this as one-of-N alternatives implicitly; reframing as a layered stack might serve readers better.

### Resolution priority is conventional and rarely documented

Multiple samples that use both CLI and env note resolution priority (CLI > env > file is typical). One sample (zilliztech) explicitly inverts to file > CLI > env. Most samples don't document resolution priority at all — implying authors and operators rely on convention. A future research direction might inspect actual implementation behavior versus documented behavior, but that's beyond depth-pass scope.

### Vendor-prefix discipline is the single strongest convention

Across 72 supporting samples for env vars, the pattern of `<TOOL>_<SETTING>` namespacing is so consistent that deviations are visible signals — non-prefixed env vars (`KUBECONFIG`, `DOCKER_HOST`, `JUPYTER_TOKEN`, `PORT`, `HOST`) trace back to the upstream library's idiom in nearly every case. This is the role's most reliable cross-corpus regularity.

### Path naming uses parentheticals; description sharpening should not

Two paths use parenthetical qualifiers in the heading (`Sidecar config files (JSON / YAML / TOML / EDN)`, `YAML manifest (declarative tool authoring)`, `Functional options at construction (code-level)`, `Wrangler config (Cloudflare Workers)`). Pattern is consistent with the rest of the consolidated and not worth changing — observation only.

### The "configuration carrier" axis spans more than this role

Multi-tenancy (URL query params for per-request scope), Authentication (per-request bearer tokens), and Capability surface (toolset filtering) all show up as configuration-delivery sub-cases too. The role boundary holds — Configuration delivery is "how does config reach the server" — but readers may benefit from cross-references already present (e.g., "Cross-role: see *Capability surface — Capability gating flags*"). Several paths could carry similar cross-references but don't; a sweep to add them where applicable would help navigation. Not a depth-pass action; flagging for the reconciler.
