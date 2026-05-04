# Pass 2 Refinements — Bin 13

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

(none from this bin)

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Build and packaging > Python version pinning` — `voska--hass-mcp.md` exhibits a `requires-python = ">=3.13"` on a 287-star production server, the highest Python floor observed so far in this bin. Most Python MCP servers target 3.10+; high floors correlate with reliance on newer-language-feature additions or recent stdlib changes. Sharpening: the `requires-python` floor is itself a signal of project posture — low floors (3.8) appear in legacy-packaging repos that haven't been updated; high floors (3.13) appear when authors deliberately track modern features and accept the deployment-environment cost. Counterpoint: `twolven--mcp-server-puppeteer-py.md` has `python_requires=">=3.8"` (from legacy `setup.py`) — the same axis at the opposite extreme.

- `Configuration delivery > Dotenv file` — `zilliztech--mcp-server-milvus.md` cleanly demonstrates the inverted-priority case the existing description already mentions ("one observed project explicitly inverts this and treats `.env` as the highest-priority source"). The Milvus server explicitly documents `.env > CLI args` precedence as a deliberate choice — likely a bias toward reproducible host-config-driven deployments. Sharpening: the inverted-priority case may deserve its own small callout since it changes the operational behavior — operators expecting CLI-overrides-env will be surprised when CLI args silently lose to a stale `.env` on disk. Also notable: this server is vendor-authored (Zilliz), so the inverted-priority choice is project policy not author idiosyncrasy.

- `Distribution channel > Source clone with `uv run` from source tree` — `zilliztech--mcp-server-milvus.md` is a vendor-official MCP server that leads README install with `uv run src/mcp_server_milvus/server.py` rather than `uvx mcp-server-milvus`. Sharpening: the source-tree `uv run` pattern can be the *primary* documented install for a vendor-authored server, not just a developer-mode posture — when the vendor wants users to clone (perhaps to access bundled examples, configs, or to verify against pinned source) rather than fetch from PyPI. The existing description already notes this is "unusual for vendor-official servers" — bin 13 adds another corpus instance.

- `Repository layout > Monorepo with multiple published packages` — `upstash--context7.md` ships a monorepo with `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n` directories alongside the standard `/packages`. Sharpening: when the monorepo carries an `i18n/` directory and a `public/` directory, the project is treating the repo as a full product surface rather than just a code repo — content/translation/marketing live alongside source. The expanded layout signals a productized monorepo posture distinct from a code-only multi-package monorepo.

- `Capability surface > Token-economy unified-tool surface` — `utensils--mcp-nixos.md` cleanly demonstrates the pattern: 2 tools (`nix()` + `nix_versions()`) with the unified `nix()` query measured at ~1,030 tokens of schema. Sharpening: the corpus signal is sharper when the author measures and documents the schema-token cost — `mcp-nixos` explicitly documents the 1,030-token figure as a design rationale, making the trade-off visible rather than implicit. Token-economy surfaces become more credible as a deliberate design choice when authors quantify them.

- `Server runtime > Remote HTTP service (no local runtime)` — `upstash--context7.md` is a clean example where the public repo carries CLI + plugin metadata + skills + rules but the actual server backend (API, parsing, crawling) is intentionally private. Sharpening: the "no local runtime" path can co-exist with a substantial public repo — the repo's role becomes shipping client-side artifacts (CLI for OAuth, skills for agent integration, marketplace metadata for discovery) rather than the server runtime itself. Distinguishes from `Configs-only repo (no server artifact)` which carries no executable code at all.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`upstash--context7.md` `rules/` folder alongside `skills/`.** The sample ships both a `skills/` and a `rules/` directory in the monorepo. `Bundled "agent SOPs" / vertical skill packs` covers the `skills/` content; the `rules/` folder is parallel content but the consolidated has no explicit "agent rules / governance content shipped alongside server" path. I placed both under the same `Bundled "agent SOPs"` path since they share the "opinionated agent context shipped alongside the server" semantics. Reconciler may want to consider whether `rules/` deserves its own path or whether the `Bundled "agent SOPs"` description should be sharpened to explicitly name "skills, rules, prompt routines" as the family of content.

- **`viant--mcp.md` SDK-as-library tenancy placement.** The Viant SDK is a Go library — tenancy is the consumer's concern. I placed it under both `Per-request tenancy by inbound credential / bearer token` (since the SDK's OAuth2 path enables this) and `N/A (library, not a runtime)` (since the SDK itself doesn't operate). The consolidated's existing convention seems to allow dual placement when the SDK actively supports a tenancy mode and is itself not a runtime — both paths fit. Reconciler should verify dual placement is intended.

- **`upstash--context7.md` Multi-host catalog placement.** README documents 30+ supported agents. I placed under `Host integration > Multi-host catalog (30+ agents)` (existing path that names the 30+ count specifically). The path's name-pinned count is unusual for a heading — most paths describe the kind, not the count. Reconciler may want to consider whether the path should be renamed (`Multi-host catalog (many agents)`) since the 30+ count anchors it to one sample's specifics rather than a general pattern; we now have two corpus instances supporting it.

- **`upstash--context7.md` configs-only-vs-multi-channel disambiguation.** Context7 has both a hosted endpoint AND ships `npx ctx7` as a real npm CLI distribution path (for OAuth setup), AND ships `.claude-plugin/marketplace.json` for discovery. I placed it under all three: `Hosted endpoint (no install)`, `npm via npx / bunx`, and `Configs-only repo (no server artifact)`. The Configs-only path's description is "the actual server is hosted remotely by the vendor" — Context7 fits this since the actual MCP server *is* hosted, but the public repo isn't *only* configs (it carries the npm CLI, skills, rules). Reconciler may want to clarify whether `Configs-only` requires the repo to literally contain only configs (then Context7 doesn't fit), or whether having a hosted server-runtime backend is sufficient regardless of accompanying client-side artifacts.

- **`zilliztech--mcp-server-milvus.md` test stack absence vs unverified.** The README does not surface a test suite; the directory was not extracted. I placed under `Test stack > No tests / not surfaced`. Same for CI under `CI > None / absent`. The existing path explicitly handles "not surfaced in README" so the placement seems correct, but the gap between "no tests exist" and "tests not extracted" is documented in the sample's gaps section without a dedicated path.

- **`v-3--discordmcp.md` MCP Inspector dual placement.** Sample documents `npx @modelcontextprotocol/inspector node build/index.js` as the verification path. I placed it under both `Test stack > MCP Inspector as test driver` and `Host integration > Inspector compatibility called out`. The consolidated's cross-role section explicitly notes MCP Inspector surfaces under both Test stack and Host integration, so dual placement matches established convention.

- **`twolven--mcp-server-puppeteer-py.md` divergent entry-point.** The sample exhibits a `setup.py` declared `[console_scripts]` entry that diverges from how the project is actually launched (`python puppeteer.py` per README). I placed both — `Console script via [project.scripts] / npm bin` (declared but inconsistent) and `Bare interpreter + script path` (actually used). The consolidated's `Setuptools` path notes this exact pattern ("Console scripts declared in setup.py's `entry_points`, but README invocation may diverge from the declared script (a sign the package was never installed/tested as a console script)"). Dual placement under both Entry point paths reflects the actual divergence rather than picking one.

- **`utensils--mcp-nixos.md` Hosted endpoint placement ambiguity.** The README mentions "HTTP remote" as one of the install paths but does not give a canonical hosted URL. I placed under `Distribution channel > Hosted endpoint (no install)` since the path is documented as available, but the sample is ambiguous on whether the project maintainers operate a hosted endpoint or merely document that `MCP_NIXOS_TRANSPORT=http` lets users self-host one. Reconciler may want to flag this if the placement should require evidence of an operated endpoint rather than just HTTP-mode capability.

- **`viant--mcp.md` Custom transports placement.** SDK exposes a transport interface so consumers can plug in their own. I placed under `Transport > Custom or experimental transports`. The sample notes "HTTPS with custom auth, experimental" in the README — same pattern the existing path describes for Go SDKs. Confident placement.
