# Pass 3 Refinements — Bin 2

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle over Bin 2 samples (`JackKuo666--PubMed-MCP-Server.md`, `PagerDuty--pagerduty-mcp-server.md`, `ahmedmustahid--postgres-mcp-server.md`, `alexei-led--k8s-mcp-server.md`, `alpacahq--alpaca-mcp-server.md`, `apollographql--apollo-mcp-server.md`, `awslabs--aws-api-mcp-server.md`, `awslabs--aws-documentation-mcp-server.md`). The reconciler integrates accepted refinements into the next consolidated revision.

## Convergence summary

All eight samples already mirror the consolidated's role tree exactly — every level-2 heading is a canonical role and every level-3 heading is a canonical path. The structural-check tool reports zero sibling-duplicate headings on every sample. Comparing each sample's `(role, path)` set against the canonical 525-entry path inventory yields zero mismatches. Pass-2's proposed sharpenings (Smithery-as-primary, requirements-driven legacy tell, OAuth-validation ambiguity, stateless-read-only-with-public-upstream coherent family, hybrid-SDK schema cascade, dual-logging) all show up integrated in the current consolidated. This bin is converged on structure; the second normalize cycle yielded no new structural moves and only minor sharpening candidates.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — every observable fact in this bin's samples maps to an existing canonical path)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Build and packaging > Hatchling + uv (Python)` — existing description focuses on the build-backend choice and uv as a workflow runner; it doesn't note that `pyproject.toml` may declare both Poetry and uv conventions side by side (PagerDuty--pagerduty-mcp-server keeps `poetry.lock` and exposes `uv sync`). Sharpening: in some repos hatchling/uv coexists with Poetry artifacts, with `poetry.lock` and uv-style invocations both present — a transitional state more than a deliberate dual-tool choice. Supporting sample: `PagerDuty--pagerduty-mcp-server`.
- `Build and packaging > Python version pinning` — existing description doesn't enumerate the asdf flavor of Python pinning. PagerDuty's `.tool-versions` file pins Python through asdf rather than `.python-version` (pyenv) or `requires-python` (pyproject). Sharpening: include asdf's `.tool-versions` as a third pinning convention alongside pyenv-style `.python-version` and pyproject `requires-python`; asdf-based pinning is rarer in this corpus but observed in vendor-authored repos. Supporting sample: `PagerDuty--pagerduty-mcp-server`.
- `Distribution channel > Windows .exe variant` — the path's existing description (if any) is narrow; awslabs--aws-documentation-mcp-server documents the explicit `uv tool run --from <pkg>@latest <pkg>.exe` invocation that Windows users need. Sharpening: document the canonical Windows-specific launch form (`uv tool run --from <pkg>@latest <pkg>.exe`) — a Windows entry that's not just "we publish a .exe" but a documented uv-tool-run incantation distinct from the `uvx` form. Supporting sample: `awslabs--aws-documentation-mcp-server`.
- `Capability surface > Tools-only, hand-curated narrow surface` — existing description captures small tool counts (3-7) but JackKuo666--PubMed-MCP-Server makes the canonical "research/literature server" instance explicit (search + metadata + PDF download + analysis = 5 tools). Sharpening: research/literature retrieval (PubMed-style: keyword + advanced search + metadata + PDF download + analysis) is a recurring 5-tool shape in this surface category. Supporting sample: `JackKuo666--PubMed-MCP-Server`.
- `Schema and types > Hand-authored tool schemas` — existing path captures the raw-SDK case but doesn't make explicit that hand-authoring co-exists with `pydantic>=2.x` for structured payloads (i.e., schema strategy ≠ no Pydantic). awslabs--aws-documentation-mcp-server hand-authors tool input schemas while still using Pydantic v2 for response/structured payloads. Sharpening: hand-authored input schemas frequently coexist with Pydantic v2 models for structured response payloads — the two paths are orthogonal (input-schema authoring style vs payload-shape modeling) and a sample can take both as siblings. Supporting samples: `awslabs--aws-documentation-mcp-server`, `awslabs--aws-api-mcp-server` (the latter also takes both, with FastMCP auto-derivation as a third sibling reflecting the hybrid SDK).

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — all factual content fits existing roles or the entity-identification preamble)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Confirmed: pass-2 refinements already integrated.** The pass-2 bin-2 refinement report proposed sharpenings to `Distribution channel > Smithery registry`, `Build and packaging > Requirements-driven (legacy Python)`, `Authentication > OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)`, `Multi-tenancy > Stateless read-only (any number of instances)`, and `Capability surface > Partition-scoped tool gating`. Spot-checking the consolidated confirms each sharpening's language is present in the current path description. No re-proposal needed.
- **Confirmed: pass-2 structural concerns dispositioned.** The dual-logging-paths concern (loguru + python-json-logger as siblings) is preserved as two sibling paths in `awslabs--aws-api-mcp-server` and the consolidated's loguru description references the dual-pipeline pattern. The OAuth + cloud-credential-chain coexistence in the same server is preserved as two siblings under Authentication. The hybrid-SDK schema cascade (FastMCP auto-derivation + Pydantic v2 + hand-authored, all siblings) is preserved. The repository-metadata-in-preamble convention is maintained across all samples.
- **Question for the reconciler.** Bin-2's samples uniformly carry repo metadata (stars, license, default branch, last-release date, vendor-vs-community signal) in the level-1 preamble rather than under any role. This continues to match bin-1 convention but is not codified anywhere as a methodology rule. Reconciler may want to record this as a normative preamble convention in the methodology doc so future bins don't drift.
- **Observation: Apollo `Transport > Selection mechanism` is sparse.** `apollographql--apollo-mcp-server` reports the config file selects transport but the README within research budget didn't enumerate which transports are supported. The sample correctly takes only `Transport > Selection mechanism` (no specific transport sibling) because none was confirmed. This is a fidelity-to-evidence choice, not a structural gap — leaving the sample under-specified accurately reflects the README evidence the researcher had access to. No refinement needed; flagged for the reconciler in case the consolidated wants to note "config-file-driven transport selection" as a sub-bullet under `Selection mechanism` (it currently lists CLI flag, env var, implicit default, separate console scripts, functional options, separate entry points, container ARG/CMD, SQL PRAGMA, profile-driven launcher, implicit single mode — but not "config-file selection").
