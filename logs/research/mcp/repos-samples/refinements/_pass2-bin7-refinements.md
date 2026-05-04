# Pass 2 Refinements — Bin 7

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Build and packaging > Go modules (go.mod / go.sum)` — `korotovsky--slack-mcp-server.md` (`go.mod`, `go.sum`), `lanbaoshen--mcp-jenkins.md` (multi-platform Docker build artifacts) — Standard Go build via `go.mod` and `go.sum`. Distinct from `Cargo (Rust)`, `npm/Node toolchain`, `Maven / Gradle (JVM)` — corpus has Go runtimes (`Go with mark3labs/mcp-go SDK`, `Go with metoro-io/mcp-golang or alternative SDK`, `Go with custom MCP implementation`) but the *Build and packaging* role lacks a Go entry. Produces single static binaries; pairs naturally with Docker container distribution.

- `Distribution channel > Source build with go toolchain` — `korotovsky--slack-mcp-server.md` (`go run mcp/mcp-server.go --transport stdio`) — Go-equivalent of `Source clone with uv run from source tree`. Distinct from `Go module via go get / go install` (SDK/binary install) and `Pre-built binary release` (artifact download). Currently absorbed into `Go module via go get / go install` for lack of a better fit. Reconciler may want to introduce a Go source-build path or generalize the existing source-clone path to be language-neutral.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`jlowin--fastmcp.md` is the FastMCP framework itself, not a server built on FastMCP.** Placed under `Server runtime > Python with FastMCP` because that's the closest existing path, but the consolidated description is for "Python server built on the FastMCP decorator framework" (i.e., a consumer). The framework is the substrate, not a server. The sample's content describes the framework's surface (decorator API, three pillars Servers/Clients/Apps, optional dependency fan-out for multiple LLM providers, very rich pytest tooling, src-layout, llms.txt). Reconciler may want a `Server runtime > FastMCP framework (Python)` path or to mark the framework as a "library, not a runtime" entity in the way the consolidated already does for `Multi-tenancy > N/A (library, not a runtime)` — and adopt analogous "N/A (library, not a runtime)" framing across roles where the framework's content is meta (no server built; the framework is the artifact).

- **`labeveryday--mcp_pdf_reader.md` lacks a `Host integration` role entirely.** Source notes "Host integrations shown in README or repo: Not captured explicitly per host." The sample documents none of `Claude Desktop`, `Cursor`, `VS Code`, etc. Per *Mirror the consolidated's role tree* I omitted the role entirely. If the reconciler views absence-of-host-integration as a meaningful observation worth flagging (vs. "no evidence"), a fallback path like `Host integration > No host integration documentation` (which exists in the consolidated at line 1551) might apply — but the sample's data isn't strong enough to assert "no integration documented" vs. "couldn't capture which hosts". Left out for honesty.

- **`korotovsky--slack-mcp-server.md` Go-modules build path missing.** Sample uses `go.mod` and `go.sum` (Go's standard build/dep tooling), but no `Build and packaging > Go modules / go.mod` path exists. Listed as a proposed new path above; sample currently has no explicit `Build and packaging` heading because no existing path fits.

- **`lanbaoshen--mcp-jenkins.md` JetBrains IDE callout.** Listed under `Host integration > JetBrains IDE`. The sample notes "JetBrains IDE integration is unusual — most MCP servers focus on Claude Desktop / Code / Cursor" — preserved as factual content. The path in the consolidated explicitly accommodates JetBrains.

- **`jbeno--cursor-notebook-mcp.md` declares dual MCP framework deps.** Sample lists both FastMCP 2.x and raw `mcp >= 0.1.0`. Resolved to single placement `Server runtime > Python with both MCP SDK and FastMCP declared` (the consolidated's purpose-built path for this pattern), rather than dual placement under `Python with FastMCP` and `Python with raw MCP SDK`.

- **`mahdin75--gis-mcp.md` REST endpoints under `Capability surface`.** Placed `/storage/upload`, `/storage/download`, `/storage/list` REST endpoints under `Capability surface > REST endpoints alongside MCP tools`, which the consolidated description names exactly this pattern (HTTP-mode servers add purpose-built REST endpoints for binary artifact transfer). Good fit; flagging because samples that exhibit dual MCP+REST surfaces are rare and this path's evidence base may be small.
