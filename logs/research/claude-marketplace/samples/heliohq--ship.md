# heliohq/ship

## Identification

- **URL**: https://github.com/heliohq/ship
- **Stars**: 42
- **Last commit date**: 2026-04-20 (pushed_at 2026-04-20T09:47:52Z)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: "An agentic development harness for Claude Code, Codex & Cursor: gated pipeline from spec to green checks." (from repo description / README opening)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, listing one plugin (`ship`) with `source: "./"` (self-hosted marketplace — repo is both marketplace and plugin).
- **Marketplace-level metadata**: top-level `name` + `description` + `owner` object (`{name, url}`). No `metadata` wrapper; no `version` at marketplace level.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: none at marketplace-entry level — the single entry has only `name`, `description`, `version`, `source`. `keywords` live in `plugin.json` (8 items: agent, coding, planning, qa, debugging, refactoring, orchestrator, workflows). No `category`, `tags` on either surface.
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: marketplace-entry `version: "1.9.0"` drifts from `plugin.json` `version: "0.1.6"` — two separate version axes for the same plugin. Commit log confirms they're maintained manually and alignment is intentional-but-separate ("align cursor plugin version to 0.1.1 to match claude plugin"; "bump version to 0.1.1 / 1.9.2"). Marketplace spec treats either as authoritative depending on consumer; drift is live.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`source: "./"`). Single entry, no aggregator.
- **`strict` field**: absent (default, implicit true).
- **`skills` override on marketplace entry**: absent. Skills are discovered from `skills/` via default layout (the `.cursor-plugin/plugin.json` variant explicitly declares `"skills": "./skills/"`, but the Claude `.claude-plugin/plugin.json` relies on default discovery).
- **Version authority**: both surfaces carry a version — `.claude-plugin/plugin.json` (`0.1.6`) and the marketplace entry (`1.9.0`). Observed drift. `.cursor-plugin/plugin.json` carries yet a third (`0.1.6`, aligned with Claude plugin.json).
- **Pitfalls observed**: three version strings for one plugin across two runtimes and one marketplace manifest — keeping them in sync is a manual discipline, already shown to drift (current tree has marketplace `1.9.0` vs plugin `0.1.6`).

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `/plugin install ship@heliohq` (README); no stable/latest channel artifacts.
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: none — this is a single-channel marketplace.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: none (`matching-refs/tags` returns empty; releases list empty).
- **Release branching**: none observed — feature branches (`fix/*`, `feat/*`, `refactor/*`, `codex/*`) merge to main via PR; `chore(plugin): bump 0.1.4 -> 0.1.5` commits on main are the release markers.
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent — version bumped manually in commits (e.g., "bump version to 0.1.2 for using-ship meta-skill injection").
- **Pre-commit version bump**: no automation observed (no `.github/`, no hook configs in-tree for this).
- **Pitfalls observed**: users consuming `@heliohq` get whatever is on `main` at resolution time — no tag-pinning to a reviewed release, no changelog, no release notes. Commit-based versioning only.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery for skills. `hooks` referenced by hooks.json at `hooks/hooks.json` (default lookup). `mcpServers` not declared in plugin.json — lives at repo-root `.mcp.json` (project-level MCP, not plugin-level). The Cursor variant explicitly sets `"skills": "./skills/"` and `"hooks": "./hooks/hooks-cursor.json"` — different path and different hook manifest.
- **Components observed**: skills yes (14 top-level skill dirs including a `shared/` references dir); commands no; agents no; hooks yes (`hooks/hooks.json`); .mcp.json yes at repo root (not plugin-scoped); .lsp.json no; monitors no; bin yes (`bin/ship-plugin-root`); output-styles no.
- **Agent frontmatter fields used**: not applicable (no agents/).
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: `.mcp.json` at repo root (registers a `codex` MCP server invoking `codex mcp-server`) is not the plugin's MCP — it's a project-level MCP file that happens to be committed. Consumers installing via `/plugin install` don't get this wired; it's for developers of `ship` itself. Two hook manifests (`hooks.json` vs `hooks-cursor.json`) reflect Claude-vs-Cursor schema divergence: Claude uses nested `"hooks": [{hooks:[{type, command}]}]`, Cursor uses flat `"sessionStart": [{command: "./hooks/session-start"}]` — the Cursor manifest invokes a separate bin-style shim (`hooks/session-start`) that execs the shared `scripts/session-start.sh`.

## 6. Dependency installation

- **Applicable**: no — pure shell/markdown plugin. No Python, Node, or other language runtime ships with the plugin. The shell scripts assume `bash`, `jq`, `git`, `python3` (optional fallback in one hook) are on `$PATH`; runtime dependencies (codex CLI, agent-browser, gh, claude, etc.) are user-installed and discovered at runtime.
- **Dep manifest format**: none.
- **Install location**: not applicable.
- **Install script location**: not applicable.
- **Change detection**: not applicable.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: not applicable.
- **Runtime variant**: no plugin-managed runtime; the Codex MCP server is ad-hoc via `codex mcp-server` (user-installed).
- **Alternative approaches**: `scripts/path-bootstrap.sh` pattern — augments PATH with common user bin dirs (`$HOME/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `$HOME/.local/bin`, `$HOME/go/bin`) at hook/skill entry so the minimal PATH that Claude Code propagates still resolves user-installed CLIs. Every hook script sources this bootstrap.
- **Version-mismatch handling**: none — runtime deps are detected (`command -v <tool>`), not version-pinned.
- **Pitfalls observed**: because Ship's hooks depend on `jq` (required — the stop-gate and phase-guardrail produce their JSON output via `jq -n`) but jq isn't auto-installed, a user on a minimal system can silently exit with degraded behavior. One hook (`session-start.sh`) has `python3` fallback for JSON escaping; phase-guardrail and stop-gate do not.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — single bin file used as a *discovery utility*, not a user-invoked CLI.
- **`bin/` files**: `ship-plugin-root` (bash, 355 bytes) — resolves and prints the ship plugin root directory. Explicitly exists so skills can locate the plugin when `$CLAUDE_PLUGIN_ROOT` isn't in scope (it's set only in hook contexts, not in skill-invocation contexts).
- **Shebang convention**: `#!/usr/bin/env bash`.
- **Runtime resolution**: script-relative only — `cd "$(dirname "$0")/.." && pwd`. No env-var fallback; relies on the bin directory being PATH-injected by the host.
- **Venv handling (Python)**: not applicable.
- **Platform support**: POSIX (bash).
- **Permissions**: file mode not directly introspectable via the contents API, but the shebang + usage-on-PATH + README convention imply 100755 (executable). Confirmed indirectly — skills invoke it as `ship-plugin-root 2>/dev/null` without a `bash` prefix.
- **SessionStart relationship**: static — no hook populates or modifies `bin/`; the wrapper is shipped as committed source.
- **Pitfalls observed**: the script's load-bearing comment explains exactly the pattern to document for other repos:

  ```bash
  #!/usr/bin/env bash
  # Resolve the ship plugin root directory.
  # This script lives in <plugin-root>/bin/ and is on PATH automatically
  # (Claude Code adds each plugin's bin/ to PATH). Skills call this to
  # locate the plugin without relying on CLAUDE_PLUGIN_ROOT, which is
  # only available in hook contexts.
  printf '%s\n' "$(cd "$(dirname "$0")/.." && pwd)"
  ```

  Consumer pattern (observed verbatim in every skill's preamble, e.g. `skills/auto/SKILL.md`, `skills/setup/SKILL.md`):

  ```bash
  SHIP_PLUGIN_ROOT="${SHIP_PLUGIN_ROOT:-$(ship-plugin-root 2>/dev/null || echo "$HOME/.codex/ship")}"
  SHIP_SKILL_NAME=<skill> source "${SHIP_PLUGIN_ROOT}/scripts/preflight.sh"
  ```

  The fallback `$HOME/.codex/ship` is the Codex install path — so the same preamble works under Claude (bin PATH resolves), Codex (fixed install path), or Cursor (bin PATH resolves). `auto-orchestrate.sh` separately honors `SHIP_PLUGIN_ROOT` *or* `CLAUDE_PLUGIN_ROOT`, confirming the env-var is hook-only. This is a meaningful discovery pattern: Claude Code populates `$CLAUDE_PLUGIN_ROOT` only in hook contexts (not in skill/agent contexts), so any skill that needs to invoke a plugin-local script must either (a) assume `bin/` is on PATH and shell out to a discovery wrapper, or (b) require hook-only invocation. Ship chose (a).

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable.
- **Pitfalls observed**: none — plugin is configuration-free. All per-repo state lives on-disk in `.ship/`, `.learnings/`, etc., produced by `/ship:setup`.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 — matcher absent (matches all tools), points at `scripts/phase-guardrail.sh`. Purpose: enforces artifact access rules per `/ship:auto` pipeline phase. Fast-exit when the tool isn't Read/Write/Edit; only active when `.ship/ship-auto.local.md` exists; only gates subagents (non-empty `agent_id`). Four rules encoded:
    1. QA phase blocks `Read` of `review.md` and `plan.md` (cross-phase independence).
    2. Review phase blocks `Write`/`Edit` of anything outside `.ship/`.
    3. QA phase blocks `Write`/`Edit` of anything outside `.ship/` or `/tmp/`.
    4. All phases block `Write`/`Edit` of `.ship/ship-auto.local.md` (state-file protection — only the orchestrator writes it).
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON (via `jq -n`) with `{"decision":"block","reason":"[Ship guardrail] …"}` on block; exit 0 silent on allow. No stderr messages.
- **Failure posture**: fail-open — on any unexpected condition (no state file, no agent_id, no tool name, unknown phase), exits 0 silently and allows the tool call. Guardrails fire only on positive matches.
- **Top-level try/catch wrapping**: absent — `set -u` only (no `-e`). Errors in intermediate commands fall through to the next conditional; fail-open posture absorbs them.
- **Pitfalls observed**: the fast-exit case-match on raw JSON (`*'"tool_name":"Read"'*`) matches both compact and spaced variants but will miss exotic whitespace. Acceptable trade-off since the goal is to skip `jq` invocation 90% of the time.

## 10. Session context loading

- **SessionStart used for context**: yes — four layered injections, composed into one `additionalContext`:
    1. **Layer 1 (always):** hard-coded Ship routing policy wrapped in `<EXTREMELY_IMPORTANT>` tags — lists the `/ship:*` skill catalog and the decision rule ("don't default to /ship:auto").
    2. **Layer 2 (if `.learnings/LEARNINGS.md` exists):** awk-filter extracts only entries with `**Status**: verified` frontmatter, separated by `---`.
    3. **Layer 3 (if `docs/DOCS_INDEX.md` exists):** whole-file inject.
    4. **Layer 4 (if `DESIGN.md` exists at repo root):** pointer-only (single line: "DESIGN.md (visual design system) exists at project root. When writing frontend code, read it first"), no body.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: yes — and the same script dual-emits: under Cursor (detected via `$CURSOR_PLUGIN_ROOT`) it emits `{"additional_context": ...}`; under Claude it emits `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ...}}`. Same script, two output schemas.
- **SessionStart matcher**: none (registration has no matcher, so fires on `startup | clear | compact`). Also note: a separate `PreCompact` hook (`scripts/auto-pre-compact.sh`) handles cancellation-aware state archiving before the agent rehydrates post-compact.
- **Pitfalls observed**: Layer-1 routing policy hard-codes the skill catalog in bash — when skills are added/removed/renamed, the hook must be updated. There is no auto-derivation from `skills/` directory contents. The awk frontmatter filter for learnings uses `RS="---[[:space:]]*\n"` which is GNU-awk / BSD-awk-compatible but sensitive to CRLF; `tr -d '\r'` only applied elsewhere, not here.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: the `handoff` skill (per recent commit `refactor(handoff): replace 30s CI poll with gh watch + Monitor`) uses the Claude Code **Monitor tool** (not `monitors.json`) to watch GitHub CI — different mechanism, not declarative monitors.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace with no tags at all.
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: bash scripts — three test files (`test-auto-orchestrate.sh`, `test-e2e-phase.sh`, `test-generate-docs-index.sh`) with hand-rolled PASS/FAIL counters, temp-dir fixtures (`mktemp -d`), and `git init -q` scratch repos. Tests mock `origin/HEAD` explicitly (workaround for `has_branch_changes()` comparing against `origin/HEAD`).
- **Tests location**: `tests/` at repo root (flat — no per-plugin subdirs since there's one plugin).
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: no — no `.github/` directory exists (404 from the API). No workflow files of any kind.
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: direct bash — each test file self-executes (`bash tests/test-*.sh`). No top-level runner script that wraps all of them.
- **Pitfalls observed**: zero CI for a 42-star plugin — all verification is manual or local. AGENTS.md documents "Test hooks" with an ad-hoc `echo '<json>' | bash scripts/<hook>.sh` pattern rather than a test harness for the hooks themselves; only `auto-orchestrate.sh`, the e2e phase flow, and the docs-index generator have dedicated test files.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — releases are not cut. Version bumps are plain commits to main.
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: not applicable.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable — no CHANGELOG.md.
- **Pitfalls observed**: no release automation of any kind. The plugin is shipped via "install from git, main HEAD" semantics — `/plugin install ship@heliohq` resolves against current main.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: not applicable.
- **Hooks.json validation**: not applicable.
- **Pitfalls observed**: none — validation relies entirely on the runtime host (Claude Code, Codex, Cursor) surfacing errors. No pre-merge linting of `marketplace.json`, `plugin.json`, `hooks.json`, or skill frontmatter.

## 16. Documentation

- **`README.md` at repo root**: present (~5.3 KB) — product narrative, install flow for all three runtimes (Claude, Codex, Cursor), skill table.
- **Owner profile README at `github.com/heliohq/heliohq`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable (single-plugin; repo README serves).
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: absent (architectural narrative is split into README "How It Works" + AGENTS.md "Architecture" section + individual `docs/design/*.md` files, currently one — `002-session-context-injection.md`).
- **`CLAUDE.md`**: absent at repo root. The repo uses `AGENTS.md` instead — Codex-first convention adopted also as the cross-agent docs surface. Per-plugin CLAUDE.md not applicable.
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: absent.
- **Pitfalls observed**: `AGENTS.md` carries what would be both `CLAUDE.md` and `architecture.md` in a Claude-native convention — a deliberate unification that trades per-agent specificity for a single documentation surface. `docs/DOCS_INDEX.md` is auto-generated by `scripts/generate-docs-index.sh` and injected into sessions via SessionStart Layer 3; it's a live index, not a hand-maintained TOC.

## 17. Novel axes

- **Triple-runtime polyglot plugin.** Three parallel plugin manifests for three runtimes: `.claude-plugin/plugin.json` (Claude Code), `.cursor-plugin/plugin.json` (Cursor), and `.codex/` (Codex, install-by-symlink per `INSTALL.md`). Same `scripts/`, same `skills/` tree, but the hook schema differs per runtime — `hooks/hooks.json` for Claude (nested `{hooks:[{hooks:[{type,command}]}]}`), `hooks/hooks-cursor.json` for Cursor (flat `sessionStart: [{command: "./hooks/session-start"}]`), and `.codex/hooks.json` for Codex global install (has `statusMessage` + `timeout` fields Claude lacks). The one shell-level adapter is `hooks/session-start` — a trivial exec wrapper that Cursor's relative-command schema invokes. **Version drift across runtimes is live** (Claude plugin.json 0.1.6, Cursor plugin.json 0.1.6, marketplace.json 1.9.0). No single-source-of-truth discipline across the manifests.
- **Bin-wrapper as discovery utility (not user CLI).** `bin/ship-plugin-root` is not a tool the user runs — it's a 5-line bash script that skills invoke to locate the plugin when `$CLAUDE_PLUGIN_ROOT` isn't exported. The load-bearing comment states the rationale explicitly: *"skills call this to locate the plugin without relying on CLAUDE_PLUGIN_ROOT, which is only available in hook contexts."* This is a distinct pattern from bin-wrappers as user-facing CLIs or as managed-runtime launchers — it's a bin-wrapper as **context-bridge** between hook-available env vars and skill-available PATH. Worth calling out as a named pattern in the pattern doc: **skill-invocable plugin-root discovery**. Consumer preamble (verbatim across `skills/*/SKILL.md`):
  ```bash
  SHIP_PLUGIN_ROOT="${SHIP_PLUGIN_ROOT:-$(ship-plugin-root 2>/dev/null || echo "$HOME/.codex/ship")}"
  SHIP_SKILL_NAME=<skill> source "${SHIP_PLUGIN_ROOT}/scripts/preflight.sh"
  ```
  Note the triple-fallback: env var → bin wrapper → Codex-install-path hard-coded default.
- **PATH-bootstrap sourced by every hook.** `scripts/path-bootstrap.sh` prepends `~/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `~/.local/bin`, `~/go/bin` to PATH. Sourced from the top of every hook script. Driven by "Claude Code and some CI environments inherit a minimal PATH that excludes common install dirs" — an adaptation layer for missing-PATH pathology.
- **Layered SessionStart context injection with frontmatter-status filtering.** Layer 2 of session-start uses an awk record-splitter on `---` to extract only entries marked `**Status**: verified` from `.learnings/LEARNINGS.md`. The rest (experimental, proposed, etc.) don't get injected. A markdown-level curation gate encoded in the hook.
- **PreCompact hook for state-file eviction on cancellation.** `scripts/auto-pre-compact.sh` scans the pre-compact transcript for an interrupt-then-unrelated-user-message pattern and archives `.ship/ship-auto.local.md` before compact removes the evidence — protecting against post-compact false resumption. A rarely-used hook event put to specific use.
- **Phase-based tool-use enforcement with subagent gating.** The PreToolUse guardrail only blocks subagent calls (non-empty `agent_id`), not orchestrator calls. Phase transitions are encoded in a YAML-frontmatter state file (`.ship/ship-auto.local.md`) that the orchestrator owns exclusively. This is a meaningful division: the orchestrator has full tool access; phase-dispatched subagents get scoped access. Encoded structurally rather than documentationally.
- **Self-emitting schema detection** in `session-start.sh` — same script produces Cursor-schema JSON (`{"additional_context": ...}`) when `$CURSOR_PLUGIN_ROOT` is set, otherwise Claude-schema JSON. Single script, runtime-discriminated output.
- **MCP at repo root, not plugin-scoped.** `.mcp.json` at repo root registers the `codex` MCP server for developers of `ship` itself (so `/ship:*` skills can dispatch a Codex peer via `mcp__codex__codex` during local iteration). Distinct from plugin-distributed MCP. Consumers installing via `/plugin install` don't inherit this — they need their own `codex` MCP registration.
- **Hook manifest version field under Cursor.** `hooks/hooks-cursor.json` has a top-level `"version": 1` that Claude's `hooks/hooks.json` lacks — Cursor's hook schema is versioned; Claude's isn't. Minor but real schema differentiator.
- **`<EXTREMELY_IMPORTANT>` XML-tag wrapping in SessionStart context.** Layer 1 wraps the routing policy in `<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT>` tags — a prompt-engineering construct emitted as session context. Not something the pattern doc currently describes; worth noting if the aggregator observes it in multiple repos.

## 18. Gaps

- **File permissions on `bin/ship-plugin-root`.** Contents API doesn't expose mode bits; inferred executable from shebang + invocation style (`ship-plugin-root 2>/dev/null`, not `bash ship-plugin-root`). Would need `gh api .../git/trees/<sha>?recursive=1` to confirm `"mode": "100755"`.
- **Git hooks (if any).** `.githooks/` or similar not surveyed; no pre-commit automation for version bumps observed in commit log, but a hidden/untracked hook on the maintainer's machine could exist. Would need `.gitattributes` / `core.hooksPath` inspection to rule out.
- **Whether `strict: true` is intended.** The marketplace entry has no `strict` field, so the default applies. Whether the author intended strict or non-strict is undocumented. Would need a design doc or CONTRIBUTING note to confirm.
- **Full content of `tests/test-e2e-phase.sh`.** Only head fetched; any additional test-infrastructure patterns (e.g., Docker fixtures, CI-style matrix runs) not surveyed. Would need full-file fetch.
- **Whether version drift (marketplace `1.9.0` vs plugin.json `0.1.6`) is a bug or intentional.** Commit history shows manual bumps to both, with one commit ("chore: align cursor plugin version to 0.1.1 to match claude plugin") suggesting intentional-but-sometimes-forgotten alignment. Would need a design doc or CONTRIBUTING note to confirm the policy.
- **What lives in `skills/shared/prompts/`, `skills/shared/references/`.** Only three `skills/shared/*.md` files were fetched (`cleanup.md`, `report-card.md`, `runtime-resolution.md`, `startup.md`). Subdirectories of specific skills (e.g., `skills/auto/prompts/`, `skills/auto/references/`) not fully enumerated. Would need per-skill tree walk.
- **Whether `auto-orchestrate.sh` carries any userConfig-style inputs via env.** Head of the script reads `SHIP_PLUGIN_ROOT`/`CLAUDE_PLUGIN_ROOT`, but doesn't show the full env surface. The `stop-gate.sh` references `SHIP_STOP_GATE_BYPASS` and `SHIP_VERIFY` (per one reverted commit). A full grep of `${SHIP_*}` across scripts would enumerate the informal user-config surface that's not declared in plugin.json.
