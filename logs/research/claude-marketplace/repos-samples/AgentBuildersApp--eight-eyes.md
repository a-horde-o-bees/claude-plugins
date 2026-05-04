# AgentBuildersApp/eight-eyes

## Identification

- **URL**: https://github.com/AgentBuildersApp/eight-eyes
- **Stars**: 2
- **Last commit date**: 2026-04-01 (commit `e13ac412`, pushed 04:16:29Z)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: primary (community)
- **One-line purpose**: "Eight constrained reviewers. Each scoped to a different failure surface. Hook-enforced walls, not just prompts." — multi-agent code-review plugin for Claude Code, Copilot CLI, and Codex CLI, with 8 role subagents whose tool scope is enforced by PreToolUse / PostToolUse / SubagentStop hooks.

## 1. Marketplace discoverability

- **Manifest layout**: two `marketplace.json` copies — canonical at `.claude-plugin/marketplace.json`, duplicate at `.github/plugin/marketplace.json`. Both carry identical content (same name, same metadata, same single plugin entry). Single plugin pointing at `./` (repo root as the plugin).
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — `description: "Multi-agent code review for Claude Code, Copilot CLI, and Codex CLI"`, `version: "4.2.0"`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: category + keywords + tags — `category: "code-quality"`, `keywords: ["code-review","multi-agent","security","testing","accessibility","tdd","blind-review"]`, `tags: ["review","security-audit","performance","accessibility","documentation"]`. Single plugin, so "all same" is moot.
- **`$schema`**: absent.
- **Reserved-name collision**: no (plugin is `8eyes`, marketplace is `8eyes-marketplace`).
- **Pitfalls observed**: duplicate manifest in `.github/plugin/marketplace.json` has no obvious consumer (Claude Code reads `.claude-plugin/marketplace.json`); likely vestigial or aspirationally aimed at a GitHub Pages / Copilot discovery path. No sync mechanism visible in hooks or CI — the two files must be edited in lockstep manually. Both contain a `_description` private key (`"_description": "Marketplace discovery metadata"` / `"Plugin manifest and marketplace metadata"`) not part of the documented schema — harmless but noise.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"`. The repo root *is* the plugin.
- **`strict` field**: absent (default implicit true).
- **`skills` override on marketplace entry**: absent.
- **Version authority**: drift — **three-way version split** observed:
    - `.claude-plugin/plugin.json` → `5.0.0-alpha`
    - `.claude-plugin/marketplace.json` plugin entry version → `4.2.0`
    - `.claude-plugin/marketplace.json` metadata.version → `4.2.0`
    - `VERSION` file → `5.0.0-alpha`
    - `pyproject.toml` version → `5.0.0a1` (PEP 440 equivalent)
    - Git tag → `v5.0.0-alpha` (only tag present, pre-release on GitHub Releases)
    - CHANGELOG.md top entry → `5.0.0-alpha`
- **Pitfalls observed**: the marketplace.json entries are stale at 4.2.0 while the rest of the repo has advanced to 5.0.0-alpha. Consumers installing via `claude plugin install 8eyes@8eyes-marketplace` will see "4.2.0" in the marketplace entry but the plugin.json they receive advertises "5.0.0-alpha" — mid-release inconsistency. The marketplace version appears to only get bumped on stable releases while `plugin.json`/`VERSION`/`pyproject.toml` track alpha/dev state. No sync script, no pre-commit hook, no CI validation catches this — it's a pure manual-discipline drift surface.

## 3. Channel distribution

- **Channel mechanism**: no split (single `8eyes-marketplace` name; users pin by `@ref` via `claude plugin marketplace add AgentBuildersApp/eight-eyes`, which resolves to default branch HEAD).
- **Channel-pinning artifacts**: absent — no `stable-*`/`latest-*` pair, no dev-counter split.
- **Pitfalls observed**: the `v5.0/foundation-hardening` branch exists alongside `main` but is not used as a long-lived release-branch channel — it looks like an in-flight feature branch that happened to be pushed. Users on `main` receive the alpha directly; there is no stable channel to fall back to.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main — single tag `v5.0.0-alpha` at commit `f3c1075a`, which is three commits back from `HEAD` (`e13ac412`). Tag is not at tip; newer work on main is untagged.
- **Release branching**: minimal — one side branch `v5.0/foundation-hardening` visible but no evidence of long-lived `release/*` pattern.
- **Pre-release suffixes**: `-alpha` observed (both in git tag and `plugin.json`). PEP 440 form `5.0.0a1` used in `pyproject.toml`. CHANGELOG heading is `5.0.0-alpha`. GitHub Releases marks the release as `prerelease: true`.
- **Dev-counter scheme**: absent — no `0.0.z` counter, no automatic dev bump.
- **Pre-commit version bump**: no (no `.pre-commit-config.yaml`, no `.githooks/` directory, no evidence in CI of version auto-bump).
- **Pitfalls observed**: the `-alpha` suffix in `plugin.json` is notable — Claude Code's plugin semver parsing is undocumented for pre-release suffixes, so consumers may not reliably sort `5.0.0-alpha` vs `4.2.0`. The mismatch between `plugin.json` (`5.0.0-alpha`) and the marketplace entry (`4.2.0`) compounds this: if Claude Code compares marketplace entries by version string, `4.2.0` sorts above `5.0.0-alpha` for some implementations.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` has no `skills`/`commands`/`agents`/`hooks` arrays. Components are discovered by convention from `skills/`, `commands/`, `agents/`, `hooks/` directories at plugin root.
- **Components observed**:
    - skills: yes (`skills/collab/SKILL.md` with supporting `references/` and `schemas/`)
    - commands: yes (`commands/8eyes.md`, `commands/8eyes-copilot.md`)
    - agents: yes (8 `collab-*.md` agents in `agents/`)
    - hooks: yes (`hooks/hooks.json` with 7 hook-event registrations)
    - .mcp.json: no
    - .lsp.json: no
    - monitors: no
    - bin: no (the CLI shim `eight-eyes` is written to `~/.local/bin/` by `install.py --add-to-path`, not shipped as a `bin/` directory)
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `tools`, `background` (boolean), `isolation: worktree`, `effort` (low/medium), `maxTurns` (numeric). The `isolation: worktree` field is conspicuous — it claims per-role git-worktree isolation for the subagent, which the README reinforces: "Worktree isolation is used where incidental writes or tool artifacts would otherwise leak across roles." Not all agents use `background: true` — only read-only review roles (skeptic, security, performance, accessibility, docs). Implementer and verifier omit `background`.
- **Agent tools syntax**: plain tool names (comma-separated: `Read, Glob, Grep, LS, Bash`). No permission-rule syntax like `Bash(uv run *)` — Bash scoping is enforced by the PreToolUse hook instead of by frontmatter rules.
- **Pitfalls observed**: agent frontmatter uses `isolation: worktree`, `background: true`, `effort: medium`, `maxTurns: N` — these are not documented in the public Claude Code plugin reference at code.claude.com/docs/en/plugins-reference. If Claude Code ignores unrecognized frontmatter keys, the isolation/background behavior the README promises may not actually be enforced by the harness. The enforcement may be entirely in-hook (scope enforcement via PreToolUse), with frontmatter fields acting as aspirational / Copilot-adapter-specific metadata. Copilot adapter (`adapters/copilot_cli/agents/collab-*.agent.md`) duplicates the frontmatter with the same fields.

## 6. Dependency installation

- **Applicable**: no — "Python 100% stdlib. Do not add pip dependencies." (CONTRIBUTING.md). Badge on README: `dependencies-zero-brightgreen`. No `requirements.txt`, no `[project.dependencies]` in `pyproject.toml`. All hook scripts use only stdlib imports.
- **Dep manifest format**: `pyproject.toml` is present but declares **no** runtime dependencies — it exists for PyPI metadata (name, version, classifiers, URLs) and license, not for dep install. No `[tool.uv]` section, no `requirements.txt`.
- **Install location**: not applicable (no deps). However, plugin *itself* is installed to `~/.claude/plugins/eight-eyes/` (by `install.py`, as a symlink or copy from repo root).
- **Install script location**: `install.py` at repo root — a standalone Python script, not tied to a hook. Runs as `python3 install.py` with `--platform` / `--uninstall` / `--verify` / `--add-to-path` flags. Invoked manually by the user for Copilot CLI and Codex CLI platforms; for Claude Code, the marketplace install flow is preferred (`claude plugin install 8eyes@8eyes-marketplace`), with `install.py` as a manual fallback.
- **Change detection**: not applicable for deps. `install.py` uses `reset_directory()` (delete + recreate) for Copilot/Codex targets, and `link_or_copy()` (symlink preferred, copy fallback on OSError) for Claude Code target — idempotent by full-wipe.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: `install.py` prints `[OK]` / `[WARN]` / `[FAIL]` lines to stdout; exit 0 on success, 1 on failure. `repo_verify()` shells out to `scripts/collabctl.py --cwd . verify` and returns its exit code. SessionStart hook uses an explicit fail-open pattern: catches all exceptions, writes `[collab]` prefixed error + stack trace to stderr, attempts to ledger the error, returns 0 unconditionally.
- **Runtime variant**: not applicable (no deps). Python stdlib only; Python 3.10+ required.
- **Alternative approaches**: not applicable — this repo deliberately eschews the entire dep-management problem space. Worth noting as a counter-pattern for the dep-management section of the pattern doc.
- **Version-mismatch handling**: none needed (stdlib).
- **Pitfalls observed**: the "zero deps" discipline is load-bearing for the plugin's install story — it sidesteps `uv`/`pip` questions, venv placement, and Python-version ABI tracking entirely. The trade-off is that hook scripts implement their own JSON schema validation, YAML parsing (via custom mini-parser in `spec/` compile step), and circuit-breaker logic by hand — ~150K of test code to guard against regressions.

## 7. Bin-wrapped CLI distribution

- **Applicable**: partial — no shipped `bin/` directory in the repo. The `collabctl` CLI is distributed as `scripts/collabctl.py` (invoked as `python3 scripts/collabctl.py ...`). An opt-in shim is written to `~/.local/bin/eight-eyes` (or `~/.local/bin/eight-eyes.cmd` on Windows) when the user passes `install.py --add-to-path`.
- **`bin/` files**: none in-repo. Generated shim at install time: `~/.local/bin/eight-eyes` (bash, `exec python3 "<abs path to collabctl.py>" "$@"`) or `~/.local/bin/eight-eyes.cmd` (CMD, `@echo off\npython3 "<path>" %*`).
- **Shebang convention**: `env bash` for the POSIX shim; `.cmd` batch for Windows (no shebang). `collabctl.py` itself has no visible shebang in the fetched content; invoked as `python3 scripts/collabctl.py` by hooks, command docs, and install output.
- **Runtime resolution**: the generated shim hardcodes the absolute path to `collabctl.py` at install time. Hook scripts resolve via `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/...` in `hooks/hooks.json`. Copilot adapter uses `"$(dirname "$0")/../../hooks/scripts/..."` (script-relative) with a PowerShell sibling. Codex adapter writes absolute paths at install time.
- **Venv handling (Python)**: not applicable — no venv. System `python3` is invoked directly.
- **Platform support**: POSIX + Windows bash/PowerShell pair for Copilot; POSIX only for Codex hooks.json (no PowerShell variant). Windows considerations throughout `install.py`: `_on_rm_error` handler for locked `.git` objects, `msvcrt` file-locking mentioned in platform-notes table, `.cmd` shim for PATH.
- **Permissions**: shim at `~/.local/bin/eight-eyes` is chmod 0755 on non-Windows; `.cmd` on Windows gets default perms.
- **SessionStart relationship**: no hook builds or populates a bin directory. The shim is purely opt-in via `install.py --add-to-path`.
- **Pitfalls observed**: the two-track CLI distribution (in-repo `scripts/collabctl.py` vs optional user-PATH shim) means there's no deterministic `collabctl` name from a fresh install. README shows `python3 scripts/collabctl.py <verb>` everywhere, acknowledging this.

## 8. User configuration

- **`userConfig` present**: no — `plugin.json` has no `userConfig` field. All configuration is passed as CLI flags to `collabctl init` (`--objective`, `--allowed-path`, `--criterion`, `--verify-command`, `--model-map`, `--custom-role`, `--tdd`, etc.) or picked up from a `REVIEW.md` file in the project root.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable — no `${user_config.KEY}` anywhere; the plugin does not expose Claude Code's user-config substitution surface.
- **Pitfalls observed**: configuration is entirely runtime (per-mission, via flags) rather than install-time. This is a deliberate design choice (`--objective` belongs to each mission, not a global setting) but it means the plugin does not participate in Claude Code's user-config UI.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 registration, matcher `"Write|Edit|MultiEdit|Bash"`, runs `collab_pre_tool.py`. Purpose: block out-of-scope writes and unapproved Bash commands for read-only roles; enforce path scope (`allowed_paths`/`test_paths`/`doc_paths`) for writer roles. This is the primary trust anchor per the skill's Trust Boundaries section.
- **PostToolUse hooks**: 1 registration, matcher `"Write|Edit|MultiEdit|Bash"`, runs `collab_post_tool.py`. Purpose: compensating revert — if a write slips past PreToolUse for a read-only role, PostToolUse does `git checkout` for tracked files and deletes untracked files, ledgering a `scope_violation_reverted` event. Applies uniformly to built-in and custom read-only roles in v5.0 (a v4.x bug allowed custom roles to bypass this).
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON (pretool_deny payloads and hookSpecificOutput contexts are `json.dumps`'d and written to stdout); stderr for human-readable error logs and circuit-breaker messages.
- **Failure posture**: configurable per-mission via `manifest.fail_closed`. Default is fail-open (the legacy `_fail_open` helper, now partly superseded by the circuit breaker). When `fail_closed: true`, the `HookCircuitBreaker` with `failure_mode="deny"` retries twice (100ms, 500ms backoff) then emits a deny payload. Different hooks have different failure modes: pre_tool → `deny`, subagent_stop → `block`, stop → `warn`.
- **Top-level try/catch wrapping**: observed — every hook script wraps `_main()` in try/except and calls `_fail_open()` (or the circuit-breaker equivalent) on any exception. Double-defensive: even the ledger-write attempt inside the error handler is wrapped in its own try/except. Pattern is documented in `skills/collab/references/hook-failure-policy.md`.
- **Pitfalls observed**: the enforcement contract is treated as a first-class, inspectable artifact — `spec/enforcement.yaml` + `spec/enforcement_compiled.json` + the `collabctl capabilities` CLI verb that prints gate classes and failure modes as a table. Tests (`tests/test_collab_hooks.py`, 148 tests, ~126K) verify the contract against actual adapter manifests. This is a notable pattern: enforcement-as-data rather than enforcement-as-prose.

## 10. Session context loading

- **SessionStart used for context**: yes — `collab_session_start.py` reads active mission manifest from `<git-common-dir>/claude-collab/`, formats a "slim" mission summary, prepends a `[COLLAB WARNING]` if the mission is >12h old, and emits it as `hookSpecificOutput.additionalContext`.
- **UserPromptSubmit for context**: no (the hook is not registered in `hooks.json`).
- **`hookSpecificOutput.additionalContext` observed**: yes — via the `hook_context("SessionStart", summary)` helper in `collab_common`, which wraps `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`.
- **SessionStart matcher**: `"startup|resume|clear|compact"` — fires on all four sub-events. This is broader than the typical `startup|clear|compact` triad (adds `resume`) and notably does not pair with `UserPromptSubmit` for resumed sessions.
- **Pitfalls observed**: mission state lives under `git-common-dir/claude-collab/`, which survives across worktrees (deliberate — the coordinator, root checkout, and worktree-isolated roles share one manifest). The SessionStart hook reads `cwd` from the hook payload's JSON stdin and falls back to `.` — subtle. If the session starts outside a git repo, the hook exits 0 silently.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable — but the README's "Requirements" section declares Python 3.10+ and Git, with a platform-support table listing Claude Code (Full GA), Copilot CLI (Full GA), Codex CLI (Experimental).
- **Pitfalls observed**: the plugin does live notification work through ledger files (`<git-common-dir>/claude-collab/ledger.jsonl`), not through a `monitors.json`. Mission status is pulled via `collabctl status --json` on demand rather than pushed via a monitor.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; tag format is `v5.0.0-alpha`).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: unittest (stdlib). One giant file `tests/test_collab_hooks.py` (~126K, 148 tests per its own docstring, 152 per README). CONTRIBUTING.md recommends `python3 -m pytest tests/ -q` — pytest is supported via its unittest discovery, but the CI workflow uses `python -m unittest discover`.
- **Tests location**: `tests/` at repo root.
- **Pytest config location**: not applicable — no `pytest.ini`, no `[tool.pytest.ini_options]` in `pyproject.toml`. Tests run under unittest.
- **Python dep manifest for tests**: `pyproject.toml` (no test deps declared; tests are stdlib-only per project policy).
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/test.yml` (single workflow).
- **CI triggers**: `push: branches: [main]` and `pull_request: branches: [main]`.
- **CI does**: `python -m unittest discover -s tests -p 'test_*.py' -v`, then `python scripts/collabctl.py --cwd . verify` as a plugin-layout check. No linters, no type-checkers, no manifest schema validator.
- **Matrix**: OS × Python — `[ubuntu-latest, macos-latest, windows-latest]` × `['3.10', '3.11', '3.12']`. Notably no 3.13 in matrix even though README claims "3.10 through 3.13" support.
- **Action pinning**: tag — `actions/checkout@v4`, `actions/setup-python@v5`.
- **Caching**: none explicit (setup-python's built-in pip cache is irrelevant since no deps).
- **Test runner invocation**: direct `python -m unittest discover` in CI; `python3 -m pytest tests/ -q` suggested locally. No `scripts/test.sh` wrapper.
- **Pitfalls observed**: one monolithic ~126K test file for 148 tests contradicts the plugin's own Composability principle (files small enough for agents to consume in a single context) — but since the plugin targets stdlib-only Python and aggressively audits its own behavior, the monolith is presumably intentional for locality with helpers. README's "152 tests" claim vs docstring's "148 tests" is a minor drift.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — only `test.yml`.
- **Release trigger**: not applicable (no release workflow).
- **Automation shape**: manual — the single `v5.0.0-alpha` GitHub Release exists but was not created by a workflow. No `softprops/action-gh-release`, no `release-please`, no `gh release create` in any visible script.
- **Tag-sanity gates**: none — CI does not verify tag-on-main, tag-equals-package-version, or tag-format.
- **Release creation mechanism**: manual (GitHub UI or `gh release create` by hand).
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable (no automated release notes extraction).
- **Pitfalls observed**: the lack of release automation is why the `plugin.json`/`marketplace.json` version drift persists — there's no CI gate that would fail when `plugin.json.version != marketplace.json.plugins[0].version` or when the tag name mismatches either of them.

## 15. Marketplace validation

- **Validation workflow present**: no (dedicated validation workflow). The `test.yml` workflow's second step, `python scripts/collabctl.py --cwd . verify`, does check plugin layout (Claude Code `.claude-plugin/plugin.json`, `hooks/hooks.json`, Copilot `adapters/copilot_cli/plugin.json`, Codex `adapters/codex_cli/AGENTS.md` and `hooks.json`) but only for *file existence*, not for JSON schema conformance.
- **Validator**: custom — `scripts/collabctl.py verify` (a Python tool, not `bun+zod` or `claude plugin validate`). Also includes adapter-parity tests inside `tests/test_collab_hooks.py` that assert installer output matches committed manifests.
- **Trigger**: push / pull_request on main (inside `test.yml`).
- **Frontmatter validation**: no — no check that agent-frontmatter fields are in any documented schema.
- **Hooks.json validation**: existence only.
- **Pitfalls observed**: the `verify` step catches missing files but not version drift, not schema errors, not the `marketplace.json` vs `plugin.json` divergence this repo exhibits.

## 16. Documentation

- **`README.md` at repo root**: present, ~15 KB — substantial with opening hook ("AI agents agree with each other. That's the problem."), a JWT HS256-confusion scare example, role table, hook-enforcement explanation, Quick Start for three CLIs, What's New in 5.0, 8-role table, CLI reference, platform support matrix, troubleshooting. Leads with outcome framing (findings the eight roles catch) rather than feature list.
- **`README.md` per plugin**: not applicable (single-plugin marketplace).
- **`CHANGELOG.md`**: present — custom format headed with "Theme: Verifiable enforcement.", no Keep-a-Changelog structure, no `[Unreleased]` section. Only the 5.0.0-alpha entry is visible in the file (only ~2 KB). Earlier versions' change history appears to live in commit messages (`v4.1.0`, `v4.2.0` mentioned in commits but not in CHANGELOG).
- **`architecture.md`**: absent at root. No per-plugin `architecture.md`. A visual diagram lives at `docs/images/architecture.png` and is linked from README.
- **`CLAUDE.md`**: absent at root. The equivalent for this plugin is the Codex-specific `adapters/codex_cli/AGENTS.md` plus `skills/collab/SKILL.md`.
- **Community health files**: present — `CONTRIBUTING.md` (4.6 KB, custom-role authoring, platform-adapter guide, code standards including "Python stays 100% stdlib"). Absent — no `SECURITY.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: observed — CI badge, Python 3.10+ badge, MIT license badge, version badge (5.0.0-alpha, orange), "dependencies: zero" badge.
- **`docs/` directory**: present — `docs/MIGRATION.md` (v4→v5 migration guide), `docs/images/{architecture.png, header.png}`. Large images (architecture.png ~7.6 MB, header.png ~9 MB) inflate repo size.
- **Pitfalls observed**: no `architecture.md` despite the system having substantial internal structure (hooks + core engine + spec + adapters + installer + CLI). The "architecture" lives half in README, half in the PNG diagram, half in CONTRIBUTING.md's Code Organization section — violates single-source-of-truth for design rationale. The PNG-only diagram is not searchable or diff-able.

## 17. Novel axes

- **Enforcement-contract-as-inspectable-artifact.** `spec/enforcement.yaml` declares, for every hook, its gate class (`hard_gate`, `recovery`, `lifecycle`, `observability`), failure mode (`deny`, `block`, `fail_open`, `async_fail_open`, `warn`), and per-platform support (`supported`, `degraded`, `—`). Compiled to `spec/enforcement_compiled.json` for runtime. Surfaced by a CLI verb `collabctl capabilities` (with `--json` for CI). Parity tests assert committed adapter manifests match the contract. This is unusual: most plugins treat "what my hooks enforce" as prose. Candidate for its own pattern-doc axis.
- **Role-spec-as-YAML-with-compiled-JSON.** `spec/roles/builtin_roles.yaml` defines all 8 built-in roles (scope mode, bash policy, blind-from rules, result schemas, phase assignments, per-platform support) plus a JSON schema for validation and a compiled JSON for fast load. Treated as source-of-truth for the core `hooks/scripts/core/role_spec_loader.py` module.
- **Structured-result-block-as-contract.** Every role agent is required to emit a `COLLAB_RESULT_JSON_BEGIN ... COLLAB_RESULT_JSON_END` block; the SubagentStop hook refuses to let the subagent finish without it. Per-role JSON schemas live in `skills/collab/schemas/*.schema.json`. Missing or malformed blocks are a hard block (not a warning). This is a stronger contract than most multi-agent plugins impose.
- **Circuit-breaker-for-hook-crashes.** `hooks/scripts/core/circuit_breaker.py` (~7 KB) implements retry-with-backoff (100ms / 500ms) before escalating, with configurable failure mode per hook (`deny` / `block` / `warn`). Inspired by Erlang/OTP + Netflix + NIST 800-53. Most plugins use a simple try/except fail-open; this one treats hook resilience as a state machine.
- **Compensating revert after PostToolUse.** Read-only roles that manage to write (because PreToolUse was bypassed or fail-open triggered) get their writes reverted automatically: `git checkout` for tracked files, `rm` for untracked. Ledger records `revert_mode` and `revert_success`. This defense-in-depth pattern (don't just block on the way in, undo on the way out) is distinctive.
- **Blind-review enforced by SubagentStart context shaping.** The skeptic agent's context deliberately excludes the implementer's summary — enforced at the hook layer, not by prompting. The README makes this the hero feature ("The skeptic literally cannot see the author's narrative"). This is a novel pattern for multi-agent review: bias mitigation via context walls, not prompt pleading.
- **Three-platform adapter pattern.** Single repo, three CLI targets (Claude Code native, Copilot CLI via `adapters/copilot_cli/`, Codex CLI via `adapters/codex_cli/`). Each adapter has its own manifest format (`.claude-plugin/plugin.json` vs Copilot's `plugin.json`+`hooks.json` vs Codex's `AGENTS.md`+`hooks.json`). Shared core in `hooks/scripts/core/`; adapters import, not duplicate. Installer detects which CLI is present and wires up the right surface.
- **User-skill fallback for Codex CLI slash-command routing.** `install.py` writes a second skill file to `~/.agents/skills/8eyes-collab/SKILL.md` because Codex apparently needs a user-level skill for `/8eyes:collab` to route. This is a workaround-as-pattern for quirky host discovery.
- **Git-common-dir as mission state root.** Mission manifest + ledger + per-role results live under `<git-common-dir>/claude-collab/` (not `.git/claude-collab/` — crucial distinction when worktrees are involved). This makes state survive worktree isolation, which the plugin uses per-role. Unusual placement for plugin state.
- **No runtime dependencies by policy.** "Python stays 100% stdlib. Do not add pip dependencies" as a documented code-quality standard. Makes the plugin a zero-setup install but pays for it in ~126K of hand-written test code and bespoke YAML parsing/JSON schema validation.
- **Duplicate marketplace.json in `.github/plugin/`.** Two copies of the marketplace manifest — one canonical, one vestigial/aspirational. No sync mechanism. Novel as an anti-pattern worth flagging.

## 18. Gaps

- **Exact mechanism of version drift.** `plugin.json` at `5.0.0-alpha`, `marketplace.json` entry at `4.2.0`. Unknown whether this is deliberate ("marketplace only advances at stable release" policy) or accidental drift. Resolving would require reading the commit `ca2fd021` ("Enforcement contract, role specifications, and custom role parity (5.0.0-alpha)") full diff or asking the maintainer. Budget-limited out.
- **Whether `isolation: worktree` in agent frontmatter is actually honored by Claude Code.** The official plugin reference at code.claude.com/docs/en/plugins-reference was not fetched (not in scope for this 25-35 WebFetch budget); whether Claude Code's agent loader recognizes `isolation`, `background`, `effort`, `maxTurns` as first-class fields or silently drops them is unverified.
- **Whether `.github/plugin/marketplace.json` has a real consumer.** No workflow references it; no GitHub Pages config in `.github/`. Could be probed by inspecting the repo's Pages settings via `gh api repos/.../pages`, not done here.
- **Full contents of `skills/collab/SKILL.md` beyond the opening.** Only the first ~80 lines were read; the full trust model, phase model, role dispatch table, and CLI reference inside the skill were not comprehensively inspected. Budget-limited.
- **The `v5.0/foundation-hardening` branch's relationship to main.** Tip commit, divergence, and purpose not examined. Could be a stale feature branch, an active parallel track, or an aborted release-branch experiment.
- **Whether CI's "verify plugin layout" step validates anything beyond file existence.** `scripts/collabctl.py verify` is 52 KB (the whole `collabctl` module) and likely does schema checks for some artifacts; the exact coverage was not read.
- **Windows test coverage in practice.** Matrix declares `windows-latest`, but whether tests actually pass on Windows (given `msvcrt` file locking, `.cmd` shim, `git-common-dir` path quirks) requires reading CI run history via `gh run list` — not fetched.
- **How custom roles integrate with the blind-review context shaping.** The SKILL.md excerpt mentions blind-from rules in the role spec schema but the read fetched only the intro; the exact hook-side implementation in `collab_subagent_start.py` and how custom roles declare their own blind-from lists was not examined.
