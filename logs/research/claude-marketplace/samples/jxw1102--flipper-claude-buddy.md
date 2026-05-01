# jxw1102/flipper-claude-buddy

## Identification

- **URL**: https://github.com/jxw1102/flipper-claude-buddy
- **Stars**: 21
- **Last commit date**: 2026-04-20 (sha d37d8490, "chore: update troubleshooting doc")
- **Default branch**: main
- **License**: MIT (`LICENSE` at repo root; SPDX: MIT; also declared in `plugin/.claude-plugin/plugin.json` and `plugin/host-bridge/pyproject.toml`)
- **Sample origin**: dep-management
- **One-line purpose**: "Flipper Zero as a physical remote control and feedback device for Claude Code. Provides sound, vibration, and display feedback on a Flipper Zero connected via USB." (from `plugin/.claude-plugin/plugin.json` `description`). The marketplace entry uses the shorter "Flipper Zero hardware controller for Claude Code."

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (repo root is also a git-subdir marketplace entry pointing at `plugin/`).
- **Marketplace-level metadata**: none — top-level has only `name`, `owner`, `plugins`. No `metadata` wrapper, no top-level `description`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: none at the marketplace entry (no `category`, `tags`, or `keywords` on the `plugins[0]` entry). Keywords exist only inside `plugin/.claude-plugin/plugin.json` (`keywords: ["flipper-zero", "claude-code", "vibe-coding", "notifications", "remote-control"]`), which is plugin-manifest keyword metadata, not marketplace-surfaced discoverability.
- **`$schema`**: absent (neither manifest references a schema URL).
- **Reserved-name collision**: no — marketplace name `flipper-claude-buddy` and plugin name `flipper-claude-buddy` are identical, which means `plugin install flipper-claude-buddy@flipper-claude-buddy` works but the two namespaces carry the same string.
- **Pitfalls observed**: marketplace and plugin share the same name — benign here but makes `@` addressing read redundantly. No discoverability metadata at the marketplace entry means tooling that surfaces categories/tags would see this plugin as untagged; the keywords live only at the plugin-manifest layer.

## 2. Plugin source binding

- **Source format(s) observed**: `git-subdir` — the marketplace pins the plugin's own repo with `path: plugin`, even though the marketplace manifest lives in the same repo. A `relative` source (e.g., `./plugin`) would also work for in-repo co-location; the author chose `git-subdir` which re-clones from the remote URL.
- **`strict` field**: absent on the marketplace entry (implicit default).
- **`skills` override on marketplace entry**: absent.
- **Version authority**: `plugin.json` only — marketplace entry carries no `version` field. Single source of truth is `plugin/.claude-plugin/plugin.json` (`0.4.0`). Tag `0.4` and `flipper-app/application.fam` `fap_version` and `plugin/host-bridge/pyproject.toml` `version` are all coordinated manually per the release checklist in `CLAUDE.md`.
- **Pitfalls observed**: `git-subdir` with `url` pointing at the same repo means `plugin install` re-fetches the plugin from GitHub instead of resolving in-tree; for users who have already cloned the marketplace this is still a network round-trip. A `relative` source would avoid it but would also prevent standalone installation (a marketplace-add without a subsequent clone). The author's choice is consistent with "users add the marketplace from GitHub, not a local checkout."

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace, no stable/latest segregation. Users pin implicitly via whatever ref `plugin marketplace add` resolves (default branch main).
- **Channel-pinning artifacts**: absent — no `stable-tools`/`latest-tools` pattern, no dev-counter branch discipline.
- **Pitfalls observed**: the plugin version tracks main with no release branch; users who install via `claude plugin marketplace add jxw1102/flipper-claude-buddy` get whatever `0.4.0` points to on main, and a future bump to `0.5.0` on main would be picked up on the next marketplace update with no opt-in buffer.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (e.g., `0.4` tag at commit 612382e0, which is on main per the release notes).
- **Release branching**: none — tag-on-main. A `feat/nus-profile` feature branch exists but no `release/*` pattern.
- **Pre-release suffixes**: none observed — tags are `0.1`, `0.2`, `0.3`, `0.4` (no `v` prefix, no semver patch segment in the tag itself even though `plugin.json` uses `0.4.0`).
- **Dev-counter scheme**: absent — no `0.0.z` discipline; main directly carries release versions.
- **Pre-commit version bump**: no — `CLAUDE.md` prescribes a manual 7-step release checklist (commit clean → update CHANGELOG → `fap_version` → ui.c version string → plugin.json version → pyproject.toml version → commit → tag → push). CI (`build-fap.yml`) reacts to tags but does not author them.
- **Pitfalls observed**: tag format (`0.4`) diverges from manifest version (`0.4.0`), which breaks "tag matches package version" validators that look for exact equality. The release workflow does not enforce tag-version match. Four places must be kept in lockstep (fam, ui.c, plugin.json, pyproject.toml) with no automation — any drift is silent.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — the plugin manifest declares no component paths. Claude Code picks up `plugin/hooks/hooks.json`, `plugin/skills/notify/SKILL.md`, and implicit script locations by convention.
- **Components observed**: skills yes (1 — `notify`), commands no, agents no, hooks yes (single `hooks/hooks.json` registering 15 event types), `.mcp.json` no, `.lsp.json` no, monitors no, bin no, output-styles no.
- **Agent frontmatter fields used**: not applicable (no agents).
- **Agent tools syntax**: not applicable. Skill frontmatter uses `allowed-tools: Bash` (plain tool name, no permission-rule brackets).
- **Pitfalls observed**: hooks.json registers 15 event types (every lifecycle event including `Notification`, `Stop`, `StopFailure`, `Elicitation`, `PostToolUseFailure`, `PostToolUse`, `TaskCompleted`, `SessionEnd`, `PermissionRequest`, `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`) each with an empty-string matcher. Several of these (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `SubagentStart`, `SubagentStop`, `Elicitation`) are not part of the canonical list in `docs-hooks.md` — the plugin either anticipates or relies on non-public events. Matchers are all `""` (fire on everything), so there's no per-tool scoping.

## 6. Dependency installation

- **Applicable**: yes — Python bridge daemon with pyserial, pyserial-asyncio, bleak must be installed into an isolated venv.
- **Dep manifest format**: `pyproject.toml` at `plugin/host-bridge/pyproject.toml` (PEP 621 style, `[project]` table, three pinned-floor dependencies).
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv` (default-fallback to `/tmp/flipper-claude-buddy/venv` if the env var is unset — see `PLUGIN_DATA="${CLAUDE_PLUGIN_DATA:-/tmp/flipper-claude-buddy}"` in `on-session-start.sh`).
- **Install script location**: inline in `plugin/scripts/on-session-start.sh` (a bash script invoked as a `SessionStart` hook). Not a separate install script.
- **Change detection**: **md5** — this is the distinctive mechanism. The hook computes a hash over `pyproject.toml` plus every `bridge/*.py` file:

    ```bash
    CURRENT_HASH=$(cat "$BRIDGE_DIR/pyproject.toml" "$BRIDGE_DIR"/bridge/*.py 2>/dev/null \
      | md5 -q 2>/dev/null \
      || cat "$BRIDGE_DIR/pyproject.toml" "$BRIDGE_DIR"/bridge/*.py 2>/dev/null \
      | md5sum | cut -d' ' -f1 \
      || echo "none")
    ```

    Portability trick: tries `md5 -q` (macOS BSD `md5(1)`) first, falls back to `md5sum | cut` (GNU coreutils on Linux), falls back to literal `"none"` if neither is available. The concatenation-then-hash approach hashes content without caring about filenames or ordering beyond the shell glob order. The computed hash is stored in `"$VENV_DIR/.installed-hash"` (the `MARKER` file) and compared on each session start. If it differs or the marker is missing, the venv is recreated and `pip install --force-reinstall "$BRIDGE_DIR"` runs; a running daemon with the old hash is killed first (`[bridge] Bridge code changed; restarting daemon $OLD_PID...`).

- **Retry-next-session invariant**: no explicit `rm` on pip-install failure — the script runs under `set -euo pipefail` so a `pip install` non-zero exit would halt the script before the marker file is written, which means the next session still sees a mismatched/missing hash and retries. The marker is only written after `pip install` succeeds (line ordering is `pip install ... 2>&1 | tail -1 >&2` then `echo "$CURRENT_HASH" > "$MARKER"`). The `tail -1` pipe masks pip's own exit code, so the marker may be written even when pip fails — partial defect: `set -o pipefail` saves this because the pipeline's exit code surfaces from `pip` when `tail` would otherwise succeed. Not identical to the "rm-on-failure" docs-prescribed pattern but converges on the same retry behavior via marker-gating.
- **Failure signaling**: mixed — `set -euo pipefail` halts on errors early; later hook steps deliberately suppress failures (`|| true`, `2>/dev/null || true`) so notification failures don't propagate. Final line `exit 0` regardless. Bridge-start failure emits a human-readable stderr message (`[bridge] Socket not available, bridge may have failed. Check $LOG`) and exits 0 — the plugin degrades gracefully when the Flipper isn't connected (`exit 0` on no-device, no-socket).
- **Runtime variant**: Python uv — incorrect, actually **Python venv + pip**. Uses `python3 -m venv` and the venv's own `pip install --force-reinstall`. No `uv` usage.
- **Alternative approaches**: none within this plugin — the md5-over-source-tree pattern is the alternative being documented. The `--force-reinstall` flag gives the same retry idempotency as a sha-based diff-q without requiring diff state. PEP 723 inline metadata is not used.
- **Version-mismatch handling**: none — the venv is per-plugin-data and re-created on content change but not on Python minor version change. If the user upgrades Python 3.10 → 3.11 system-wide, the existing venv keeps pointing at the old interpreter until the hash file changes for some other reason. No Python version tracking in the marker.
- **Pitfalls observed**: the marker-vs-Python-interpreter-version gap described above. The `md5 -q` → `md5sum | cut` fallback is elegant but silently drops the hash to literal `"none"` if neither exists (e.g., busybox `sh` on a minimal system), which would make every session re-install. The `|| echo "none"` at the pipeline tail is a fallback trapdoor — compared to a missing marker, a literal `"none"` stored would pin the install forever since subsequent runs also resolve to `"none"` and skip. The pipe-to-`tail -1` masks pip output detail in the log — a failed install's stderr is lost to `>&2` of just the last line. Globbing over `bridge/*.py` with only top-level source (no recursion) is correct for this layout but would need update if subpackages were added.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory. The plugin does install an entry point (`flipper-bridge = "bridge.__main__:main"` in `pyproject.toml`), but it is reached via `"$VENV_DIR/bin/python" -m bridge` from the hook, not via a plugin-level `bin/` wrapper. Users never invoke `flipper-bridge` directly.
- **`bin/` files**: not applicable.
- **Shebang convention**: not applicable for plugin bin/, but hook scripts themselves use `#!/bin/bash` (`on-session-start.sh`) and `#!/usr/bin/env python3` (all `on-*.py` scripts).
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: `"$VENV_DIR/bin/python" -m bridge` — direct exec of the venv's python, not `source activate`. Spawned via `nohup ... &` so the daemon detaches from the hook process.
- **Platform support**: not applicable for bin/.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable (no bin/).
- **Pitfalls observed**: the daemon lifecycle is managed via socket/PID files in `/tmp/` (`claude-flipper-bridge.sock`, `claude-flipper-bridge.pid`, `claude-flipper-bridge.refcount`) rather than any plugin-provided CLI. Users wanting to manually inspect or restart the bridge must either tail the log or kill the PID themselves.

## 8. User configuration

- **`userConfig` present**: yes.
- **Field count**: 3 (`serial_port`, `transport`, `bluetoothName`).
- **`sensitive: true` usage**: correct (all three flagged `sensitive: false` — none are secrets). Serial port paths and BLE names are device identifiers, not credentials; flagging them `false` is deliberate rather than the anti-pattern of omitting the flag.
- **Schema richness**: typed — each field has `title`, `type: "string"`, `description`, `sensitive`. No `default`, no `enum` for `transport` (which accepts "auto"/"usb"/"ble" but doesn't enumerate those as a typed choice — validation relies on the hook code interpreting the string).
- **Reference in config substitution**: `CLAUDE_PLUGIN_OPTION_<KEY>` env var style — `on-session-start.sh` reads `CLAUDE_PLUGIN_OPTION_serial_port`, `CLAUDE_PLUGIN_OPTION_transport`, and `CLAUDE_PLUGIN_OPTION_bluetoothName`, then re-exports them under `FLIPPER_*` names the Python bridge expects. No `${user_config.KEY}` substitution syntax used — the plugin only has hook scripts, no MCP/LSP/monitor commands that would consume the substitution form.
- **Pitfalls observed**: `transport` is a free-form string without a typed enum — a typo like `"usb "` (trailing space) or `"blue"` falls through to the "else" path and silently treats it as `auto`. Not ideal for a three-valued choice. The `bluetoothName` field casing uses camelCase while `serial_port` and `transport` use snake_case — inconsistent within the same manifest.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — `hooks.json` registers `PostToolUse` and `PermissionRequest` but not `PreToolUse`. The plugin does not block or gate tool calls before they run; `PermissionRequest` is how it participates in permission decisions.
- **PostToolUse hooks**: 2 with matcher `""` (fire on all tools) — `on-post-tool-use.py` (per-tool sound based on tool-name classification) and `on-post-tool-use-failure.py` (error sound on failure).
- **PermissionRequest/PermissionDenied hooks**: `PermissionRequest` observed — `on-permission-request.py` delegates the allow/deny decision to the Flipper hardware via a socket round-trip with a 60-second timeout, then emits a `hookSpecificOutput.decision` JSON structure (`{"behavior": "allow"}` / `{"behavior": "deny"}` / `{"behavior": "ask"}`). This is substantive `PermissionRequest` integration, not just notification.
- **Output convention**: mixed — `on-permission-request.py` writes structured JSON to stdout (`hookSpecificOutput`); the sound/notification hooks exit silently (`sys.exit(0)`) without emitting JSON; failure-path scripts (`on-stop-failure.sh`) write to stderr via the `||` fallthrough pattern rather than structured JSON.
- **Failure posture**: fail-open. When the bridge socket is missing, hooks exit 0 (non-blocking) rather than exit 1. `on-permission-request.py` is the one exception — it exits 1 on "no bridge" to fall back to Claude's default permission dialog, and exits 1 on timeout or error (letting Claude's dialog handle the decision). The rest prioritize "don't break Claude if the Flipper isn't plugged in."
- **Top-level try/catch wrapping**: mixed per-script — most `send_to_flipper` calls are wrapped `try: ... except Exception: pass`. No central emit helper; each script re-implements the socket-send-with-swallow pattern.
- **Pitfalls observed**: the 60-second timeout on `PermissionRequest` is long — if the user walks away from the Flipper after the request appears, Claude sits for a full minute before falling back. No configurable timeout. The status-code ladder (`ok` / `ask` / `no_flipper` / `timeout` / `busy` / `error`) is defined in the bridge daemon, not the plugin manifest — a reader inspecting only the hook script sees opaque string comparisons.

## 10. Session context loading

- **SessionStart used for context**: no (for context). Yes for dep install and daemon lifecycle.
- **UserPromptSubmit for context**: no — `on-prompt-submit.sh` sends a "Thinking..." display message to the Flipper; it does not emit `additionalContext` to Claude.
- **`hookSpecificOutput.additionalContext` observed**: no. The only `hookSpecificOutput` shape observed is in `on-permission-request.py` and uses `decision`, not `additionalContext`.
- **SessionStart matcher**: none (empty string, fires on all sub-events). The script distinguishes `source` (startup/resume/clear/compact/model) internally for the subtext label but executes the same init logic regardless.
- **Pitfalls observed**: the plugin runs full daemon-lifecycle logic on every `SessionStart` variant including `compact`, which is slightly wasteful (the daemon is already running after compaction) — but guarded by the "socket exists → skip start" check, so the waste is limited to re-forwarding env vars and re-registering the session target.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none (the plugin uses hook events, not the monitors system).
- **`when` values used**: not applicable.
- **Version-floor declaration**: absent (no `monitors` dependency, no min-Claude-Code-version declared anywhere in README or plugin.json).
- **Pitfalls observed**: the plugin registers hook events (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`) that aren't in the canonical list — these require a Claude Code version that emits them. Without a version floor declared, users on older Claude Code versions silently get a subset of functionality with no diagnostic.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none — single plugin in single marketplace, no cross-plugin dependency.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; tags are bare `0.1`…`0.4`).
- **Pitfalls observed**: the plugin depends on the host-side Python package `flipper-claude-buddy-bridge` and on the Flipper firmware app (`claude_buddy.fap`) — these are real runtime dependencies but live outside the `dependencies` field because they are not plugins. Plugin-dependency semantics only address other marketplace plugins; hardware/daemon prereqs are documented in README instead.

## 13. Testing and CI

- **Test framework**: none — no `tests/` directory, no `pytest.ini`/`conftest.py`, no `[tool.pytest.ini_options]` section in `pyproject.toml`.
- **Tests location**: not applicable.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes — one workflow, `.github/workflows/build-fap.yml`.
- **CI file(s)**: `build-fap.yml`.
- **CI triggers**: `workflow_dispatch`, `push` with path filter `flipper-app/**`, and `tags: '*'`.
- **CI does**: builds the Flipper FAP firmware binary via `ufbt build`, uploads as an artifact, and when the ref is a tag attaches the built `.fap` to a GitHub release via `softprops/action-gh-release@v2`. No pytest, no linting, no manifest validation.
- **Matrix**: none — single `ubuntu-latest` runner with Python 3.11.
- **Action pinning**: tag — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `softprops/action-gh-release@v2` all pinned by major version tag, not SHA.
- **Caching**: none — no `actions/cache` step, no `cache: 'pip'` argument to `setup-python`.
- **Test runner invocation**: not applicable.
- **Pitfalls observed**: no tests for the Python bridge or the hook scripts — a refactor would surface regressions only via user-observed misbehavior on the Flipper. CI only exercises the firmware build path, so a broken `on-session-start.sh` or `on-permission-request.py` ships green. The YAML declares `on.push.paths` and `on.push.tags` as sibling keys of `on.push`, which in GitHub Actions semantics means the tag trigger is evaluated independently from the path filter — the actual union-behavior here (path-matching push OR any tag push) is likely what the author intends but is a common source of confusion.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — release is a side-effect of the build workflow's tag-conditional step, not a dedicated workflow.
- **Release trigger**: `push` with tags (`push: tags: '*'`) embedded in the build workflow's `on` block.
- **Automation shape**: binary build + attach — `ufbt build` produces `~/.ufbt/build/claude_buddy.fap`; a conditional `softprops/action-gh-release@v2` step attaches it when the ref is a tag. GitHub release notes are auto-generated (no body is provided to the action), producing the default "compare since previous tag" notes.
- **Tag-sanity gates**: none — no verify-tag-on-main, no tag-matches-version check, no tag-format regex. Any tag matching `*` triggers a release (including accidental tags).
- **Release creation mechanism**: `softprops/action-gh-release@v2`.
- **Draft releases**: no — releases are published immediately (`draft` is not set; defaults to false).
- **CHANGELOG parsing**: no — `flipper-app/CHANGELOG.md` exists and follows a custom format (`## vX.Y` sections, bullet list of changes) but is not parsed into release notes. The 0.4 release body on GitHub is `null`; earlier releases have empty-string bodies.
- **Pitfalls observed**: the release checklist in CLAUDE.md instructs updating four version strings and the CHANGELOG, but CI does not enforce any of them — a tag push with mismatched `plugin.json`/`fap_version`/`ui.c`/`pyproject.toml`/CHANGELOG would publish successfully. The tag pattern `*` is very permissive; a tag like `test` or `v0.4-backup` would fire a release build.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: the marketplace.json and plugin.json are hand-authored with no CI validation — a malformed JSON change would only fail at `claude plugin marketplace add` time on a user's machine.

## 16. Documentation

- **`README.md` at repo root**: present — 5163 bytes, user-facing quickstart (what it does, button reference, install, per-OS setup notes for macOS and Linux, troubleshooting table, support/license).
- **Owner profile README at `github.com/jxw1102/jxw1102`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: mixed — `flipper-app/README.md` exists (firmware-oriented), no README inside `plugin/`. The root README covers installation of both components.
- **`CHANGELOG.md`**: present at `flipper-app/CHANGELOG.md` (scoped to firmware) — custom `## vX.Y` section format, not Keep-a-Changelog. No root-level CHANGELOG, no `plugin/CHANGELOG.md`.
- **`architecture.md`**: absent as a dedicated file. Architectural content (three-layer diagram, threading model, protocol, runtime files, platform notes) lives in `CLAUDE.md` at the repo root, which blurs the agent-ops vs architecture separation this project's own conventions enforce.
- **`CLAUDE.md`**: at repo root only (no per-plugin `CLAUDE.md`). Combines build commands, architecture, threading rules, protocol reference, BLE transport details, runtime files, platform notes, command menu system, and release procedure.
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`.
- **LICENSE**: present — 1064 bytes, MIT (standard text).
- **Badges / status indicators**: absent in README (no CI badge, no release badge, no license shield).
- **Pitfalls observed**: CHANGELOG is firmware-scoped; host-bridge and plugin changes are not tracked separately despite having their own versioned manifests. CLAUDE.md carries architecture content that the project's own documentation conventions would place in architecture.md — this plugin doesn't follow those conventions, which is fine for a smaller project but worth noting as the pattern.

## 17. Novel axes

- **md5-over-source-concatenation for dep-install change detection with cross-platform fallback.** The install-hash mechanism concatenates `pyproject.toml` + `bridge/*.py` and hashes the stream, preferring macOS's `md5 -q` and falling back to GNU `md5sum | cut -d' ' -f1`, with a final `|| echo "none"` trapdoor. Stored as `.installed-hash` in the venv directory and compared on every `SessionStart`. The pattern is lighter than `diff -q` (no reference tree needed) and more precise than existence-only checks; the cross-platform shebang-avoidance is elegant but the `"none"` fallback can pin forever on a minimal system.
- **Hardware device as the plugin "UI".** The plugin ships the daemon that talks to a physical Flipper Zero; the Flipper firmware is the UI surface for permission requests, command menus, and status. `PermissionRequest` is routed through hardware button input with a 60-second timeout and fallback to Claude's native dialog on timeout/error/no-device. The `hookSpecificOutput.decision` shape (allow/deny/ask) is used as a generic permission dispatch to a physical input device — a pattern that generalizes to any "remote approval" surface.
- **Unix-socket IPC with refcount-gated daemon lifecycle.** Sessions increment `/tmp/claude-flipper-bridge.refcount` on start and decrement on end; the daemon is killed only when the counter reaches zero. This pattern handles multi-session (multiple concurrent Claude Code windows) without duplicating daemons. Runtime state lives in `/tmp/` with convention-named files (sock, pid, refcount, log, skip-stop flag, turn-stats JSON, bt-name cache).
- **Hook-event fan-out beyond canonical list.** Registers `StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact` — several of which are not in the canonical `docs-hooks.md` surface. The plugin treats hook-event variety as a way to discriminate notification sounds at fine granularity. Worth researching whether these are documented in current Claude Code releases or anticipate planned events.
- **`CLAUDE_PLUGIN_OPTION_<KEY>` forwarding pattern.** The SessionStart hook reads the three `CLAUDE_PLUGIN_OPTION_*` env vars, re-exports them as `FLIPPER_*`, then Python daemon reads `FLIPPER_*`. Decouples the plugin-manifest key naming from the daemon's env-var contract, allowing either side to evolve independently. Useful precedent for the env-var substitution purpose area.
- **Firmware + Python-daemon + plugin-scripts tri-repo pattern.** Single GitHub repo contains the Flipper FAP C source, a Python host daemon (packaged as its own PEP 621 project), and the Claude Code plugin that glues them. `CLAUDE.md` has a 7-step manual release checklist that updates four version strings + CHANGELOG in lockstep. Illustrates a multi-artifact plugin where the plugin surface is only one of three products and version-string drift is a real risk.
- **Hook script as daemon lifecycle manager.** `on-session-start.sh` is simultaneously a dep-install gate, a daemon launcher, a stale-state cleaner, and a session-registration step — all in one bash script under `set -euo pipefail`. This expands the SessionStart hook from "prepare context" to "manage a long-running process with IPC." Distinct from the pattern of "SessionStart installs deps, other hooks do work" because this hook both manages and consumes the daemon.
- **`skip-stop` flag file for self-overriding notification.** `/tmp/claude-flipper-bridge.skip-stop.flag` is written by `on-post-tool-use.py` when a Bash command's text contains the socket path, signaling to `on-stop.sh` that the user (via the `flipper-notify` skill) already set the display — so the Stop hook shouldn't overwrite with a generic "Turn complete." A simple filesystem-flag coordination pattern between sibling hook scripts that would otherwise race on the Flipper display.

## 18. Gaps

- **`on-stop.sh` content.** WebFetch refused to return verbatim content. The summary confirms it reads turn stats from `/tmp/claude-flipper-turn-stats.json` and sends a socket notification, but exact shell logic (pipeline flags, exit handling, flag-file coordination) is not captured. Would be resolved by fetching via a different URL form (e.g., GitHub `blob` view) or inspecting in a clone.
- **Full source of `on-session-end.sh` was obtained; `on-stop.sh` and the Python daemon internals (`daemon.py`, `config.py`, `input.py`) were not fetched.** The daemon's dependency on `pyserial-asyncio` and `bleak` and its asyncio event-loop posture were inferred from CLAUDE.md's architecture section; field-level detail (timeouts, UUIDs, reconnect cadence) was not verified against code.
- **Whether the hook events outside the canonical list (`StopFailure`, `TaskCompleted`, `SubagentStart`, `SubagentStop`, `Elicitation`, `PostToolUseFailure`, `PreCompact`, `PostCompact`) are emitted by current Claude Code.** The hooks.json registers handlers for these; whether they ever fire was not verified. Resolution would require either the current Claude Code source or a live session log.
- **`flipper-app/application.fam` `fap_version` value.** Not fetched. The release checklist treats it as one of four coordinated version strings; the current value (presumably `0.4` or `0.4.0`) was not directly observed.
- **Whether any git pre-commit or pre-push hooks are configured.** Repo has no `.pre-commit-config.yaml` visible in the tree (confirmed via recursive listing), and no `scripts/hooks/` directory. The release checklist is entirely manual.
- **Plugin installation testing / whether marketplace.json actually resolves.** No validator runs in CI, and a dry-run `claude plugin marketplace add` was not performed. The `git-subdir` source with `url` and `path: plugin` should work; not independently verified.
- **Total WebFetch cost.** Approximately 15 WebFetch calls plus 6 `gh api` calls — well under the 25-35 WebFetch budget, leaving room for the bridge-daemon internals fetch if a deeper pass were wanted.
