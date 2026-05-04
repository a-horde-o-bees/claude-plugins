# Pass 2 Refinements — Bin 6

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — every fact in this bin mapped to an existing role/path)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Capability surface > Read/write tool split` — `geropl--linear-mcp-go` shows the per-tool URL-input ergonomic alongside the read/write split (e.g., `linear_add_comment` accepts Linear comment URLs directly without manual ID extraction). Sharpening: read/write splits often pair with input ergonomics that reduce the LLM's identifier-extraction burden — accepting URLs/canonical references in addition to opaque IDs is a common co-occurring choice that makes the gating worthwhile (read tools get fewer "bad ID" errors; write tools get cleaner audit trails).

- `Developer ergonomics > Setup subcommands on the MCP binary` — `geropl--linear-mcp-go` shows `setup --tool=cline` as a scoped extension point: only `cline` is supported today but the flag's existence signals a plan to automate other host configs. Sharpening: setup subcommands frequently start with one host and use `--tool` (or equivalent) as the extension point for additional hosts — the flag's presence is itself a signal of intended scope expansion.

- `Capability surface > Tools plus internal "skills" abstraction` — `getsentry--sentry-mcp` documents `MCP_DISABLE_SKILLS` (comma-separated env var) as a per-deployment toggle for skill subsets, and skills live under `.agents/skills/`. Sharpening: skills as a first-class abstraction often pair with a deployment-level toggle (env var with comma-separated subset list) — the toggle gives operators a way to trim the behavioral surface without code changes, distinct from per-tool gating which targets the tools list rather than the higher-level skill grouping.

- `Domain logic and embedded intelligence > In-server LLM client` — `getsentry--sentry-mcp` exposes a provider-selection env var (`EMBEDDED_AGENT_PROVIDER` set to `openai` or `anthropic`) plus provider-specific keys, letting the operator choose which LLM the server invokes. Sharpening: in-server LLM clients sometimes expose the provider as a deployment knob (provider env var + keyed credentials per provider) so the same server can be deployed against different LLM vendors without code changes.

- `Distribution channel > Multi-channel publication` — `googleapis--mcp-toolbox` is the corpus-extreme case: 5 distinct channels (binary releases, Docker, `go install`, Homebrew, npm shim wrapping native binary). Sharpening: multi-channel publication can scale to 5+ channels when the project deliberately pursues cross-ecosystem discoverability (Homebrew + Go-native + Docker + binary release + npm shim). The npm-shim-wrapping-native-binary is itself a glue pattern that brings node-oriented hosts onto a non-node binary.

- `Configuration delivery > Runtime reconfiguration tool` — `googleapis--mcp-toolbox` runs dynamic reload on by default; the opt-out is a flag (`--disable-reload`). Sharpening: runtime reconfiguration is typically opt-in but can be a default; when it is, the opt-out is the documented surface, and the implication is that state survives across configuration changes — a different lifecycle assumption from the typical re-exec pattern.

- `Server runtime > Python with FastMCP (pre-2.x era)` — `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` is a clean reference case for the pre-2.x era (`fastmcp==0.4.1` pinned in `requirements.txt`, no `pyproject.toml`, single-script repo, `fastmcp install` for distribution). Sharpening: the pre-2.x FastMCP era often co-occurs with `Build and packaging > Requirements-driven (legacy Python)` and `Repository layout > Single-file script / monolith` — a coherent "early FastMCP" cluster predating the package-restructuring conventions.

- `Capability surface > Tools-only, hand-curated narrow surface` — `idosal--git-mcp` parameterizes tool names by a URL parameter (`fetch_<repo-name>_documentation`, where `<repo-name>` comes from the URL path). Sharpening: hand-curated tool surfaces can use URL-template parameterization to keep the tool list small while serving many tenants — the same tool name pattern serves any repo by virtue of the URL routing.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Repo metadata in preamble vs roles.** Following the bin-1 / bin-2 convention, I placed `stars`, `last-commit`, `license-name`, `default branch`, `commits count`, and vendor-vs-community signal in the level-1 preamble rather than under any role. This matched bin-1 convention but means license/lifecycle details live in two places: preamble (license name, last commit) and `Release and lifecycle` paths (license-permissive, active development, tagged release). Reconciler may want to clarify whether the preamble is canonical for "raw fact metadata" and the Release-and-lifecycle role is reserved for "qualitative posture".

- **`Capability surface > Read/write tool split` vs `Safety and security posture > Read-only by default with explicit write flag`.** `geropl--linear-mcp-go` exhibits both the capability-side split (read tools vs write tools as distinct toolsets) and the safety-side gate (`--write-access` flag is required to enable the write group). I placed both — capability under capability, safety under safety. Reconciler should verify the cross-role pair is intentional (capability surface = what tools exist; safety posture = how access is gated). The two are correlated but conceptually distinct.

- **`getsentry--sentry-mcp` skills abstraction.** Skills live under `.agents/skills/` — clearly distinct from `.claude/skills/` directory in repo (a Claude Code wrapper convention) and from the consolidated's `Tools plus internal "skills" abstraction` (a server-internal capability). I placed skills under `Capability surface > Tools plus internal "skills" abstraction` since it's the server's own behavioral primitive, not a Claude Code wrapper. Reconciler should confirm `.agents/skills/` is treated as the in-server skills abstraction rather than as a Claude Code wrapper variant.

- **`getsentry--sentry-mcp` `.claude-plugin/` placement.** I placed it under `Host integration > .claude-plugin/ directory in repo` (the in-repo wrapper marker) AND under `Distribution channel > .claude-plugin/marketplace.json` (the marketplace-discovery surface). Both apply because the README documents both the in-repo wrapper and a marketplace plugin install path. Reconciler may want to confirm a single sample can legitimately take both paths.

- **`googleapis--mcp-toolbox` HTTP-only transport.** I placed it under `Transport > Streamable HTTP` with `Selection mechanism > Implicit default`. The README does not surface a stdio transport at all (HTTP-first, port 5000). Whether stdio is unsupported, undocumented, or available-but-unused is unclear — the gap is preserved as "stdio not surfaced" rather than escalated to a refinement, since it could be evidence-only and not a methodology gap.

- **`hannesrudolph--sqlite-explorer-fastmcp-mcp-server` license.** README and landing page do not surface a license name within budget. I omitted the License path under `Release and lifecycle` rather than guessing — the absence is documented in the preamble ("License not surfaced"). Reconciler may want a convention for samples with truly-missing facts: omit the path, or include a placeholder?

- **`hugoduncan--mcp-clj` Polylith layout.** `Repository layout > Polylith components (Clojure)` exists in the consolidated and matches well — but the sample also has a separate `.mcp-vector-search/` directory implying embedded RAG/retrieval. I placed that under `Capability surface > Embedded RAG / retrieval pipeline`, but the implementation is opaque (the sample notes "vector search integration" without detail). The Capability path may technically over-claim — there's a directory present, but no documented user-facing capability. Reconciler may want to flag the sample's evidence as inadequate (directory presence ≠ confirmed capability) and either drop the path or sharpen to reflect speculation.

- **`idosal--git-mcp` per-tool URL parameterization.** Tools like `fetch_<repo-name>_documentation` are parameterized by URL — the same tool name is generated dynamically per tenant. This blurs `Capability surface > Tools-only, hand-curated narrow surface` (which implies a fixed tool list) and `Capability surface > Spec-driven dynamic tool generation` (which implies generation from a spec). I placed it under `Tools-only, hand-curated narrow surface` because the tool count and shape are fixed (4 tools), only the names parameterize. Reconciler may want to flag this as a sub-axis under the hand-curated path or note it inline.

- **`idosal--git-mcp` cloud-native deployment model.** I placed it under `Container artifacts > Cloudflare Workers config` even though there's literally no container — Workers are V8 isolates. The consolidated uses `Cloudflare Workers config` as the artifact-equivalent for Workers deployments, treating Wrangler config as the analog of Dockerfile. Reconciler should verify this convention; alternative would be a "no container artifact" placement, but that loses the deployment-artifact information.

- **`isaaccorley--planetary-computer-mcp` co-located VS Code extension.** I placed under `Host integration > Co-located VS Code extension` — but this is also a kind of repository-layout signal (mixed-language monorepo). I placed both: `Host integration > Co-located VS Code extension` (what role does the parallel artifact serve) and `Repository layout > Cross-language monorepo / mixed-language layout` (how is the repo structured). Reconciler should confirm dual placement is intended.

- **`isaaccorley--planetary-computer-mcp` async + visualization synthesis.** The sample notes "STAC clients tend to be async — likely async tool signatures" and "Generates visualizations for LLM analysis". I placed async under `Schema and types > Pydantic v2 models` (with a sentence noting "likely async tool signatures") and visualization synthesis under `Domain logic and embedded intelligence > Visualization synthesis`. Note the consolidated has a separate `Schema and types > Async model (cross-cutting)` path that may also apply — reconciler may want to add it as a parallel `###` if the cross-cutting axis is the better fit.
