# Pass 3 Refinements — Bin 5

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 5 samples (`designcomputer--mysql_mcp_server.md`, `docker--hub-mcp.md`, `duolingo--slack-mcp.md`, `echelon-ai-labs--servicenow-mcp.md`, `elastic--mcp-server-elasticsearch.md`, `exa-labs--exa-mcp-server.md`, `executeautomation--mcp-playwright.md`, `feiskyer--mcp-kubernetes-server.md`). Samples were already in role-tree format from Pass 2; this pass verified alignment, applied targeted updates, and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Convergence summary

All eight samples already mirror the consolidated's role tree exactly — every level-2 heading is a canonical role and every level-3 heading is a canonical path. The structural-check tool reports zero sibling-duplicate headings on every sample. Comparing each sample's `(role, path)` set against the canonical 525-entry path inventory yields zero mismatches. Most Pass-2 sharpenings (OAuth-2.1 dev-tunneling friction, capability-gating-matrix shape, llms-single-file variant, multi-channel-as-positioning) show up integrated in the current consolidated path descriptions. This bin is converged on structure; the second normalize cycle yielded only one fidelity fix and a small set of cross-entity-claim cleanups in sample prose.

## Pass-3 sample edits applied

> Targeted updates made during this pass — each addresses a fidelity or methodology issue without introducing new structural moves.

- `elastic--mcp-server-elasticsearch.md` — added `Configuration delivery > Sidecar config files (JSON / YAML / TOML / EDN)` with `elastic-mcp.json5` evidence. Pass 2's notes said this was "absorbed under that path without a refinement," but in fact the heading was missing from the sample; the JSON5 sidecar appeared only under Repository layout. Added so the configuration-delivery role reflects the sample's actual sidecar config artifact.
- Cross-entity-claim cleanup — Pass 2 left several cross-corpus comparisons in sample prose that violate the methodology's "each sample stands alone" rule. Pass 3 rewrote each to entity-internal language without dropping the underlying observation:
    - `designcomputer--mysql_mcp_server.md` — removed "higher than the corpus 3.10 mode," "most newer projects in the corpus consolidate into pyproject.toml," and "one of the few DB MCP servers to use the resource surface — most DB MCP servers expose everything through tools."
    - `docker--hub-mcp.md` — removed "(contrast with github-mcp-server's subcommand approach)" from Selection mechanism prose.
    - `duolingo--slack-mcp.md` — removed "atypical for Python servers; inverts the typical PyPI packaging path" and "unusual; most servers use a nested package module path."
    - `echelon-ai-labs--servicenow-mcp.md` — removed "(an explicit choice — many other servers use FastAPI + uvicorn)," "more conservative than the uv/uvx-heavy trend among newer servers," and "a touch more modern than awslabs' 3.10."
    - `elastic--mcp-server-elasticsearch.md` — removed "a deprecation-status posture most repos don't surface" from the deprecation entry.
    - `executeautomation--mcp-playwright.md` — rewrote preamble's "one of the most broadly-distributed MCP servers," removed "(Coexists with Microsoft's `@playwright/mcp` as a parallel non-vendor implementation.)," and rewrote "one of the more broadly-distributed MCP servers" to entity-internal channel enumeration.
    - `feiskyer--mcp-kubernetes-server.md` — removed "(rarer for independent-maintainer MCP servers, which skew MIT)" from the license entry.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Distribution channel > Vendor container registry (non-Docker-Hub)` — `elastic--mcp-server-elasticsearch.md` (`docker.elastic.co/mcp/elasticsearch` distributed via AWS Marketplace and Elastic's own container registry) — Pass 2 proposed; carried forward unresolved. Distinct from generic `Docker / OCI image` (any registry, including ghcr.io and Docker Hub) and `Docker Hub MCP Registry` (the MCP-specific Docker Hub scope). The vendor's own registry as primary distribution carries a brand/operational signal — the publisher operates the registry and is the one responsible for image freshness, access control, and SLAs. Often paired with marketplace publication (AWS Marketplace) for enterprise distribution. Currently absorbed into `Docker / OCI image` but the vendor-registry-as-primary stance is structurally distinct from "publish to Docker Hub like everyone else." Cross-reference with `Container artifacts > Vendor-namespaced image` which captures the in-repo-metadata side of this same axis.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Configuration delivery > Sidecar config files (JSON / YAML / TOML / EDN)` — Pass 2 flagged that JSON5 isn't enumerated in the path's name or description. `elastic--mcp-server-elasticsearch.md` ships `elastic-mcp.json5` (JSON5 allows comments and trailing commas, JSON's nearest cousin). Sharpening: add JSON5 as an enumerated variant in the description (or rename the path to "Sidecar config files (JSON / JSON5 / YAML / TOML / EDN)"). The path-name itself enumerates four formats; JSON5 fits naturally without a structural split. Supporting sample: `elastic--mcp-server-elasticsearch`.
- `Capability surface > Tools plus resources` — Pass 2 surfaced the "particularly rare among DB MCP servers" observation as a corpus-level finding for the consolidated; not yet integrated. `designcomputer--mysql_mcp_server.md` exposes MySQL tables as MCP resources alongside SQL execution as tools; the resource path is reportedly under-used for DB-class servers, where the tools-only pattern dominates. Sharpening: note in the consolidated description that DB-class MCP servers commonly skip the resource surface (everything-as-tools) and that tables-as-resources is a deliberate mid-frequency choice rather than the default for that domain. Supporting sample: `designcomputer--mysql_mcp_server`.
- `Server runtime > Python with raw MCP SDK` — `echelon-ai-labs--servicenow-mcp.md` uses Starlette as the SSE web framework rather than the FastAPI + uvicorn pairing more commonly seen with the raw MCP SDK in HTTP/SSE mode. The HTTP-stack choice within a given runtime is a sub-axis (Starlette standalone vs FastAPI + uvicorn vs other) that the path description doesn't currently surface. Sharpening: note that the raw MCP SDK leaves the HTTP-stack choice to the implementer, with Starlette and FastAPI + uvicorn as observed alternatives — a sub-axis that affects deployability and middleware composition. Supporting sample: `echelon-ai-labs--servicenow-mcp`.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — bin 5 samples all map to existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Pass 2 concerns carried forward unresolved.** The Pass 2 refinement file noted six structural observations the reconciler has not yet integrated:
    1. `Distribution channel > Vendor container registry (non-Docker-Hub)` proposal (re-proposed above; remains unintegrated).
    2. JSON5 not explicitly named in `Sidecar config files` path/description (re-proposed above; remains unintegrated).
    3. exa-labs `skills/` directory is dual-classified under both `Capability surface > Bundled "agent SOPs" / vertical skill packs` and `Documentation surface > \`agents/\` example directory`. The first is a strong fit (capability-surface concern); the second is loose (documentation-surface concern). The reconciler may want to clarify the boundary or pick one. Pass 3 left both in place because the surface they describe is genuinely cross-cutting.
    4. duolingo `[project.scripts]: slack-mcp = "main:main"` is declared but Dockerfile uses `uv run python main.py` rather than the console script. The console-script entry exists but isn't the primary run path — a "declared-but-unused entry-point" pattern that signals packaging conventions met but Docker-first deployment. Currently captured under `Console script via [project.scripts] / npm bin` with prose noting the divergence. Pass 3 confirms; reconciler may want a description sharpening on that path naming the "declared-but-not-primary-run-path" variant.
    5. feiskyer dual-auth (`Delegated to upstream toolchain credentials` AND `Mounted file credentials`) — kubectl reads `~/.kube/config`, but the server itself doesn't authenticate; it shells out. The two paths describe the same fact at different abstraction levels (delegation pattern + credential-delivery mechanism). Pass 3 retained both because they each capture a distinct observation, but the path descriptions overlap enough that the reconciler may want to merge into one path with two facets.
    6. echelon Starlette-vs-FastAPI sub-axis on `Python with raw MCP SDK` — re-proposed above as a description sharpening.

- **`Capability surface > Tools plus resources` corpus rarity is now sample-internal-clean.** Pass 3 removed the cross-entity claim from `designcomputer--mysql_mcp_server.md` ("Notable as one of the few DB MCP servers to use the resource surface — most DB MCP servers expose everything through tools"). The factual observation is preserved as a proposed description sharpening on the consolidated path (above), which is the appropriate home for a corpus-level claim.

- **Bin 5 entity diversity supports breadth signal.** This bin spans Python (4 samples: designcomputer, duolingo, echelon, feiskyer), TypeScript (3: docker, exa, executeautomation), and Rust (1: elastic). Among Python samples, all four take different `Server runtime` paths or differ in their distribution patterns: raw MCP SDK + hatchling (designcomputer), Anthropic Claude Agent SDK + setuptools + Docker-first (duolingo), raw MCP SDK + pip-only (echelon), raw MCP SDK + uvx-first (feiskyer). The TypeScript samples each take different distribution shapes too: data-file tool catalog (docker), hosted SaaS endpoint primary (exa), four-channel publication (executeautomation). The breadth holds up under a second read.

## Convergence assessment

The bin is **converged**. All sample level-2 and level-3 headings exactly match consolidated role/path names after Pass 3 cleanup. One genuine fidelity gap was fixed (elastic JSON5 sidecar config now appears under `Configuration delivery`). Six cross-entity-claim violations were rewritten to entity-internal language without losing factual content. Two Pass-2 proposals (vendor container registry path, JSON5 sharpening) and one new sharpening (HTTP-stack sub-axis on Python raw-MCP-SDK runtime) carry forward to the reconciler. Pass 4 should not be required if the reconciler integrates the proposed sharpenings; the structural alignment is solid.
