# Sample

Mirrors of `https://github.com/AgentBuildersApp/eight-eyes`. Multi-agent code-review plugin for Claude Code, Copilot CLI, and Codex CLI: 8 role subagents whose tool scope is enforced by PreToolUse / PostToolUse / SubagentStop hooks ("Hook-enforced walls, not just prompts"). MIT-licensed; 2 stars at sample time; current tip is `5.0.0-alpha`.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry pointing at `"./"` — repo root *is* the plugin. Plugin name `8eyes`, marketplace name `8eyes-marketplace`. Both `marketplace.json` copies (canonical and duplicate) carry a `_description` private key (`"_description": "Marketplace discovery metadata"` / `"Plugin manifest and marketplace metadata"`) outside the documented schema.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper — `description: "Multi-agent code review for Claude Code, Copilot CLI, and Codex CLI"`, `version: "4.2.0"`. `metadata.pluginRoot` is absent.

### Duplicated marketplace manifest at root and nested

Two `marketplace.json` copies: canonical at `.claude-plugin/marketplace.json`, duplicate at `.github/plugin/marketplace.json`. Both carry identical content (same name, same metadata, same single plugin entry). No sync mechanism visible in hooks or CI — the two files must be edited in lockstep manually. The duplicate has no obvious consumer (Claude Code reads `.claude-plugin/marketplace.json`); likely vestigial or aspirational.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; `strict` is absent (default implicit `true`). The repo root is the plugin.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

`category: "code-quality"`, `keywords: ["code-review","multi-agent","security","testing","accessibility","tdd","blind-review"]`, `tags: ["review","security-audit","performance","accessibility","documentation"]`.

### `$schema` absence on per-plugin manifests

`$schema` is absent.

## Version coordination

### Multi-site sprawl (5+ locations)

Seven sites carry the version: `.claude-plugin/plugin.json` → `5.0.0-alpha`; `.claude-plugin/marketplace.json` plugin entry version → `4.2.0`; `.claude-plugin/marketplace.json metadata.version` → `4.2.0`; `VERSION` file → `5.0.0-alpha`; `pyproject.toml` version → `5.0.0a1` (PEP 440 equivalent); git tag → `v5.0.0-alpha` (only tag present, pre-release on GitHub Releases); CHANGELOG.md top entry → `5.0.0-alpha`. The marketplace.json entries are stale at 4.2.0 while the rest of the repo has advanced to 5.0.0-alpha. Consumers installing via `claude plugin install 8eyes@8eyes-marketplace` see "4.2.0" in the marketplace entry but the plugin.json they receive advertises "5.0.0-alpha". The marketplace version appears to only get bumped on stable releases while `plugin.json`/`VERSION`/`pyproject.toml` track alpha/dev state.

### Multi-site drift accepted as cosmetic

`5.0.0-alpha` (semver) and `5.0.0a1` (PEP 440) and `v5.0.0-alpha` (tag) are three forms of the same version that downstream sorting rules may not reconcile. Pre-release suffix handling differs across formats. No sync script, no pre-commit hook, no CI validation catches this — pure manual-discipline drift surface.

## Channel distribution

### Pre-release tag suffixes on a single channel

Single `8eyes-marketplace` name; users pin by `@ref` via `claude plugin marketplace add AgentBuildersApp/eight-eyes`. The `-alpha` suffix in `plugin.json` and the `v5.0.0-alpha` git tag mark the current release as pre-release. GitHub Releases marks the release as `prerelease: true`. No `stable-*`/`latest-*` pair, no dev-counter split. The `v5.0/foundation-hardening` branch exists alongside `main` but is not used as a long-lived release-branch channel — looks like an in-flight feature branch. Users on `main` receive the alpha directly.

## Tag and release lifecycle

### Tag-on-main, single branch

Tag `v5.0.0-alpha` at commit `f3c1075a`, three commits back from HEAD (`e13ac412`). Tag is not at tip; newer work on main is untagged. One side branch `v5.0/foundation-hardening` visible; no long-lived `release/*` pattern. No `.pre-commit-config.yaml`, no `.githooks/` directory, no evidence in CI of version auto-bump.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no `skills`/`commands`/`agents`/`hooks` arrays. Components are discovered by convention from `skills/`, `commands/`, `agents/`, `hooks/` directories at plugin root.

## Component composition

### Skills (universal)

One skill: `skills/collab/SKILL.md` with supporting `references/` and `schemas/` directories.

### Commands

Two commands: `commands/8eyes.md`, `commands/8eyes-copilot.md`.

### Agents

Eight `collab-*.md` agents in `agents/` (skeptic, security, performance, accessibility, docs, implementer, verifier, plus one more inferred). Frontmatter declares `name`, `description`, `tools`, `background` (boolean), `isolation: worktree`, `effort` (low/medium), `maxTurns` (numeric). `isolation: worktree` claims per-role git-worktree isolation; the README reinforces "Worktree isolation is used where incidental writes or tool artifacts would otherwise leak across roles." Read-only review roles (skeptic, security, performance, accessibility, docs) use `background: true`; implementer and verifier omit `background`. Tools are plain comma-separated names (`Read, Glob, Grep, LS, Bash`); no permission-rule syntax — Bash scoping is enforced by the PreToolUse hook instead. Copilot adapter (`adapters/copilot_cli/agents/collab-*.agent.md`) duplicates the frontmatter with the same fields.

### Hooks

`hooks/hooks.json` registers 7 hook-event handlers: PreToolUse (`Write|Edit|MultiEdit|Bash`), PostToolUse (`Write|Edit|MultiEdit|Bash`), SessionStart, plus four others (SubagentStart/SubagentStop/Stop and similar) running scripts under `hooks/scripts/`.

## Skill authoring conventions

### Standard frontmatter

`skills/collab/SKILL.md` carries standard frontmatter. The skill directory holds supporting `references/hook-failure-policy.md` and `schemas/*.schema.json` (per-role JSON schemas for the `COLLAB_RESULT_JSON_BEGIN ... COLLAB_RESULT_JSON_END` result blocks).

## Agent declaration conventions

### Rich behavior fields (background, isolation, memory)

Agents declare `background: true` (read-only roles), `isolation: worktree` (per-role git-worktree isolation), `effort: low|medium`, `maxTurns: <N>`. These fields are not documented in the public Claude Code plugin reference at `code.claude.com/docs/en/plugins-reference`; whether Claude Code's agent loader recognizes them as first-class or silently drops them is unverified. Enforcement may be entirely in-hook (scope enforcement via PreToolUse), with frontmatter fields acting as aspirational / Copilot-adapter-specific metadata.

### Plain tool-name list

Agents declare `tools:` as a comma-separated scalar string (`Read, Glob, Grep, LS, Bash`). No permission-rule syntax like `Bash(uv run *)`. Bash scoping is enforced by the PreToolUse hook rather than by frontmatter rules.

## Cross-platform skill publishing

### Multi-runtime skill mirrors

The Codex-specific user skill is duplicated by `install.py` to `~/.agents/skills/8eyes-collab/SKILL.md` because Codex apparently needs a user-level skill for `/8eyes:collab` to route. Two locations of the same skill file under different roots.

## Bin entry mechanism

### No bin entry / direct invocation

No shipped `bin/` directory. The `collabctl` CLI is distributed as `scripts/collabctl.py` (invoked as `python3 scripts/collabctl.py ...`). Hook scripts resolve via `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/...` in `hooks/hooks.json`. Copilot adapter uses `"$(dirname "$0")/../../hooks/scripts/..."` (script-relative) with a PowerShell sibling. Codex adapter writes absolute paths at install time. README shows `python3 scripts/collabctl.py <verb>` everywhere.

## Server runtime (MCP)

### No bin entry / direct invocation

No `.mcp.json`; no MCP server. All work is via skills, commands, agents, hooks.

## Dependency installation

### Zero dependencies / stdlib only

CONTRIBUTING.md states "Python stays 100% stdlib. Do not add pip dependencies." Badge on README: `dependencies-zero-brightgreen`. No `requirements.txt`; `pyproject.toml` is present but declares no `[project.dependencies]` — exists for PyPI metadata (name, version, classifiers, URLs) and license, not for dep install. No `[tool.uv]` section. All hook scripts use only stdlib imports. Tests are stdlib-only too (unittest, no pytest). Python 3.10+ required. Trade-off: hook scripts implement their own JSON schema validation, YAML parsing (custom mini-parser in `spec/` compile step), and circuit-breaker logic by hand — ~150K of test code to guard against regressions.

## Install change detection

### Full-wipe (no detection)

`install.py` uses `reset_directory()` (delete + recreate) for Copilot/Codex targets, and `link_or_copy()` (symlink preferred, copy fallback on OSError) for Claude Code target. Idempotent by full-wipe rather than diff-based.

## Install trigger and lifecycle

### User-invoked one-shot installer

`install.py` at repo root — a standalone Python script, not tied to a hook. Runs as `python3 install.py` with `--platform` / `--uninstall` / `--verify` / `--add-to-path` flags. Invoked manually by the user for Copilot CLI and Codex CLI platforms; for Claude Code, the marketplace install flow is preferred (`claude plugin install 8eyes@8eyes-marketplace`), with `install.py` as a manual fallback.

## Install failure posture

### `[OK]/[WARN]/[FAIL]` print + non-zero exit

`install.py` prints `[OK]` / `[WARN]` / `[FAIL]` lines to stdout; exit 0 on success, 1 on failure. `repo_verify()` shells out to `scripts/collabctl.py --cwd . verify` and returns its exit code.

## User configuration and authentication

### Per-mission flags (no install-time config)

No `userConfig` field. All configuration is passed as CLI flags to `collabctl init` (`--objective`, `--allowed-path`, `--criterion`, `--verify-command`, `--model-map`, `--custom-role`, `--tdd`, etc.) or picked up from a `REVIEW.md` file in the project root. Configuration is entirely runtime (per-mission, via flags) rather than install-time. The plugin does not participate in Claude Code's user-config UI; no `${user_config.KEY}` substitution.

## Session context loading

### `additionalContext` payload at SessionStart

`collab_session_start.py` reads active mission manifest from `<git-common-dir>/claude-collab/`, formats a "slim" mission summary, prepends a `[COLLAB WARNING]` if the mission is >12h old, and emits it as `hookSpecificOutput.additionalContext`. Wrapped via the `hook_context("SessionStart", summary)` helper in `collab_common`, which produces `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`. The hook reads `cwd` from the hook payload's JSON stdin and falls back to `.`. If the session starts outside a git repo, the hook exits 0 silently.

## SessionStart matcher scope

### Explicit subset

SessionStart matcher is `"startup|resume|clear|compact"` — fires on all four sub-events. Broader than the typical `startup|clear|compact` triad (adds `resume`); does not pair with `UserPromptSubmit` for resumed sessions.

## Tool-use enforcement

### Scope enforcement (block out-of-scope writes)

PreToolUse hook with matcher `"Write|Edit|MultiEdit|Bash"` runs `collab_pre_tool.py`. Blocks out-of-scope writes and unapproved Bash commands for read-only roles; enforces path scope (`allowed_paths`/`test_paths`/`doc_paths`) for writer roles. Reads role declaration from `spec/roles/builtin_roles.yaml` and emits `pretool_deny` payloads as JSON on stdout. Configurable failure mode (`fail_open` / `deny`) per mission. The skill's Trust Boundaries section names this as the primary trust anchor. The enforcement contract is treated as a first-class, inspectable artifact — `spec/enforcement.yaml` declares, for every hook, its gate class (`hard_gate`, `recovery`, `lifecycle`, `observability`), failure mode (`deny`, `block`, `fail_open`, `async_fail_open`, `warn`), and per-platform support (`supported`, `degraded`, `—`). Compiled to `spec/enforcement_compiled.json` for runtime. Surfaced by `collabctl capabilities` (with `--json` for CI). Parity tests assert committed adapter manifests match the contract.

### Compensating revert (PostToolUse defense in depth)

PostToolUse hook with matcher `"Write|Edit|MultiEdit|Bash"` runs `collab_post_tool.py`. If a write slips past PreToolUse for a read-only role, PostToolUse does `git checkout` for tracked files and `rm` for untracked files, ledgering a `scope_violation_reverted` event. Applies uniformly to built-in and custom read-only roles in v5.0 (a v4.x bug allowed custom roles to bypass this). Ledger records `revert_mode` and `revert_success`.

### Universal-matcher rule evaluator

The broader hook system includes additional matchers: SubagentStart context shaping that excludes the implementer's summary from the skeptic agent's context (blind-review enforced at hook layer, not by prompting); SubagentStop hook that refuses to let the subagent finish without a `COLLAB_RESULT_JSON_BEGIN ... COLLAB_RESULT_JSON_END` block matching per-role JSON schemas in `skills/collab/schemas/*.schema.json`. Missing or malformed blocks are a hard block.

## Hook handler runtime

### Python stdlib runner with external probing

Every hook script is Python (stdlib-only) under `hooks/scripts/`. Top-level try/except wraps `_main()` in every script and calls `_fail_open()` (or the circuit-breaker equivalent) on any exception. Even the ledger-write attempt inside the error handler is wrapped in its own try/except. Pattern documented in `skills/collab/references/hook-failure-policy.md`.

## Hook output contract

### Stderr for human display + stdout JSON for harness

`pretool_deny` payloads and `hookSpecificOutput` contexts are `json.dumps`'d and written to stdout; stderr carries human-readable error logs and circuit-breaker messages. Both surfaces are produced for blocking exits.

## Hook failure posture

### Fail-closed with circuit breaker (retry with backoff)

`HookCircuitBreaker` (in `hooks/scripts/core/circuit_breaker.py`, ~7 KB) wraps the hook body, retrying with backoff (100ms, 500ms) before escalating, with configurable failure mode per hook: `deny` for pre-tool, `block` for subagent-stop, `warn` for stop. Configurable per-mission via `manifest.fail_closed`. Default is fail-open (legacy `_fail_open` helper, partly superseded by the circuit breaker). When `fail_closed: true`, the circuit-breaker `failure_mode="deny"` retries twice (100ms, 500ms backoff) then emits a deny payload. Pattern-influenced by Erlang/OTP + Netflix + NIST 800-53. SessionStart hook uses an explicit fail-open pattern: catches all exceptions, writes `[collab]` prefixed error + stack trace to stderr, attempts to ledger the error, returns 0 unconditionally.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Plugin code lives under repo root (= `${CLAUDE_PLUGIN_ROOT}` when installed via marketplace). Mission state lives under `<git-common-dir>/claude-collab/` (not `${CLAUDE_PLUGIN_DATA}`) — see *State persistence*.

## State persistence

### `<git-common-dir>/<plugin>/` for mission state

Mission manifest, ledger (`<git-common-dir>/claude-collab/ledger.jsonl`), and per-role results live under `<git-common-dir>/claude-collab/`. The `git-common-dir` placement (rather than `.git/claude-collab/`) is crucial when worktrees are involved — coordinator, root checkout, and worktree-isolated roles share one manifest. Mission status is pulled via `collabctl status --json` on demand rather than pushed via a monitor.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The plugin does live notification work through ledger files (`<git-common-dir>/claude-collab/ledger.jsonl`), not through a `monitors.json`.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field. Single-plugin marketplace; tag format is `v5.0.0-alpha`. No cross-plugin coupling.

## Testing

### Python unittest with explicit `unittest discover`

Tests use unittest (stdlib). One giant file `tests/test_collab_hooks.py` (~126K, 148 tests per its own docstring, 152 per README). CI uses `python -m unittest discover -s tests -p 'test_*.py' -v`. CONTRIBUTING.md recommends `python3 -m pytest tests/ -q` for local dev — pytest is supported via its unittest discovery, but the CI workflow uses unittest. No `pytest.ini`, no `[tool.pytest.ini_options]` in `pyproject.toml`. `pyproject.toml` declares no test deps (stdlib-only per project policy). One monolithic ~126K test file for 148 tests is intentional for locality with helpers. README's "152 tests" claim vs docstring's "148 tests" is a minor drift.

## CI workflow shape

### Single workflow, OS × language matrix

`.github/workflows/test.yml` (single workflow). Triggers `push: branches: [main]` and `pull_request: branches: [main]`. Steps: `python -m unittest discover -s tests -p 'test_*.py' -v`, then `python scripts/collabctl.py --cwd . verify` as a plugin-layout check. No linters, no type-checkers, no manifest schema validator. Matrix OS × Python — `[ubuntu-latest, macos-latest, windows-latest]` × `['3.10', '3.11', '3.12']`. README claims "3.10 through 3.13" but matrix omits 3.13. Action pinning by tag — `actions/checkout@v4`, `actions/setup-python@v5`. No explicit caching (setup-python's built-in pip cache is irrelevant since no deps). Direct `python -m unittest discover` invocation; no `scripts/test.sh` wrapper.

## Marketplace validation

### Custom verify command (existence-only)

The `test.yml` workflow's second step `python scripts/collabctl.py --cwd . verify` checks plugin layout (Claude Code `.claude-plugin/plugin.json`, `hooks/hooks.json`, Copilot `adapters/copilot_cli/plugin.json`, Codex `adapters/codex_cli/AGENTS.md` and `hooks.json`) but only for *file existence*, not for JSON schema conformance. Adapter-parity tests inside `tests/test_collab_hooks.py` assert installer output matches committed manifests. No version drift detection, no schema errors, no `marketplace.json` vs `plugin.json` divergence detection.

## Release automation

### No release automation / manual

No `release.yml`. The single `v5.0.0-alpha` GitHub Release exists but was not created by a workflow. No `softprops/action-gh-release`, no `release-please`, no `gh release create` in any visible script. Manual (GitHub UI or `gh release create` by hand). CI does not verify tag-on-main, tag-equals-package-version, or tag-format. The lack of release automation is why the version drift across `plugin.json`/`marketplace.json` persists.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

`README.md` (~15 KB) — opening hook ("AI agents agree with each other. That's the problem."), JWT HS256-confusion scare example, role table, hook-enforcement explanation, Quick Start for three CLIs, What's New in 5.0, 8-role table, CLI reference, platform support matrix, troubleshooting. Leads with outcome framing rather than feature list. Badges: CI badge, Python 3.10+ badge, MIT license badge, version badge (5.0.0-alpha, orange), "dependencies: zero" badge. `CHANGELOG.md` is custom — headed with "Theme: Verifiable enforcement.", no Keep-a-Changelog structure, no `[Unreleased]` section. Only the 5.0.0-alpha entry is visible (~2 KB). Earlier versions' change history lives in commit messages (`v4.1.0`, `v4.2.0` mentioned in commits but not in CHANGELOG). `CONTRIBUTING.md` (4.6 KB) covers custom-role authoring, platform-adapter guide, code standards including "Python stays 100% stdlib".

### Sprawling root with many entry-point markdowns

A `docs/` directory holds `docs/MIGRATION.md` (v4→v5 migration guide) and `docs/images/{architecture.png, header.png}`. No `architecture.md` at root despite the system having substantial internal structure (hooks + core engine + spec + adapters + installer + CLI). The "architecture" lives half in README, half in the PNG diagram (`docs/images/architecture.png` ~7.6 MB), half in CONTRIBUTING.md's Code Organization section. The PNG-only diagram is not searchable or diff-able. Large images (`header.png` ~9 MB) inflate repo size. `CLAUDE.md` is absent at root; the equivalent for this plugin is the Codex-specific `adapters/codex_cli/AGENTS.md` plus `skills/collab/SKILL.md`.

## License declaration

### Single repo-level license

`LICENSE` at repo root, MIT.

## Community health files

### Bare minimum (LICENSE only)

`CONTRIBUTING.md` (4.6 KB, custom-role authoring, platform-adapter guide, code standards). `LICENSE` (MIT). No `SECURITY.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`.

## Cross-platform discipline

### Adapter directory per host CLI

Single repo, three CLI targets — Claude Code native (`.claude-plugin/`), Copilot CLI (`adapters/copilot_cli/`), Codex CLI (`adapters/codex_cli/`). Each adapter has its own manifest format (`.claude-plugin/plugin.json` vs Copilot's `plugin.json`+`hooks.json` vs Codex's `AGENTS.md`+`hooks.json`). Shared core in `hooks/scripts/core/`; adapters import, not duplicate. `install.py` detects which CLI is present and wires up the right surface. Windows considerations throughout `install.py`: `_on_rm_error` handler for locked `.git` objects, `msvcrt` file-locking mentioned in platform-notes table, `.cmd` shim for PATH (POSIX shim at `~/.local/bin/eight-eyes` is `env bash` `exec python3 "<abs path to collabctl.py>" "$@"`; Windows shim at `~/.local/bin/eight-eyes.cmd` is `@echo off\npython3 "<path>" %*`, no shebang).

## Multi-runtime portability

### Parallel manifests for Claude + Cursor + Codex

Three platform manifests under different roots: `.claude-plugin/marketplace.json`+`plugin.json` for Claude Code, `adapters/copilot_cli/plugin.json`+`hooks.json` for Copilot CLI, `adapters/codex_cli/AGENTS.md`+`hooks.json` for Codex CLI. Each ecosystem reads its own manifest. Hook schemas differ per runtime; shared core in `hooks/scripts/core/` is imported by all three.

## PATH augmentation and host-project setup

### None (plugin operates standalone)

Plugin requires no host-project scaffolding for the Claude Code path. State lives under `<git-common-dir>/claude-collab/` and is derived from the user's existing repo. The opt-in `~/.local/bin/eight-eyes` shim (added by `install.py --add-to-path`) hardcodes the absolute path to `collabctl.py` at install time and is chmod 0755 on non-Windows.

## Cross-role tools

### Python (stdlib + pip + uv)

Python 3.10+ stdlib-only — Python is the runtime for hook scripts (`hooks/scripts/`), the install-script language (`install.py`), the test framework (unittest stdlib), and helper-script runtime (`scripts/collabctl.py`). No pip, no uv — `[project.dependencies]` is empty; `pyproject.toml` is for metadata only.

### Git as state substrate

Git fills tag placement (only `v5.0.0-alpha` tag at commit `f3c1075a`, three commits behind HEAD), `<git-common-dir>/claude-collab/` as state-storage root for mission state, and `git checkout` / `rm` as the compensating-revert mechanism in PostToolUse. Worktree isolation is the per-role agent sandbox per the `isolation: worktree` frontmatter. Marketplace install path resolves to `<repo-root>/.claude-plugin/...`.
</content>
</invoke>