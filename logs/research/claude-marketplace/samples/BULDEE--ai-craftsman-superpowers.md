# BULDEE/ai-craftsman-superpowers

## Identification

- **URL**: https://github.com/BULDEE/ai-craftsman-superpowers
- **Stars**: 7
- **Last commit date**: 2026-04-09 (commit `dfb643a`, merge of fix/wrong-paths-in-commands)
- **Default branch**: main
- **License**: Apache-2.0 (LICENSE file present, 10.5 KB full Apache 2.0 text)
- **Sample origin**: primary (community)
- **One-line purpose**: "Senior craftsman methodology for Claude Code. DDD, Clean Architecture, TDD, Rule Engine, Multi-CI" — transforms Claude into a disciplined senior software engineer via 21 commands / 11 agents / 14-event hooks.json / a rules engine / an SQLite-backed correction-learning loop / a multi-provider CI adapter.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root alongside `.claude-plugin/plugin.json` and a `.claude-plugin/ignore` sibling (distribution exclusion list).
- **Marketplace-level metadata**: `metadata.{description}` wrapper (description only — no `version` or `pluginRoot` inside `metadata`); top-level `name`, `version`, `owner` alongside the `metadata` object.
- **`metadata.pluginRoot`**: absent. Single-plugin manifest binds via `source: "./"` instead.
- **Per-plugin discoverability**: `category: "development"` plus `tags: [architecture, quality, php, symfony, react, typescript, ci, rule-engine]` (8 tags) on the marketplace entry. `plugin.json` additionally carries an 18-item `keywords` array (ddd, domain-driven-design, clean-architecture, tdd, craftsman, software-engineering, code-quality, symfony, react, typescript, php, testing, refactoring, methodology, quality-metrics, static-analysis, sentry, channels). Both category+tags and keywords are used.
- **`$schema`**: absent from both `marketplace.json` and `plugin.json`.
- **Reserved-name collision**: no (`craftsman` is not a reserved Claude Code command name).
- **Pitfalls observed**: marketplace entry repeats the plugin version (`3.4.4` in both the root-level and per-plugin slots of `marketplace.json` and again in `plugin.json` — three sources to keep in sync; see also ci/craftsman-ci.sh `VERSION=`, README version badge, and CLAUDE.md "Current version:" string — six locations total, manually bumped by `scripts/bump-version.sh`). The tag list on the marketplace entry and the keyword list on `plugin.json` overlap but are not identical (rule-engine, ci appear only on the marketplace entry; domain-driven-design, clean-architecture, methodology, static-analysis, sentry, channels, refactoring, testing appear only in plugin.json keywords) — two discovery surfaces with drift potential.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — the plugin lives at the marketplace repo root.
- **`strict` field**: not set (implicit default). No `strict: false` override.
- **`skills` override on marketplace entry**: absent — marketplace.json only carries name/version/description/author/source/category/tags.
- **Version authority**: both — `marketplace.json` has a top-level `version: "3.4.4"` AND a per-plugin `version: "3.4.4"`, AND `plugin.json` has its own `version: "3.4.4"`. Three-way sync enforced by `scripts/bump-version.sh` patching all three (plus three other files). CI validator (`validate-plugin-manifest` job) checks plugin.json version is semver but does not cross-check against marketplace.json.
- **Pitfalls observed**: two-in-one-file version duplication inside marketplace.json itself (root `version` + `plugins[0].version`) — no validator guards drift between them. `scripts/bump-version.sh` uses `sed -i ''` (BSD sed syntax with empty extension), which will fail on GNU Linux sed; the author appears to work on macOS. Running the script in CI or on Linux would break silently or emit errors.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via git ref (`BULDEE/ai-craftsman-superpowers` resolves to default branch; `@vX.Y.Z` tags are available but there is no stable/latest marketplace pair).
- **Channel-pinning artifacts**: the plugin itself exposes `channels.sh` as an internal library (`hooks/lib/channels.sh`, 9.5 KB) and a `channel-cache.sh` (2.7 KB) — those are application-level channel semantics (for the plugin's own feature routing, not for marketplace distribution channels).
- **Pitfalls observed**: none — single-channel distribution, users pin at install by tag (`/plugin install craftsman@BULDEE-ai-craftsman-superpowers`) without explicit stable/dev splitting.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main (e.g., v3.4.4 is tag of commit `97219e3` on main). 30 tags observed spanning v1.2.1 → v3.4.4.
- **Release branching**: none — tag-on-main pattern. CONTRIBUTING.md instructs branching `feature/*` off main and merging back.
- **Pre-release suffixes**: none observed in current tag list; however, plugin.json CI schema allows `-[\w.]+` semver suffix (regex `^\d+\.\d+\.\d+(-[\w.]+)?$`), so pre-release suffixes are tolerated but unused.
- **Dev-counter scheme**: absent. Every commit that bumps version bumps a real semver patch (e.g., v3.4.1 → v3.4.2 → v3.4.3 → v3.4.4 on 2026-04-05 through 2026-04-06 — four patches in two days as reactive fixes).
- **Pre-commit version bump**: no — version bumps are manual via `scripts/bump-version.sh <new_version>` which the contributor runs before committing, then manually tags.
- **Pitfalls observed**: tight release cadence (four patches in 36 hours for v3.4.x) means every push is a user-visible release candidate — no dev/hidden-bump lane. CHANGELOG.md shows the full patch burst as visible entries ("Hook blocking messages now visible to users", "Pre-push verification downgraded to warning", "Auto-verify on test success", "CI hooks schema validator"). `bump-version.sh` does not also run `git tag` or commit — the script's tail prints next-step instructions.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — no `skills`, `commands`, `agents`, or `hooks` path arrays in plugin.json. Claude Code auto-discovers from conventional directories (`commands/`, `agents/`, `skills/`, `hooks/hooks.json`). CHANGELOG v3.2.2 explicitly notes: "`skills` and `agents` fields in `plugin.json` used inline objects incompatible with Claude Code v2.1.92 schema. Removed inline definitions; Claude Code now auto-discovers from `commands/` and `agents/` directories." Exception: `mcpServers` IS inlined in plugin.json (`knowledge-rag` stdio server pointing at `packs/ai-ml/mcp/knowledge-rag/start.mjs`) — mixed inline/discovery within the same manifest.
- **Components observed**: skills yes (`skills/craftsman/session-init/SKILL.md` — single hidden session-init skill with `disable-model-invocation: true`); commands yes (20 `.md` files under `commands/`, symlinks bring pack commands in); agents yes (5 core agents in `agents/` with pack symlinks for 11 total per README); hooks yes (`hooks/hooks.json` + 18 `.sh` scripts + `hooks/lib/` helper library); `.mcp.json` NO (MCP servers declared inline in plugin.json rather than via dedicated `.mcp.json`); `.lsp.json` no; monitors no; bin yes (2 thin wrappers `bin/craftsman-ci` and `bin/craftsman-validate`); output-styles yes (2 `.md` files: `output-styles/craftsman-review.md`, `output-styles/craftsman-terse.md`); teams yes (`teams/wizard.md`, 3.5 KB — appears to be a non-standard component); config yes (`config/default-config.yml`); setup yes (`setup/templates/`, empty dir). 
- **Agent frontmatter fields used**: `name`, `description`, `model` (sonnet), `effort` (high), `memory` (project / user), `isolation` (worktree), `maxTurns` (20 / 50), `allowedTools` (array), `skills` (array of `craftsman:<skill>` refs). `security-pentester.md` omits the `skills` field. `team-lead.md` additionally includes `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage` in `allowedTools` — references to agent-orchestration tools not documented in the plugin reference. CHANGELOG v3.2.2 notes: "Fixed `tools:` → `allowedTools:` in react-reviewer, symfony-reviewer, security-pentester" — prior releases used the wrong field name.
- **Agent tools syntax**: plain tool names only (e.g., `Bash`, `Read`, `Glob`, `Grep`, `Write`, `Agent`). No permission-rule syntax (`Bash(...)`) observed in agent frontmatter.
- **Pitfalls observed**: CHANGELOG v3.3.3 documents a regression from putting explicit `name:` fields in command frontmatter: "Claude Code uses the `name:` value as-is in autocomplete, bypassing automatic `craftsman:` prefix. Without `name:`, Claude Code derives from filename and correctly shows `/craftsman:setup` instead of `/setup`. Aligns with official plugin conventions (vercel, metrikia, stripe all omit `name:`)." So current convention: OMIT `name:` from command frontmatter to get automatic plugin-namespacing. CHANGELOG v3.3.2 also records an absolute-symlink regression (`commands/knowledge.md` was an absolute symlink, broken on other machines — restored to relative). `mcpServers` being inline in plugin.json rather than in a `.mcp.json` companion means the MCP server is bundled with the plugin manifest rather than composable. Presence of `teams/` and `output-styles/` directories points to experimental component surfaces not in the plugin reference.

## 6. Dependency installation

- **Applicable**: partial — the plugin itself is pure bash+Python+Markdown with no `requirements.txt` / `pyproject.toml` / root `package.json`. However, `packs/ai-ml/mcp/knowledge-rag/` ships a Node MCP server (referenced from `mcpServers.knowledge-rag.command: "node"` and `args: ["packs/ai-ml/mcp/knowledge-rag/start.mjs"]`), and `.claude-plugin/ignore` excludes `packs/*/mcp/*/node_modules/` — implying a node_modules tree must exist locally but is not installed by the plugin itself.
- **Dep manifest format**: none at plugin root. Pack-level `packs/ai-ml/mcp/knowledge-rag/` is a Node module (implicit `package.json` inferred from `.mjs` extension and `node_modules/` ignore rule), not fetched.
- **Install location**: n/a — no SessionStart dep-install hook. `CLAUDE_PLUGIN_DATA` is used for runtime state (`session-state.json`, `metrics.db`) — not for dependencies.
- **Install script location**: n/a.
- **Change detection**: n/a.
- **Retry-next-session invariant**: n/a.
- **Failure signaling**: n/a.
- **Runtime variant**: Python3 used for helper scripts (`hooks/lib/session_state.py`, `metrics-query.py`, `yaml-parser.py`) — invoked via `python3` on system PATH with graceful degradation when absent (`HAS_PYTHON3=true; command -v python3 >/dev/null 2>&1 || HAS_PYTHON3=false`). No `uv`, no venv, no pip. Pack MCP server uses `node` on system PATH, not bundled.
- **Alternative approaches**: none — plugin assumes `python3`, `jq`, `bash 3.2+`, and (optionally) `node`, `phpstan`, `eslint`, `deptrac`, `dependency-cruiser`, `shellcheck` are already installed on the host. Graceful degradation is the install story: features light up when their required tool is present.
- **Version-mismatch handling**: no Python venv, so no minor-version tracking needed. README.md declares "Claude Code v1.0.33 or later" as host-version floor.
- **Pitfalls observed**: MCP server shipped under `packs/ai-ml/mcp/knowledge-rag/` has no install/bootstrap — if a user enables the ai-ml pack without running `npm install` in that subdirectory manually, the MCP server fails at stdio connect time. No hook primes node_modules; `.claude-plugin/ignore` excludes node_modules from the distributed archive so users would need to run `npm install` themselves post-clone.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/craftsman-ci` (225 bytes) and `bin/craftsman-validate` (380 bytes) are thin exec-wrappers around internal scripts, exposed as bare commands in the Bash tool.
- **`bin/` files**:
  - `craftsman-ci` — `exec bash "$(cd "$(dirname "$0")/.." && pwd)/ci/craftsman-ci.sh" "$@"` (delegates to `ci/craftsman-ci.sh`, the 20 KB multi-provider CI pipeline script).
  - `craftsman-validate` — builds a JSON tool_input envelope via `jq -n` and pipes it into `hooks/post-write-check.sh`, letting a user run the same PostToolUse validator from a terminal: `jq -n --arg fp "$FILE" '{"tool_input":{"file_path":$fp}}' | bash .../hooks/post-write-check.sh`.
- **Shebang convention**: `env bash` (both wrappers start `#!/usr/bin/env bash`).
- **Runtime resolution**: script-relative only — `$(cd "$(dirname "$0")/.." && pwd)` resolves the plugin root from the bin script's own path. No `${CLAUDE_PLUGIN_ROOT}` reference, no pointer file.
- **Venv handling (Python)**: n/a (these wrappers shell out to bash scripts, not Python).
- **Platform support**: bash-only, no `.cmd` or `.ps1` companions — POSIX/nix only.
- **Permissions**: GitHub API doesn't expose mode directly via the contents endpoint, but the CI `validate-shell-scripts` job runs a "Check scripts are executable" step that `exit 1`s if any listed script lacks `+x` — `hooks/*.sh` and `tests/run-tests.sh` are checked but `bin/*` is NOT in the checked list, so executability is not CI-enforced for the bin wrappers.
- **SessionStart relationship**: static — bin wrappers exist at rest, no hook writes or modifies them. Separately, `session-start.sh` generates a different runtime wrapper at `~/.claude/craftsman-set-verified.sh` (a per-session wrapper with baked-in `CLAUDE_PLUGIN_ROOT`, so skills running in Bash-tool context — where `CLAUDE_PLUGIN_ROOT` is absent — can still call the `session_state.py set-verified` command without path resolution).
- **Pitfalls observed**: `craftsman-validate` reconstructs the PostToolUse JSON input envelope by hand (`{"tool_input": {"file_path": ...}}`) — works today but drifts if the Claude Code hook input schema changes. The generated `~/.claude/craftsman-set-verified.sh` wrapper is rebuilt on every SessionStart, so stale copies from old plugin versions are silently overwritten — but test-suite pollution caused v3.3.5 bug ("Tests calling `session-start.sh` overwrote `~/.claude/craftsman-session-state-path` with temp paths, corrupting the real session's bridge file") — tests need backup/restore guards around SessionStart execution.

## 8. User configuration

- **`userConfig` present**: yes.
- **Field count**: 7 fields — `strictness` (string, default "strict"), `stack` (string, default "fullstack"), `agent_hooks` (boolean, default true), `packs` (string, default ""), `sentry_org` (string, no default), `sentry_project` (string, no default), `sentry_token` (string, no default, **`sensitive: true`**).
- **`sensitive: true` usage**: correct — `sentry_token` explicitly flagged; description says "stored securely in keychain". Other secret-shaped fields (`sentry_org`, `sentry_project`) are non-secret slugs and correctly not flagged.
- **Schema richness**: typed — every field declares `type` (string/boolean), most declare `title`, `description`, and `default`. This is a rich schema by plugin-reference standards.
- **Reference in config substitution**: `CLAUDE_PLUGIN_OPTION_<KEY>` env-var form used — `agent-ddd-verifier.sh` gates on `"${CLAUDE_PLUGIN_OPTION_agent_hooks:-true}" == "false"` (early-exit if user disabled agent hooks). No `${user_config.KEY}` tokens in hook commands. `config.sh` library presumably reads `.craft-config.yml` (separate YAML-based project config) for strictness/stack — userConfig is separate from the project-level config file.
- **Pitfalls observed**: two parallel config sources — plugin userConfig (claudec settings) AND `.craft-config.yml` (project YAML). `session-start.sh` warns when they mismatch: "detected 'fullstack' but config says 'symfony'. Run /craftsman:setup to update." Overlapping concerns can drift without a single source of truth. Sentry secret stored via Claude Code's secure storage (`sensitive: true`) but the hook reading the token was not observed in the WebFetch budget — assumed to happen in `agent-sentry-context.sh`.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 2 matchers in hooks.json —
  - `matcher: "Write|Edit"` → `pre-write-check.sh` (5.3 KB, layer-import validation on PHP/TS/TSX before write, LAYER001-003 and PHP001 rules, `exit 2` to block).
  - `matcher: "Bash"`, `if: "Bash(git push*)"` → `pre-push-verify.sh` (2.3 KB, warns when `/craftsman:verify` has not run; v3.4.3 downgraded from blocking to warning). This is a rare example of the **conditional matcher syntax** — `"if": "Bash(git push*)"` is a permission-rule-style guard that further narrows a `matcher: "Bash"` PreToolUse handler to git-push-shaped commands only.
- **PostToolUse hooks**: 2 matchers —
  - `matcher: "Write|Edit"` → `post-write-check.sh` (13.5 KB, full rules engine with correction-learning, cross-file pattern detection, `exit 2` blocks, stderr human + stdout JSON).
  - `matcher: "Bash"` → `post-bash-test-verify.sh` (1.5 KB, `async: true`, matches `run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test` on exit 0 and auto-sets `verified=true` to unblock subsequent git-push).
- **PermissionRequest/PermissionDenied hooks**: absent — only the built-in hook events are used. Also uses `PostToolUseFailure` matching `Write|Edit|Bash` → `tool-failure-tracker.sh` (async), `FileChanged` matching `*.php|*.ts|*.tsx` → `file-changed.sh` (async), `SubagentStop` → `subagent-quality-gate.sh` (async), `InstructionsLoaded` → `agent-structure-analyzer.sh`, `UserPromptSubmit` → `bias-detector.sh`, `PreCompact`/`PostCompact`/`Stop`/`SessionStart`/`SessionEnd` — 14 total hook entries across 12 distinct event types.
- **Output convention**: stderr human + stdout JSON. `post-write-check.sh` CHANGELOG v3.4.4 notes: "When `post-write-check.sh` or `pre-write-check.sh` blocks a write, a human-readable violation summary is now emitted on stderr (displayed in Claude Code UI). Previously only JSON was written to stdout, resulting in an unhelpful 'No stderr output' message." So both surfaces are written: stderr shows `🚫 BLOCKED by AI Craftsman — N violation(s):` with bulleted `✗` lines and a `Fix these or add: // craftsman-ignore: <RULE_ID>` footer, while stdout emits `{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: "BLOCKED: ..."}}` consumed by Claude. Warning-only (non-blocking) exits use `{systemMessage: "WARNINGS: ..."}` on stdout.
- **Failure posture**: fail-open, documented centrally. Every hook opens with `set -uo pipefail` (note: `-u -o pipefail` but NOT `-e`) and `trap 'echo "WARNING: hook.sh failed at line $LINENO" >&2; exit 0' ERR` — on crash, the hook emits a warning to stderr but exits 0 so writes/pushes are never blocked by bugs in the hook itself. CLAUDE.md codifies: "All hook scripts MUST use `exit 0` (pass) or `exit 2` (block). NEVER `exit 1`." SECURITY.md restates this as a hook security guarantee.
- **Top-level try/catch wrapping**: observed — the `trap ... ERR` pattern is effectively bash's try/catch around the script body.
- **Pitfalls observed**: the conditional matcher (`"if": "Bash(git push*)"` inside a PreToolUse `matcher: "Bash"` entry) is a high-value pattern for narrowing Bash hooks to specific command shapes, but it relies on the plugin-reference permission-rule syntax being interpreted at hook-matcher time — if a future Claude Code version changes how `if` is parsed, the hook silently stops firing. No fallback matcher guards the skill if `if:` support regresses. The 14-event hooks.json includes `PostToolUseFailure` (added in v3.4.1 per CHANGELOG to the CI validator's VALID_HOOK_EVENTS list — prior releases would have failed CI on this event), so this plugin is near the leading edge of event-coverage.

## 10. Session context loading

- **SessionStart used for context**: yes — `hooks/session-start.sh` emits a `systemMessage` JSON payload with the active profile (`Craftsman active | Stack: fullstack | Strictness: strict | PHP rules: ON | TS rules: ON | Metrics: initialized | PACKS: ai-ml,bash,python,react,symfony | ...`), plus correction-learning trends from past sessions (`Learning: PHP001 fix rate 78%`), a healthcheck summary (`Healthcheck: session-bridge OK, ...`), and a full command routing table (`ROUTING` block).
- **UserPromptSubmit for context**: yes but NOT for loading context — `bias-detector.sh` inspects each user prompt for cognitive biases (acceleration, scope creep, over-optimization, missing-design) and emits non-blocking warnings via `{systemMessage: ...}`.
- **`hookSpecificOutput.additionalContext` observed**: yes in `pre-push-verify.sh` (`{hookSpecificOutput: {hookEventName: "PreToolUse", additionalContext: "WARNING: ..."}}`) and `post-write-check.sh` (PostToolUse form, see §9). `session-start.sh` and `bias-detector.sh` use `systemMessage` (the broader form) instead.
- **SessionStart matcher**: none (no matcher key on the SessionStart hook entry, so it fires on all SessionStart sub-events: startup/clear/compact).
- **Pitfalls observed**: session-start.sh writes a bridge file `~/.claude/craftsman-session-state-path` containing the resolved `CLAUDE_PLUGIN_DATA` path, AND generates `~/.claude/craftsman-set-verified.sh` — both outside the plugin-managed storage area. This side-effect-at-startup pattern caused v3.3.5 test-pollution bug and v3.2.3 "bridge desync" bug (fixed by introducing the bridge file pattern, then hardened by the set-verified wrapper). The bridge-file indirection is necessary because `CLAUDE_PLUGIN_DATA` is not exposed to skills running via the Bash tool.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none — the plugin does not use the `monitors` component.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable for monitors. Host-version floor for the plugin overall: "Claude Code v1.0.33 or later" stated in README.md (under Requirements) and enforced only by documentation, not by manifest.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace. Tags follow `vX.Y.Z` form (v1.2.1 through v3.4.4, 30 tags).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: bash scripts only — `tests/run-tests.sh` (19 KB) is the single entry point, with subdirectories `tests/hooks/`, `tests/ci/`, `tests/core/`, `tests/lib/`, `tests/packs/`, `tests/templates/` each holding their own `.sh` test files (hierarchical bash-script test suite, no pytest/unittest/jest).
- **Tests location**: `tests/` at repo root, excluded from distribution via `.claude-plugin/ignore`.
- **Pytest config location**: not applicable — no Python tests.
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/ci.yml` (18.3 KB, single workflow).
- **CI triggers**: `push: branches: [main, develop]` + `pull_request: branches: [main]`.
- **CI does**: 9 jobs in a dependency DAG —
  1. **secrets-scan** — runs `.github/scripts/secrets-scan.sh` (5.5 KB, git-history+current-file scanner for OpenAI `sk-*`, AWS `AKIA*`, GitHub `ghp_*`/`github_pat_*`, Anthropic `sk-ant-*`, local filesystem paths `/Users/*` and `/home/*`, `.env`/`.pem`/`.key`/`id_rsa` tracked filenames, private IPs with warn severity). Full git history scan (`fetch-depth: 0`). Seed job — all other jobs `needs: [secrets-scan]`.
  2. **validate-json** — Python3 `json.load()` round-trip on `hooks/hooks.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.
  3. **validate-hooks-schema** — inline Python3 validator asserting hook event names are in a 13-entry `VALID_HOOK_EVENTS` set (SessionStart/PreToolUse/PostToolUse/PostToolUseFailure/SubagentStop/PreCompact/PostCompact/UserPromptSubmit/FileChanged/Notification/InstructionsLoaded/Stop/SessionEnd), hook types are in `["command", "agent"]`, agent hooks declare `prompt`, agent `model` is one of `["haiku", "sonnet", "opus"]`. Added `PostToolUseFailure`, `SubagentStop`, `PreCompact`, `PostCompact` in v3.4.1 patch.
  4. **validate-plugin-manifest** — inline Python3 asserting required fields `["name", "description", "version"]`, `repository` is string not object, version matches `^\d+\.\d+\.\d+(-[\w.]+)?$`.
  5. **validate-shell-scripts** — three stages: bash `-n` syntax check, executable-permission check, `shellcheck -x` lint (warning-only, doesn't fail the job). Operates on an explicit allowlist of 8 scripts.
  6. **validate-skills** — traverses `skills/`, validates each SKILL.md has YAML frontmatter with `name:`, `description:`, `model:` (exception for `session-init`). Recognizes namespace directories (parent containing SKILL.md subdirs) and recurses.
  7. **validate-knowledge-base** — checks `knowledge/patterns.md`, `knowledge/principles.md`, `knowledge/anti-patterns/` exist, and at least one `packs/*/knowledge/canonical/` directory exists (noted as "moved from core in v2.4.0").
  8. **run-tests** — `needs: [validate-json, validate-shell-scripts]`, runs `./tests/run-tests.sh`.
  9. **check-agents** — validates `agents/*.md` have YAML frontmatter with `name:` field.
  10. **summary** — `needs: [all above]`, `if: always()`, aggregates results and fails if any upstream failed.
- **Matrix**: none — all jobs on `ubuntu-latest` / Python 3.12 single target.
- **Action pinning**: major-version tag pinning (`actions/checkout@v4`, `actions/setup-python@v5`) — not SHA-pinned.
- **Caching**: none — no `actions/cache` steps, no `cache: 'pip'` / `cache: 'npm'` hints on setup-python.
- **Test runner invocation**: direct `./tests/run-tests.sh` bash execution (chmod +x first).
- **Pitfalls observed**: the hardcoded script allowlists in validate-shell-scripts and the hooks/*.sh list in the ShellCheck step are fragile — adding a new hook requires editing ci.yml too. Skills frontmatter check is grep-based (`grep -q "^name:"` / `grep "^model:"`), not YAML-parsed, so quoted values or multi-line descriptions could produce false negatives. `validate-knowledge-base` has a subtle count bug (`count=$(find ... | wc -l)` — the variable is echoed but never compared to a minimum, so an empty directory with zero files would still pass the `[ -d "$KNOWLEDGE_DIR/anti-patterns" ]` existence check).

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — no dedicated release workflow, no `workflow_dispatch` trigger, no `release: [published]` handler.
- **Release trigger**: not applicable — releases are created manually. `scripts/bump-version.sh` explicitly prints the manual next-steps: `git add -A && git commit -m 'chore: bump version to X'; git tag vX; git push origin main && git push origin vX`. GitHub Releases (if present) are created through the GitHub UI.
- **Automation shape**: none.
- **Tag-sanity gates**: none automated — version lockstep between 6 files is enforced only by `bump-version.sh` discipline on the author's side.
- **Release creation mechanism**: manual `git tag` + GitHub UI.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: no — CHANGELOG.md is authored in Keep-a-Changelog v1.1.0 format (`## [3.4.4] — 2026-04-06` / `### Fixed` / `### Added` / `### Changed` / `### Removed` sections), linked explicitly in the CHANGELOG header ("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)"), but no CI job consumes it.
- **Pitfalls observed**: 30 tags with no automation to guarantee tag == plugin.json version — a human-forgetting-to-tag or wrong-commit-tag failure is silent. Rich CHANGELOG is a human-written artifact with no validator; release notes on GitHub would need manual copy-paste.

## 15. Marketplace validation

- **Validation workflow present**: yes — `validate-plugin-manifest`, `validate-hooks-schema`, `validate-json`, `validate-skills`, `check-agents`, `validate-knowledge-base` jobs in ci.yml together constitute one of the most comprehensive manifest-validation surfaces observed across the sample.
- **Validator**: Python 3.12 inline scripts (heredoc Python in ci.yml), not a dedicated library. No `bun+zod`, no `claude plugin validate` CLI, no pre-commit hook.
- **Trigger**: same as CI — `push` main/develop + `pull_request` to main.
- **Frontmatter validation**: yes — grep-based for `name:`/`description:`/`model:` in `skills/*/SKILL.md` and `agents/*.md`. Grep-based (not YAML-parsed), so partial; still catches missing-fields.
- **Hooks.json validation**: yes — deep: validates event names, hook types, `command` vs `agent` subtype requirements, agent model values. Most thorough hooks validator observed so far.
- **Pitfalls observed**: validator is inline in ci.yml rather than a tracked Python script — diffs on validation rules appear as ci.yml diffs, which is worse for review. Update cadence: v3.4.1 patch specifically added 4 hook events to VALID_HOOK_EVENTS — the validator itself needed a patch release because it was stricter than the runtime.

## 16. Documentation

- **`README.md` at repo root**: present (27.7 KB — substantial). Opens with badge row (License, Claude Code compat, Version, Commands count, Agents count, PRs Welcome), tagline "Transform Claude into a disciplined Senior Software Craftsman", ToC links (Installation, Skills, Security, Contributing). Sections cover Requirements, Installation (From GitHub + From Local Path + Verify), API Cost Model (explicit Haiku-call cost disclosure: ~$0.15-0.30/session), Quick Start with command examples, "Why Craftsman? — 6 Core Differentiators" marketing section, Additional Features, and links to examples.
- **Owner profile README at `github.com/BULDEE/BULDEE`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: n/a — single-plugin marketplace; the root README serves the one plugin.
- **`CHANGELOG.md`**: present (41 KB) — Keep a Changelog v1.1.0 format, explicit SemVer adherence, dated entries for every version from v1.2.1 forward. Very detailed fix/change narratives — CHANGELOG entries routinely reference ADRs (e.g., "See [ADR-0013](docs/adr/0013-workflow-orchestrator.md)").
- **`architecture.md`**: absent. Architectural content is embedded inline in CLAUDE.md ("## Architecture" section with directory tree + role annotations) and distributed across 15 ADRs under `docs/adr/`.
- **`CLAUDE.md`**: present at repo root (5 KB) — project instructions oriented toward agents contributing to the plugin itself. Covers Development Rules (exit codes, JSON output, atomic SQLite writes, adapter interface), Testing commands, 6 Key Differentiators, Architecture directory tree, Version Sync Checklist.
- **Community health files**: `SECURITY.md` (5.5 KB, security policy with per-hook security table and what-the-plugin-does/doesn't-do bullets — explicit trust surface), `CONTRIBUTING.md` (4.3 KB, bug report template, PR steps, Conventional Commits guidance, command/agent development standards), `CODE_OF_CONDUCT.md` (2.1 KB), and `.github/PULL_REQUEST_TEMPLATE.md` + `.github/ISSUE_TEMPLATE/` directory. Complete community-health surface.
- **LICENSE**: present — Apache-2.0 (SPDX identifier).
- **Badges / status indicators**: observed — 6 shields.io badges (License, Claude Code compat, Version, Commands count, Agents count, PRs Welcome). No CI status badge despite CI being present.
- **ADR directory**: `docs/adr/` with 15 ADRs (0000-template + 0001 through 0014), Nygard-style format (Status/Date/Context/Decision/Consequences). Topics: skills-over-prompts, ollama-over-openai, sqlite-over-pgvector, 3p-agent-pattern, knowledge-first-architecture, project-specific-knowledge, commands-over-skills, inline-sqlite-over-bash-expansion, command-hooks-over-agent-hooks, model-tiering, context-fork-strategy, progressive-disclosure, workflow-orchestrator, quick-setup-mode. ADRs are routinely referenced from CHANGELOG entries.
- **Pitfalls observed**: no architecture.md at root despite substantial internal structure — structural docs are split between CLAUDE.md's "Architecture" section (directory tree only) and the 15 ADRs (decision rationale). A first-time reader needs to reconcile both. Missing CI status badge hides a highly useful signal given the rich CI surface. `docs/superpowers/` appears in `.claude-plugin/ignore`'s exclusion list but the WebFetch budget didn't surface its contents — possibly internal-only marketing material.

## 17. Novel axes

Patterns not cleanly covered by purposes 1-16:

- **Hook `if:` conditional sub-matcher**: `pre-push-verify.sh` is registered under `matcher: "Bash"` with an additional `"if": "Bash(git push*)"` field that narrows the handler to git-push-shaped bash commands only, using the same permission-rule syntax documented for the `permissions.allow` / `deny` system. This is the first observed use of `if:` as a sub-matcher on a hook registration — far more precise than alternatives (matching all Bash commands and re-parsing the command string inside the hook). Candidate for a new pattern-doc row on hook matcher granularity.
- **SessionStart-generated runtime wrappers at well-known stable paths**: `session-start.sh` writes TWO files outside the plugin-managed data dir on every session: `~/.claude/craftsman-session-state-path` (path-bridge file) and `~/.claude/craftsman-set-verified.sh` (executable wrapper with the plugin's resolved lib path baked in). Motivation: skills running in Bash-tool context do not receive `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA`, so they cannot locate sibling resources. The bridge-file + generated-wrapper pattern is a workaround for the Bash-tool-context environment-variable gap. Candidate pattern: "Bash-tool-context bridge via SessionStart-generated artifacts."
- **`bin/` wrappers as plugin-exposed CLIs**: `craftsman-ci` and `craftsman-validate` are thin exec-wrappers that make internal scripts invokable as bare commands from the Bash tool (Claude Code adds `bin/` to PATH when a plugin is enabled). `craftsman-validate` notably reconstructs the PostToolUse input envelope via `jq -n` so a single implementation (`post-write-check.sh`) serves both the hook invocation and the CLI invocation — "one implementation, two surfaces."
- **Dual validation surface for the same rules engine**: `ci/craftsman-ci.sh` (pipeline-mode CI) and `hooks/post-write-check.sh` (real-time-mode hook) both source `hooks/lib/pack-loader.sh` and `hooks/lib/rules-engine.sh`. README's §5 calls this "zero drift" — same rules engine invoked at two different lifecycle points, with adapter pattern (`adapter_detect/run/annotate/comment/exit`) providing four CI-provider implementations (GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins). Candidate: a "rules-engine-shared-between-hook-and-CI" axis.
- **Correction-learning SQLite with session-to-session memory**: `session-state.json` + `metrics.db` track violation fixes across sessions. SessionStart injects a `Learning: ...` clause in the systemMessage derived from correction trends. README positions this as "unique in the ecosystem — no other Claude Code plugin creates this behavioral feedback loop." Persistence is local per-machine — no cloud sync.
- **Cross-file pattern detection inside a hook**: `post-write-check.sh` consults `session-state.json` after recording a violation and, if the same rule has fired in 3+ files this session, appends "PROJECT-WIDE PATTERN: {rule} found in {N} files — consider a project-wide fix or global craftsman-ignore" to the block/warn message. This is a rule-engine feature delivered through hook output, not a standalone tool. Candidate axis: "session-aware violation aggregation."
- **Non-standard component surfaces**: `teams/wizard.md` (3.5 KB) and `setup/templates/` — these don't correspond to any component type in the plugin reference. Possibly experimental/forward-looking, possibly consumed only by the plugin's own commands. Worth flagging as "unofficial component experimentation."
- **Per-rule inline suppression comments**: `craftsman-ignore: <RULE_ID>` or multi-rule `craftsman-ignore: PHP001, TS001, LAYER001` comments inside source files disable specific rules on that line or file (`line_has_ignore` and `file_has_ignore` helpers). Metrics record both "blocked violations" and "ignored violations" — partial suppression is a first-class concept, not a workaround.
- **Auto-verify via PostToolUse[Bash] pattern**: `post-bash-test-verify.sh` watches for successful test-runner invocations on stdin's `.tool_result.exit_code == 0` and matches a regex against common test-runner commands (`run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test`); on match, it flips the session's `verified=true` flag so the subsequent `git push` PreToolUse hook allows the push without friction. Emergent workflow: "test-then-push unlocks push automatically." Candidate axis: session-state state machines driven by tool-outcome observation.
- **PostToolUseFailure event**: registered with `matcher: "Write|Edit|Bash"` to record tool failures into metrics. This event isn't in the baseline plugin-reference hook list and was added to CI's `VALID_HOOK_EVENTS` only in v3.4.1 — plugin is on the leading edge of event coverage.
- **Keep-a-Changelog strictness**: CHANGELOG.md explicitly declares the format in its header and maintains it through 30 versions — one of the most discipline-adherent CHANGELOG surfaces in the sample.
- **Nygard-style ADR discipline**: 15 ADRs under `docs/adr/` with consistent structure (Status/Date/Context/Decision/Consequences) and cross-references from CHANGELOG entries — unusually strong design-decision capture for a plugin of this size.
- **Graceful degradation as core install story**: with no dependency installer at all, the plugin uses Level 1 (regex-only validation) as the baseline; Level 2 (PHPStan, ESLint) and Level 3 (deptrac, dependency-cruiser) features light up only when those tools happen to be installed. README explicitly documents the degradation ladder as a design feature rather than a caveat.
- **Six-location version sync enforced by a standalone script**: `scripts/bump-version.sh` touches `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (2 occurrences), `ci/craftsman-ci.sh`, `README.md` (badge), `CLAUDE.md` (Current version string), `tests/ci/test-adapters.sh` (mock report versions). CLAUDE.md has a "Version Sync Checklist" listing all six. Candidate pattern: "many-file version sync via a project-local script."
- **Explicit API-cost model in README**: the "API Cost Model" section quantifies the agent-hook cost at ~$0.15-0.30 per session with a per-hook breakdown table, and provides an explicit opt-out (`agent_hooks: false`). Rare for plugins to publish cost transparency — candidate axis: "runtime cost disclosure."
- **`.claude-plugin/ignore` for distribution exclusion**: 14-line ignore file listing heavy dependencies (`packs/*/mcp/*/node_modules/`, `packs/*/mcp/*/dist/`), dev-only dirs (`tests/`, `scripts/`, `examples/`, `docs/superpowers/`), CI artifacts, and selected docs (`BRUTAL-EVALUATION-PROMPT.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`). Indicates the plugin archive served to users is a curated subset of the repo — a distribution-shaping mechanism distinct from `.gitignore`.

## 18. Gaps

Budget-bounded unknowns and the source that would resolve them:

- **Actual commit that set mode on `bin/*` wrappers**: the CI `validate-shell-scripts` job does not include `bin/*` in its executable-permission check. Running `gh api repos/BULDEE/ai-craftsman-superpowers/git/trees/HEAD:bin --jq '.tree[] | {path, mode}'` would expose the permission bits. Not fetched in this budget.
- **Full `hooks/lib/*.sh` and `hooks/lib/*.py` contents**: the 14 files under `hooks/lib/` (including `rules-engine.sh` at 17.6 KB, `session_state.py` at 12.5 KB, `yaml-parser.py` at 8 KB) encode the actual validation logic. Only size + file listing captured. Reading these would nail down rule-id taxonomy, metrics schema, and correction-learning state shape.
- **`ci/craftsman-ci.sh` body and `ci/adapters/`**: the 20 KB craftsman-ci script and its per-provider adapters (`ci/adapters/` subdir — contents not fetched) are the concrete implementation of the §17 "same rules engine for hooks and CI" claim. Reading them would confirm whether adapter interface is truly `detect/run/annotate/comment/exit` as CLAUDE.md states.
- **Test-suite internals**: `tests/run-tests.sh` is 19 KB and dispatches into `tests/{core, ci, lib, packs, hooks, templates}/`. Structure described at index level only. Would clarify whether pure-bash testing is the team's intentional stance or a temporary scaffold.
- **`packs/*` structure detail**: 5 packs listed (ai-ml, bash, python, react, symfony). `packs/ai-ml/mcp/knowledge-rag/start.mjs` referenced from plugin.json but not opened; the pack commands symlinked into `commands/knowledge.md` (relative symlink restored in v3.3.2) would reveal how pack-to-core integration works in practice.
- **Individual agent/command frontmatter audit**: 11 agents and 21 commands exist; only 3 agent headers (architect, team-lead, security-pentester) and 2 command headers (design, git) were sampled. A full audit would confirm the no-`name:` convention and consistent `effort:` use across the fleet.
- **GitHub Releases vs raw tags**: whether tags correspond to published GitHub Releases with release notes, or are bare tags with CHANGELOG as the only narrative, wasn't checked. `gh api repos/BULDEE/ai-craftsman-superpowers/releases` would answer.
- **Actual network behavior of agent-sentry-context.sh and agent-structure-analyzer.sh**: SECURITY.md's hook table claims these are READ-ONLY but "via MCP" — meaning they call an MCP server on network. The MCP configuration for Sentry and the invocation pattern weren't fetched.
