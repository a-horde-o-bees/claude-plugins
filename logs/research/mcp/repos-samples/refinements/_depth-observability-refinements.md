# Depth Pass Refinements — Sample > Observability

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Observability` (role-level)

- **What the description misses.** The role intro says observability "splits between agent-facing logs (visible in MCP client) and ops-facing logs (disk/stdout/external systems)." Cross-corpus evidence shows a third axis the description doesn't name: **discipline-only** (suppress stdout/route-elsewhere) is forced by stdio-transport framing, not chosen for observability — yet half the corpus is shaped by this constraint (Stderr-default, Suppressed-stdout, File-based logging, Pluggable sinks all exist primarily because stdout is reserved for JSON-RPC). The current intro frames observability as a feature space; the corpus shows it's largely a constraint space.
- **Cross-corpus evidence.** Stderr-logging (5), Suppressed-stdout (2), File-based logging (2), `mcp` sink option in mongodb-js's pluggable config — at least 10 samples explicitly cite stdio-cleanliness as the design driver. Health endpoint (3) and Container logs (1) are explicitly tied to "HTTP-mode only."
- **Sharpened text suggestion.** "How the server surfaces what it's doing for operators and debuggers. Three forces shape choices: transport (stdio reserves stdout for JSON-RPC, forcing logs elsewhere; HTTP frees stdout for cluster log capture); audience split (agent-facing logs visible in the MCP client vs. ops-facing logs to disk, stderr, or external systems); and substrate (Lambda, Workers, and containers inherit a logging tier the server doesn't manage). Most corpus entries combine multiple paths — a stdio server typically pairs a destination choice (stderr / file / `mcp` sink) with a level-control choice (env var / `--verbose`)."

### `Sample > Observability > Stderr logging (convention / SDK default)`

- **What the description misses.** Description treats this as a single path; cross-corpus evidence shows it covers two distinct cases — **explicitly chosen** (chroma-core, modelcontextprotocol/servers, zilliztech state SDK-default behavior; FastMCP-standard) versus **inferred from stdio convention** (twolven, v-3 say "destination not specified — likely stderr"). The latter is an epistemic placement, not observed evidence.
- **Cross-corpus evidence.** 3/5 samples explicitly state stderr or SDK-default; 2/5 explicitly mark the placement as inference.
- **Sharpened text suggestion.** "Servers log to stderr by default — implicit in stdio transport since stdout is the protocol channel. Format and levels typically not documented. The host captures stderr if it cares. Configurable level via `FASTMCP_LOG_LEVEL` when FastMCP is in use. Appropriate as the default; explicit only when the project deviates. Some samples are placed here by inference rather than explicit documentation — when a stdio server claims 'detailed error handling' without naming a destination, stderr is the convention."

### `Sample > Observability > loguru (Python)`

- **What the description misses.** Description says loguru is "sometimes paired with `python-json-logger` for JSON-formatted log records — dual logging paths in one server." Cross-corpus evidence shows this pairing happens in only 1/4 samples (awslabs--aws-api-mcp-server). Three of the four are loguru-only. The "sometimes" is over-stated as common.
- **Cross-corpus evidence.** awslabs--aws-api-mcp-server (loguru + python-json-logger), awslabs--aws-documentation-mcp-server (loguru only), awslabs--bedrock-kb-retrieval (loguru only), awslabs--openapi-mcp-server (loguru only). All four are awslabs-pattern servers — loguru is awslabs-house-style, not a broader corpus pattern.
- **Sharpened text suggestion.** "Python `loguru` library used for application logging — replacement logging library favored for ergonomics, structured output, formatting, and rotation without configuring stdlib logging by hand. House style across awslabs servers (every loguru appearance in the corpus is an awslabs sample). One awslabs variant pairs loguru with `python-json-logger` for JSON-formatted records — dual logging paths in one server, presumably one human-readable for dev output and one structured for ingest."

### `Sample > Observability > Standard library \`logging\` (Python)`

- **What the description misses.** Description is one-line ("Python's stdlib `logging` module, default handlers. Minimal but ubiquitous."). It misses that one of the two samples (awslabs--aws-api-mcp-server) is actually `python-json-logger` paired with `loguru` — a JSON formatter on top of stdlib *and* alongside loguru, not stdlib alone. The placement is debatable (see Mis-placed samples).
- **Cross-corpus evidence.** JackKuo666--PubMed (genuine stdlib logging); awslabs--aws-api-mcp-server (python-json-logger + loguru, not really stdlib).
- **Sharpened text suggestion.** "Python's stdlib `logging` module, default handlers. Minimal but ubiquitous when no stronger logging library is brought in. Some entries combine stdlib with formatter libraries (e.g., `python-json-logger` for JSON-structured output) layered onto stdlib's `Logger` class."

### `Sample > Observability > \`rich\`-decorated stdlib logging (Python)`

- **What the description misses.** Single sample (datalayer--earthdata-mcp-server) and the placement is observed only via deps-presence — `rich` in dependencies "implies colorized console output." The sample itself says "no structured observability layer documented." Description claims "same posture as Pino on the Python side" but neither sample evidence supports that comparison.
- **Cross-corpus evidence.** 1 sample, deps-only inference, no actual logging behavior documented.
- **Sharpened text suggestion.** "`rich` library declared as a dependency, implying colorized console output for human-readable logs in development; structured observability not documented. Inferred from deps presence rather than explicit logging configuration."

### `Sample > Observability > Pino / Winston structured logging (Node)`

- **What the description misses.** Description bundles two libraries (Pino, Winston) and adds "often paired with file rotation and a configurable log level via env var." Cross-corpus evidence: both samples (cyanheads--git-mcp-server with Pino; neondatabase--mcp-server-neon with Winston) pair the structured-logger choice with a separate Env-var-controlled log level path. This co-occurrence is universal in the path's two samples — worth promoting from "often" to "always observed in the corpus."
- **Cross-corpus evidence.** cyanheads--git-mcp-server: Pino + env var LOG_LEVEL. neondatabase--mcp-server-neon: Winston + configurable levels via env. Both also pair with additional observability layers (cyanheads adds OTel + request context; neondatabase adds Sentry).
- **Sharpened text suggestion.** "Pino (Node) or Winston (Node/Next.js) for structured logging. Always paired with env-var-controlled log level in the corpus — the structured-logger choice and the level-control mechanism are separable concerns under the same configuration. Appropriate when the server runs as a long-lived process or in production where log searchability matters. Often layered with additional observability (Sentry, OTel, request-context tracking) in the same project."

### `Sample > Observability > Env-var-controlled log level`

- **What the description misses.** Description names env var examples and claims "most common observability surface in the corpus." Cross-corpus evidence supports the claim (7 samples, the largest path after `None`), but misses two patterns: (1) many env-var-controlled samples co-occur with a structured-logger choice (Pino/Winston, loguru) — env-var-level is a *modifier*, not a destination; (2) one sample (severity1--terraform-cloud-mcp) is placed here by inference ("Likely env-var-controlled (mechanism inferred, not directly observed)"). The path mixes confirmed and inferred placements.
- **Cross-corpus evidence.** awslabs--mcp (FASTMCP_LOG_LEVEL), cyanheads--git (env var paired with Pino), cyanheads--perplexity (env var with file rotation), korotovsky--slack (SLACK_MCP_LOG_LEVEL with macOS log path documented), mongodb-js (MCP_CLIENT_LOG_LEVEL paired with pluggable sinks), neondatabase (paired with Winston), severity1 (inferred only).
- **Sharpened text suggestion.** "A single env var (e.g., `PERPLEXITY_LOG_LEVEL`, `MCP_REDIS_LOG_LEVEL`, `FASTMCP_LOG_LEVEL`) sets log severity at startup. Most common observability surface in the corpus, but rarely a *complete* observability story — the path co-occurs with a destination choice (stderr default, structured logger, file-based, pluggable sinks) in most samples. Treat as a level-control modifier on top of a separate destination decision."

### `Sample > Observability > Health endpoint`

- **What the description misses.** Description says "appears where the server is expected to run behind a load balancer or orchestrator" but cross-corpus evidence shows two distinct shapes: bare-protocol path on the main server (elastic `/ping`, teaguesterling `/health`) versus separable monitoring-sidecar (mongodb-js — only available in HTTP mode, surfaces as a separate optional server). The shape difference matters for deployment.
- **Cross-corpus evidence.** elastic--mcp-server-elasticsearch (`/ping` returning "pong"); teaguesterling--duckdb_mcp (`/health` for liveness); mongodb-js--mongodb-mcp-server (optional monitoring-server health endpoint, separable). The first two are inline routes; the third is a sidecar.
- **Sharpened text suggestion.** "An HTTP endpoint (e.g., `/ping` returning 'pong', `/health` for liveness probes). Only meaningful in HTTP-mode deployments. Two shapes observed: inline route on the main MCP server (bare-protocol exposure), or a separable monitoring sidecar that runs alongside the MCP server when HTTP mode is enabled. Sidecar shape pairs with companion-dashboard expectations."

### `Sample > Observability > OpenTelemetry instrumentation`

- **What the description misses.** Description hedges "sometimes baked into core deps so every install ships observability; sometimes optional." Cross-corpus evidence shows a clean 1-1 split — not a continuum: cyanheads--git (optional, instrumentation off by default) vs. datalayer--jupyter (`opentelemetry-api`/`opentelemetry-sdk` >=1.24.0 as core deps, every install ships OTel). Worth presenting as the binary choice rather than a continuum.
- **Cross-corpus evidence.** 2 samples, opposite postures.
- **Sharpened text suggestion.** "OTel API + SDK as a dependency, emitting traces and metrics to whatever collector the operator wires up. Two postures in the corpus: opt-in (declared as an optional/extras dependency, instrumentation off by default — operator activates), and always-on (declared as a core dependency, every install ships observability). The choice is binary, not a continuum: opt-in suits broad-distribution servers where most users won't wire a collector; always-on suits production-grade servers where the operator is expected to integrate with an observability stack."

### `Sample > Observability > Pluggable logger sinks`

- **What the description misses.** Description characterizes this as "Server picks logger destinations from a list (`disk`, `mcp`, `stderr`) controlled by env var (`LOGGERS`)." Cross-corpus evidence: only 1/3 samples (mongodb-js) actually fits this characterization. The other two are different patterns mis-placed under this name (see Mis-placed samples and Proposed bucket splits).
- **Cross-corpus evidence.** mongodb-js (true pluggable sinks via `LOGGERS` config); ClickHouse (example middleware demonstrating extensibility — not the same as built-in pluggable sinks); viant (`Logging()` SDK method to set log level — runtime control primitive, not sink selection).
- **Sharpened text suggestion.** "Server selects logger destinations from a fixed set (`disk`, `mcp`, `stderr`) controlled by configuration; multiple sinks may be combined. The `mcp` sink emits log entries to the connected client — the agent-facing observability path. Appropriate when the operator wants to choose between agent-visible and ops-visible logs per deployment. Distinct from middleware extensibility (where the operator writes their own logger) and from SDK-level log-level primitives (which control verbosity, not destination)."

### `Sample > Observability > Change-notification channels / JSON-RPC notifications`

- **What the description misses.** Description acknowledges this is "indirectly observable but primarily a feature for reactive client UIs." Cross-corpus evidence reinforces this: all 4 samples describe these as protocol features, not observability mechanisms. Three of the four describe notifications-of-availability-changes (tools/resources/prompts), one (viant) describes subscription primitives + progress reporting. Whether this belongs under Observability at all is the larger question — see Categorization decisions.
- **Cross-corpus evidence.** bhauman (JSON-RPC notifications for nREPL connection + tool init); mark3labs (per-client notification channels); metoro-io (change notifications as a supported feature); viant (subscription + progress reporting). Zero of the four describe these notifications being used to observe server health/behavior — they signal capability changes, not operational state.
- **Sharpened text suggestion.** "Server-emitted JSON-RPC notifications for tool/resource/prompt availability changes, surfaced via the SDK as event channels. Indirect observability — primarily a feature for reactive client UIs and capability-set refresh, not an ops-tier observability surface. Appropriate when capabilities are dynamic (REPL state changes which tools are valid) and the host needs to refresh its view. Whether this belongs in 'observability' depends on framing: it surfaces server state-changes to the client, but operators don't reach for it for debugging."

### `Sample > Observability > None / unspecified`

- **What the description misses.** Description says "appropriate for early-stage or single-user-stdio servers where the host's own logging is sufficient. A widespread gap." Cross-corpus evidence shows 11 samples but they fall into two distinct sub-cases: **genuine absence** (the project doesn't document logging at all — blazickjp, misbahsy, upstash) versus **not-surfaced-in-extract** (the sample's research extract didn't capture the logging story even though some logging may exist — slackapi, voska, samuelgursky, modelcontextprotocol--kotlin-sdk). The latter is an artifact of research-extract scope, not a project choice.
- **Cross-corpus evidence.** 11 samples; about half explicitly say "not surfaced/documented in extract," about half say "no logging documented at the project level."
- **Sharpened text suggestion.** "Project doesn't document logging beyond default stdout/stderr; observability is whatever the language/SDK defaults provide, with no project-level shaping. Appropriate for early-stage or single-user-stdio servers where the host's own logging is sufficient. Two sub-cases in the corpus: genuine absence (project explicitly leaves observability to defaults) and research-extract gap (logging may exist but wasn't surfaced in the per-sample research). Both share the consolidated outcome: no project-level shaping visible to a downstream consumer."

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### `Sample > Observability > Health endpoint`

- **Sub-pattern.** Inline route on main server (`/ping`, `/health`) vs. separable monitoring-sidecar (only in HTTP mode).
- **Supporting samples.** 2 inline (elastic, teaguesterling) vs. 1 sidecar (mongodb-js).
- **Recommendation.** Fold into description (above). Too few samples to justify a split, but the shape difference is real and worth surfacing in the description.

### `Sample > Observability > OpenTelemetry instrumentation`

- **Sub-pattern.** Opt-in (extras / off by default) vs. always-on (core deps, every install ships OTel).
- **Supporting samples.** 1 each.
- **Recommendation.** Fold into description (above). Binary choice with clear semantics; description should present it as such.

### `Sample > Observability > Stderr logging (convention / SDK default)`

- **Sub-pattern.** Explicitly stated (chroma, modelcontextprotocol/servers, zilliztech) vs. inferred from stdio convention (twolven, v-3 — "destination not specified — likely stderr").
- **Supporting samples.** 3 explicit, 2 inferred.
- **Recommendation.** Fold into description. The inferred-placement note is an epistemic flag that should be visible to readers — the path is partly observation and partly inference.

### `Sample > Observability > Env-var-controlled log level`

- **Sub-pattern.** Standalone (env var is the only observability surface — awslabs--mcp, severity1) vs. modifier on top of a destination choice (cyanheads--git pairs with Pino, mongodb-js pairs with pluggable sinks, neondatabase pairs with Winston).
- **Supporting samples.** Roughly even split (3 standalone, 4 modifier).
- **Recommendation.** Fold into description. The modifier-vs-standalone distinction reframes how to count "most common observability surface" — many env-var entries are not destination choices but level controls layered on top of another path.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The current paths cover distinct mechanisms; no two paths describe the same choice with different framing.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

### `Sample > Observability > Pluggable logger sinks` — possible split into three

- **Why split.** The current path bundles three distinct mechanisms: (a) genuine pluggable destinations (mongodb-js's `LOGGERS=disk,mcp,stderr` — operator selects from a fixed set), (b) middleware extensibility for logging (ClickHouse's `example_middleware.py` — operator writes their own logger), and (c) SDK runtime log-level primitive (viant's `Logging()` method — operator changes verbosity at runtime). These are different operator interfaces with different mental models.
- **Into what.**
    - `Pluggable logger sinks` (mongodb-js only — keep current name, restrict to true sink-selection)
    - `Logging middleware extensibility` (ClickHouse — middleware example demonstrating where the operator can hook logging into request lifecycle; could fold into existing `Request lifecycle hooks for telemetry`)
    - `SDK log-level primitive` (viant — runtime verbosity control via SDK; could be folded into `Env-var-controlled log level` as a different mechanism, or kept distinct as "SDK runtime control")
- **Distribution.** 1 + 1 + 1 — too few to justify three new buckets, but the conflation in the current single bucket misleads anyone reading the path description.
- **Recommendation.** Surface for reconciler. Either split, or sharpen the description to acknowledge the three patterns under one name (already drafted in Sharpenings above).

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

- **`awslabs--aws-api-mcp-server.md`** currently under `Standard library logging (Python)` better fits `loguru (Python)` (where it's also placed). The sample's content under `Standard library logging` says "`python-json-logger` paired with `loguru` for JSON-formatted log records — second logging path alongside loguru" — that's a JSON formatter layered on stdlib *as a complement to loguru*, not a stdlib-only choice. The sample is already placed under loguru; the stdlib placement is double-counting a single composite logging strategy. Either remove from stdlib or, if double-placement is intentional, sharpen the stdlib description to acknowledge the composite case.

- **`ClickHouse--mcp-clickhouse.md`** currently under `Pluggable logger sinks` better fits `Request lifecycle hooks for telemetry`. The sample's content describes "Example middleware (`example_middleware.py`) demonstrates request logging, tool-call tracking, and performance measurement — extensibility shape rather than fixed observability." That's the same shape as mark3labs--mcp-go's "SDK exposes hooks across all functionality so applications can wire OpenTelemetry, metrics, or logging without modifying SDK code." Both are extensibility hooks for application-layer instrumentation. The Pluggable-sinks path implies fixed sink selection (mongodb-js's mode), which ClickHouse's middleware doesn't fit.

- **`viant--mcp.md`** currently under `Pluggable logger sinks` is a poor fit. Content says "`Logging()` method for setting log levels; progress reporting and request cancellation capabilities exposed as SDK primitives." That's a runtime log-level control primitive, not sink selection. Closest existing match is `Env-var-controlled log level` (it's a level-control mechanism, just SDK-level rather than env-var-level), or it could prompt a new bucket for SDK-level runtime controls. Surface for reconciler.

- **`severity1--terraform-cloud-mcp.md`** under `Env-var-controlled log level` is a self-flagged inferred placement: "Debug logging 'enabled by default' per README; format/destination not surfaced. Likely env-var-controlled (mechanism inferred, not directly observed)." If the reconciler wants the path to contain only observed evidence, this sample arguably belongs under `None / unspecified` (logging exists but the mechanism isn't surfaced) with a note. Alternatively, keep but acknowledge the inference in the description (drafted above).

- **`twolven--mcp-server-puppeteer-py.md`** and **`v-3--discordmcp.md`** under `Stderr logging (convention / SDK default)` are also inferred placements ("destination not specified — likely stderr per stdio convention"). Same shape as severity1; if `None / unspecified` is meant for "not surfaced," these could move there. Description sharpening (above) is the lighter-touch alternative — flag the inference in the path description rather than re-routing the samples.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Stacking is the norm

Most production-shaped samples combine 3-4 paths under Observability rather than picking one. cyanheads--git-mcp-server: Pino + env var + OTel + request context. mongodb-js: pluggable sinks + env var + health endpoint. awslabs--openapi-mcp-server: loguru + Prometheus. neondatabase: Winston + env var + Sentry. The role-level intro should acknowledge this — readers shouldn't expect each sample to pick one path; they should expect a stack.

### Stdio constraint shapes half the corpus

Stderr-default + Suppressed-stdout + File-based logging + the `mcp` sink option in pluggable-sinks all exist primarily because stdout is reserved for JSON-RPC. ~10+ samples are shaped by this constraint. The role description currently doesn't name this force — observability choices for stdio servers are often *constrained* rather than *chosen*.

### Substrate-inherited observability is invisible to the project

CloudWatch via Lambda, Worker logs, Container logs — three paths, four samples — share a property: the project does nothing for observability and inherits the substrate's logging tier for free. This is a distinct *posture* (delegation) rather than a series of similar choices. Worth naming as such if a fourth or fifth sample joins.

### The `None / unspecified` count is muddled by extract scope

11/47 samples are placed here, but roughly half are "not surfaced in extract" rather than "project genuinely doesn't shape observability." The path is mixing two failure modes: project absence and research scope. If the consolidated wants to claim "23% of samples have no observability story," it's actually "23% of samples either have no story or didn't surface one to the researcher." This is an honest signal for the reconciler — the path's count is bounded above by truth, not at it.

### Audit-tier logging is its own micro-cluster

Three paths describe audit-shaped logging — `CloudTrail audit logging`, `Rotating JSON audit log on disk`, `Audit logging for compliance modes` — plus `Request context tracking for audit` is named for audit. Four samples between them. The cluster shares a property (compliance/security framing, redaction discipline, retention rather than triage as the design driver) that's distinct from ops-tier observability. Could earn a sub-axis label like "audit-shaped vs. triage-shaped" within the role intro, but probably too thin to justify restructuring.

### Zero-sample path leftover

`Sample > Observability > \`--interactive\` REPL mode` has 0 supporting samples in the consolidated, but pragmar--mcp-server-webcrawl's content has the exact pattern this path describes (`--interactive` flag drops into terminal REPL, doubles as debug surface, line 95 of the sample). The path may have been authored ahead of evidence and the sample never re-attached, or the sample was placed elsewhere. Surface for reconciler — either remove the zero-count path or attach the pragmar sample to it.
