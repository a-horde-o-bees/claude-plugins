# Sample

Mirrors `https://github.com/damionrashford/trader-os`. Multi-plugin marketplace shipping AI trading plugins for Claude Code (Polymarket prediction markets, Coinbase AgentKit, quant strategies + backtesting). MIT license. Last commit 2026-04-18; default branch `main`; 1 star. Sample origin: dep-management + bin-wrapper.

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root advertises three plugins (`polymarket-plugin`, `coinbase-agent-kit`, `trading-core`) under `./plugins/<name>/`, each carrying its own `.claude-plugin/plugin.json`. The owner authors all three plugins; entries use relative sources. Top-level `name` (`trader-os`) and `owner` are siblings of a `metadata` block carrying `description`, `version` (`0.4.0`), and `license`. No `metadata.pluginRoot`. Plugin names are `polymarket-plugin`, `coinbase-agent-kit`, `trading-core` — no reserved-name collision with the marketplace name `trader-os`.

### Top-level `metadata` wrapper variants

Marketplace declares the `metadata.{description, version, license}` shape. `metadata.version` (`0.4.0`) decouples from per-plugin `0.1.0` streams — three-way version space (marketplace meta / marketplace-entry / plugin.json) where only the latter two are required to match per CLAUDE.md.

## Plugin source binding

### Relative source pointing to subdirectory

Three marketplace entries use relative sources (`./plugins/polymarket`, `./plugins/coinbase-agent-kit`, `./plugins/trading-core`). No github/url/git-subdir/npm sources. No `skills` override on marketplace entries — full plugin trees ship as-is.

### `strict` field default

No explicit `strict` on any entry; default (implicit true) applies.

## Source layout

### Single tree (plugin equals repo)

Plugins live under `plugins/<name>/` subdirectories of the marketplace repo. Authoring sources and packaged copies are co-located — no dual-tree sync gate.

## Per-plugin discoverability metadata

### Category + tags pair

Each plugin entry carries `category` (`trading`, `web3`, `quant` — one each, no reuse) plus `tags`. No `keywords` field at marketplace-entry level (keywords live inside each plugin.json).

### `$schema` absence on per-plugin manifests

`$schema` absent on `marketplace.json`. Present on `.claude/settings.json` (`https://json.schemastore.org/claude-code-settings.json`) — different file.

## Version coordination

### Triple-file version (build manifest joins)

Three sites carry version: marketplace `metadata.version` (`0.4.0`), marketplace-entry `version` per plugin (`0.1.0` each), and plugin `plugin.json.version` (`0.1.0` each). CLAUDE.md prescribes the invariant "Per-plugin entry `version` in marketplace.json must match each plugin's own `plugin.json`." Marketplace-root version evolves on independent cadence. Hand-maintained dual-version discipline with no CI gate to enforce.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Single `main` branch; users pin by marketplace ref only (`/plugin marketplace add damionrashford/trader-os`). No stable/latest split. README directs users to run `/plugin marketplace update trader-os` manually since "third-party marketplaces don't auto-update." The word "channel" elsewhere in the repo refers exclusively to the MCP channel feature (`channels/trading-alerts/`), not a distribution channel.

## Tag and release lifecycle

### No tags at all

`gh api .../tags` returns `[]`. Default branch `main`. No release branching, no pre-release suffixes. CLAUDE.md documents `v<MAJOR>.<MINOR>.<PATCH>` tags and "Releases via GitHub Releases tagged `v<SEMVER>`" but at 2026-04-18 the repo has zero tags and zero releases. Versions are static hand-set values (`0.1.0` per plugin, `0.4.0` at marketplace).

## Plugin-component registration

### Default convention discovery

No `plugin.json` declares explicit component paths in any of the three plugins; all rely on Claude Code's default discovery under `skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `monitors/monitors.json`, `bin/`, `.mcp.json`, `channels/`.

### `.mcp.json` sibling file

`trading-core/.mcp.json` references `channels/trading-alerts/server.ts` for the MCP channel. The other two plugins ship no `.mcp.json`.

## Component composition

### Skills (universal)

All three plugins ship skills: 8 (polymarket-plugin), 10 (coinbase-agent-kit), 12 (trading-core).

### Agents

Each plugin ships 5 agents: polymarket router + trader + researcher + risk + executor; coinbase router + trader + wallet-ops + payment-ops + agent-builder; trading router + quant-analyst + backtester + risk-officer + strategy-researcher.

### Hooks

All three plugins ship `hooks/hooks.json`. polymarket: PreToolUse(Bash) + SessionStart. coinbase-agent-kit: PreToolUse(Bash) + SessionStart. trading-core: SessionStart×2 + PostToolUse(Bash) + SessionEnd.

### MCP servers

trading-core ships `.mcp.json` referencing `channels/trading-alerts/server.ts` (a Bun/TypeScript server). polymarket and coinbase-agent-kit ship no MCP servers.

### bin

All three plugins ship one `bin/` entry: `polymkt`, `cbkit`, `tcore` respectively.

### Composition shapes

trading-core hits the broadest palette — skills, agents, hooks, `.mcp.json`, bin, plus the channel under `channels/trading-alerts/`. polymarket and coinbase-agent-kit add `monitors.json` (3 and 2 monitors respectively).

## Skill authoring conventions

### `allowed-tools` with permission-rule syntax

Skills ship under each plugin's `skills/` directory; agents enforce tool gating via `tools:` arrays mixing bare names (`Read`, `Grep`, `Glob`) and Bash-with-glob patterns (`Bash(uv run *)`, `Bash(jq *)`, `Bash(tcore *)`, `Bash(polymkt *)`, `Bash(cbkit *)`).

## Agent declaration conventions

### Rich behavior fields (background, isolation, memory)

Agent frontmatter fields used: `name`, `description`, `model`, `effort`, `maxTurns`, `skills`, `memory`, `tools`, `isolation`. `quant-analyst` uses `model: inherit`, `effort: high`, `maxTurns: 20`, `skills: [quant-math, position-sizing, bayesian-updating, time-series]`, `memory: project`. `backtester` and `strategy-researcher` add `isolation: worktree`. `maxTurns` ranges 15-40 across agents; `effort` values: `medium` (routers), `high` (specialists). `model: inherit` on every agent. CLAUDE.md explicitly lists supported frontmatter (`name description model effort maxTurns tools disallowedTools skills memory background isolation`) versus silently-ignored (`color hooks mcpServers permissionMode`).

### `model` + `effort` + `maxTurns` for cost control

Each plugin ships one broad `medium`-effort router (20-turn budget) plus 4-5 specialist agents with `effort: high`, 15-40 turn budgets, narrow skill lists. `model: inherit` on every agent (no hardcoded model selection).

### `skills:` array delegating to skill packages

Specialist agents declare bare-name in-plugin skill references (e.g., `skills: [quant-math, position-sizing, bayesian-updating, time-series]`).

## Server runtime (MCP)

### `.mcp.json` sibling file

trading-core's `.mcp.json` references `channels/trading-alerts/server.ts` — a Bun/TypeScript MCP channel server, gated by HMAC, declaring `claude/channel` capability. Per README: "Channels are in research preview and require Claude Code 2.1.80+ with claude.ai login (not API-key auth). During the preview, activate with `claude --dangerously-load-development-channels plugin:trading-core@trader-os`."

## Bin entry mechanism

### Multi-script bin family / CLI dispatcher

All three plugins ship a PATH-level CLI: `polymkt` (polymarket), `cbkit` (coinbase-agent-kit), `tcore` (trading-core). Each is a dispatcher to `skills/*/scripts/*.py`.

- `plugins/polymarket/bin/polymkt` — `auth/markets/clob/positions/stream/onchain/research/strategy` subcommands plus `status` and `watchlist` shortcuts.
- `plugins/coinbase-agent-kit/bin/cbkit` — `auth/accounts/tx/webhooks/commerce/kit` plus `status` and `providers` shortcuts.
- `plugins/trading-core/bin/tcore` — `math/size/mm/bt/store` plus `dirs` and `journal` shortcuts.

### Python `bin/` script with uv injection

All three bin files use `#!/usr/bin/env -S uv run --script` shebang (PEP 723). Same shebang on every hook and monitor `.py` script. Bin scripts declare `dependencies = []` (tcore, cbkit) or a single dep (polymkt declares `httpx==0.27.2`), then `subprocess`-dispatch to skill scripts that declare their own inline deps. Each skill invocation materializes a fresh `uv run --script` subprocess rather than sharing the parent bin's env — deliberate separation per skill, cold-start cost per subcommand.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Bin scripts use `e = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip(); if e: return Path(e); return Path(__file__).resolve().parent.parent`. Same pattern in polymkt, cbkit, and tcore. Permissions 100755 on every bin/hook/monitor script.

## Dependency installation

### Inline-deps-per-script (PEP 723)

Every Python file (bin dispatchers, skills scripts, hooks, monitors) starts with `#!/usr/bin/env -S uv run --script` plus a `# /// script` block declaring `requires-python` and exact-pinned deps (e.g. `httpx==0.27.2`). No `requirements.txt`, no `pyproject.toml`, no `__init__.py`. Each script invocation creates/reuses uv's cached ephemeral env keyed by inline-dep hash. Plugin-wide commitment across ~20+ files.

### SessionStart hook → npm install local to plugin

trading-core's `plugins/trading-core/hooks/scripts/install-channel-deps.sh` (registered in `hooks/hooks.json` as a SessionStart `command`-type hook with no matcher) installs Node deps for the channel into `${CLAUDE_PLUGIN_DATA}/node_modules`. Source manifest at `channels/trading-alerts/package.json` declares one dep (`@modelcontextprotocol/sdk ^1.0.0`).

### Mixed Python + Node install

Two parallel dep stories coexist: Python via PEP 723 `uv run --script` ephemeral runs (no plugin-managed venv), and Node `node_modules` for the MCP channel installed via a `diff -q`-gated SessionStart shell hook.

## Install change detection

### Diff-based byte comparison of manifest

trading-core's install hook `diff -q`s source `channels/trading-alerts/package.json` against cached copy at `${CLAUDE_PLUGIN_DATA}/trading-alerts-package.json`. Reinstalls only when manifests differ or cache is missing.

### Version-stamp file written after success

The install script copies source `package.json` to cache AFTER a successful install (`if [[ -d "${NODE_MODULES}" ]]; then cp "${SRC_PKG}" "${CACHED_PKG}"`). On failure, `rm -f "${DATA}/package.json"` cleans up the intermediate write. Cached-manifest stamp is only written on verified success — next session re-diffs and retries.

## Install trigger and lifecycle

### SessionStart direct invocation

trading-core registers `install-channel-deps.sh` as a SessionStart `command`-type hook with no matcher. Fires on every sub-event (startup, resume, clear, compact). polymarket and coinbase-agent-kit register only `session-start-env.py` on SessionStart.

## Install failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`set -euo pipefail` at top of `install-channel-deps.sh`, then `|| true` on the actual install command (`bun install --silent 2>/dev/null || true`), plus an early-exit path when neither `bun` nor `npm` is available (`exit 0`). Downstream `session-start-env.py` surfaces channel readiness to the user; the install hook itself never complains. No JSON `systemMessage`, no `continue: false`. Runtime variant: bun preferred with npm fallback (`command -v bun >/dev/null 2>&1; then ... elif command -v npm >/dev/null 2>&1; then ...`).

## User configuration and authentication

### userConfig as typed schema with stringly-typed values

All three plugins declare `userConfig`: 15 fields (polymarket), 16 (coinbase-agent-kit), 18 (trading-core). Every field has `type: "string"` and `default: ""` or a concrete default. No enums, no numeric or boolean types. Numeric-looking values (`POLYMARKET_MAX_ORDER_USDC: "100"`, `TRADING_CORE_KELLY_FRACTION: "0.25"`) are stringly-typed and parsed downstream.

### Native `userConfig` with `${user_config.KEY}` substitution

`${user_config.KEY}` observed in `trading-core/.mcp.json` for all five channel-related secrets (`TRADING_ALERTS_PORT`, `TRADING_ALERTS_SECRET`, `CDP_WEBHOOK_SECRET`, `COINBASE_COMMERCE_WEBHOOK_SECRET`, `POLYMARKET_WEBHOOK_SECRET`) piped into the MCP server's `env` block. Hook/monitor scripts read the same keys via `os.environ.get(...)` — Claude Code's plugin layer populates env from userConfig before spawning scripts. No `CLAUDE_PLUGIN_OPTION_<KEY>` pattern observed.

### `sensitive: true` flag absent on secret fields

Across all three plugins, every secret-class field lacks the `sensitive: true` flag despite descriptions explicitly labelling them "SECRET — treat like a password." Polymarket `POLYMARKET_PRIVATE_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`; coinbase `CDP_API_KEY_SECRET`, `CDP_WALLET_SECRET`, `COINBASE_COMMERCE_WEBHOOK_SECRET`; trading-core `TRADING_ALERTS_SECRET`, `CDP_WEBHOOK_SECRET`, `POLYMARKET_WEBHOOK_SECRET` all end their description with the word "Secret." but no field uses the `sensitive: true` flag. README acknowledges secrets "stay in your local Claude Code config; never committed, never written to disk" via `/plugin config set` — relies on the storage backend entirely, not the schema flag. Repeated three times across three plugins — systematic authoring gap.

## Session context loading

### SessionStart prints plain markdown to stdout

All three plugins ship `session-start-env.py` that prints a "session ready-check" markdown block to stdout (shown to the user and ingested as context). Contents: which env vars are set/missing, data-dir status, channel-runtime status. trading-core also runs `install-channel-deps.sh` from SessionStart (separate concern; that script stays silent and does not inject context).

### SessionStart purely for non-context side effects

trading-core's SessionStart has multi-script division of labor — `install-channel-deps.sh` installs dep silently, `session-start-env.py` prints a markdown readiness block separately. Splits "make the world ready" from "tell the user what's ready."

## SessionStart matcher scope

### Empty matcher (all sub-events)

All three SessionStart entries omit the matcher field, firing on every sub-event (startup, resume, clear, compact). The readiness-report runs on every compact and clear; users doing heavy compaction see the block repeat. `install-channel-deps.sh` re-runs its `diff -q` on every compact — idempotent and cheap when manifest hasn't changed.

## Tool-use enforcement

### PreToolUse Bash matcher as ask-first guardrail

Two distinct PreToolUse scripts on `Bash` matcher emit `permissionDecision: ask` with trade summaries before approval; `deny` reserved for hard policy violations.

- polymarket `pre-trade-validate.py` — parses clob.py `place|market|batch|cancel-all` subcommands out of Bash argv; checks notional against `POLYMARKET_MAX_ORDER_USDC`; requires `--yes-really` on `cancel-all`; enforces `--dry-run` vs `--live` based on `POLYMARKET_DRY_RUN_DEFAULT`.
- coinbase `pre-tx-validate.py` — analogous guard on `cbkit tx` / `kit.py` transactions; enforces `DRY_RUN_DEFAULT`, checks `ALLOWED_NETWORKS` allow-list, estimates `MAX_TX_VALUE_USD`.

### PostToolUse as audit trail

trading-core's `post-trade-journal.py` on matcher `"Bash"` sniffs placements across venues (polymkt / cdp-tx / cbkit) and appends to SQLite journal. Runs after tool success; silent on non-trade Bash commands. No hook-level DB locking discipline visible — `PostToolUse` fires in parallel and writes to the same `journal.sqlite`. The trading-storage skill is documented as using "SQLite WAL" mode but isn't verified in the hook script itself.

## Hook handler runtime

### Bash scripts at conventional path

Hook scripts use `#!/usr/bin/env -S uv run --script` (Python with PEP 723) for `.py` hooks (`pre-trade-validate.py`, `pre-tx-validate.py`, `post-trade-journal.py`, `session-start-env.py`) and `#!/usr/bin/env bash` for `install-channel-deps.sh`. Permissions 100755 across all hook scripts.

## Hook output contract

### JSON-only stdout, no stderr-human parallel

PreToolUse hooks emit stdout JSON with `hookSpecificOutput.permissionDecision` (`ask` / `deny` / implied `allow` on no-op). Reason lines in `permissionDecisionReason`. No stderr-human-parallel pattern — decisions are JSON-only.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

PreToolUse scripts default `permissionDecision=ask` with a trade summary; `deny` for hard policy violations; `allow` implied on no-op. PostToolUse journal hook is fail-open silent (exit 0 on parse failure). No top-level try/catch wrapping observed in script heads — each hook relies on Python exception propagation and `uv run --script` exit-code handling. No centralized emit-helper library.

### Silent fail-open (`exit 0` always, retry every hook)

`install-channel-deps.sh` follows the silent-fail-open pattern — never blocks the session, retries on every SessionStart sub-event.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Per CLAUDE.md, `${CLAUDE_PLUGIN_ROOT}` is cache (wiped on update), `${CLAUDE_PLUGIN_DATA}` is persistent. CLAUDE.md warns: "Using `${CLAUDE_PLUGIN_ROOT}` for persistent state — WRONG, it's the cache dir that gets wiped on plugin update. Use `${CLAUDE_PLUGIN_DATA}`."

## State persistence

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Five distinct persistent artifacts pinned to `${CLAUDE_PLUGIN_DATA}`: `journal.sqlite` (trade log, WAL), `prices.duckdb` (columnar OHLCV), `research.lancedb/` (vector embeddings), `models/` (PyTorch cache), `node_modules/` + `trading-alerts-package.json` (channel deps).

## Live monitoring

### Polling daemons via monitors.json

polymarket and coinbase-agent-kit ship `monitors.json` (trading-core does not — confirmed 404 on `plugins/trading-core/monitors/monitors.json`).

- polymarket (3): `price-watch` (YES-price moves on `POLYMARKET_WATCH_SLUGS`, 30s poll, alert on `POLYMARKET_PRICE_MOVE_ALERT_PCT` within `POLYMARKET_PRICE_MOVE_WINDOW_MIN`), `order-status` (poll user's open orders every 60s, notify on fills/partial fills/server-side cancels), `news-watch` (every 15min query RivalSearchMCP news_aggregation per watched market topic).
- coinbase-agent-kit (2): `balance-watch` (poll `WATCH_ADDRESSES` every 60s via Polygon/Ethereum/Base RPC, notify on native-balance delta > `BALANCE_ALERT_DELTA_USD`), `tx-status` (watch `${CLAUDE_PLUGIN_DATA}/pending-txs.txt`, poll receipts every 15s, notify on confirmation/revert).

`when: always` on all five monitors. No `on-skill-invoke:<skill>` variant. Schema fields used: `name`, `command`, `description`, `when`. Each monitor is a `.py` script with PEP 723 inline deps. trading-core ships ZERO monitors — venue-coupling is intentional; trading-core is venue-agnostic.

### Version-floor declaration absent

Neither plugin.json nor README declares a minimum Claude Code version for the monitors feature. README declares "Claude Code 2.1.80+" overall for the channel-preview dependency but doesn't tie it specifically to monitors (docs floor is v2.1.105+).

## Plugin-to-plugin coordination

### `dependencies` field absent

The plugin-to-plugin `dependencies` schema (v2.1.110+) is not used anywhere. trading-core is the shared math layer that polymarket + coinbase scripts "consume" at the file-read / subprocess layer, but no `plugin.json` declares another plugin as a dependency.

### Implicit prose-only dependency

README architecture diagram and CLAUDE.md describe trading-core as "shared quant layer the other plugins consume," but the coupling is documentation-only. CLAUDE.md tells contributors to "Consume trading-core's math + journal from your scripts (don't re-implement Kelly)" without wiring the `dependencies` field. Users installing polymarket without trading-core would get broken scripts; nothing in manifest-land warns them.

## Testing

### No tests

No `tests/` directory anywhere in the tree. No test framework. No separate dev deps; every runtime script pins its own deps via PEP 723.

### Author-time validator agents instead of automated tests

Validation posture leans entirely on the vendored `plugin-dev` toolkit's `plugin-validator` and `skill-reviewer` agents invoked manually during authoring sessions (documented in CLAUDE.md Step 4). Repo-level `.claude/settings.json` blocks `git commit --no-verify` and `git push --force`.

## CI workflow shape

### No CI

`gh api repos/damionrashford/trader-os/contents/.github` returns 404 — no `.github/` directory of any kind. No automated gate on push.

## Marketplace validation

### Manual validator-agent invocation

CLAUDE.md documents manual validation through `plugin-validator` and `skill-reviewer` agents from the vendored `plugin-dev` toolkit (Anthropic's official suite, vendored at `.claude/plugins/plugin-dev/agents/plugin-validator.md`). Runs interactively inside a Claude Code session. Frontmatter validation handled by `skill-reviewer`. Hooks.json validation included in `plugin-validator`. Trigger is manual — contributor runs after any component change per CLAUDE.md Step 4.

## Release automation

### No release automation / manual

CLAUDE.md says "Releases via GitHub Releases tagged `v<SEMVER>`" but it's a manual process; no workflow automates it and no releases have been cut. Per-plugin `CHANGELOG.md` exists at `plugins/<name>/CHANGELOG.md` in Keep-a-Changelog-lite format (date-prefixed version heading, `### Added` section, narrative body). No automation consumes them.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` (17606 bytes) — architecture diagram, FAQ (six collapsibles), use cases, schema.org JSON-LD block for LLM/search indexing, badges. Repo-root `CLAUDE.md` (10701 bytes) — repo layout, vendored dev toolkits, mandatory pipeline for plugin work (6 steps), hard rules (script conventions, plugin-agent frontmatter rules, prohibited patterns), version management, git workflow, pitfalls. No `architecture.md`. No per-plugin `CLAUDE.md`. Per-plugin `README.md` present on all three (`plugins/polymarket/README.md`, `plugins/coinbase-agent-kit/README.md`, `plugins/trading-core/README.md`). Each leads with "Default main-thread agent" section explaining the router pattern.

### Free-form CHANGELOG variants

Per-plugin `CHANGELOG.md` (not at repo root) follows Keep-a-Changelog-lite — `## [VERSION] — YYYY-MM-DD` heading, `### Added` subsection, narrative bullet lists. First-release entries only.

### Schema.org JSON-LD as LLM-indexer surface

Last visible element of `README.md` is a `<script type="application/ml+json">` block with `@type: SoftwareApplication`. Comment: "Machine-readable metadata for LLM + search indexers (Perplexity / ChatGPT / Claude / Google AI Overviews)."

### Badges and status indicators

README has Shields.io badges for license, Claude Code, Python, MCP, LinkedIn, and four dynamic-status badges (stars/forks/issues/last-commit).

## License declaration

### Single repo-level license

LICENSE present at repo root (MIT, SPDX `MIT`, 1074 bytes).

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`. README has a "Contributing" H2 inline; sensitive-file patterns are handled in `.claude/settings.json` deny rules rather than a SECURITY.md.

## Cross-platform discipline

### POSIX-only with no Windows story

nix-only bin scripts. No `.cmd` / `.ps1` siblings. Shebang uses `env -S` (needs GNU-compatible coreutils); `bash`-only install hook.

## Permission and contributor governance

### Plugin-root settings.json — agent pointer only

Every distributed plugin has a `settings.json` containing `{"agent": "<router-name>"}`. Three routers: `polymarket`, `coinbase`, `trading`. CLAUDE.md notes only `agent` and `subagentStatusLine` are supported keys; unknown keys silently ignored. Convention: point `agent` at a broad router (not a narrow specialist).

### Repo-root .claude/settings.json — contributor-only permission matrix

`.claude/settings.json` at repo root declares `defaultMode: "acceptEdits"`, ~100-entry allow/ask/deny permission matrix, and secret-file deny rules (`Read/Edit/Write` against `.env*`, `credentials*`, `*.pem`, `*private*key*`, `wallet.json`, `cdp_api_key.json`). Distinct from plugin-root `settings.json` which only carries `agent:`. Repo-root file governs contributor sessions; plugin-root files govern end-user sessions.

### Vendored contributor toolkit as sibling marketplace

`.claude/plugins/.claude-plugin/marketplace.json` hosts a separate marketplace (`trader-os-local`) with two plugins (`plugin-dev`, `claude-code-setup`) vendored from Anthropic's official suite. Contributors activate via `/plugin marketplace add ${CLAUDE_PROJECT_DIR}/.claude/plugins`. Repo invariant: "`.claude/` is contributor-only and never shipped to end users."

## Novel and cross-cutting concerns

### MCP "channel" as inbound event bus

trading-core ships an MCP-channels-as-inbound-event-bus pattern (research-preview Claude Code feature gated to v2.1.80+ and `claude.ai` login, not API-key auth). The channel server (Bun/TypeScript at `channels/trading-alerts/server.ts`) declares `claude/channel` capability, exposes HMAC-gated webhook routes (`/tradingview`, `/polymarket/fill`, `/polymarket/resolve`, `/cdp`, `/commerce`, `/custom?kind=...`), each converted to `<channel source="trading-alerts" type="..." ...>...</channel>` context tags inside the running Claude session. Distinct primitive from `monitors.json` (outbound stdout lines) and from normal MCP tool servers (stateful request/response).

## Cross-role tools

### `${CLAUDE_PLUGIN_ROOT}` env var

Bin scripts resolve plugin root via `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback. Per CLAUDE.md, `${CLAUDE_PLUGIN_ROOT}` is the cache directory.

### `${CLAUDE_PLUGIN_DATA}`

Five persistent artifacts pinned to `${CLAUDE_PLUGIN_DATA}` (journal.sqlite, prices.duckdb, research.lancedb/, models/, node_modules/+trading-alerts-package.json).

### Python (stdlib + pip + uv)

Python (via `uv run --script` PEP 723) is the dominant runtime — every `.py` hook, monitor, bin, and skill script. `httpx==0.27.2` is the most-pinned external dep.
