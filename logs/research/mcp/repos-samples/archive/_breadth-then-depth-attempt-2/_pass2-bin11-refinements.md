# Pass 2 Refinements — Bin 11

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Distribution channel > Shell / PowerShell installer script (Unix + Windows)` — `rust-mcp-stack--rust-mcp-filesystem.md` (ships POSIX shell installer plus PowerShell installer alongside Cargo, Homebrew, Docker, npm) — A pair of platform-native installer scripts (POSIX shell + PowerShell) that fetch a pre-built binary release. Distinct from `Custom Python installer script` (bespoke Python orchestrator that writes host configs) and `Pre-built host installer / one-click install URL` (host-vendor URL handler). The shell-pair is a minimal-dependency way to deliver a native binary cross-platform when neither `cargo install` nor a host-targeted bundle is enough.

- `Configuration delivery > Multi-axis safety toggles` — `severity1--terraform-cloud-mcp.md` (`READ_ONLY_TOOLS` + `ENABLE_DELETE_TOOLS` orthogonal envs); `rust-mcp-stack--rust-mcp-filesystem.md` (read-only-by-default + write flag + tool-disabling) — Two or more independent boolean envs/flags scope tool exposure on orthogonal axes (read-only vs enable-delete; write flag vs tool-disable list). Distinct from `Capability gating flags (per-tool, per-category, write-mode)` which is one axis with multiple categories — here the axes are independent and combine multiplicatively. The Safety/security role already has `Read-only by default with explicit write flag` and `Destructive-action gating flag` for the *posture* angle; this proposed path captures the *delivery* angle (env vars / flags carrying the toggles).

- `Authentication > Multi-backend provider credential bundle (per-service env keys with runtime switching)` — `sandraschi--email-mcp.md` (SMTP/IMAP creds + SendGrid/Mailgun/Resend/Postmark/SES per-provider keys + ProtonMail Bridge + webhook tokens; `configure_service` tool switches at runtime) — Each backend provider has its own env-supplied credential block; the server holds them all simultaneously and a runtime tool selects which one is active per call or globally. Distinct from `Multi-provider credential bundles` (similar shape but typically static per-process), `Per-source independent API keys with graceful degradation` (aggregator semantics — degradation is the focus), and `Multi-method selector` (auth method choice, not provider choice). Suggest reconciler decide whether this is a sharpening of `Multi-provider credential bundles` or a new path.

- `Capability surface > Runtime service-reconfiguration tool` — `sandraschi--email-mcp.md` (`configure_service` tool reconfigures backend at runtime without process restart) — A first-class MCP tool that mutates server configuration during the session. Distinct from `Configuration delivery > Runtime reconfiguration tool` (which captures the same mechanism on the *configuration* side). The capability-surface framing matters because it advertises the reconfiguration as part of the surface the LLM can call. May be a description sharpening on the existing `Runtime reconfiguration tool` path rather than a new entry — flagging for reconciler.

- `Developer ergonomics > Companion web dashboard (Vite + Uvicorn)` — `sandraschi--email-mcp.md` (separate `webapp/` with Vite frontend + Uvicorn backend on ports 10812/10813 for monitoring and control); `samuelgursky--davinci-resolve-mcp.md` partial overlap (no dashboard but `examples/` + `docs/` companion dirs) — A standalone web UI shipped in the same repo as a monitoring/control sidecar to the MCP server, separate from the MCP transport itself. Distinct from `Inspector/debug tooling references` (just pointing at MCP Inspector). The role `Observability > Companion monitoring dashboard` already exists; this proposed path captures the *developer ergonomics* angle where the dashboard is shipped as scaffold-and-build assets rather than just observability output.

- `Distribution channel > Zed extension` — already exists at line 800. Confirming `sandraschi--email-mcp.md` exhibits this, no new path needed.

- `Host integration > OAuth deeplink / browser-based setup` — `slackapi--slack-mcp-plugin.md` (deeplink for Cursor; browser-based OAuth flow with callback port; clientId per host) — Setup begins by the user clicking a deeplink that hands off to the host; the host then performs OAuth-callback integration with port-based callback. Distinct from existing `Vendor-specific companion config` — the deeplink is the install vector itself, not just a config snippet.

- `Capability surface > Document creation/export tool subset (vendor-native artifact format)` — `slackapi--slack-mcp-plugin.md` (canvas document create/export); `samuelgursky--davinci-resolve-mcp.md` (export tools with auto-cleanup) — Tools whose effects produce vendor-native documents (Slack canvas, Resolve project state) that the LLM can create and export. Distinct from generic file-write — the artifact is shaped by the upstream platform's document model. Likely subsumed by `Tools-heavy domain wrapper / domain-tool catalog` for the broad case; flagging for reconciler whether sub-axis is warranted.

- `Build and packaging > Mixed Python + Rust packaging (`pyproject.toml` + `Cargo.toml`)` — `sandraschi--email-mcp.md` (Cargo.toml alongside pyproject.toml, attributed to MCPB bundle signing) — A Python project that also carries a Rust manifest for ancillary build steps (typically MCPB signing tooling or a native helper). Distinct from `Single-package with dual-ecosystem wrapper` (in Repository layout) which captures the layout angle; this captures the build-system angle. May be redundant with the layout role; flagging for reconciler.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Container artifacts > Multi-stage Dockerfile` — `rust-mcp-stack--rust-mcp-filesystem.md` adds the muslrust-builder + alpine-final pattern with a non-root user (`rust-mcp-user`); the existing description should mention this two-stage minimal-image pattern as a representative shape for native-binary servers. Suggestion: append "Common Rust-specific shape: `clux/muslrust:stable` builder yielding a static binary, `alpine:latest` final image with a dedicated non-root user."

- `Capability surface > Tools-heavy domain wrapper / domain-tool catalog` — `samuelgursky--davinci-resolve-mcp.md` exposes 324 API methods across 13 object classes; `severity1--terraform-cloud-mcp.md` exposes 50+ tools across 11 domain modules. The existing description should note that domain-tool catalogs commonly group by upstream-API object class (one module per object class) — this is a recurring decomposition shape, not just "many tools."

- `Configuration delivery > Persistent OS-native config` — N/A here; no sample touches this. Flagging absence so reconciler doesn't expect updates.

- `Multi-tenancy > Per-call tenancy argument` — `sajal2692--mcp-weaviate.md` is a textbook example for vector DBs with tenant collections. Existing description already mentions this; the sharpening is to elevate the *first-class tool-signature* framing — tenancy as an argument means search/retrieval tools all take a `tenant` parameter consistently, which matters for tool-naming convention. Suggestion: append "Tools take a tenant parameter consistently (e.g., `search_in_tenant(tenant, query)`); naming convention shifts because tenancy enters every tool's signature."

- `Entry point and launch > `uv --directory` from source` — `shibuiwilliam--mcp-server-scikit-learn.md` uses `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn`. The existing description should flag that `--directory=` is path-anchored and incompatible with `uvx`-style zero-install runners — implies the package isn't meant for general distribution, only developer-installed local runs.

- `Capability surface > Tools plus resources plus prompts (full primitive coverage)` — `shreyaskarnik--huggingface-mcp-server.md` adds a custom URI scheme (`hf://`) under resources. The existing description should mention that custom URI schemes are a recurring pattern when resources expose a vendor-native namespace. Suggestion: append "Custom URI schemes (e.g., `hf://model/...`) are a common shape when resources expose a vendor-native namespace not naturally addressable by `file://` or `http://`."

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Distribution channel > Source clone with editable install` and `Source clone with `uv run` from source tree` — `shibuiwilliam--mcp-server-scikit-learn.md` exhibits both shapes: the README documents `pip install -e ".[dev]"` (editable install) AND the host-config uses `uv --directory=... run` (uv-from-source). Two paths under the same role coexist for one sample, not a split — but the reconciler should confirm both are accepted as siblings without deduplication.

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`slackapi--slack-mcp-plugin.md` is a configs-only repo with no local runtime.** The consolidated has `Server runtime > Remote HTTP service (no local runtime)` and `Distribution channel > Configs-only repo (no server artifact)` and `Repository layout > Configs-only` — three separate paths capturing the same essential property from different role angles. I used all three, but the reconciler may want to reduce to one canonical reference if the others should always trail along. Also: the sample's `commands/`, `skills/`, `.claude-plugin/`, `.cursor-plugin/` directories are interesting — they push the repo from "configs-only" into "configs + client-side skills" territory. I placed `.claude-plugin/` under `Host integration > .claude-plugin/ directory in repo` and noted the `commands/` + `skills/` content under `Documentation surface > Bundled cursor_rules.md / AI-guidance content` — flagging that "client-side skills" may want its own path.

- **`samuelgursky--davinci-resolve-mcp.md` lacks `pyproject.toml`/`setup.py`/`requirements.txt` entirely.** This is rare. The consolidated has `Build and packaging > Bare script (no build)` which seems closest, but `install.py` (the bespoke installer that creates the venv) is not really a "bare script" pattern — it's a Python-installer-as-build-system. Placed under `Bare script (no build)` with a note. Also placed `Custom Python installer script` under both `Distribution channel` and `Universal installer covering many hosts` under `Host integration` — these two paths are tightly coupled in this case (the same script does both). Reconciler may want a cross-reference.

- **`samuelgursky--davinci-resolve-mcp.md` Python upper-bound (3.10–3.12, 3.13 unsupported).** The consolidated `Python version pinning` path mentions runtime files like `.python-version`/`runtime.txt` but not the *upper-bound* pattern. This sample is rare in pinning an ABI-driven upper bound; flagging for whether a separate path is warranted.

- **`sandraschi--email-mcp.md` console script name mismatch.** `[project.scripts]` ships `schip-mcp-email = ...` but README references `email-mcp`. Doesn't fit any existing path cleanly; placed evidence under `Entry point and launch > Console script via [project.scripts] / npm bin` with the mismatch noted in description. Reconciler may want a "naming-mismatch" annotation in the path's qualitative description if this happens elsewhere.

- **`sandraschi--email-mcp.md` `pytest.ini` alongside `pyproject.toml`.** Legacy dual-config pattern — pytest config at root, not in `[tool.pytest.ini_options]` of pyproject. Doesn't fit any existing path; placed evidence under `Test stack > pytest with async + coverage` with a parenthetical. Flagging for whether the reconciler wants a `Legacy dual-config (pytest.ini + pyproject.toml)` path under `Build and packaging` or `Test stack`.

- **`severity1--terraform-cloud-mcp.md` claims "debug logging enabled by default".** No env var or flag observed surfacing this. Placed under `Observability > Env-var-controlled log level` as a presumed mechanism with a note flagging the gap.

- **`shreyaskarnik--huggingface-mcp-server.md` ships single-file at repo root with `src/huggingface/` for helpers.** Hybrid layout — flat at root plus a structured subpackage. Placed under `Repository layout > Single-package flat layout` with a parenthetical about the helper subpackage. Reconciler may want a "Flat-with-subpackage helpers" sub-path.

- **`rust-mcp-stack--rust-mcp-filesystem.md` Windows installer via WiX toolset.** The consolidated has `Distribution channel > Windows .exe variant` which fits, but the WiX-toolset detail (and the `wix/` directory in the repo layout) is more specific — flagging for whether the qualitative description on `Windows .exe variant` should mention WiX as a representative tool.

- **No transport surfaced explicitly for `rust-mcp-stack--rust-mcp-filesystem.md`.** Inferred stdio. Placed under `Transport > stdio` without a `Selection mechanism` sub-path, mirroring how `DaInfernalCoder--perplexity-mcp.md` was handled in bin1. Reconciler may want a convention for "transport inferred, not documented."
