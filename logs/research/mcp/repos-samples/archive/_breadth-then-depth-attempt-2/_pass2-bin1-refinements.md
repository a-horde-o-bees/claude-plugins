# Pass 2 Refinements — Bin 1

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Release and lifecycle > License — Copyleft (AGPLv3)` — `HenkDz--postgresql-mcp-server.md` (AGPLv3) — Strong network-copyleft license. Rare for MCP servers (most are MIT/Apache); has copyleft implications for hosts embedding the server. Distinct from `License — Permissive (MIT / Apache-2.0)` (no copyleft) and `License — Copyleft / non-commercial (CC BY-NC-SA)` (non-commercial restriction). Trade-off: signals that derivatives must remain open, but does not block commercial use the way CC BY-NC-SA would.

- `Build and packaging > Python version pinning > runtime.txt (Heroku-style)` — `AlwaysSany--deepl-fastmcp-python-server.md` (`runtime.txt` references Python 3.13.3) — Heroku-style runtime declaration file pinning a specific patch-level Python version. Distinct from `requires-python` (range), `.python-version` (pyenv-style), `.tool-versions` (asdf). Often used alongside `.python-version`; surfaces in projects that have legacy Heroku/Procfile heritage or want a third independent pin signal.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Capability surface > Self-reflective analytics tool` — `AlwaysSany--deepl-fastmcp-python-server.md` carries both `analyze_usage_patterns` and `get_translation_history` — together they form a translation-history-plus-analytics pattern, where the *history* is itself a queryable tool (separate from the *aggregate* analytics tool). Existing description names "analyze_usage_patterns" and "get_translation_history" together; could split into the underlying axis (history persistence) vs the analytics overlay.

- `Configuration delivery > Persistent OS-native config` — `DiversioTeam--clickup-mcp.md` adds a concrete pairing — the same `set-api-key` subcommand is the path that persists the credential, tying this mechanism directly to *Developer ergonomics — Setup subcommands on the MCP binary*. Existing description notes the management-subcommand pattern but doesn't surface the pairing as a deliberate design choice — `platformdirs` + setup-subcommand often co-occur, suggesting a cluster.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **HenkDz license is AGPLv3, not CC BY-NC-SA.** I placed it under `License — Copyleft / non-commercial (CC BY-NC-SA)` for now with a note flagging the mismatch — the existing path's framing (CC BY-NC-SA) excludes AGPLv3. Reconciler should add the AGPLv3 path proposed above and move the HenkDz placement.

- **Azure--azure-mcp.md is largely an archived stub.** The bulk of its content describes the *successor* repo (`microsoft/mcp`) rather than the archived repo itself. I kept those facts attached to `Repository layout > Umbrella consolidation` and `Release and lifecycle > Archived`, plus `Host integration` paths the successor documents. Some facts (e.g., "Latest commit noted as 2026-04-14 (Fabric.Mcp.Server 1.0.0)") describe the successor's state, not this archived repo's. Reconciler may want a convention for sample files describing archived-with-successor entities — should the sample's evidence be about the archived state only, or carry forward what the successor exhibits when the successor isn't separately sampled?

- **DaInfernalCoder--perplexity-mcp.md transport selection** is not explicitly documented. I inferred HTTP from the Anthropic Agent SDK dependency but the README does not surface a transport selection mechanism. Listed under `Transport > Streamable HTTP` without a `Selection mechanism` sub-path. Reconciler may want to flag this as inadequate evidence vs. genuinely undocumented behavior.

- **FuzzingLabs uses `python-mcp` hand-rolled** but the consolidated's `Server runtime > Python with hand-rolled MCP` exists. The fit is good — but the FuzzingLabs case is unusual in that it's hand-rolled *per server* (38 different tiny implementations), not one shared hand-rolled framework. The "decision boundary" within this path may benefit from a sub-axis; currently absorbed without comment.

- **AlwaysSany history persistence is implied, not documented.** The sample notes `get_translation_history` and `analyze_usage_patterns` exist but does not say where history is stored (DB? file?). Listed under `Capability surface > Self-reflective analytics tool` and the gap is preserved at the role level rather than escalated to a refinement.
