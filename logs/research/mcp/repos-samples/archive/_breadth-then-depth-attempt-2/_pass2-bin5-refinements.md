# Pass 2 Refinements — Bin 5

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Distribution channel > Vendor container registry (non-Docker-Hub)` — `elastic--mcp-server-elasticsearch.md` (`docker.elastic.co/mcp/elasticsearch` distributed via AWS Marketplace and Elastic's own container registry) — Distinct from generic `Docker / OCI image` (which covers any registry including ghcr.io and Docker Hub) and `Docker Hub MCP Registry` (the MCP-specific Docker Hub scope). The vendor's own registry as primary distribution carries a brand/operational signal — the publisher operates the registry and is the one responsible for image freshness, access control, and SLAs. Often paired with marketplace publication (AWS Marketplace) for enterprise distribution. Currently absorbed into `Docker / OCI image` but the vendor-registry-as-primary stance is structurally distinct from "publish to Docker Hub like everyone else." Cross-reference with `Container artifacts > Vendor-namespaced image` which captures the in-repo metadata side of this same axis.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Authentication > OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)` — `duolingo--slack-mcp.md` adds a concrete forcing-function pairing: HTTP-only transport with port 8001, no stdio fallback, and ngrok required for local dev OAuth callback. The existing description names "forces HTTP transport" but the duolingo sample illustrates the operational consequence — local development needs a tunneling tool, which raises the dev-loop friction enough that some authors document it explicitly. Sharpening: surface the dev-environment-tunneling friction as a paired cost of this auth path, distinct from the production deployment cost.

- `Capability surface > Capability gating flags (per-tool, per-category, write-mode)` — `feiskyer--mcp-kubernetes-server.md` exhibits a very specific four-way verb-disable shape (`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`) where the gates are orthogonal denial axes per upstream tool family AND per verb class. Existing description captures `--disable-kubectl --disable-helm --disable-write --disable-delete` as examples but doesn't surface the `<tool-family> × <verb-class>` matrix as a structurally interesting subpattern. Sharpening: name the matrix-style gating (per-tool-family × per-verb-class) as a distinct shape from a flat `--disable-X` list; it's a denial-axis-multiplication design pattern.

- `Documentation surface > `llms.txt` / `llms-full.txt`` — `exa-labs--exa-mcp-server.md` ships `llm_mcp_docs.txt` (411.7 KB) — large, single-file LLM-ingestion doc that doesn't follow the `llms.txt`/`llms-full.txt` two-file naming convention but serves the same purpose. Existing description names the two-file pattern as "emerging convention." Sharpening: acknowledge that some projects ship a single large LLM-ingestion doc under a different filename (e.g., `llm_mcp_docs.txt`), which fits the same role even though it doesn't follow the emerging two-file convention.

- `Distribution channel > Multi-channel publication` — `executeautomation--mcp-playwright.md` exhibits four parallel mechanisms (npm, mcp-get, Smithery, Docker) with the README explicitly serving as a reference for "how many channels to publish to" decisions. Existing description names the pattern but the executeautomation sample illustrates the upper-bound: when a server is broadly-distributed enough that maintainers of other servers cite it as a reference, multi-channel becomes a positioning move beyond just maximizing reach. Sharpening: distinguish "multi-channel for reach" from "multi-channel as positioning/canonical-status signal."

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every sample mapped onto existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **executeautomation/mcp-playwright README mentions "Microsoft's own `@playwright/mcp` exists as a competitor — both ship, neither is officially crowned."** This is a corpus-level observation about parallel implementations rather than a fact about this sample. The current sample structure has nowhere clean to put "this competes with another implementation in the same niche." I dropped it from the rewrite because it doesn't fit a role and is more about the ecosystem than about this server. Reconciler may want a "Coexisting implementations" note in the consolidated overview, or this can stay as a Pass-1-era observation.

- **exa-labs/exa-mcp-server's "skills" directory is ambiguous between two consolidated paths.** I placed it under both `Capability surface > Bundled "agent SOPs" / vertical skill packs` (matches the consolidated description: "company research, code search, people research, financial reports, academic papers... markdown/prompt artifacts shaped for specific use cases") and `Documentation surface > `agents/` example directory`. The first is a strong fit; the second is a loose fit. Reconciler may want to reduce the duplication or clarify the boundary between "bundled agent SOPs" (capability-surface concern) and `agents/` example directory (documentation-surface concern).

- **elastic/mcp-server-elasticsearch carries `elastic-mcp.json5` config file.** This is a JSON5 sidecar config the server appears to consume; existing path `Configuration delivery > Sidecar config files (JSON / YAML / TOML / EDN)` covers JSON/YAML/TOML/EDN but not JSON5 specifically. JSON5 is JSON's nearest cousin (allows comments and trailing commas) and likely was meant to be covered. Currently absorbed under that path without a refinement; flagging in case JSON5 deserves explicit mention.

- **duolingo/slack-mcp's `[project.scripts]: slack-mcp = "main:main"` is declared but Dockerfile uses `uv run python main.py`.** This is a structural anomaly — the console script entry exists but isn't the primary run path. Currently captured under `Entry point and launch > Console script via [project.scripts] / npm bin` with a note about the divergence. Reconciler may want a "declared-but-unused entry-point" pattern note, since this signals the package was set up with packaging conventions in mind but the deployment shape is Dockerfile-first.

- **feiskyer/mcp-kubernetes-server uses BOTH `Delegated to upstream toolchain credentials` AND `Mounted file credentials`** — kubectl reads `~/.kube/config`, but the server itself doesn't authenticate; it shells out. The two paths describe the same fact at different abstraction levels (delegation pattern + credential-delivery mechanism). Currently listed both. Reconciler may want a convention for samples where one fact maps to two roles legitimately — the consolidated descriptions of these two paths overlap (the file-mounted-credentials path even cites kubectl-class servers as a canonical example), suggesting they should perhaps be one path with two facets rather than two paths.

- **echelon-ai-labs/servicenow-mcp's "Starlette as the SSE web framework — many other servers use FastAPI + uvicorn."** This is a corpus-level structural observation about Starlette's role in the Python ecosystem for HTTP-mode MCP servers. Doesn't fit cleanly under any role — it's a sub-axis observation about runtime composition. Currently absorbed into the runtime description; may warrant a sub-axis note under `Server runtime > Python with raw MCP SDK` about the HTTP-stack choice (Starlette standalone vs FastAPI + uvicorn vs other).

- **designcomputer/mysql_mcp_server resources-as-tables pattern.** README-noted observation: "one of the few DB MCP servers to use the resource surface — most DB MCP servers expose everything through tools." Captured under `Capability surface > Tools plus resources` with the note. The corpus-rarity claim is a Pass-2 observation, not a per-sample fact; flagging in case reconciler wants to surface it as a description sharpening on the existing path (e.g., "Particularly rare among DB MCP servers, where the tools-only pattern dominates").
