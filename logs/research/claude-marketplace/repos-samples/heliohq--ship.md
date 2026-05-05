# Sample

Mirrors `https://github.com/heliohq/ship`. Single-plugin marketplace — agentic development harness for Claude Code, Codex & Cursor: gated pipeline from spec to green checks. MIT license. Last commit 2026-04-20; default branch `main`; 42 stars. Sample origin: bin-wrapper.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root listing one plugin (`ship`) with `source: "./"` — repo is both marketplace and plugin. Top-level `name`, `description`, `owner` object (`{name, url}`). No `metadata` wrapper; no `version` at marketplace level.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the single marketplace entry. No aggregator. Trailing slash applies.

### `strict` field default

`strict` field absent (default, implicit true). No `skills` override on marketplace entry. Skills discovered from `skills/` via default layout. The Cursor variant explicitly declares `"skills": "./skills/"`, but the Claude `.claude-plugin/plugin.json` relies on default discovery.

## Source layout

### Single tree (plugin equals repo)

Plugin manifest at `.claude-plugin/`; components at conventional top-level directories.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry has `name`, `description`, `version`, `source`. `keywords` lives in `plugin.json` (8 items: agent, coding, planning, qa, debugging, refactoring, orchestrator, workflows). No `category`, `tags` on either surface.

### `$schema` absence on per-plugin manifests

`$schema` absent.

## Version coordination

### Cross-runtime version multiplication

Three version strings across two runtimes and one marketplace manifest: `.claude-plugin/plugin.json` (`0.1.6`), `.cursor-plugin/plugin.json` (`0.1.6`), and the marketplace entry (`1.9.0`). Manual sync discipline already shown to drift: commits like "align cursor plugin version to 0.1.1 to match claude plugin" and "bump version to 0.1.1 / 1.9.2" make the alignment intent visible. Marketplace spec treats either as authoritative depending on consumer; drift is live (current tree has marketplace `1.9.0` vs plugin `0.1.6`).

## Channel distribution

### No pinning surface

No tags (`matching-refs/tags` returns empty; releases list empty). No release branches, no marketplace channel artifacts. Users install via `/plugin install ship@heliohq` — gets whatever main HEAD is at resolution time.

## Tag and release lifecycle

### Hand-bumped versions on main (untagged)

Default branch `main`. No tags. Release marker is plain commits like `chore(plugin): bump 0.1.4 -> 0.1.5`. Feature branches (`fix/*`, `feat/*`, `refactor/*`, `codex/*`) merge to main via PR. No automation, no pre-commit hook to derive bumps. CHANGELOG absent. Version drift across multiple manifest surfaces is hand-aligned via separate "align cursor plugin version to match claude plugin" commits when contributors notice.

## Plugin-component registration

### Default convention discovery

Default discovery for skills. `hooks` referenced by hooks.json at `hooks/hooks.json` (default lookup). `mcpServers` not declared in plugin.json — `.mcp.json` lives at repo root (project-level MCP, not plugin-level).

### Mixed convention per runtime (per-runtime manifests)

Three concurrent manifest systems:

- `.claude-plugin/plugin.json` (Claude Code) relies on default discovery; `hooks/hooks.json` uses nested `{hooks:[{hooks:[{type, command}]}]}`.
- `.cursor-plugin/plugin.json` (Cursor) explicitly sets `"skills": "./skills/"` and `"hooks": "./hooks/hooks-cursor.json"`. `hooks-cursor.json` uses flat `sessionStart: [{command: "./hooks/session-start"}]` plus a top-level `version: 1` field. The Cursor manifest invokes a separate bin-style shim (`hooks/session-start`) that execs the shared `scripts/session-start.sh`.
- `.codex/` (Codex, install-by-symlink per `INSTALL.md`) carries `.codex/hooks.json` with `statusMessage` + `timeout` fields Claude lacks.

Same `scripts/`, same `skills/` tree across all three runtimes; only the manifest views differ.

## Component composition

### Skills (universal)

14 top-level skill dirs including a `shared/` references dir.

### Hooks

`hooks/hooks.json` at conventional path.

### MCP servers

`.mcp.json` at repo root registers the `codex` MCP server invoking `codex mcp-server`. Project-level MCP (for developers of `ship` itself), not plugin-distributed; consumers installing via `/plugin install` don't get it wired.

### bin

`bin/ship-plugin-root` — single bash script.

## Server runtime (MCP)

### Repo-root MCP server for contributor use

`.mcp.json` at repo root (not under any plugin tree) registers a `codex` MCP server (`codex mcp-server`) for use by skills during local development of `ship` itself. Consumers installing via `/plugin install` don't inherit this — contributors clone the repo and get the MCP wiring as part of working on the plugin source. Distinct from plugin-distributed MCP.

## Bin entry mechanism

### Discovery utility — bin as context bridge

`bin/ship-plugin-root` (bash, 355 bytes, `#!/usr/bin/env bash`, mode 100755 inferred from invocation style) — resolves and prints the ship plugin root directory. Not a user CLI; skills invoke `ship-plugin-root 2>/dev/null` to locate the plugin tree when `$CLAUDE_PLUGIN_ROOT` is unavailable. Load-bearing comment in source: "Skills call this to locate the plugin without relying on CLAUDE_PLUGIN_ROOT, which is only available in hook contexts." Static — no hook populates or modifies `bin/`. Consumer pattern observed verbatim in every skill's preamble (e.g. `skills/auto/SKILL.md`, `skills/setup/SKILL.md`):

```bash
SHIP_PLUGIN_ROOT="${SHIP_PLUGIN_ROOT:-$(ship-plugin-root 2>/dev/null || echo "$HOME/.codex/ship")}"
SHIP_SKILL_NAME=<skill> source "${SHIP_PLUGIN_ROOT}/scripts/preflight.sh"
```

Triple-fallback: env var → bin wrapper → Codex-install-path hard-coded default. Same preamble works under Claude (bin PATH resolves), Codex (fixed install path), or Cursor (bin PATH resolves). `auto-orchestrate.sh` separately honors `SHIP_PLUGIN_ROOT` *or* `CLAUDE_PLUGIN_ROOT`, confirming the env var is hook-only.

### Script-relative shell wrapper

`bin/ship-plugin-root` resolves via `cd "$(dirname "$0")/.." && pwd`. No env-var fallback in the wrapper itself; relies on the bin directory being PATH-injected by the host. POSIX (bash). Skills invoke as `ship-plugin-root 2>/dev/null` without a `bash` prefix — confirms 100755.

## Plugin-runtime root resolution

### Cascading multi-host fallback

Skill preamble pattern uses a triple-fallback chain — `SHIP_PLUGIN_ROOT` env var → `ship-plugin-root` bin wrapper output → hard-coded `$HOME/.codex/ship`. Same preamble works under Claude (bin PATH resolves), Codex (fixed install path), or Cursor (bin PATH resolves).

## Dependency installation

### No managed install — pure shell/markdown

Pure shell/markdown plugin. No Python, Node, or other language runtime ships with the plugin. Shell scripts assume `bash`, `jq`, `git`, `python3` (optional fallback in one hook) on `$PATH`; runtime dependencies (codex CLI, agent-browser, gh, claude, etc.) are user-installed and discovered at runtime via `command -v <tool>`. No dep manifest, no install location, no install script. The Codex MCP server is ad-hoc via `codex mcp-server` (user-installed).

### Zero-dep system-tool stance (bash + jq only)

Hooks depend on `jq` (required — `stop-gate` and `phase-guardrail` produce JSON via `jq -n`) but jq isn't auto-installed. A user on a minimal system can silently exit with degraded behavior. One hook (`session-start.sh`) has `python3` fallback for JSON escaping; phase-guardrail and stop-gate do not.

## User configuration and authentication

### No user-supplied config

`plugin.json` declares no `userConfig`. No settings file, no env vars in manifest. Per-repo state lives on-disk in `.ship/`, `.learnings/`, etc., produced by `/ship:setup`.

## Session context loading

### Layered SessionStart context with conditional inclusion

SessionStart composes one `additionalContext` from up to four layers, each conditional on a file existing in the repo:

1. **Layer 1 (always):** hard-coded Ship routing policy wrapped in `<EXTREMELY_IMPORTANT>` tags — lists the `/ship:*` skill catalog and the decision rule ("don't default to /ship:auto").
2. **Layer 2 (if `.learnings/LEARNINGS.md` exists):** awk-filter extracts only entries with `**Status**: verified` frontmatter, separated by `---`. Uses `RS="---[[:space:]]*\n"` (GNU-awk / BSD-awk-compatible but sensitive to CRLF; `tr -d '\r'` only applied elsewhere, not here).
3. **Layer 3 (if `docs/DOCS_INDEX.md` exists):** whole-file inject.
4. **Layer 4 (if `DESIGN.md` exists at repo root):** pointer-only (single line: "DESIGN.md (visual design system) exists at project root. When writing frontend code, read it first"), no body.

Layer-1 routing policy hard-codes the skill catalog in bash — when skills are added/removed/renamed, the hook must be updated. There is no auto-derivation from `skills/` directory contents.

### XML-tag emphasis wrapping

Layer-1 routing policy is wrapped in `<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT>` tags as a prompt-engineering construct emitted as session context.

### Self-emitting schema detection for cross-runtime context

Same SessionStart script dual-emits: under Cursor (detected via `$CURSOR_PLUGIN_ROOT`) it emits `{"additional_context": ...}`; under Claude it emits `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ...}}`. Single script, runtime-discriminated output.

### PreCompact hook for state-file eviction

`scripts/auto-pre-compact.sh` scans the pre-compact transcript for an interrupt-then-unrelated-user-message pattern and archives `.ship/ship-auto.local.md` before compact removes the evidence — protecting against post-compact false resumption.

## SessionStart matcher scope

### Empty matcher (all sub-events)

Registration has no matcher, so SessionStart fires on `startup | clear | compact`.

## Tool-use enforcement

### PreToolUse as phase-scoped artifact gate

One PreToolUse hook (matcher absent — matches all tools) points at `scripts/phase-guardrail.sh`. Enforces artifact access rules per `/ship:auto` pipeline phase. Fast-exit when the tool isn't Read/Write/Edit (case-match on raw JSON like `*'"tool_name":"Read"'*` to skip `jq` invocation 90% of the time); only active when `.ship/ship-auto.local.md` exists; only gates subagents (non-empty `agent_id`). Four rules encoded:

1. QA phase blocks `Read` of `review.md` and `plan.md` (cross-phase independence).
2. Review phase blocks `Write`/`Edit` of anything outside `.ship/`.
3. QA phase blocks `Write`/`Edit` of anything outside `.ship/` or `/tmp/`.
4. All phases block `Write`/`Edit` of `.ship/ship-auto.local.md` (state-file protection — only the orchestrator writes it).

Fast-exit case-match on raw JSON matches both compact and spaced variants but will miss exotic whitespace.

## Hook handler runtime

### Bash scripts at conventional path

Hook scripts under `scripts/`. `scripts/path-bootstrap.sh` is sourced from the top of every hook script. `set -u` only (no `-e`); errors in intermediate commands fall through to the next conditional; fail-open posture absorbs them.

## Hook output contract

### jq-built JSON

Hook scripts use `jq -n` to construct stdout JSON. `phase-guardrail` emits `{"decision":"block","reason":"[Ship guardrail] …"}` on block; exit 0 silent on allow. No stderr-human-parallel pattern.

## Hook failure posture

### Fail-open with always-exit-0

`set -u` only (no `-e`). On any unexpected condition (no state file, no agent_id, no tool name, unknown phase), exits 0 silently and allows the tool call. Guardrails fire only on positive matches. Top-level try/catch wrapping absent — relies on shell exit-code propagation.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Per-repo state lives on-disk in `.ship/`, `.learnings/`, `docs/` of the consumer's repo (not in `${CLAUDE_PLUGIN_DATA}`). Plugin code lives under the plugin root.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The `handoff` skill (per recent commit `refactor(handoff): replace 30s CI poll with gh watch + Monitor`) uses the Claude Code Monitor tool (not `monitors.json`) to watch GitHub CI — different mechanism.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` field. Single-plugin marketplace with no tags at all.

## Testing

### Hand-rolled bash tests

Three test files (`test-auto-orchestrate.sh`, `test-e2e-phase.sh`, `test-generate-docs-index.sh`) at `tests/` repo root with hand-rolled PASS/FAIL counters, temp-dir fixtures (`mktemp -d`), and `git init -q` scratch repos. Tests mock `origin/HEAD` explicitly (workaround for `has_branch_changes()` comparing against `origin/HEAD`). No top-level runner script that wraps all of them — each test file self-executes (`bash tests/test-*.sh`). AGENTS.md documents "Test hooks" with an ad-hoc `echo '<json>' | bash scripts/<hook>.sh` pattern rather than a test harness for the hooks themselves.

## CI workflow shape

### No CI

No `.github/` directory exists (404 from API). No workflow files. Zero CI for a 42-star plugin — all verification is manual or local.

## Marketplace validation

### No validation

No CI, no validator. Validation relies entirely on the runtime host (Claude Code, Codex, Cursor) surfacing errors. No pre-merge linting of `marketplace.json`, `plugin.json`, `hooks.json`, or skill frontmatter.

## Release automation

### No release automation / manual

No release workflow. Releases not cut. Version bumps are plain commits to main. No CHANGELOG.md. Plugin shipped via "install from git, main HEAD" semantics — `/plugin install ship@heliohq` resolves against current main.

## Documentation surface

### AGENTS.md as cross-runtime governance unification

Repo serves Claude + Cursor + Codex consumers. Uses `AGENTS.md` (Codex-first convention) as the single agent-facing governance doc instead of Claude-native `CLAUDE.md`. Carries content `CLAUDE.md` would (operational procedures) plus content `architecture.md` would (architectural narrative). Trade-off: per-runtime specificity for a single doc surface. Sub-architecture lives in `docs/design/<NNN>-<topic>.md` files (currently one — `002-session-context-injection.md`). No `architecture.md`. No `CLAUDE.md` at repo root. Per-plugin CLAUDE.md not applicable.

### README only

Repo-root `README.md` (~5.3 KB) — product narrative, install flow for all three runtimes (Claude, Codex, Cursor), skill table. No per-plugin README (single-plugin; repo README serves). No CHANGELOG.md.

### Auto-generated docs index

`docs/DOCS_INDEX.md` is auto-generated by `scripts/generate-docs-index.sh` and injected into sessions via SessionStart Layer 3. Live index, not a hand-maintained TOC.

## License declaration

### Single repo-level license

LICENSE present (MIT). README has no shield badges.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.

## Cross-platform discipline

### POSIX-only with no Windows story

Hook scripts under `scripts/` use bash. Bin wrapper uses bash. No `.cmd` / `.ps1` siblings.

## Multi-runtime portability

### Triple-runtime parallel manifests

Repo ships three parallel manifest trees: `.claude-plugin/plugin.json` (Claude Code), `.cursor-plugin/plugin.json` (Cursor), and `.codex/` (install-by-symlink). Same `scripts/`, same `skills/` tree. Hook schemas differ per runtime — Claude uses nested `{hooks:[{hooks:[{type, command}]}]}`, Cursor uses flat `sessionStart: [{command: "./hooks/session-start"}]` plus a top-level `version: 1` field, Codex adds `statusMessage` and `timeout` fields Claude lacks. A trivial bash exec wrapper (`hooks/session-start`) bridges Cursor's relative-command schema to the shared script. Cross-runtime version drift is live (Claude plugin.json 0.1.6, Cursor plugin.json 0.1.6, marketplace.json 1.9.0) and hand-aligned.

## Cross-ecosystem distribution

### Triple-ecosystem (Claude + Codex + Cursor)

Single repo serves Claude Code, Codex, and Cursor with three concurrent manifest systems. Bootstrap differs per host: Claude via `/plugin install`, Cursor via marketplace add, Codex via symlink install per `INSTALL.md`. Skill preamble's triple-fallback chain (`SHIP_PLUGIN_ROOT` env, `ship-plugin-root` bin discovery, hard-coded `$HOME/.codex/ship` default) supports invocation from any host.

## PATH augmentation and host-project setup

### PATH-bootstrap script sourced by every hook

`scripts/path-bootstrap.sh` prepends `~/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `~/.local/bin`, `~/go/bin` to PATH. Sourced from the top of every hook script. Driven by "Claude Code and some CI environments inherit a minimal PATH that excludes common install dirs" — adaptation layer for missing-PATH pathology.

## Cross-role tools

### bash

bash fills bin-wrapped CLI distribution (`bin/ship-plugin-root`), hook scripts (phase-guardrail, stop-gate, session-start), and hand-rolled test runners. `set -u` only on hooks (deliberately not `-e`).

### `jq`

`jq` builds hook output (`jq -n` for `{decision, reason}` JSON), required for stop-gate and phase-guardrail. User PATH must carry it.

### `${CLAUDE_PLUGIN_ROOT}` env var

Consumed by `auto-orchestrate.sh` as one of two accepted env vars (along with `SHIP_PLUGIN_ROOT`). Skills explicitly avoid relying on `CLAUDE_PLUGIN_ROOT` because the harness only populates it in hook contexts — hence the `bin/ship-plugin-root` discovery utility.
