# Pass 2 Refinements — Bin 8

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Build and packaging > Go modules / go.mod` — `mark3labs--mcp-go.md` (`go.mod` specifies Go 1.25.5), `metoro-io--mcp-golang.md` (Go module `github.com/metoro-io/mcp-golang`) — Standard Go module layout where `go.mod` declares the module path and Go version constraint; built and resolved by the Go toolchain. Distinct from `Cargo (Rust)` (Rust-specific) and `npm/Node toolchain` (JavaScript) — Go's package and version-pinning surface lives in `go.mod`/`go.sum` rather than in pyproject/package.json/Cargo.toml. The consolidated currently has `Distribution channel > Go module via go get / go install` for distribution but no Build-and-packaging path for the toolchain itself; this is the missing peer to `Cargo (Rust)` for Go-source projects.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Capability surface > Capability gating via tool subsets at install time` — `microsoft--playwright-mcp.md` adds an explicit author-narrated rationale: the project documents `--caps=<group>` as deliberately distinct from per-tool toggles or coarse `--read-only` flags. Existing description captures the mechanism (gates groups of related tools as a unit) but could explicitly note that authors using this path frequently *contrast* it against per-tool gating and present it as a different gating axis — a stylistic stance the corpus surfaces.

- `Transport > Streamable HTTP` — `metoro-io--mcp-golang.md` exposes HTTP via *both* Go stdlib `net/http` and the Gin web framework as parallel integration patterns. Existing description mentions Hono on Node and axum on Rust but doesn't mention Gin — could add Gin as a recognized HTTP-tier framework binding for Go SDK consumers. Could also note the "stateless request-response pattern" framing some Go SDKs use.

- `Test stack > Mock transport layer for protocol-level testing` — `modelcontextprotocol--kotlin-sdk.md` adds Knit-based code-snippet testing (a Kotlin-specific tooling pattern that tests documented snippets). Existing description doesn't mention this style; could note that documentation-as-test patterns also surface here, distinct from `kotlin-sdk-testing` module mocks.

- `Distribution channel > Multi-channel publication` — `modelcontextprotocol--servers.md` ships TypeScript via npm, Python via PyPI, *and* both via Docker — but each reference *server* is multi-channel, while the *repo* is a monorepo of single-language servers. Existing description treats multi-channel as one server published several ways; this case adds a "monorepo where heterogeneous-language children are each multi-channel-published" axis. Sharpening: note that multi-channel can apply per-server within a monorepo, not just per-product.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Go SDK build/packaging is structurally absent from the consolidated.** Both `mark3labs--mcp-go.md` and `metoro-io--mcp-golang.md` are pure SDK libraries distributed via `go get` (under Distribution channel) and consumed by application code. There is no Build-and-packaging path that fits — `Cargo (Rust)`, `npm/Node toolchain`, `Hatchling + uv (Python)`, and `Maven / Gradle (JVM)` cover other ecosystems but no Go peer exists. I left these samples without a `Build and packaging` section rather than mis-bucket them; flagged the gap as a proposed new path above.

- **`metoro-io--mcp-golang.md` Custom or experimental transports** — the README documents "HTTPS with custom auth" as experimental/in-progress. Mapped to `Transport > Custom or experimental transports`, but the auth side is in flux (no real implementation surfaced). I kept the placement but the auth detail under `Authentication > Application-delegated (SDK provides nothing)` is a partial-coverage description rather than capturing the in-progress custom-auth ambition. Reconciler may want a path for "auth-in-progress / experimental" or to leave as Application-delegated.

- **`microsoft--playwright-mcp.md` test stack underspecified.** The sample says `.github/workflows` are present and Playwright's own test harness is "likely used given project heritage" but the actual framework isn't extracted. I placed under `Test stack > No tests / not surfaced` because the path covers "presence of tests not deeply extracted" cases. Reconciler may want a "test surface inferred but unverified" sub-path or to leave it as not-surfaced.

- **`marlonluo2018--pandas-mcp-server.md` PyPI publication unverified.** README hints at `uvx pandas-mcp-cli` but it's unclear whether the package is actually published. I placed under both `Source clone with editable install` (definitely available) and `PyPI via uvx` (hinted/unverified). If the reconciler wants stricter evidence discipline, the uvx path could be flagged as unverified; otherwise this is a reasonable hedged placement.

- **`modelcontextprotocol--servers.md` MCP Roots placement.** The reference Filesystem server implements MCP Roots — placed under `Capability surface > MCP Roots participation` (consumes host roots) and `Configuration delivery > Host-supplied protocol-level config (MCP Roots)`. Both placements feel correct (one for capability, one for config delivery) but they're describing the same fact from two angles. Reconciler may want to clarify whether MCP Roots gets one canonical placement or genuinely is dual-roled.

- **`misbahsy--video-audio-mcp.md` `pytest` in runtime deps.** The sample notes `pytest>=8.3.5` declared in `[project.dependencies]` rather than as a dev extra. I mapped this to `Test stack > Dev extras gating test deps` (the sub-path's existing description explicitly calls out this anti-pattern: "Quirk where pytest lands under [project.dependencies] rather than [dependency-groups]"). Good fit; flagging here only for transparency.

- **`modelcontextprotocol--kotlin-sdk.md` JS / Wasm targets are unusual.** The Kotlin Multiplatform SDK targets JVM, Native, JS, and Wasm. Mapped to `Server runtime > Kotlin Multiplatform SDK` which mentions multiplatform targets, so the description is adequate. But "Wasm-targeted MCP SDK" is a meaningful structural axis for hosts (browser MCP, edge runtimes) that the consolidated does not explicitly surface anywhere else. Reconciler may want to flag Wasm/JS-multiplatform as worth its own discoverability path under either `Server runtime` or `Deployment topology`.

- **`mark3labs--mcp-go.md` task-augmented tool execution and recovery middleware** are unanticipated axes the original sample called out. The closest mappings are `Capability surface > Tools plus resources plus prompts` (full primitive coverage) and `Observability > Request lifecycle hooks for telemetry` (which mentions "recovery middleware that catches handler panics so a single bad tool call doesn't crash the process" — already surfaced). Reconciler may want a separate `Capability surface > Task-augmented tool execution (asynchronous with concurrency limits)` path if it recurs across the corpus; for now the facts are absorbed into the existing paths' descriptions.
