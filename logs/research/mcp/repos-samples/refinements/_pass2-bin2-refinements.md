# Pass 2 Refinements — Bin 2

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Configuration delivery > CORS origin configuration` — supporting sample: ahmedmustahid--postgres-mcp-server (`CORS_ORIGIN` env var as a first-class config knob in HTTP-mode servers). Existing `Environment variables` covers it loosely; a CORS-specific path may be warranted if cross-bin evidence shows other HTTP servers expose the same axis. Description draft: HTTP-mode servers expose CORS origin allowlist as a first-class config dimension distinct from the upstream-credential surface; required when browser-style clients reach the MCP endpoint. The Streamable HTTP path in `Transport` already mentions CORS in passing — possibly resolve there instead.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Distribution channel > Smithery registry` — existing description focuses on Smithery as an additive channel atop npm/PyPI; JackKuo666--PubMed-MCP-Server demonstrates the "Smithery instead of PyPI" case (no PyPI publication, distributed entirely via Smithery + git clone + Docker). Sharpening: Smithery can be a primary distribution channel for servers that opt out of PyPI/npm publication entirely, not only an additive layer over an existing language registry.
- `Build and packaging > Requirements-driven (legacy Python)` — existing wording captures "both coexist redundantly" but JackKuo666--PubMed-MCP-Server makes the diagnostic explicit: bare-script repo at root with `pyproject.toml` + `requirements.txt` redundancy strongly suggests a requirements-driven template was the bootstrap origin. Sharpening: The redundant pair is a tell that the project predated `pyproject.toml` adoption and the manifest was added later without removing the original. The `requirements.txt` is typically the install contract that's actually exercised.
- `Authentication > OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)` — awslabs--aws-api-mcp-server documents the configurable issuer/JWKS endpoints as separate env vars but the README does not specify whether OAuth validation is real JWT verification or a stub. Sharpening: Note that the issuer + JWKS endpoint configurability is the typical API surface; whether downstream JWT validation is implemented or stubbed is not always clear from READMEs and may differ across implementations.
- `Multi-tenancy > Stateless read-only (any number of instances)` — awslabs--aws-documentation-mcp-server demonstrates the canonical "no-auth, public-upstream-fronting" instance of this path. Sharpening: This pattern often co-occurs with `Authentication > None / implicit` and a public unauthenticated upstream (docs, search, public APIs) — together they form a coherent "credential-free read-only" server family.
- `Capability surface > Partition-scoped tool gating` — awslabs--aws-documentation-mcp-server confirms the AWS global vs China partition pattern; the existing description already names this case. Sharpening: Could note that the partition-switching mechanism (which env var or flag triggers it) is often not explicit in README and may need source-level inspection to confirm.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin — all factual content fit into existing roles or repo-metadata-preamble)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Repository metadata not represented in the role tree.** Samples carry `stars`, `last-commit`, `default branch`, `commits count`, `vendor-vs-community authorship` — none of these correspond to a functional role in the consolidated. Per methodology guidance ("the consolidated tree is organized by ROLE, not by tool / metadata"), this is correct: stars/last-commit are *about the repo* not *what the project DOES*. Following the bin-1 convention, I placed all of this in the level-1 preamble (e.g., "207 stars, MIT, default branch `master`, last release v1.4.2 on 2026-02-27, vendor-authored (Alpaca)"). Question for the reconciler: is the preamble the canonical home for repo metadata, or should a `Repository identification` role exist for those facts? Bin-1 normalization put them in the preamble; I matched that convention.
- **Vendor-vs-community authorship signal.** Samples surface "vendor-authored" as a maintenance/trust signal (PagerDuty, Alpaca, Apollo, awslabs). The `Release and lifecycle > Active development` path sometimes captures it, but the signal is more about who authors than about lifecycle. Currently spread across the preamble identification line and `Release and lifecycle > Active development`. Reconciler may want to consolidate this into a dedicated path under `Release and lifecycle` (e.g., `Vendor-authored vs community-authored maintenance signal`) or leave it as preamble metadata.
- **Dual logging paths in one server.** awslabs--aws-api-mcp-server declares both `loguru` and `python-json-logger` — the consolidated mentions this in the loguru description ("dual logging paths in one server, presumably one for human-readable dev output and one for ingest") but treats them as one path. I rendered them as two sibling `### loguru (Python)` and `### Standard library logging (Python)` paths to honor the "one path per choice" rule, since the sample takes both. Reconciler may want a dedicated `### loguru + python-json-logger dual-pipeline` path if other samples in the corpus exhibit the same combo, or leave them as siblings.
- **OAuth alongside `None` auth in the same server.** awslabs--aws-api-mcp-server takes `Cloud-native identity / credential chain` for stdio mode and `OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)` for streamable-HTTP mode. README also notes a no-auth mode under streamable-HTTP. I represented the cloud-credential-chain and OAuth paths as siblings under `Authentication`; the no-auth-HTTP mode is implicit in the OAuth path's "optional" framing. Question: should "optional OAuth (no-auth fallback)" be a separate path under Authentication, or is the existing "OAuth 2.x with issuer + JWKS" wording already sufficient since it implies the optional/no-auth fallback?
- **Hybrid SDK declaration manifests as both runtime and schema-and-types choices.** awslabs--aws-api-mcp-server declares both `mcp` and `fastmcp`. I placed it under `Server runtime > Python with both MCP SDK and FastMCP declared` (which correctly captures the hybrid). The implications cascade into schema strategy (FastMCP auto-derivation + Pydantic v2 hand-registration coexist) — I represented both schema paths as siblings. Reconciler may want to verify that "both SDKs declared" automatically implies "both schema strategies in play" and consider whether the consolidated should make the cascade explicit.
