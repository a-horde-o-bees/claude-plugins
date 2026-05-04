# Depth Pass Refinements — Sample > Cross-role tools

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

This is a meta-section. Per the instructions, the section lists tools that span multiple functional roles; "supporting samples" is therefore zero by design (the section claims spans within the consolidated, not new evidence). Cross-corpus inspection here means verifying each listed tool's claimed cross-role span against the body of the consolidated, and noting tools whose corpus footprint clearly spans roles but are absent from the section.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Cross-role tools > Docker`

Current: "Surfaces as *Distribution channel* (Docker image, Docker Hub MCP Registry, generic Dockerfile pulls), *Container artifacts* (Dockerfile in repo, multi-stage Alpine build, published image, Compose for dev/test/multi-server), *Test stack* (Docker-Compose backend for end-to-end tests; container-based test stack mirroring deploy shape), *Deployment topology* (containerized local process, published container image), and *Entry point and launch* (docker container entrypoint via `docker run -i --rm`)."

Misses:

- Distribution channel parenthetical names "generic Dockerfile pulls" — that phrase is not a real path under Distribution channel. The actual paths are `Docker / OCI image`, `Docker Hub MCP Registry`, and `docker-compose variants` (line 1019). Replace with the real path names.
- *Container artifacts* parenthetical names "Compose for dev/test/multi-server" but the consolidated has three distinct compose paths under *Container artifacts*: `Docker Compose for local dev` (line 1497), `Docker Compose for multi-server orchestration` (line 1501), and `Docker-Compose backend for end-to-end tests` (line 1505); also missing `Multi-Dockerfile (prod / dev split)`, `Per-server Dockerfile in monorepo`, `Dockerfile.template as scaffold`, `Hardened-by-default container posture`, `Vendor-namespaced image`, `Multi-architecture image publishing`, `Makefile-driven Docker build`, `Podman alternative`, `Devcontainer for contributors` — over a dozen Docker-shaped paths live under *Container artifacts*, not just the four listed.
- Missing role: *Configuration delivery > Environment variables* explicitly calls out "container runtimes (Docker `-e` flags)" (line 477) as the natural fit; *Transport > Selection mechanism > Container ARG/CMD* (line 225) names Docker-specific selection. These are not mentioned in the cross-role span.
- Missing role: *Build and packaging > Hatchling + uv* description ties Dockerfile lock-file installs to the build/packaging concern (line 1463: "Often installs from a lock file (`uv.lock`, `requirements.lock`) for reproducibility"). Not strictly a "Docker tool" surface but Docker's transitive presence in build/packaging discussion is real.

Sharpened text suggestion:

> Surfaces as *Distribution channel* (`Docker / OCI image`, `Docker Hub MCP Registry`, `docker-compose variants`), *Container artifacts* (every Dockerfile-shaped path: single-stage, multi-stage, multi-Dockerfile, per-server in monorepo, Dockerfile.template, hardened-by-default, vendor-namespaced, multi-arch, plus Compose for dev / multi-server / end-to-end tests, plus Makefile-driven Docker build, Podman alternative, devcontainer), *Test stack* (`Container-based test stack`, end-to-end tests against Compose-backed substrate), *Deployment topology* (`Containerized local process`, `Published container image (artifact = image)`), *Entry point and launch* (`Docker container entrypoint` via `docker run -i --rm`), *Transport > Selection mechanism* (Container ARG/CMD form), and *Configuration delivery* (env vars passed through `docker run -e`).

### `Sample > Cross-role tools > uv`

Current: "Surfaces as *Distribution channel* (uvx execution, install-from-git via uvx, source clone with editable install), *Entry point and launch* (`uvx <package>`, `uv --directory` from source, source-tree `uv run`), *Build and packaging* (uv_build backend, uv.lock, hatchling + uv pairing), and *Developer ergonomics* (`uv run <tool>` invocations)."

Misses:

- *Distribution channel* parenthetical names "uvx execution" but the actual path name is `PyPI via uvx (zero-install runner)` (line 951); "install-from-git via uvx" maps to `Install-from-git via uvx` (line 959); "source clone with editable install" maps to `Source clone with uv run from source tree` (line 967). Listed entries match conceptually but nominal labels don't match the consolidated headings.
- *Build and packaging* — the consolidated calls these `Hatchling + uv (Python)` and `uv_build backend (Python)` and `uv.lock committed` (lines 1285, 1289, 1317). Naming is approximately right; "uv.lock" path's real heading is `uv.lock committed` (a release-and-lifecycle path also exists named `PyPI + lockfile-tracked` that references `uv.lock`).
- Missing role: *Container artifacts > Dockerfile (single-stage, build-from-source)* description (line 1463) names `uv.lock` and `requirements.lock` install conventions — uv's reach into Dockerfile authoring is a corpus pattern.
- Missing role: *Release and lifecycle > PyPI + lockfile-tracked* (line 2881) — "`uv.lock` committed; PyPI uploads on tag" pairs uv with the release pipeline. This is a fifth role worth surfacing.

Sharpened text suggestion:

> Surfaces as *Distribution channel* (`PyPI via uvx (zero-install runner)`, `Install-from-git via uvx`, `Source clone with uv run from source tree`), *Entry point and launch* (`uvx <package>`, `uv --directory from source`, `Source-tree uv run`), *Build and packaging* (`uv_build backend (Python)`, `Hatchling + uv (Python)`, `uv.lock committed`), *Developer ergonomics* (`uv run <tool> invocations`), *Release and lifecycle* (`PyPI + lockfile-tracked` — `uv.lock` + PyPI publish on tag), and as a transitive presence inside `Container artifacts > Dockerfile` paths (lock-file-driven reproducible image builds).

### `Sample > Cross-role tools > MCPB / Desktop Extension bundle`

Current: "Surfaces as *Distribution channel* (drag-and-drop bundle for Claude Desktop), *Release and lifecycle* (signed bundle artifact, MCPB bundle signing pipeline), *Host integration* (MCPB / DXT manifest among multi-host config samples), and *Container artifacts* (`.mcpbignore` for bundle packaging)."

Misses:

- *Distribution channel* parenthetical "drag-and-drop bundle for Claude Desktop" is a description, not the actual path name. The consolidated heading is `MCPB bundle / Desktop Extension manifest` (line 1047).
- *Container artifacts* role placement is technically correct (`.mcpbignore` lives there) but reads strangely — `.mcpbignore` isn't a *container* artifact in the Docker sense; it's a bundle-packaging artifact filed under *Container artifacts* because that section evolved to host all "what-goes-in-the-shipping-package" files. Surface this categorical oddity to the reconciler — either rename *Container artifacts* to a broader term, or add a note that MCPB packaging artifacts share that role.
- Missing role: *Pre-first-class entry point* / *Entry point and launch* mention. MCPB bundles are runnable artifacts that Claude Desktop launches via its own internal entry-point machinery; the consolidated does not name an MCPB-specific entry point but the bundle is functionally an entry-point packaging.

Sharpened text suggestion:

> Surfaces as *Distribution channel* (`MCPB bundle / Desktop Extension manifest`), *Release and lifecycle* (`MCPB bundle signing` — Rust-toolchain-signed bundle pipeline), *Host integration* (`MCPB / DXT bundle manifest` among multi-host config samples), and *Container artifacts* (`.mcpbignore for bundle packaging` — note: filed under container artifacts as a bundle-packaging artifact, not a Docker artifact).

### `Sample > Cross-role tools > Cargo / Cargo.toml`

Current: "Surfaces as *Server runtime* (Rust SDK declaration, rust-toolchain.toml pin), *Build and packaging* (Cargo backend, Cargo.lock), *Distribution channel* (`cargo install`, crates.io), *Test stack* (Cargo test / cargo-nextest), and *Release and lifecycle* (signing dependency for MCPB bundles in Python projects)."

Misses:

- *Entry point and launch* — Cargo also surfaces here at `Generated binary from scaffolded project` (line 1196: "Project generator emits a Rust crate; user runs `cargo build` and launches `target/debug/<name>`"). This is a sixth role.
- *Container artifacts > Multi-stage Dockerfile* (line 1467) names a Cargo-driven Rust builder stage (`clux/muslrust:stable` → `alpine:latest`) — Cargo's transitive presence in container build is real.
- *Distribution channel* parenthetical "cargo install" exists as a path (`Cargo crate / cargo install`, line 987) but missing the cross-channel `npm package wrapping native binary` path (line 979) which explicitly names Cargo as the underlying toolchain ("forcing users to install Cargo/Go").

Sharpened text suggestion:

> Surfaces as *Server runtime* (`Rust with rmcp / rust-mcp-sdk`, with `rust-toolchain.toml` pin), *Build and packaging* (`Cargo (Rust)` — `Cargo.toml` + `Cargo.lock`), *Distribution channel* (`Cargo crate / cargo install`, plus transitive presence in `npm package wrapping native binary`), *Test stack* (`Cargo test / cargo-nextest (Rust)`), *Entry point and launch* (`Generated binary from scaffolded project` via `cargo build`), *Release and lifecycle* (`MCPB bundle signing` — Rust signing toolchain alongside Python pyproject), and as a transitive presence in `Container artifacts > Multi-stage Dockerfile` (Rust builder stage producing a static binary).

### `Sample > Cross-role tools > Go modules / go.mod`

Current: "Surfaces as *Server runtime* (Go SDK declarations: mark3labs/mcp-go, metoro-io/mcp-golang, custom MCP implementation), *Build and packaging* (`go.mod` / `go.sum` for module path and dependency hashes), *Distribution channel* (`go module via go get / go install`, pre-built binary release, standalone bridge binary), and *Test stack* (Go stdlib testing)."

Misses:

- *Distribution channel* — the listed "go module via go get / go install" matches `Go module via go get / go install` (line 991); "pre-built binary release" and "standalone bridge binary" are not direct path names. The actual related paths are `Pre-built binary release` (under Distribution channel) — let me verify in consolidated.
- *Entry point and launch* — `Native binary` (line 1192: "Pre-built standalone executable from a release artifact (Cargo, Homebrew, npm, release download); users run the binary path directly. Appropriate for Rust/Go-style compiled servers") covers Go binary entry points. Missing from the cross-role span.
- *Container artifacts > Dockerfile single-stage* implicitly covers Go's static-binary friendliness but Cargo's case is the exact same pattern.

Sharpened text suggestion:

> Surfaces as *Server runtime* (`Go with mark3labs/mcp-go SDK`, `Go with metoro-io/mcp-golang or alternative SDK`, `Go with custom MCP implementation`), *Build and packaging* (`Go modules (go.mod / go.sum)` — module path + dependency hashes; native single static binary), *Distribution channel* (`Go module via go get / go install`, plus transitive presence in `Multi-channel publication` for Go-runtime products), *Entry point and launch* (`Native binary`), and *Test stack* (`Go stdlib testing`).

### `Sample > Cross-role tools > Smithery`

Current: "Surfaces as *Distribution channel* (Smithery registry, aggregator/installer registry) and *Host integration* (Smithery / Glama discovery via `glama.json`, `smithery.yaml`, CLI installer chooses host)."

Misses / overclaims:

- "Aggregator/installer registry" path (line 1041) is a generalized path — Smithery is *one* example, alongside `mcp-get`, the Docker MCP catalog, and Glama. Listing Smithery as the residing tool in that path is a slight overclaim; Smithery is an exemplar, not the path's identity.

Sharpened text suggestion:

> Surfaces as *Distribution channel* (`Smithery registry` directly; also exemplifies the broader `Aggregator/installer registry` path) and *Host integration* (`Smithery / Glama discovery` — install via `@smithery/cli install <name> --client <host>` or `glama.json` registration).

### `Sample > Cross-role tools > .claude-plugin/`

Current: "Surfaces as *Distribution channel* (`.claude-plugin/marketplace.json` for marketplace discovery), *Host integration* (`.claude-plugin/` directory in repo for one-click Claude install), and *Claude Code plugin / skill wrapper* (full plugin manifest with dedicated CLI commands)."

Misses:

- *Claude Code plugin / skill wrapper* role's actual paths are `\`.claude-plugin/\` wrapper` (line 2841) and `\`.claude-plugin/marketplace.json\` only` (line 2845) — the role hosts both a plugin wrapper and a discovery-only variant. Cross-role listing should distinguish.

Sharpened text suggestion:

> Surfaces as *Distribution channel* (`.claude-plugin/marketplace.json` for marketplace discovery), *Host integration* (`.claude-plugin/ directory in repo` for one-click Claude install), and *Claude Code plugin / skill wrapper* (both `.claude-plugin/ wrapper` — full plugin.json with CLI commands — and `.claude-plugin/marketplace.json only` — discovery hook without full plugin install).

### `Sample > Cross-role tools > MCP Inspector`

Current: "Surfaces as *Test stack* (manual verification driver), *Host integration* (compatibility called out as a verification surface), and *Developer ergonomics* (Inspector/debug tooling references)."

Accurate. The three real paths are `MCP Inspector as test driver` (line 1620), `Inspector compatibility called out` (line 2023), and `Inspector/debug tooling references` (line 2714). Description matches; only nominal sharpening helpful.

Sharpened text suggestion:

> Surfaces as *Test stack* (`MCP Inspector as test driver`), *Host integration* (`Inspector compatibility called out`), and *Developer ergonomics* (`Inspector/debug tooling references`).

### `Sample > Cross-role tools > Pydantic`

Current: "Surfaces as *Server runtime* (transitive runtime dependency for FastMCP), *Schema and types* (Pydantic v2 models with raw or FastMCP SDK), and *Configuration delivery* (pydantic-settings for env var validation)."

Accurate. *Server runtime* claim is supported by the FastMCP path's prose (line 41: "FastMCP auto-derives JSON Schema from typed function signatures via Pydantic 2"). *Schema and types > Pydantic v2 models* (line 1399). *Configuration delivery > Environment variables* (line 477) names "Pydantic validation so misconfiguration fails loudly at startup". All three claims are evidence-supported.

No sharpening needed beyond optional nominal alignment to path names.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

None applicable — this is a meta-section without sample evidence; sub-axes are properties of underlying paths inspected by other depth-pass agents.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

None — no per-sample placements at this level.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Tools that span multiple roles in the corpus but are missing from this section

Three additional tools have a corpus footprint that meets the "surfaces in N functional roles" bar of the listed entries but are absent from `Cross-role tools`:

**FastMCP.** Corpus footprint:

- *Server runtime*: three direct paths (`Python with FastMCP`, `Python with FastMCP (pre-2.x era)`, `Python with both MCP SDK and FastMCP declared`), 30 of 104 samples (29%).
- *Schema and types*: `FastMCP auto-derivation from type hints` (26 samples, 45% of role).
- *Configuration delivery*: `Framework-specific config file` (line 513 names `fastmcp.json`).
- *Entry point and launch*: `Click-based CLI wrapper` (line 1172 dispatches to FastMCP runner internally); `Framework CLI run` (line 1212: `fastmcp run` / `fastmcp install`).
- *Distribution channel*: `Framework-specific install` (line 1073 names `fastmcp install`).
- *Build and packaging*: pin-discipline taxonomy at line 1307 explicitly indexes on FastMCP version pins.

This is a five-or-six-role span — at or above Pydantic's three-role footprint and Cargo's six. Worth adding as `### FastMCP` in Cross-role tools.

**GitHub Actions.** Corpus footprint:

- *CI*: `GitHub Actions` (76 samples / 84% — the dominant CI choice) and `GitHub Actions plus dedicated lint config` (1 sample).
- *Release and lifecycle*: `GitHub Actions release workflow` (line 2877 — release.yml on tag push).
- *Build and packaging*: line 1782 names Turborepo running inside GitHub Actions for monorepo builds.
- *Distribution channel*: implicit — release pipelines fan out to npm/Docker/PyPI/Cargo from GitHub Actions (line 2879).
- *Documentation surface*: line 1798 names GitHub Actions YAML examples in README as a copy-paste seed.

Multi-role span at very high adoption (84% in CI alone). Worth adding.

**Cloudflare Workers / Wrangler.** Corpus footprint:

- *Server runtime*: `TypeScript on Cloudflare Workers (V8 isolate)` (2 samples).
- *Configuration delivery*: `Wrangler config (Cloudflare Workers)` (line 515).
- *Build and packaging*: `Wrangler bundle (Cloudflare Workers)` (line 1356).
- *Container artifacts*: `Cloudflare Workers config` (line 1525 — `wrangler.jsonc`).
- *Deployment topology*: `Edge / serverless deployment (Cloudflare Workers, V8 isolate)` (line 1845).
- *Distribution channel*: implicit — hosted endpoint URL is the artifact (line 1057 mentions "Cloudflare account's resources" as the platform).

Five-role span. Worth adding even though sample count is low (2 samples), because the listed `Cargo / Cargo.toml` and `Go modules / go.mod` entries are at similar low absolute counts but high cross-role span. The criterion driving this section is span, not count.

### Possible additional candidates (less confident)

**npm / Node toolchain.** Spans Distribution channel (`npm via npx / bunx`, `npm package wrapping native binary`), Build and packaging (`npm/Node toolchain`), Entry point and launch (`Console script via [project.scripts] / npm bin`, `npx -y <package> / bunx`, `Built JS file`, `npm scripts`), Test stack (Vitest/Jest invoked via `npm test`/`npm run`). Five-role span; likely belongs alongside uv as a cross-ecosystem peer. Excluded from confident list because much of npm's role is "the implicit packaging substrate of every Node sample" rather than a deliberate cross-role tool — listing it might overclaim.

**Pyproject.toml.** Universal substrate file for Python servers; surfaces in Build and packaging, Distribution channel, Entry point, Schema (via Pydantic registration), and Release. Excluded because it's a *file format*, not a *tool*; the existing Cross-role tools entries are tools/products, not file types. (Same reasoning argues against listing "package.json" or "Cargo.toml" standalone — though Cargo / Cargo.toml is currently listed and could be argued either way.)

### Structural observation about the section's category

The section currently mixes three category types: (1) products/tools (`uv`, `Smithery`, `MCP Inspector`, `Pydantic`), (2) language toolchains / package-manager + manifest pairs (`Cargo / Cargo.toml`, `Go modules / go.mod`), and (3) bundle/manifest formats (`MCPB / Desktop Extension bundle`, `.claude-plugin/`). The naming convention is inconsistent (sometimes "tool", sometimes "tool / file"). If FastMCP, GitHub Actions, Cloudflare Workers / Wrangler, and possibly npm are added, the categorical heterogeneity grows. Worth flagging to reconciler whether this section is "ecosystem brands the corpus deals with" (broad) or "specific tools whose binaries/files appear across roles" (narrower); the answer determines what else belongs.

### Adoption-table semantics

The adoption table at line 2949 reports "0 samples / 0% coverage" for every Cross-role tool. That's accurate per the chain-key model but misleading on first read — a future reader may assume these tools are unused. The role-level prose ("Tools that surface under multiple functional roles in this merge — named in each role's section above where they appear, not duplicated as a top-level branch") explains it, but the table itself reads as evidence of absence rather than meta-listing. Consider either suppressing the adoption table for this role or replacing the count column with the count of *role appearances* (Docker = 5 roles, uv = 4 roles, etc.) so the numbers carry meaning.
