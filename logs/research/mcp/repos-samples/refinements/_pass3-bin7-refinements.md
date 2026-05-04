# Pass 3 Refinements — Bin 7

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 7 samples. Samples were already in role-tree format from Pass 2; this pass verified chain-key alignment, applied targeted prose updates (cross-corpus phrasing trims), and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Build and packaging > Go modules (`go.mod` / `go.sum`)` — `korotovsky--slack-mcp-server.md` uses `go.mod` and `go.sum` as Go's native build/dep tooling; `lanbaoshen--mcp-jenkins.md` ships multi-platform Docker build artifacts that imply Go modules under the hood. Sibling to existing language-native build paths (`Cargo (Rust)`, `Maven / Gradle (JVM)`, `npm/Node toolchain`). Same path proposed by Pass 3 bin-6 with broader corpus support — reconciler should integrate. Until integrated, korotovsky drops `Build and packaging` entirely (rather than using a placeholder), per the methodology's "do not include empty nodes" rule. Carried forward from Pass 2 unresolved.

- `Distribution channel > Source build with go toolchain` — `korotovsky--slack-mcp-server.md` documents `go run mcp/mcp-server.go --transport stdio` as a self-built launch path. Currently absorbed into `Go module via go get / go install`. Pass 3 bin-6 resolved this same gap by leaving Go source-build evidence under `Distribution channel > Go module via go get / go install`, treating the existing path as broad enough. Reconciler may want to either generalize the existing Go-module path's description, introduce a new source-build path, or accept the current placement. Carried forward from Pass 2 unresolved.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Server runtime > Python with both MCP SDK and FastMCP declared` — `jbeno--cursor-notebook-mcp.md` lists FastMCP `>= 2.7.0, < 2.11` and `mcp >= 0.1.0` together with the `< 2.11` upper bound explicitly guarding against FastMCP 2.11 breaking changes. Sharpening: dual-declaration is sometimes paired with narrow upper-bound version pins on the FastMCP side (e.g., `<2.11`) to control churn while raw `mcp` carries a loose floor — reflects the migration-or-compatibility-shim posture more concretely than the existing path describes. Carried forward from Pass 2 unresolved.

- `Distribution channel > MCPB bundle / Desktop Extension manifest` — `korotovsky--slack-mcp-server.md` ships `manifest-dxt.json` as a primary alternative-channel for non-developer Claude Desktop install. Sharpening: DXT manifest is a viable primary channel for Go binary servers (where neither PyPI nor npm is the natural path) — a frictionless install path that lets Go-based MCP servers reach the broad Claude Desktop audience without requiring users to manage Go toolchains. Carried forward from Pass 2 unresolved.

- `Authentication > Multi-mode token selection` — `korotovsky--slack-mcp-server.md` exposes four distinct token types (`XOXC` browser cookie, `XOXD` additional cookie, `XOXP` user OAuth, `XOXB` bot) with the combination determining operating mode. Sharpening: multi-mode token selection can range from privilege-minimized "stealth mode" (cookie-based, no workspace permissions) to formal OAuth (workspace admin approval required) — a deliberate sliding-scale trust posture, not just multiple ways to authenticate the same identity. Carried forward from Pass 2 unresolved.

- `Configuration delivery > HTTP request headers` — `lanbaoshen--mcp-jenkins.md` uses `x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password` headers per request to route different requests to different Jenkins instances from a single deployed server. Sharpening: per-request HTTP-header credentials commonly carry not just the credential itself but also the upstream URL, enabling a single deployed server to serve multiple upstream instances (each tenant's own Jenkins/Confluence/etc.) without per-tenant deployment. Carried forward from Pass 2 unresolved.

- `Multi-tenancy > Connection-lifecycle as a knob` — `ktanaka101--mcp-server-duckdb.md` exposes `--keep-connection` as an explicit flag enabling TEMP objects across calls; `lanbaoshen--mcp-jenkins.md` exposes session-singleton mode for connection pooling. Sharpening: connection-lifecycle knobs surface in multiple substrates (DuckDB sessions, Jenkins HTTP clients) when persistent state is valuable for one use case but breaks the stateless-per-request model — reflects a recurring design tension between cross-call state and stateless-multi-tenant safety. Carried forward from Pass 2 unresolved.

- `Capability surface > Library fan-out` — `mahdin75--gis-mcp.md` exhibits the shape with 92 tools across 5+ libraries, paired with eight domain-specific optional extras (`administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, plus `test`). Sharpening: library fan-out commonly co-occurs with per-upstream-library optional-extras packaging, letting users install only the toolchain slices they need — but heavy core deps (geopandas, rasterio) sometimes stay in core regardless, prioritizing install simplicity over minimal footprint. Carried forward from Pass 2 unresolved.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every fact in this bin maps to an existing role)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`jlowin--fastmcp.md` is the FastMCP framework itself, not a server built on FastMCP.** Currently placed under `Server runtime > Python with FastMCP` because that's the closest existing path, but the consolidated description for that path reads "Python server built on the FastMCP decorator framework" (i.e., a consumer). The framework is the substrate, not a server. The sample's content describes the framework's surface (decorator API, three pillars Servers/Clients/Apps, optional dependency fan-out for multiple LLM providers, very rich pytest tooling, src-layout, llms.txt). Pass 2 already raised this; Pass 3 retained the placement (no better path exists) but trimmed cross-corpus prose — "Modern Python default and the FastMCP reference shape" was edited down to bare-fact "src-layout, etc." since calling itself the reference shape is self-referential and "Modern Python default" is a corpus-level claim. Pass 2's proposal stands: reconciler may want a `Server runtime > FastMCP framework (Python)` path or analogous "N/A (library, not a runtime)" framing across roles where the framework's content is meta. Carried forward from Pass 2 unresolved.

- **`labeveryday--mcp_pdf_reader.md` lacks a `Host integration` role entirely.** Source notes "Host integrations shown in README or repo: Not captured explicitly per host." The sample documents none of `Claude Desktop`, `Cursor`, `VS Code`, etc. Per *Mirror the consolidated's role tree* the role is omitted entirely. If the reconciler views absence-of-host-integration as a meaningful observation worth flagging (vs. "no evidence"), a fallback path like `Host integration > No host integration documentation` (which exists in the consolidated) might apply — but the sample's data isn't strong enough to assert "no integration documented" vs. "couldn't capture which hosts". Left out for honesty. Carried forward from Pass 2 unresolved.

- **`korotovsky--slack-mcp-server.md` Go-modules build path missing.** Sample uses `go.mod` and `go.sum`, but no `Build and packaging > Go modules / go.mod` path exists in the consolidated. Listed as a proposed new path above. Sample currently has no `Build and packaging` heading because no existing path fits — same posture as Pass 3 bin-6 took with its Go samples. Reconciler may want to either add the Go path or confirm that `Distribution channel > Go module via go get / go install` adequately covers Go's build-and-distribution story without a dedicated `Build and packaging` entry.

- **Cross-corpus phrasing cleanup applied in Pass 3.** Three samples carried prose comparing themselves to the broader corpus rather than describing themselves. Pass 3 trimmed these per the methodology's "samples should describe themselves, not compare to other samples":
    - `jbeno--cursor-notebook-mcp.md` — "rare for MCP servers (which overwhelmingly pick permissive licenses)" → trimmed to "non-commercial license. Limits commercial adoption."
    - `ktanaka101--mcp-server-duckdb.md` — "a deliberate session-state trade-off most servers hide" → trimmed to "a deliberate session-state trade-off."
    - `lanbaoshen--mcp-jenkins.md` — "Documented JetBrains IDE integration — unusual; most MCP servers focus on Claude Desktop / Code / Cursor." → trimmed to "Documented JetBrains IDE integration."
    - `jlowin--fastmcp.md` — "Modern Python default and the FastMCP reference shape" → trimmed to bare repo-layout description.
    Other comparison-flavored prose in `jlowin--fastmcp.md` (self-claim of powering "70% of MCP servers", "absorbed into the official MCP Python SDK in 2024", "de facto the canonical Python MCP authoring path") was preserved as describing the framework's own self-claims and history — these are facts about the entity, not cross-sample comparisons.

- **Repo metadata in preamble vs roles.** Following the bin-1 / bin-2 convention from earlier passes, repo metadata (stars, last-commit, license-name, default branch, version) lives in the level-1 preamble rather than under any role. License/lifecycle details thus appear in two places: preamble (raw fact) and `Release and lifecycle` paths (qualitative posture). Same concern raised by other bins; reconciler decision still needed. Carried forward from Pass 2 unresolved.

- **`jparkerweb--mcp-sqlite.md` Build and packaging absent.** TypeScript/Node sample with no `Build and packaging` heading. The sample uses `@modelcontextprotocol/sdk`, npm distribution, and a CommonJS `bin` entry — `Build and packaging > npm/Node toolchain` would technically apply, but the sample's current content (npm publish, bin entry) is already captured under `Distribution channel > npm via npx / bunx` and `Entry point and launch`. Per "do not include empty nodes" the role is omitted; reconciler may want to confirm whether npm-toolchain build details are expected to appear separately when distribution and launch already cover the npm story.

- **`mahdin75--gis-mcp.md` REST endpoints alongside MCP tools.** Placed `/storage/upload`, `/storage/download`, `/storage/list` under `Capability surface > REST endpoints alongside MCP tools` — the consolidated's purpose-built path for HTTP-mode binary artifact transfer. Good fit, but this path's evidence base across the corpus may be small; flagging in case the reconciler wants to confirm or split the path further (e.g., distinguishing "REST for binary transfer" from "REST as alternative client surface"). Carried forward from Pass 2 unresolved.

## Convergence assessment

The bin is **almost converged**. All sample level-2 and level-3 headings exactly match consolidated role/path names — chain-key match verified by exhaustive comparison against the consolidated's `### ` set. Pass 3 applied four targeted prose trims to remove cross-corpus phrasing from samples that carried comparative claims about the broader corpus. No new roles needed. Two structural questions remain reconciler-side: whether `Build and packaging` deserves a Go-modules path (so korotovsky can express its actual build mechanism rather than omit the role), and whether `jlowin--fastmcp.md` should have a framework-level `Server runtime` path distinct from the consumer-shaped `Python with FastMCP`. Pass 4 should not be required if the reconciler integrates the proposed paths and acknowledges the framework-vs-server placement.
