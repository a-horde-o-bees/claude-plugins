# damionrashford/trader-os

## Identification

- **URL**: https://github.com/damionrashford/trader-os
- **Stars**: 1
- **Last commit date**: 2026-04-18 (pushed_at 2026-04-18T08:21:52Z)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: dep-management + bin-wrapper (both, observed in all three distributed plugins)
- **One-line purpose**: "AI trading plugin marketplace for Claude Code. Polymarket prediction markets, Coinbase AgentKit, quant strategies + backtesting." (from README opening)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root. A secondary marketplace exists at `.claude/plugins/.claude-plugin/marketplace.json` for the vendored dev toolkits (`plugin-dev` + `claude-code-setup`), but that is a contributor-only surface explicitly scoped to `${CLAUDE_PROJECT_DIR}/.claude/plugins` per CLAUDE.md — not part of the published marketplace.
- **Marketplace-level metadata**: `metadata.{description, version, license}` wrapper. `name` and `owner` are top-level siblings; `description`/`version`/`license` live inside `metadata`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: category + tags on every plugin entry. No `keywords` field at marketplace-entry level (keywords live inside each plugin.json). Categories used: `trading`, `web3`, `quant` (one each — no reuse).
- **`$schema`**: absent on `marketplace.json`. Present on `.claude/settings.json` (`https://json.schemastore.org/claude-code-settings.json`) — different file.
- **Reserved-name collision**: no. Marketplace name is `trader-os`; plugin names are `polymarket-plugin`, `coinbase-agent-kit`, `trading-core`.
- **Pitfalls observed**: marketplace-entry `version` fields (all `0.1.0`) drift from marketplace `metadata.version` (`0.4.0`) — nothing validates the two; authors treat them as independent version streams.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`./plugins/polymarket`, `./plugins/coinbase-agent-kit`, `./plugins/trading-core`). No github/url/git-subdir/npm sources.
- **`strict` field**: default (implicit true) — no explicit `strict` on any entry.
- **`skills` override on marketplace entry**: absent (no carving — full plugin trees ship as-is).
- **Version authority**: both — marketplace entry `version` is duplicated in each plugin's `plugin.json`. CLAUDE.md calls out the invariant explicitly: "Per-plugin entry `version` in marketplace.json must match each plugin's own `plugin.json`." Drift is possible but documented as a hand-maintained contract, not automated.
- **Pitfalls observed**: hand-maintained dual-version discipline with no CI gate — CLAUDE.md mandates matching but nothing enforces it. Also: marketplace-root `metadata.version` (`0.4.0`) is decoupled from the per-plugin `0.1.0` streams, creating a three-way version space (marketplace meta / marketplace-entry / plugin.json) where only the latter two are supposed to match.

## 3. Channel distribution

- **Channel mechanism**: no split. Single `main` branch; users pin by marketplace ref only (`/plugin marketplace add damionrashford/trader-os`). No stable/latest split.
- **Channel-pinning artifacts**: absent. The word "channel" in this repo refers exclusively to the MCP channel feature (`channels/trading-alerts/`), not a distribution channel.
- **Pitfalls observed**: none — intentional single-channel distribution. README directs users to run `/plugin marketplace update trader-os` manually since "third-party marketplaces don't auto-update."

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: none. `gh api .../tags` returns `[]`.
- **Release branching**: none.
- **Pre-release suffixes**: not applicable — no releases exist.
- **Dev-counter scheme**: absent. Versions are static hand-set values (`0.1.0` per plugin, `0.4.0` at marketplace).
- **Pre-commit version bump**: no — no `.githooks/`, no `.pre-commit-config.yaml`, no husky config observed.
- **Pitfalls observed**: CLAUDE.md documents "Tag git releases `v<MAJOR>.<MINOR>.<PATCH>`" and "Releases via GitHub Releases tagged `v<SEMVER>`" but at 2026-04-18 the repo has zero tags and zero releases — release process is documented but untested in practice.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery. No explicit component paths in any `plugin.json` — all three rely on Claude Code's default component discovery under `skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `monitors/monitors.json`, `bin/`, `.mcp.json`, `channels/`.
- **Components observed**:

| Plugin | skills | commands | agents | hooks | .mcp.json | monitors | bin | channels | output-styles |
|--------|--------|----------|--------|-------|-----------|----------|-----|----------|---------------|
| polymarket-plugin | 8 | no (empty `.gitkeep` only) | 5 (polymarket router + trader + researcher + risk + executor) | PreToolUse(Bash) + SessionStart | no | 3 (price-watch, order-status, news-watch) | polymkt | no | no |
| coinbase-agent-kit | 10 | no | 5 (coinbase router + trader + wallet-ops + payment-ops + agent-builder) | PreToolUse(Bash) + SessionStart | no | 2 (balance-watch, tx-status) | cbkit | no | no |
| trading-core | 12 | no | 5 (trading router + quant-analyst + backtester + risk-officer + strategy-researcher) | SessionStart×2 + PostToolUse(Bash) + SessionEnd | yes (`.mcp.json` referencing `channels/trading-alerts/server.ts`) | no | tcore | yes (trading-alerts, Bun/TypeScript) | no |

- **Agent frontmatter fields used**: `name`, `description`, `model`, `effort`, `maxTurns`, `skills`, `memory`, `tools`, `isolation`. Sample: `quant-analyst` uses `model: inherit`, `effort: high`, `maxTurns: 20`, `skills: [quant-math, position-sizing, bayesian-updating, time-series]`, `memory: project`. `backtester` and `strategy-researcher` add `isolation: worktree`. `maxTurns` ranges 15-40 across agents; `effort` values observed: `medium` (routers), `high` (specialists).
- **Agent tools syntax**: permission-rule syntax. Observed forms: `Read`, `Grep`, `Glob`, `Bash(uv run *)`, `Bash(jq *)`, `Bash(tcore *)`, `Bash(polymkt *)`, `Bash(cbkit *)`. Mix of bare tool names and Bash-with-glob patterns in the same list. CLAUDE.md explicitly notes which frontmatter fields are supported vs ignored (supported: `name description model effort maxTurns tools disallowedTools skills memory background isolation`; unsupported: `color hooks mcpServers permissionMode`).
- **Pitfalls observed**: `commands/.gitkeep` empty directories carried forward from plugin-dev scaffolding — CLAUDE.md flags this as a known pitfall ("Leaving scaffolding placeholder files after plugin-dev scaffolding — delete once real files exist") but it persists in polymarket. `agents/.gitkeep`, `bin/.gitkeep`, `hooks/scripts/.gitkeep`, `monitors/scripts/.gitkeep`, `skills/.gitkeep` also present in polymarket.

## 6. Dependency installation

- **Applicable**: yes — two parallel dep stories coexist. (a) Python scripts via PEP 723 `uv run --script` ephemeral runs (no plugin-managed venv). (b) Node `node_modules` for the MCP channel, installed via a `diff -q`-gated SessionStart shell hook.
- **Dep manifest format**: mixed per language. Python deps inline in PEP 723 script headers (e.g. `httpx==0.27.2` inside `# /// script` block). Node deps in `channels/trading-alerts/package.json` (single dep: `@modelcontextprotocol/sdk ^1.0.0`). No `requirements.txt`, no `pyproject.toml`.
- **Install location**: `${CLAUDE_PLUGIN_DATA}/node_modules` for Node. Python has no install location — `uv run --script` manages an ephemeral per-script env out of view. Per CLAUDE.md the convention is that `${CLAUDE_PLUGIN_ROOT}` is cache (wiped on update) and `${CLAUDE_PLUGIN_DATA}` is persistent.
- **Install script location**: `plugins/trading-core/hooks/scripts/install-channel-deps.sh` (registered in `hooks/hooks.json` as a SessionStart `command`-type hook with no matcher).
- **Change detection**: `diff -q` between source `channels/trading-alerts/package.json` and cached copy at `${CLAUDE_PLUGIN_DATA}/trading-alerts-package.json`. Only reinstalls when manifests differ or cache is missing.
- **Retry-next-session invariant**: yes but inverse of docs pattern — the script copies source `package.json` to cache AFTER a successful install (`if [[ -d "${NODE_MODULES}" ]]; then cp "${SRC_PKG}" "${CACHED_PKG}"`), and on failure `rm -f "${DATA}/package.json"` to clean up the intermediate write. The cached-manifest stamp is only written on verified success, so next session re-diffs and retries. This functionally satisfies the docs-prescribed "retry on next session" invariant by other means (stamp-on-success instead of rm-on-failure).
- **Failure signaling**: silent-on-failure. `set -euo pipefail` at top, then `|| true` on the actual install command (`bun install --silent 2>/dev/null || true`), plus an early-exit path when neither `bun` nor `npm` is available (`exit 0`). Downstream `session-start-env.py` surfaces channel readiness to the user; the install hook itself never complains. No JSON `systemMessage`, no `continue: false`.
- **Runtime variant**: Python uv (PEP 723 inline-dep scripts via `uv run --script`) + Node bun with npm fallback. bun/npm choice is runtime-probed: `command -v bun >/dev/null 2>&1; then ... elif command -v npm >/dev/null 2>&1; then ...`.
- **Alternative approaches**: PEP 723 inline metadata is the dominant Python distribution mechanism — every `.py` hook / monitor / bin / skill script starts with `#!/usr/bin/env -S uv run --script` followed by a `# /// script` block declaring `requires-python` and exact-pinned `dependencies` (e.g. `httpx==0.27.2`). No pointer files, no `uvx` ad-hoc. The channel-deps Node install is the only persistent managed install.
- **Version-mismatch handling**: none explicit. `uv run --script` handles Python-version pinning transparently via its `requires-python` clause. No Node ABI tracking observed.
- **Pitfalls observed**: install hook cites the docs URL directly in a comment (`https://code.claude.com/docs/en/plugin-reference#persistent-data-directory`), showing the author derived the pattern from the docs-worked-example but chose stamp-on-success over rm-on-failure — functionally equivalent but structurally a different idiom. Also: the install is wrapped in a sub-shell `( cd "${DATA}" && ... )` which works but conflicts with the project-local rule "No `cd` in hooks" (project-level, not observed in this external repo — but worth flagging as an axis of variation).

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes. All three plugins ship a PATH-level CLI: `polymkt` (polymarket), `cbkit` (coinbase-agent-kit), `tcore` (trading-core).
- **`bin/` files**:
  - `plugins/polymarket/bin/polymkt` — dispatcher to `skills/*/scripts/*.py`; `auth/markets/clob/positions/stream/onchain/research/strategy` subcommands plus `status` and `watchlist` shortcuts.
  - `plugins/coinbase-agent-kit/bin/cbkit` — dispatcher to `skills/*/scripts/*.py`; `auth/accounts/tx/webhooks/commerce/kit` plus `status` and `providers` shortcuts.
  - `plugins/trading-core/bin/tcore` — dispatcher to `skills/*/scripts/*.py`; `math/size/mm/bt/store` plus `dirs` and `journal` shortcuts.
- **Shebang convention**: PEP 723 `#!/usr/bin/env -S uv run --script` on all three bin files. Same shebang on every hook and monitor `.py` script. Only non-Python shebang is `install-channel-deps.sh` with `#!/usr/bin/env bash`.
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback. Observed pattern in tcore: `e = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip(); if e: return Path(e); return Path(__file__).resolve().parent.parent`. Same pattern in polymkt and cbkit.
- **Venv handling (Python)**: `uv run --script` ephemeral — no persistent venv, no `source activate`, no pointer file. Each script invocation creates/reuses uv's own cached ephemeral env keyed by its inline-dep hash.
- **Platform support**: nix-only. No `.cmd` / `.ps1` siblings. Shebang uses `env -S` which needs GNU-compatible coreutils; `bash`-only install hook.
- **Permissions**: 100755 (executable) on every bin script, hook script, and monitor script. Confirmed via git tree mode inspection.
- **SessionStart relationship**: static — the bin wrappers are pre-built shipped scripts, not hook-populated. SessionStart hooks in trading-core install Node deps for the channel (separate concern); SessionStart hooks in polymarket + coinbase only report env readiness. No bin file is written or mutated by any hook.
- **Pitfalls observed**: bin scripts declare `dependencies = []` in their PEP 723 block (tcore, cbkit) or a single dep (polymkt declares `httpx==0.27.2`), but then `subprocess`-dispatch to skill scripts that declare their own inline deps. This means each skill invocation materializes a fresh `uv run --script` subprocess rather than sharing the parent bin's env — deliberate separation per skill but a cold-start cost on every subcommand.

## 8. User configuration

- **`userConfig` present**: yes on all three plugins.
- **Field count**: 15 (polymarket), 16 (coinbase-agent-kit), 18 (trading-core). CLAUDE.md summary sample said "17" for trading-core — actual count is 18, indicating the summary was approximate.
- **`sensitive: true` usage**: incorrect / anti-pattern on all three plugins. Descriptions explicitly flag secrets (polymarket: `POLYMARKET_PRIVATE_KEY` description says "SECRET — treat like a password"; coinbase: `CDP_API_KEY_SECRET`, `CDP_WALLET_SECRET`, `COINBASE_COMMERCE_WEBHOOK_SECRET` all say "SECRET" in text; trading-core: four `*_SECRET` fields end their description with the word "Secret."), but NO field anywhere uses the `sensitive: true` flag. README acknowledges secrets "stay in your local Claude Code config; never committed, never written to disk" via `/plugin config set` — relies on the storage backend entirely, not the schema flag. Per the docs-plugins-reference context, `sensitive: true` is the prescribed mechanism to signal a field as a secret for keychain routing.
- **Schema richness**: typed (every field has `type: "string"` and `default: ""` or a concrete default). No enums, no numeric types — numeric-looking values (`POLYMARKET_MAX_ORDER_USDC: "100"`, `TRADING_CORE_KELLY_FRACTION: "0.25"`) are stringly-typed and parsed downstream.
- **Reference in config substitution**: `${user_config.KEY}` observed in `trading-core/.mcp.json` for all five channel-related secrets (`TRADING_ALERTS_PORT`, `TRADING_ALERTS_SECRET`, `CDP_WEBHOOK_SECRET`, `COINBASE_COMMERCE_WEBHOOK_SECRET`, `POLYMARKET_WEBHOOK_SECRET`) piped into the MCP server's `env` block. Hook/monitor scripts read the same keys via `os.environ.get(...)` — Claude Code's plugin layer populates env from userConfig before spawning scripts. No `CLAUDE_PLUGIN_OPTION_<KEY>` pattern observed.
- **Pitfalls observed**: the "description says SECRET, flag absent" anti-pattern is repeated three times across three plugins — a systematic authoring gap rather than a one-off. All seven secret-class fields (`POLYMARKET_PRIVATE_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`, `CDP_API_KEY_SECRET`, `CDP_WALLET_SECRET`, `COINBASE_COMMERCE_WEBHOOK_SECRET`, `TRADING_ALERTS_SECRET` + `CDP_WEBHOOK_SECRET` + `POLYMARKET_WEBHOOK_SECRET`) lack the flag. `CDP_API_KEY_ID` (a key name, not a secret) correctly lacks the flag, but the distinction isn't signalled mechanically.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 2 distinct scripts, both with matcher `"Bash"`:
  - polymarket `pre-trade-validate.py` — parses clob.py `place|market|batch|cancel-all` subcommands out of Bash argv; checks notional against `POLYMARKET_MAX_ORDER_USDC`; requires `--yes-really` on `cancel-all`; enforces `--dry-run` vs `--live` based on `POLYMARKET_DRY_RUN_DEFAULT`.
  - coinbase `pre-tx-validate.py` — analogous guard on `cbkit tx` / `kit.py` transactions; enforces `DRY_RUN_DEFAULT`, checks `ALLOWED_NETWORKS` allow-list, estimates `MAX_TX_VALUE_USD`.
- **PostToolUse hooks**: 1 — trading-core `post-trade-journal.py` on matcher `"Bash"`. Sniffs placements across venues (polymkt / cdp-tx / cbkit) and appends to SQLite journal. Runs after tool success; silent on non-trade Bash commands.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON with `hookSpecificOutput.permissionDecision` (`ask` / `deny` / implied `allow` on no-op). Reason lines in `permissionDecisionReason`. No stderr-human-parallel pattern observed — decisions are JSON-only.
- **Failure posture**: mixed per-hook but biased ask-first. Both PreToolUse scripts default `permissionDecision=ask` with a trade summary so the user sees the intent before approval; `deny` reserved for hard policy violations (cancel-all without `--yes-really`, network not in allow-list). PostToolUse journal hook is fail-open silent (exit 0 on parse failure).
- **Top-level try/catch wrapping**: not observed in the script heads inspected — each hook relies on normal Python exception propagation and `uv run --script` exit-code handling. No centralized emit-helper library.
- **Pitfalls observed**: no hook-level DB locking discipline around the shared SQLite journal visible in the fetched head lines — `PostToolUse` fires on every Bash in parallel potentially and writes to the same `journal.sqlite`. The trading-storage skill is called out as using "SQLite WAL" mode which mitigates this but isn't verified in the hook script itself.

## 10. Session context loading

- **SessionStart used for context**: yes — all three plugins have a `session-start-env.py` that prints a "session ready-check" markdown block to stdout (shown to the user and also ingested as context). Contents: which env vars are set / missing, data-dir status, channel-runtime status. In addition, trading-core SessionStart also runs `install-channel-deps.sh` (see §6) — that script stays silent and does not inject context.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: not observed in the head lines fetched — session-start-env scripts appear to print markdown directly to stdout rather than wrap it in an `additionalContext` JSON payload. Needs full-file read to confirm; marking "not applicable/unclear" for this field.
- **SessionStart matcher**: none — all three SessionStart entries in all three `hooks.json` files omit the matcher field, so they fire on every sub-event (startup, resume, clear, compact).
- **Pitfalls observed**: no matcher narrowing means the readiness-report runs on every compact and clear, not just session startup — users doing heavy compaction see the block repeat. Also `install-channel-deps.sh` re-runs its `diff -q` on every compact; idempotent and cheap when the manifest hasn't changed, but a non-trivial disk op.

## 11. Live monitoring and notifications

- **`monitors.json` present**: yes on polymarket and coinbase-agent-kit; no on trading-core (confirmed 404 on `plugins/trading-core/monitors/monitors.json`; no `monitors/` directory in trading-core's tree).
- **Monitor count + purposes**:
  - polymarket (3): `price-watch` (YES-price moves on `POLYMARKET_WATCH_SLUGS`, 30s poll, alert on `POLYMARKET_PRICE_MOVE_ALERT_PCT` within `POLYMARKET_PRICE_MOVE_WINDOW_MIN`), `order-status` (poll user's open orders every 60s, notify on fills / partial fills / server-side cancels), `news-watch` (every 15min query RivalSearchMCP news_aggregation per watched market topic).
  - coinbase-agent-kit (2): `balance-watch` (poll `WATCH_ADDRESSES` every 60s via Polygon/Ethereum/Base RPC, notify on native-balance delta > `BALANCE_ALERT_DELTA_USD`), `tx-status` (watch `${CLAUDE_PLUGIN_DATA}/pending-txs.txt`, poll receipts every 15s, notify on confirmation/revert).
- **`when` values used**: `always` on all five monitors across both plugins. No `on-skill-invoke:<skill>` observed.
- **Version-floor declaration**: absent — neither plugin.json nor README declares a minimum Claude Code version for the monitors feature. README declares "Claude Code 2.1.80+" overall for the channel-preview dependency but doesn't tie it specifically to monitors (docs floor is v2.1.105+ per the context index).
- **Pitfalls observed**: "the monitors reference" — five distinct monitors across two venue plugins, each a `.py` script with PEP 723 inline deps emitting one line per event. Schema matches what a docs-compliant monitor looks like: `name` / `command` / `description` / `when`. No `on-skill-invoke` variant used; all are polling daemons launched at session start. The fact that trading-core (the heaviest plugin by other metrics) ships ZERO monitors is intentional — monitors are venue-coupled; trading-core is venue-agnostic.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — the plugin-to-plugin `dependencies` schema (v2.1.110+) is NOT used anywhere. trading-core is the shared math layer that polymarket + coinbase scripts "consume" at the file-read / subprocess layer, but no `plugin.json` declares another plugin as a dependency.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: no (no tags exist at all — see §4).
- **Pitfalls observed**: the README architecture diagram and CLAUDE.md both describe trading-core as "shared quant layer the other plugins consume," but that coupling is documentation-only, not wired into the dependency schema. Users who install polymarket without also installing trading-core would get broken scripts, but nothing in manifest-land warns them — CLAUDE.md tells contributors to "Consume trading-core's math + journal from your scripts (don't re-implement Kelly)" but doesn't wire the `dependencies` field. This is a case of schema-supported enforcement being deliberately skipped.

## 13. Testing and CI

- **Test framework**: none.
- **Tests location**: not applicable — no `tests/` directory anywhere in the tree.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable — no separate dev deps; every runtime script pins its own deps via PEP 723.
- **CI present**: no — `gh api repos/damionrashford/trader-os/contents/.github` returns 404.
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: not applicable.
- **Pitfalls observed**: the validation posture leans entirely on the vendored `plugin-dev` toolkit's `plugin-validator` and `skill-reviewer` agents invoked manually during authoring sessions (documented in CLAUDE.md Step 4). No automated gate on push.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — CLAUDE.md says "Releases via GitHub Releases tagged `v<SEMVER>`" but this is a manual process; no workflow automates it and no releases have been cut.
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: not applicable.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: per-plugin `CHANGELOG.md` exists at `plugins/<name>/CHANGELOG.md` in Keep-a-Changelog-lite format (date-prefixed version heading, `### Added` section, narrative body). No automation consumes them.
- **Pitfalls observed**: documented-but-unbuilt release pipeline. The repo is one week old (first commit 2026-04-18) and may simply not have reached release cadence yet.

## 15. Marketplace validation

- **Validation workflow present**: no CI workflow. CLAUDE.md documents manual validation through `plugin-validator` and `skill-reviewer` agents from the vendored `plugin-dev` toolkit.
- **Validator**: plugin-dev's `plugin-validator` agent (Anthropic's official suite, vendored at `.claude/plugins/plugin-dev/agents/plugin-validator.md`). Runs interactively inside a Claude Code session. Not a standalone CLI validator; not `bun+zod`, not `claude plugin validate` (though the latter may exist — not invoked here).
- **Trigger**: manual — contributor runs the agent after any component change per CLAUDE.md Step 4.
- **Frontmatter validation**: yes, by the `skill-reviewer` agent (also vendored).
- **Hooks.json validation**: included in `plugin-validator` per the agent's description (fetched separately — not reviewed in full here).
- **Pitfalls observed**: no pre-push gate; validation correctness depends on the contributor remembering to invoke the agents. Repo-level `.claude/settings.json` blocks `git commit --no-verify` and `git push --force`, but there's no commit hook that invokes the validators — the blocks prevent the contributor from BYPASSING hooks, but no hook exists to bypass.

## 16. Documentation

- **`README.md` at repo root**: present, 17606 bytes. Heavy — includes architecture diagram, FAQ (six collapsibles), use cases, schema.org JSON-LD block for LLM/search indexing, badges.
- **Owner profile README at `github.com/damionrashford/damionrashford`**: present (~59 lines, resume-tier portfolio — project table + tech badges)
- **`README.md` per plugin**: present on all three (`plugins/polymarket/README.md`, `plugins/coinbase-agent-kit/README.md`, `plugins/trading-core/README.md`). Each leads with a "Default main-thread agent" section explaining the router pattern.
- **`CHANGELOG.md`**: present per plugin (not at repo root). Format: Keep-a-Changelog-lite — `## [VERSION] — YYYY-MM-DD` heading, `### Added` subsection, narrative bullet lists. First-release entries only.
- **`architecture.md`**: absent. Architecture content lives in the root `README.md` (ASCII diagram) and `CLAUDE.md` (layout + invariants).
- **`CLAUDE.md`**: at repo root (10701 bytes). No per-plugin `CLAUDE.md`. Documents: repo layout, vendored dev toolkits, mandatory pipeline for plugin work (6 steps), hard rules when authoring (script conventions, plugin-agent frontmatter rules, prohibited patterns), version management, git workflow, pitfalls.
- **Community health files**: none observed — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md`.
- **LICENSE**: present, MIT (SPDX `MIT`, 1074 bytes).
- **Badges / status indicators**: observed — README has Shields.io badges for license, Claude Code, Python, MCP, LinkedIn, and four dynamic-status badges (stars / forks / issues / last-commit). Plus a schema.org `SoftwareApplication` JSON-LD block explicitly targeted at "LLM + search indexers (Perplexity / ChatGPT / Claude / Google AI Overviews)."
- **Pitfalls observed**: CONTRIBUTING and SECURITY files are referenced-but-missing — README has a "Contributing" H2 inline, and sensitive-file patterns are handled in `.claude/settings.json` deny rules rather than a SECURITY.md.

## 17. Novel axes

- **Vendored dev-toolkit marketplace as a sibling surface.** `.claude/plugins/.claude-plugin/marketplace.json` hosts a separate marketplace (`trader-os-local`) with two plugins (`plugin-dev`, `claude-code-setup`) vendored from Anthropic's official suite. Users activate it with `/plugin marketplace add ${CLAUDE_PROJECT_DIR}/.claude/plugins`. This is a deliberate contributor-only surface — invariant in CLAUDE.md is "`.claude/` is contributor-only and never shipped to end users" — but it reuses the marketplace.json mechanism as a dev-toolkit bootstrap, not just plugin distribution.
- **Plugin-root `settings.json` with `agent:` pointing at a router.** Every distributed plugin has a `settings.json` containing `{"agent": "<router-name>"}`. Comment from CLAUDE.md: "Only two keys supported: `agent` (activates a custom agent as the main thread), `subagentStatusLine`. Unknown keys silently ignored. Use `agent` to point at a BROAD ROUTER agent (not a narrow specialist) so the plugin feels natural when enabled." The same router agent also appears in the plugin's `agents/` directory. Three routers observed: `polymarket`, `coinbase`, `trading`. The two-key restriction on plugin-root settings is repo-policy-sourced and also appears in Anthropic docs.
- **Agent frontmatter support/unsupport matrix documented in contributor docs.** CLAUDE.md explicitly lists `color`, `hooks`, `mcpServers`, `permissionMode` as SILENTLY-IGNORED fields. Most repos don't document what they are deliberately NOT using; this repo enshrines the constraint.
- **MCP channel (research-preview feature) ships in production.** `trading-core/.mcp.json` + `channels/trading-alerts/` is a one-way Bun/TypeScript MCP server gated by HMAC, declaring `claude/channel` capability. Per README: "Channels are in research preview and require Claude Code 2.1.80+ with claude.ai login (not API-key auth). During the preview, activate with `claude --dangerously-load-development-channels plugin:trading-core@trader-os`." The repo uses MCP-channels-as-an-inbound-event-bus pattern — five inbound webhook routes (`/tradingview`, `/polymarket/fill`, `/polymarket/resolve`, `/cdp`, `/commerce`, `/custom?kind=...`), each converted to `<channel source="trading-alerts" type="..." ...>...</channel>` context tags inside the Claude session. This is a distinct primitive from `monitors.json` (outbound stdout lines) and from normal MCP tool servers (stateful request/response).
- **`.claude/settings.json` at repo root as permission governance.** The file `.claude/settings.json` at repo root declares `defaultMode: "acceptEdits"`, a ~100-entry allow/ask/deny permission matrix, and secret-file deny rules (`Read/Edit/Write` against `.env*`, `credentials*`, `*.pem`, `*private*key*`, `wallet.json`, `cdp_api_key.json`). Distinct from plugin-root `settings.json` which only carries `agent:`. The repo-root file governs contributor Claude Code sessions against this repo; the plugin-root files govern end-user sessions with the plugin enabled.
- **PEP 723 inline metadata as the Python distribution primitive.** Every `.py` file (bin dispatchers, skills scripts, hooks, monitors) starts with `#!/usr/bin/env -S uv run --script` + a `# /// script` block pinning `requires-python` and exact-version deps. No `requirements.txt`, no `pyproject.toml`, no `__init__.py`. This is a plugin-wide commitment — one pattern, ~20+ files — contrasting the `requirements.txt`+plugin-venv approach used by other marketplaces.
- **`${CLAUDE_PLUGIN_DATA}` as the persistence contract.** Five distinct persistent artifacts pinned to `${CLAUDE_PLUGIN_DATA}`: `journal.sqlite` (trade log, WAL), `prices.duckdb` (columnar OHLCV), `research.lancedb/` (vector embeddings), `models/` (PyTorch cache), `node_modules/` + `trading-alerts-package.json` (channel deps). CLAUDE.md warns: "Using `${CLAUDE_PLUGIN_ROOT}` for persistent state — WRONG, it's the cache dir that gets wiped on plugin update. Use `${CLAUDE_PLUGIN_DATA}`." Repeated enforcement of the root/data split.
- **PostToolUse as an audit-trail primitive.** trading-core's `post-trade-journal.py` sniffs Bash commands across venues (polymkt / cdp-tx / cbkit) to auto-journal every real placement. It's not validating behavior (PreToolUse does that); it's recording it. PostToolUse as side-effect logging rather than gate.
- **Schema.org JSON-LD block embedded in README for LLM indexers.** Last visible element of README.md is a `<script type="application/ml+json">` block with `@type: SoftwareApplication`. Explicit comment: "Machine-readable metadata for LLM + search indexers (Perplexity / ChatGPT / Claude / Google AI Overviews)." README-as-LLM-metadata-surface is a novel distribution concern.
- **Three-tier version space.** marketplace `metadata.version` (`0.4.0`) vs marketplace-entry `version` (`0.1.0` each) vs plugin.json `version` (`0.1.0` each). Only the latter two are required to match per CLAUDE.md; the marketplace-root version evolves independently on its own cadence. Most repos collapse these to a single version line.
- **Router-plus-specialist agent topology with `memory: project`.** Every plugin ships one broad `medium`-effort router (20-turn budget) pointed at via `settings.json`, plus 4–5 specialist agents with `effort: high`, 15–40 turn budgets, narrow skill lists, and often `isolation: worktree`. All agents declare `memory: project`. `Bash(uv run *)` + `Bash(jq *)` are the two near-universal tool permissions; venue-specific agents add `Bash(polymkt *)` / `Bash(cbkit *)` / `Bash(tcore *)`. `model: inherit` on every agent (no hardcoded model selection).

## 18. Gaps

- **`hookSpecificOutput.additionalContext` usage in `session-start-env.py`.** Only head lines fetched; didn't confirm whether the readiness-report is emitted as raw stdout or wrapped in the `additionalContext` JSON envelope. Needs full-file read to resolve.
- **Exact output discipline of the pre-trade/pre-tx hooks on non-matching Bash commands.** Only heads fetched — whether the scripts silently exit 0 or emit a no-op JSON payload when the Bash command is not a trade/tx placement isn't confirmed. Resolvable by reading the full hook scripts.
- **Whether `post-trade-journal.py` takes any exclusive lock on the SQLite journal.** Partial read only; WAL mode is declared at the skill level (trading-storage) but the hook script's own connection handling isn't verified.
- **Whether `trading-storage`'s SQLite init creates the `journal.sqlite` schema defensively on first write.** Schema creation path not traced.
- **Whether the vendored `plugin-dev/agents/plugin-validator.md` actually validates marketplace.json or only individual plugin.json files.** Full agent body not read.
- **channels/trading-alerts/server.ts contents.** Only its `package.json` + `README.md` head fetched. The actual capability declaration (`claude/channel` advertising), HMAC verification code, and MCP-tool surface (or absence thereof — README says "NO reply tool, NO permission relay") is inferred from the README claim but not verified in source.
- **Whether `isolation: worktree` on `backtester` and `strategy-researcher` is a docs-prescribed frontmatter field or a repo-local convention.** Present in CLAUDE.md's "supported frontmatter" list but not cross-checked against the docs-plugins-reference context file within this task's budget.
- **Whether `memory: project` is a standard plugin-agent frontmatter field.** Used consistently across all agents here; its origin (docs vs custom extension) not verified.
- **The marketplace's relationship to Anthropic's own plugin suite at `.claude/plugins/`.** The vendored `plugin-dev` and `claude-code-setup` are noted as "from Anthropic's official plugin suite" but their upstream origin URLs aren't recorded. Resolvable by inspecting the vendored plugins' LICENSE and README metadata.
- **Whether any of the skill `scripts/*.py` actually execute without the venue's user-config set.** Runtime-verification gap; the session-start-env.py readiness reports indicate env-dependence but the graceful-degradation behavior of individual skill calls on partial config isn't traced.
