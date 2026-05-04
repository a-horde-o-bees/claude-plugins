# Pass 3 Refinements — Bin 4

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on bin 4 samples (`ckreiling--mcp-server-docker.md`, `cloudflare--mcp-server-cloudflare.md`, `conikeec--mcpr.md`, `crystaldba--postgres-mcp.md`, `cyanheads--git-mcp-server.md`, `cyanheads--perplexity-mcp-server.md`, `datalayer--earthdata-mcp-server.md`, `datalayer--jupyter-mcp-server.md`). Samples were already in role-tree format from Pass 2; this pass verified alignment, applied targeted updates from new consolidated paths, and re-surfaces unresolved structural concerns.

## Convergence summary

All eight samples already mirror the consolidated's role tree with high fidelity. Pass 3 applied three license-path migrations now that the consolidated has integrated the Pass 2 license proposals: `ckreiling--mcp-server-docker.md` (GPL-3.0) moved from the MIT/Apache placeholder to the new `License — Copyleft (GPL-3.0)` path; `datalayer--earthdata-mcp-server.md` and `datalayer--jupyter-mcp-server.md` (BSD-3-Clause) moved to the new `License — Permissive (BSD-3-Clause)` path. The placeholder prose under those headings ("placed under closest existing path with a refinement proposed…") was rewritten as clean license descriptions matching the consolidated's voice. No other structural moves were needed — the level-2 and level-3 headings on every sample exactly match consolidated role/path names.

Several Pass 2 sharpening proposals from this bin remain unresolved in the consolidated: per-notebook switchable session under Multi-tenancy (`datalayer--jupyter-mcp-server`), Devbox under Developer ergonomics (`ckreiling--mcp-server-docker`), multi-version env-var migration under Configuration delivery (`datalayer--jupyter-mcp-server`), and several description-sharpening proposals across Cloudflare's hosted-endpoint catalog and crystaldba's optimization stack. These are re-surfaced under Structural concerns rather than re-proposed as new refinements — the reconciler already has them from Pass 2.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — Pass 2 license proposals are now integrated; remaining Pass 2 proposals carry forward unresolved but are not re-proposed here)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

(none new in Pass 3 — Pass 2 sharpenings carry forward; see Structural concerns)

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — bin 4 samples all map to existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none new in Pass 3)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **License path migrations applied in this pass.** `ckreiling--mcp-server-docker.md` (GPL-3.0), `datalayer--earthdata-mcp-server.md` (BSD-3-Clause), and `datalayer--jupyter-mcp-server.md` (BSD-3-Clause) previously sat under `License — Permissive (MIT / Apache-2.0)` with placeholder prose noting a proposed refinement. The consolidated has since integrated `License — Copyleft (GPL-3.0)` and `License — Permissive (BSD-3-Clause)`; the three samples were re-rooted under those paths. Sample prose under the new headings is now self-contained (no "placed under closest existing path" placeholder language).

- **Pass 2 proposals carried forward unresolved.** The Pass 2 bin-4 refinement file proposed several non-license items the reconciler has not yet integrated:
    - `Multi-tenancy > Per-notebook switchable session` — `datalayer--jupyter-mcp-server.md` exposes `use_notebook` tool plus `DOCUMENT_ID` env var for runtime notebook switching. Currently rendered as siblings `Single connection per server instance` + `Connection-lifecycle as a knob` (closest existing fit).
    - `Developer ergonomics > Devbox dev environment` — `ckreiling--mcp-server-docker.md` uses Devbox (Nix-backed). Currently rendered under existing `Devcontainer / mise / dev-environment manifests` path, since the existing path's description names devcontainer/mise but not Devbox.
    - `Configuration delivery > Multi-version env var migration` — `datalayer--jupyter-mcp-server.md` v1.0.0 introduced `MCP_TOKEN` distinct from `JUPYTER_TOKEN`. Currently captured under `Layered auth (protocol-level + upstream-level)` with the version-split detail in prose.
    - Description sharpenings for `Server runtime > TypeScript on Cloudflare Workers (V8 isolate)`, `Distribution channel > Hosted endpoint (no install)`, `Transport > Stdio-to-HTTP shim on the client side`, `Multi-tenancy > Workspace-scoped sandboxing within a single tenant`, `Authentication > OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)`, `Transport > stdio`, `Capability surface > Tools-only, hand-curated narrow surface`, `Domain logic and embedded intelligence > Deterministic optimization layered on top of raw ops`, `Container artifacts > Dockerfile (single-stage, build-from-source)`, `Observability > OpenTelemetry instrumentation`, `Repository layout > Sibling-package factoring`, and `Multi-tenancy > N/A (library, not a runtime)`.

  These remain valid concerns after Pass 3 re-examination — re-proposing them would duplicate the Pass 2 record. Reconciler should decide between integrating, deferring, or rejecting each.

- **`mcpr` library samples take limited path coverage.** `conikeec--mcpr.md` is a Rust scaffolding library, not a server. Several roles either don't apply (Authentication, Multi-tenancy, Host integration) or apply degenerately (`Multi-tenancy > N/A (library, not a runtime)` is the honest answer). The sample includes only roles with substantive content. Reconciler may want to record a methodology convention about library-shaped samples (omit roles where N/A is the only honest answer vs always include with N/A path); currently the convention is observed implicitly.

- **`cloudflare--mcp-server-cloudflare` umbrella semantics.** The sample documents the *aggregate* repo (14 domain Workers under one monorepo), not any single domain Worker. Per-Worker per-role precision (which Worker takes which auth scope, which capability surface) isn't surfaced because the README treats them as one umbrella. The umbrella-vs-leaf framing parallels the `Azure--azure-mcp` archived-with-successor ambiguity raised in bin-1; both deserve a methodology decision about how to render multi-artifact samples.

- **`datalayer--jupyter-mcp-server` brokers an upstream stateful service.** Most MCP servers wrap a database, an API, or a local tool; this one wraps another long-lived stateful service (a running Jupyter kernel). The `use_notebook` runtime-switch pattern doesn't fit cleanly into existing tenancy paths — `Connection-lifecycle as a knob` is closest but doesn't capture target-selection-without-restart. Reconciler should decide whether the per-notebook switching pattern merits its own path or folds into existing tenancy paths.

- **`crystaldba--postgres-mcp` Python 3.12 floor.** Highest in-corpus per Pass 2 inventory. The consolidated's `Build and packaging > Python version pinning` enumerates pinning mechanisms but doesn't surface a "version-floor distribution" axis. Not a refinement, but a noteworthy data point for the eventual quantification pass.

- **`crystaldba--postgres-mcp` exact-pinning of dev tooling.** ruff==0.14.13, pyright==1.1.408 — applies discipline at the developer-environment layer, distinct from production-dep pinning. Currently folded into `Pin discipline (Python)` with the dev-tooling distinction captured in prose; reconciler may eventually want a separate path.

- **`ckreiling--mcp-server-docker` MCP prompts as docker-compose orchestration primitives.** `Tools plus resources plus prompts (full primitive coverage)` covers the mechanical fit, but the "prompts as orchestration primitives for natural-language → multi-step action" framing is unusual — most servers' prompts (when they have them) are research/analysis aids, not workflow orchestrators. Could sharpen the existing path's description to surface this variant.

## Convergence assessment

The bin is **converged on structure**. All sample level-2 and level-3 headings exactly match consolidated role/path names after the three Pass 3 license migrations. No new roles needed. No new paths or sharpenings beyond what Pass 2 already proposed; remaining gaps are reconciler-side (integrate or reject the Pass 2 proposals). Pass 4 should not be required for this bin if the reconciler dispositions the Pass 2 carryover items.
