# Pass 3 Refinements — Bin 11

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 11 samples. Samples were already in role-tree format from Pass 2; this pass verified alignment, scrubbed cross-corpus phrasings from sample prose, fixed one role-mismatched heading, and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none — the Pass 2 proposed paths for bin 11 — `Distribution channel > Shell / PowerShell installer script (Unix + Windows)`, `Configuration delivery > Multi-axis safety toggles`, `Authentication > Multi-backend provider credential bundle (per-service env keys with runtime switching)`, `Capability surface > Runtime service-reconfiguration tool`, `Developer ergonomics > Companion web dashboard (Vite + Uvicorn)`, `Host integration > OAuth deeplink / browser-based setup`, `Capability surface > Document creation/export tool subset (vendor-native artifact format)`, `Build and packaging > Mixed Python + Rust packaging` — remain unintegrated in the consolidated; samples continue to map their relevant facts under the closest existing paths and preserve the underlying detail in path prose. These are carry-forwards awaiting reconciler decisions.)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Safety and security posture > Auto-cleanup of temporary export artifacts` — the consolidated has `Auto-cleanup of temporary export artifacts` only under `Caching and rate-limiting infrastructure`; `samuelgursky--davinci-resolve-mcp.md` exhibits the same mechanism with both a caching/cleanup angle (resource-management hygiene) and a safety angle (transient artifacts not retained on disk after use, reducing data-at-rest exposure). Sharpening: the consolidated should add `Auto-cleanup of temporary export artifacts` under `Safety and security posture` with a `Cross-role: see Caching and rate-limiting infrastructure — Auto-cleanup of temporary export artifacts` annotation, mirroring the `Hardened-by-default container posture` cross-role pattern that already exists between Container artifacts and Safety. The Pass 3 sample retains the dual placement to preserve both angles.

- `Capability surface > Tools-heavy domain wrapper / domain-tool catalog` — `samuelgursky--davinci-resolve-mcp.md` maps 342 granular tools to 324 API methods across 13 upstream object classes (Resolve, ProjectManager, Project, MediaStorage, MediaPool, Folder, MediaPoolItem, Timeline, TimelineItem, Gallery, GalleryStillAlbum, Graph, ColorGroup); `severity1--terraform-cloud-mcp.md` partitions 50+ tools across 11 upstream-API domain modules (account, workspace, run, plan, apply, project, organization, cost_estimation, assessment_results, state_versions, variables); `sandraschi--email-mcp.md` consolidates 6 core tools across SMTP/IMAP plus 10+ transactional-email APIs plus 5 local-test servers plus 4 webhook integrations behind a single tool surface. Sharpening (carry-forward from Pass 2): domain-tool catalogs commonly group by upstream-API object class (one module per class) — this is a recurring decomposition shape that the existing description does not surface.

- `Multi-tenancy > Per-call tenancy argument` — `sajal2692--mcp-weaviate.md` is a textbook example for vector DBs with tenant collections. Sharpening (carry-forward from Pass 2): tools take a tenant parameter consistently (e.g., `search_in_tenant(tenant, query)`) rather than the server resolving tenancy from env vars or session state — naming convention shifts because tenancy enters every tool's signature.

- `Entry point and launch > \`uv --directory\` from source` — `shibuiwilliam--mcp-server-scikit-learn.md` uses `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn`. Sharpening (carry-forward from Pass 2): `--directory=` is path-anchored and incompatible with `uvx`-style zero-install runners — implies the package is developer-installed locally rather than published for general distribution.

- `Capability surface > Tools plus resources plus prompts (full primitive coverage)` — `shreyaskarnik--huggingface-mcp-server.md` adds a custom URI scheme (`hf://`) under resources. Sharpening (carry-forward from Pass 2): custom URI schemes (e.g., `hf://model/...`) are a recurring pattern when resources expose a vendor-native namespace not naturally addressable by `file://` or `http://`.

- `Container artifacts > Multi-stage Dockerfile` — `rust-mcp-stack--rust-mcp-filesystem.md` adds the muslrust-builder + alpine-final pattern with a non-root user (`rust-mcp-user`). Sharpening (carry-forward from Pass 2): a representative shape for native-binary servers is a `clux/muslrust:stable` builder yielding a static binary, then `alpine:latest` as the final image with a dedicated non-root user.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every fact in this bin maps to an existing role)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`samuelgursky--davinci-resolve-mcp.md` cross-role placement of `Auto-cleanup of temporary export artifacts`.** The sample places this path under both `Safety and security posture` and `Caching and rate-limiting infrastructure` because the mechanism has both angles (data-at-rest hygiene; resource-management hygiene). The consolidated has the path only under `Caching and rate-limiting infrastructure`. Pass 3 retains the dual placement and surfaces the resolution as a description sharpening above; the reconciler's call is whether to add the path under Safety with a cross-role annotation. Carried forward from Pass 2 unresolved.

- **`slackapi--slack-mcp-plugin.md` triple-encoding of "configs-only, hosted runtime".** The sample sits in `Server runtime > Remote HTTP service (no local runtime)`, `Distribution channel > Configs-only repo (no server artifact)`, `Distribution channel > Hosted endpoint (no install)`, and `Repository layout > Configs-only` — four paths across three roles capturing the same essential property from different angles. Each angle is genuinely different (runtime location, distribution mechanism, repo content), but the four-path co-occurrence is unique to this sample shape. Reconciler may want to confirm whether all four belong or whether some are redundant. Carried forward from Pass 2 unresolved.

- **`slackapi--slack-mcp-plugin.md` `commands/` and `skills/` directories alongside configs.** The repo is configs-only (no server) but ships `commands/` and `skills/` directories with client-side AI guidance content. Placed under `Documentation surface > Bundled cursor_rules.md / AI-guidance content`. The pattern is "configs + client-side skills" rather than a pure configs-only repo — flagging whether `Documentation surface > Client-side skill content (commands/, skills/ directories)` warrants its own path. Carried forward from Pass 2 unresolved.

- **`samuelgursky--davinci-resolve-mcp.md` lacks `pyproject.toml`/`setup.py`/`requirements.txt` entirely.** Placed under `Build and packaging > Bare script (no build)`, but the `install.py` orchestrator (which creates a venv, installs deps, writes per-client JSON config for 10 hosts) is doing build-system + installer + host-config work that "Bare script" does not capture. Reconciler may want a separate path like `Python-installer-as-build-system` distinct from "Bare script (no build)". Carried forward from Pass 2 unresolved.

- **`samuelgursky--davinci-resolve-mcp.md` Python upper-bound (3.10–3.12, 3.13 unsupported).** The consolidated `Python version pinning` path mentions runtime files like `.python-version`/`runtime.txt` but not the *upper-bound* pattern. This sample pins an ABI-driven upper bound; flagging whether a separate `Python upper-bound (binary-compat-driven)` path is warranted. Carried forward from Pass 2 unresolved.

- **`sandraschi--email-mcp.md` console script name mismatch.** `[project.scripts]` ships `schip-mcp-email = ...` but README references `email-mcp`. Placed under `Entry point and launch > Console script via [project.scripts] / npm bin` with the mismatch noted in description. Reconciler may want a "naming-mismatch" annotation in the path's qualitative description if this happens elsewhere. Carried forward from Pass 2 unresolved.

- **`sandraschi--email-mcp.md` `pytest.ini` alongside `pyproject.toml`.** Legacy dual-config pattern — pytest config at root, not in `[tool.pytest.ini_options]` of pyproject. Placed under `Test stack > pytest with async + coverage` with a parenthetical. Reconciler may want a `Legacy dual-config (pytest.ini + pyproject.toml)` path. Carried forward from Pass 2 unresolved.

- **`severity1--terraform-cloud-mcp.md` claims "debug logging enabled by default" without surfaced mechanism.** No env var or flag observed. Placed under `Observability > Env-var-controlled log level` as a presumed mechanism with a note flagging the gap. Carried forward from Pass 2 unresolved.

- **`shreyaskarnik--huggingface-mcp-server.md` ships single-file at repo root with `src/huggingface/` for helpers.** Hybrid layout — flat at root plus a structured subpackage. Placed under `Repository layout > Single-package flat layout` with prose noting the helper subpackage. Reconciler may want a `Flat-with-subpackage helpers` sub-path. Carried forward from Pass 2 unresolved.

- **`rust-mcp-stack--rust-mcp-filesystem.md` Windows installer via WiX toolset.** Placed under `Distribution channel > Windows .exe variant`. The WiX-toolset detail (and the `wix/` directory in the repo layout) is more specific than the existing path's prose; reconciler may want to mention WiX as a representative tool in the path's qualitative description. Carried forward from Pass 2 unresolved.

- **No transport surfaced explicitly for `rust-mcp-stack--rust-mcp-filesystem.md`.** Inferred stdio. Placed under `Transport > stdio` without a `Selection mechanism` sub-path. Reconciler may want a convention for "transport inferred, not documented." Carried forward from Pass 2 unresolved.

## Convergence assessment

The bin is **converged**. All sample level-2 and level-3 headings now exactly match consolidated role/path names after Pass 3 changes. The Pass 3 changes were narrow:

- **Heading fix** — `rust-mcp-stack--rust-mcp-filesystem.md` had `Linter/formatter test gate` placed under `CI`; the consolidated has this path only under `Test stack`. Moved to `Test stack` (the path was already in the sample's `Test stack` section under `Cargo test / cargo-nextest (Rust)` as a sibling target — moved to its own sibling heading under `Test stack`).
- **Cross-corpus phrasing scrubbed** — eight sites across five samples:
    - `sajal2692--mcp-weaviate.md` — "Rare across Python MCP servers, which typically push tenancy to env vars" replaced with self-describing prose about consistent tool-signature tenancy.
    - `samuelgursky--davinci-resolve-mcp.md` — "outlier in the sample" replaced with "Python-installer-as-build-system rather than a standard packaging manifest"; "One of the few repos in the corpus pinning an upper bound..." replaced with self-describing prose about the binary-compat constraint; "One of the largest tool surfaces among MCPs surveyed" replaced with self-describing prose about context-window pressure on the 342-tool surface.
    - `sandraschi--email-mcp.md` — "highest FastMCP floor in the sample" replaced with "pinning to the 3.x major"; "(unusual)" annotation removed; "tied for highest in the sample" replaced with the bare floor declaration; "uncommon in MCP-server samples" removed from Justfile entry.
    - `shreyaskarnik--huggingface-mcp-server.md` — "one of few Python servers that uses MCP's resource surface for vendor-native namespaces" replaced with prose describing the vendor-native namespace addressing; "demonstrates the underused MCP prompt feature across the Python ecosystem" replaced with bare statement of two prompts shipped; "common 'hackable' pattern for community MCP servers" replaced with self-describing prose about the flat-with-subpackage shape.

The `Auto-cleanup of temporary export artifacts` cross-role placement on `samuelgursky--davinci-resolve-mcp.md` is preserved because both placements correspond to genuinely different role-angles (caching/cleanup hygiene vs data-at-rest safety). The reconciler's call on adding the Safety variant to the consolidated is recorded in description sharpenings above.

No new paths needed beyond what Pass 2 already proposed. The structural concerns above are all carry-forwards awaiting reconciler decisions; none are blocking. Pass 4 should not be required.
