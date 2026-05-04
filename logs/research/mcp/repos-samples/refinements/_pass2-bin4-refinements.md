# Pass 2 Refinements — Bin 4

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Release and lifecycle > License — Copyleft (GPL-3.0)` — `ckreiling--mcp-server-docker.md` (GPL-3.0) — Strong copyleft license. Distinct from `License — Permissive (MIT / Apache-2.0)` (no copyleft) and `License — Copyleft / non-commercial (CC BY-NC-SA)` (non-commercial restriction). Bin 1 already proposed an AGPLv3 path; pairing this with that proposal suggests a broader split: a single `License — Copyleft (GPL-family / AGPL)` path, or sibling paths per variant. GPL-3.0 has copyleft implications for derivative works but unlike AGPL does not extend obligations to network use, and unlike CC BY-NC-SA permits commercial use.

- `Release and lifecycle > License — Permissive (BSD-3-Clause)` — `datalayer--earthdata-mcp-server.md`, `datalayer--jupyter-mcp-server.md` — BSD-3-Clause permissive license with attribution + non-endorsement clauses. The existing `License — Permissive (MIT / Apache-2.0)` path is named after MIT/Apache; BSD-3-Clause is functionally similar (permissive, commercial-friendly) but distinct in license text. Could either be folded into a renamed `License — Permissive (MIT / Apache / BSD)` path, or kept separate to surface the BSD-specific attribution requirements. Bin 1's proposed AGPLv3 path and this bin's GPL-3.0 / BSD-3-Clause observations together suggest the licensing taxonomy may benefit from a flatter "license family" axis.

- `Developer ergonomics > Devbox dev environment` — `ckreiling--mcp-server-docker.md` — Devbox (`devbox.json`) for reproducible Nix-backed dev environments. Distinct from existing `Devcontainer / mise / dev-environment manifests` path which names devcontainer/mise but not Devbox specifically. Devbox is a Nix-backed alternative to mise/asdf with a different distribution model (per-project shell rather than per-user runtime manager). Could fold into the existing path with a rename, or split out.

- `Multi-tenancy > Per-notebook switchable session` — `datalayer--jupyter-mcp-server.md` — Server holds one connection at a time but exposes a `use_notebook` tool plus `DOCUMENT_ID` env var to switch the active notebook target at runtime. Distinct from `Single connection per server instance` (which is fixed at process launch) and `Connection-lifecycle as a knob` (which controls persistence, not target selection). Specific to servers brokering one of N nameable upstream resources where the runtime can re-point without restart.

- `Configuration delivery > Multi-version env var migration` — `datalayer--jupyter-mcp-server.md` (v1.0.0 added `MCP_TOKEN` distinct from `JUPYTER_TOKEN`) — Versioned breaking-change pattern where a major release introduces a new env var to split previously-conflated concerns (here, MCP-layer auth vs upstream-layer auth). Could fold into `Layered auth (protocol-level + upstream-level)` description as a "v1.x split" example, or surface as its own configuration-delivery sub-pattern. Sharpening more likely than a new path.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Server runtime > TypeScript on Cloudflare Workers (V8 isolate)` — `cloudflare--mcp-server-cloudflare.md` is the canonical example of this path. Could sharpen the description to note that this runtime constrains transport selection (HTTP-only, no stdio) and authentication model (per-request bearer tokens, no env-var credentials available to a stateless worker) as cascading consequences.

- `Distribution channel > Hosted endpoint (no install)` — `cloudflare--mcp-server-cloudflare.md` exemplifies a 14-domain catalog of hosted endpoints under one repository — the "many endpoints, one repo" pattern. Existing description focuses on the single-endpoint case. Sharpening: hosted-endpoint distribution can also be a *catalog* shape where a single monorepo deploys N domain-scoped endpoints, with the README's primary content being which URL serves which capability rather than install instructions.

- `Transport > Stdio-to-HTTP shim on the client side` — `cloudflare--mcp-server-cloudflare.md` documents `mcp-remote` (npm) as the canonical client-side shim. Existing description names `mcp-remote` already; sharpening could note that the server author ships zero stdio code and the shim is universally consumed across hosts (each host's `mcpServers` JSON spawns `npx mcp-remote <url>`).

- `Multi-tenancy > Workspace-scoped sandboxing within a single tenant` — `cyanheads--git-mcp-server.md` shows `BASE_DIR` env var canonicalizing paths against an allow-listed root combined with per-session working-directory management — the per-session aspect adds a layer the existing description doesn't surface. Sharpening: workspace-scoped sandboxing can include both (a) a server-wide root constraint and (b) per-session subdirectory tracking, where the same server process serves multiple stdio sessions each scoped to their own subdir.

- `Authentication > OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)` — `cyanheads--git-mcp-server.md`, `cyanheads--perplexity-mcp-server.md` confirm the three-mode auth pattern (`none` / `jwt` / `oauth`). Sharpening: this path often appears as one branch of a tri-modal switch (`AUTH_MODE=none|jwt|oauth`) rather than as a sole option, where the dev default is `none` and the production deployment opts into JWT or OAuth.

- `Transport > stdio` — `crystaldba--postgres-mcp.md` notes `--access-mode` (`unrestricted` vs `restricted`) interacts with stdio mode — the read-only enforcement happens via SQL parsing in-process, decoupled from transport. Sharpening: stdio servers sometimes layer in-process safety modes orthogonal to the transport itself (read-only-via-parser is decoupled from "stdio" but co-occurs with it).

- `Capability surface > Tools-only, hand-curated narrow surface` — `crystaldba--postgres-mcp.md` documents the explicit rationale: README states "no resources/prompts because the MCP client ecosystem has widespread support for MCP tools." Sharpening: tools-only is sometimes a deliberate ecosystem-compatibility decision rather than an oversight; some authors opt out of resources/prompts citing variable host support.

- `Domain logic and embedded intelligence > Deterministic optimization layered on top of raw ops` — `crystaldba--postgres-mcp.md` documents this path concretely: hypopg-based hypothetical indexing, Pareto cost-benefit selection, workload compression, greedy search adapted from Microsoft Anytime. Existing description should pick up these specific algorithmic terms as evidence of the path's depth (not just "optimization" but a specific algorithm family).

- `Container artifacts > Dockerfile (single-stage, build-from-source)` — `crystaldba--postgres-mcp.md` adds an unusual quality-of-life feature: Dockerfile auto-remaps host address (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux). Sharpening: Dockerfiles in this corpus sometimes carry host-network UX shims for the cross-platform "connect from container to host service" problem.

- `Observability > OpenTelemetry instrumentation` — `datalayer--jupyter-mcp-server.md` makes OTel `api+sdk (>=1.24.0)` core deps (not optional extras). Sharpening: OTel can be a *core* dependency rather than an opt-in extra — every install ships observability. Distinct from servers where OTel is gated behind an `[otel]` extra.

- `Repository layout > Sibling-package factoring` — `datalayer--jupyter-mcp-server.md` factors tool definitions into a separate companion package `jupyter-mcp-tools>=0.1.6` on PyPI. Sharpening: sibling-package factoring sometimes manifests as "tool definitions in a sibling PyPI package" — splitting the protocol harness from the tool catalog as an explicit reuse pattern.

- `Multi-tenancy > N/A (library, not a runtime)` — `conikeec--mcpr.md` (Rust MCP scaffolding library, archived Feb 2026). Sharpening: this path can describe archived libraries that ship scaffolding primitives but were superseded; archive status and `N/A (library)` often co-occur for libraries that didn't survive ecosystem evolution.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin — all factual content fits into existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Release and lifecycle > License — Permissive (MIT / Apache-2.0)` — should expand to a more general "permissive" family bucket that includes BSD-3-Clause, or split into per-license sibling paths. Two BSD-3-Clause samples in this bin + cross-bin AGPLv3 / GPL-3.0 / CC BY-NC-SA observations argue for either (a) a flatter license-family taxonomy or (b) explicit per-license sibling paths to capture the legal-text differences.

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`mcpr` is a library/SDK, not a server.** The consolidated has a few "library" carve-outs (`Multi-tenancy > N/A (library, not a runtime)`, `Capability surface > Library fan-out`) but the role tree was clearly designed for server projects. For `mcpr`, several roles either don't apply (Authentication, Multi-tenancy, Host integration) or apply degenerately. I included the roles that have meaningful content (Server runtime = Rust with rmcp, Transport = stdio + SSE, Configuration delivery = Functional options at construction, etc.) and either omitted or used N/A paths for the others. Reconciler may want a convention: "for library samples, omit roles where N/A is the only honest answer" vs "always include with the N/A path."

- **`cloudflare--mcp-server-cloudflare` is a 14-domain monorepo of hosted Workers.** The sample documents the *aggregate* repo, not any single domain Worker. Each domain Worker may take different paths under several roles (capabilities, auth scopes), but the README treats them as one umbrella. I rendered all 14 as a single sample exhibiting `Distribution channel > Hosted endpoint`, `Server runtime > TypeScript on Cloudflare Workers`, etc., with capability surface noting "14 domain Workers" as one fact. Reconciler may want per-Worker per-role precision but the sample doesn't carry that detail.

- **`datalayer--jupyter-mcp-server` brokers an upstream Jupyter server.** This puts it in an unusual position — most MCP servers either wrap a database, an API, or a local tool; this one wraps another long-lived stateful service. The "use_notebook tool switches the active document" pattern (proposed new path under Multi-tenancy) is not cleanly captured by existing tenancy paths. Reconciler should decide whether this becomes its own path or folds into an existing one (`Connection-lifecycle as a knob` is closest).

- **`crystaldba--postgres-mcp` declares Python 3.12 floor — highest in corpus per sample.** The consolidated's `Build and packaging > Python version pinning` enumerates the mechanisms (`requires-python`, `.python-version`, `.tool-versions`) but doesn't surface a "version-floor distribution" axis. Not a refinement, but a noteworthy data point for the eventual quantification pass.

- **`crystaldba--postgres-mcp` exact-pins dev tooling versions** (ruff==0.14.13, pyright==1.1.408). The consolidated's `Build and packaging > Pin discipline (Python)` covers production-dep pinning; dev-tooling exact-pinning is a related but distinct axis (reproducible *developer* environment vs reproducible *runtime*). May warrant a sharpening of `Pin discipline` description, or could be a separate path. I folded it into `Pin discipline (Python)` for now.

- **`ckreiling--mcp-server-docker` exposes MCP prompts for docker-compose workflow.** The capability surface path `Tools plus resources plus prompts (full primitive coverage)` covers it, but the "prompts as orchestration primitives for natural-language → multi-step action" framing is unusual — most servers' prompts (when they have them) are research/analysis aids, not workflow orchestrators. Could sharpen the existing path's description.
