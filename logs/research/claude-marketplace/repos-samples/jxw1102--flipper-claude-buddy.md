# Sample

Mirrors of `https://github.com/jxw1102/flipper-claude-buddy`. Flipper Zero hardware controller for Claude Code: sound, vibration, and display feedback on a physical Flipper Zero connected via USB or BLE; the plugin ships a daemon that talks to a Flipper firmware app and routes hook events through it. MIT-licensed; 21 stars at sample time; current tip is `0.4.0` on default branch `main`.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry. Top-level carries only `name`, `owner`, `plugins` — no `metadata` wrapper, no top-level `description`, no `pluginRoot`. The marketplace entry uses `source: "git-subdir"` with `path: plugin` pointing at the same GitHub URL — re-clones the repo from origin even though marketplace and plugin co-locate. A `relative` source would also work for in-repo co-location; the author chose `git-subdir` so a marketplace-add from GitHub resolves the plugin without users cloning separately.

## Plugin source binding

### `git-subdir` into upstream

Source format `git-subdir` with `path: plugin`. Marketplace name `flipper-claude-buddy` and plugin name `flipper-claude-buddy` are identical — `plugin install flipper-claude-buddy@flipper-claude-buddy` works but reads redundantly. `strict` field absent (implicit default); `skills` override absent.

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

No `category`, `tags`, or `keywords` on the `plugins[0]` marketplace entry. Keywords exist only inside `plugin/.claude-plugin/plugin.json` (`keywords: ["flipper-zero", "claude-code", "vibe-coding", "notifications", "remote-control"]`) — plugin-manifest keyword metadata, not marketplace-surfaced discoverability.

### `$schema` absence on per-plugin manifests

Neither `marketplace.json` nor `plugin.json` references a `$schema` URL.

## Version coordination

### Multi-site sprawl (5+ locations)

Four manifests must be kept in lockstep per the release checklist in `CLAUDE.md`: `plugin/.claude-plugin/plugin.json` (`0.4.0`), `flipper-app/application.fam` `fap_version`, `plugin/host-bridge/pyproject.toml` `version`, and a UI version string in `flipper-app/ui.c`. The CHANGELOG (firmware-scoped at `flipper-app/CHANGELOG.md`) is also part of the manual update sequence. Tag is `0.4` (no `v` prefix, no patch segment); `plugin.json` is `0.4.0` — tag/manifest format diverges.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No stable/latest segregation. Users pin implicitly via whatever ref `claude plugin marketplace add jxw1102/flipper-claude-buddy` resolves (default branch main). A future bump from `0.4.0` to `0.5.0` on main would be picked up on the next marketplace update with no opt-in buffer.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags placed on main (e.g., `0.4` at commit 612382e0). A `feat/nus-profile` feature branch exists; no `release/*` pattern. Tag format is `0.1`, `0.2`, `0.3`, `0.4` — no `v` prefix, no semver patch segment in the tag itself even though `plugin.json` uses `0.4.0`. CI reacts to tags but does not author them.

## Plugin-component registration

### Default convention discovery

`plugin/.claude-plugin/plugin.json` declares no component paths. Claude Code picks up `plugin/hooks/hooks.json`, `plugin/skills/notify/SKILL.md`, and implicit script locations by convention.

### Hooks-json with broad event coverage

`hooks.json` registers 15 event types each with empty-string matcher (fire on everything): `Notification`, `Stop`, `StopFailure`, `Elicitation`, `PostToolUseFailure`, `PostToolUse`, `TaskCompleted`, `SessionEnd`, `PermissionRequest`, `SessionStart`, `UserPromptSubmit`, `PreCompact`, `PostCompact`, `SubagentStart`, `SubagentStop`. Several of these (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `SubagentStart`, `SubagentStop`, `Elicitation`) are not in the canonical `docs-hooks.md` surface — the plugin treats hook-event variety as a way to discriminate notification sounds at fine granularity, anticipating or relying on non-public events.

## Component composition

### Skills (universal)

One skill: `plugin/skills/notify/SKILL.md`. Skill frontmatter uses `allowed-tools: Bash` (plain tool name, no permission-rule brackets).

### Hooks

`plugin/hooks/hooks.json` registers 15 event types, all with empty-string matcher. Handler scripts split between bash (`on-session-start.sh`, `on-stop.sh`) and Python (`on-*.py`).

## Skill authoring conventions

### Standard frontmatter

Skill `notify` declares standard `name` and `description` plus `allowed-tools: Bash` (single tool name, scalar form).

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. The plugin installs a Python entry point (`flipper-bridge = "bridge.__main__:main"` in `pyproject.toml`), but it is reached via `"$VENV_DIR/bin/python" -m bridge` from the SessionStart hook, not via a plugin-level `bin/` wrapper. Users never invoke `flipper-bridge` directly. The daemon is launched as `nohup "$VENV_DIR/bin/python" -m bridge ... &` from `on-session-start.sh` so it detaches from the hook process. Lifecycle managed via socket/PID/refcount files in `/tmp/`: `claude-flipper-bridge.sock`, `claude-flipper-bridge.pid`, `claude-flipper-bridge.refcount`, `claude-flipper-bridge.log`, plus a `skip-stop.flag`. SessionStart increments refcount on start, SessionEnd decrements; daemon dies only at zero. Multi-session (concurrent Claude Code windows) coordinates via the shared refcount.

## Server runtime (MCP)

### No bin entry / direct invocation

No `.mcp.json`, no MCP server. All work is via skills and hooks; the Python daemon is not an MCP server but a Unix-socket-based notification dispatcher.

## Dependency installation

### Pip + stdlib venv (no `uv`)

Uses `python3 -m venv` and the venv's own `pip install --force-reinstall`. No `uv` usage. Install location: `${CLAUDE_PLUGIN_DATA}/venv` with default fallback `/tmp/flipper-claude-buddy/venv` if the env var is unset (`PLUGIN_DATA="${CLAUDE_PLUGIN_DATA:-/tmp/flipper-claude-buddy}"`). The dependency-install path coexists with daemon-lifecycle work in the same SessionStart hook — after install completes, the script forks a long-running Python daemon (`nohup "$VENV_DIR/bin/python" -m bridge ... &`) and registers the session in `/tmp/claude-flipper-bridge.refcount`.

### Self-healing inline install at MCP launch

`on-session-start.sh` concatenates `pyproject.toml` + every `bridge/*.py` file and pipes through `md5 -q` (BSD `md5(1)` on macOS) with fallback to `md5sum | cut -d' ' -f1` (GNU coreutils on Linux) and a final `|| echo "none"` trapdoor:

```bash
CURRENT_HASH=$(cat "$BRIDGE_DIR/pyproject.toml" "$BRIDGE_DIR"/bridge/*.py 2>/dev/null \
  | md5 -q 2>/dev/null \
  || cat "$BRIDGE_DIR/pyproject.toml" "$BRIDGE_DIR"/bridge/*.py 2>/dev/null \
  | md5sum | cut -d' ' -f1 \
  || echo "none")
```

Hash stored in `$VENV_DIR/.installed-hash` (the `MARKER` file). On each SessionStart, mismatched/missing hash triggers venv recreate + `pip install --force-reinstall "$BRIDGE_DIR"`. A running daemon with the old hash is killed first (`[bridge] Bridge code changed; restarting daemon $OLD_PID...`). The hash mechanism is content-based rather than version-based — concatenates source and hashes the stream rather than diffing files against a reference tree.

## Install change detection

### Diff-based byte comparison of manifest

Concatenation hash over `pyproject.toml` + `bridge/*.py` rather than file-pair `diff -q`. Same idempotency property — content-based detection — but stored as a single hash file rather than a reference tree.

## Install failure posture

### `set -euo pipefail` + `trap 'exit 0' ERR` — non-blocking with cleanup

`on-session-start.sh` runs under `set -euo pipefail` early; later hook steps deliberately suppress failures (`|| true`, `2>/dev/null || true`) so notification failures don't propagate. Final line is `exit 0` regardless. Bridge-start failure emits a human-readable stderr message (`[bridge] Socket not available, bridge may have failed. Check $LOG`) and exits 0 — the plugin degrades gracefully when the Flipper isn't connected.

### Implicit retry via late-write cache marker

The marker (`$VENV_DIR/.installed-hash`) is written only after `pip install` succeeds (line ordering: `pip install ... 2>&1 | tail -1 >&2` then `echo "$CURRENT_HASH" > "$MARKER"`). The `tail -1` pipe masks pip's exit code at the pipeline level, but `set -o pipefail` surfaces pip's failure code so the marker is not written on failed install. A failed install therefore retries on the next session.

## Install trigger and lifecycle

### SessionStart direct invocation

`on-session-start.sh` (bash) runs as the SessionStart hook handler. Performs install (md5-gated venv recreation), then daemon-lifecycle work (kill stale, launch fresh, refcount-register the session).

## Hook handler runtime

### Per-hook bash scripts with selective strict mode

Hook scripts split between bash (`on-session-start.sh`, `on-stop.sh`) and Python (`on-*.py`). Bash scripts use `#!/bin/bash` shebang with `set -euo pipefail`; Python scripts use `#!/usr/bin/env python3`. Most `send_to_flipper` calls are wrapped `try: ... except Exception: pass`. No central emit helper; each script re-implements the socket-send-with-swallow pattern.

## Hook output contract

### `decision: "block"` for gating

`on-permission-request.py` emits structured JSON to stdout with the `hookSpecificOutput.decision` shape: `{"behavior": "allow"}` / `{"behavior": "deny"}` / `{"behavior": "ask"}`. The decision is delegated to a Flipper Zero device via socket round-trip with a 60-second timeout; on timeout/error/no-device the script exits 1 to fall back to Claude's native dialog.

### Stderr for human display + stdout JSON for harness

The sound/notification hooks exit silently (`sys.exit(0)`) without emitting JSON; failure-path scripts (`on-stop-failure.sh`) write to stderr via the `||` fallthrough pattern rather than structured JSON. `on-permission-request.py` is the script that uses structured stdout JSON.

## Hook failure posture

### Fail-open with always-exit-0

When the bridge socket is missing, hooks exit 0 (non-blocking). The rest prioritize "don't break Claude if the Flipper isn't plugged in." The exception is `on-permission-request.py` which exits 1 on "no bridge" or timeout/error to let Claude's permission dialog handle the decision.

## Tool-use enforcement

### `PermissionRequest` with `if:` allowlist

`on-permission-request.py` participates in `PermissionRequest` and delegates allow/deny decisions to the Flipper hardware via a Unix-socket round-trip with 60-second timeout. Status-code ladder defined in the bridge daemon (`ok` / `ask` / `no_flipper` / `timeout` / `busy` / `error`). Emits `hookSpecificOutput.decision` (`allow|deny|ask`). Falls back to Claude's native dialog on timeout, error, or absent device (`exit 1`). No configurable timeout — the 60-second wait is hardcoded.

### PostToolUse `*` context tracking

Two PostToolUse hooks with empty-string matcher — `on-post-tool-use.py` (per-tool sound based on tool-name classification) and `on-post-tool-use-failure.py` (error sound on failure). No PreToolUse hooks; the plugin does not block or gate tool calls before they run.

## Session context loading

### Dependency install only (no context emission)

SessionStart hook does no `additionalContext` emission. It runs full daemon-lifecycle logic (install gating, daemon launch, session registration). The `source` field (startup/resume/clear/compact/model) is consulted internally for the Flipper subtext label but the same init logic executes regardless. UserPromptSubmit (`on-prompt-submit.sh`) sends a "Thinking..." display message to the Flipper rather than emitting context.

## SessionStart matcher scope

### Empty matcher (all sub-events)

Empty-string matcher fires on all sub-events. `socket exists → skip start` guard avoids redundant daemon launches on `compact`/`resume` after the daemon is already running.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The plugin uses hook events, not the monitors system. Live behavior is implemented via the daemon and per-event sound/vibration/display dispatch, not via monitors.

### Version-floor declaration absent

No `monitors` dependency, no min-Claude-Code-version declared in README or plugin.json. The plugin registers hook events (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`) that aren't in the canonical list — these require a Claude Code version that emits them. Without a version floor declared, users on older Claude Code versions silently get a subset of functionality with no diagnostic.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field. Single plugin in single marketplace. Tag format is `0.1`…`0.4` (no plugin-name prefix). The plugin depends on the host-side Python package and Flipper firmware app — real runtime dependencies but they live outside the `dependencies` field because they are not plugins.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

`userConfig` declared with three fields (`serial_port`, `transport`, `bluetoothName`). Each field has `title`, `type: "string"`, `description`, `sensitive: false`. No `default`, no `enum` for `transport` (which accepts "auto"/"usb"/"ble" but isn't typed as a choice).

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

`on-session-start.sh` reads `CLAUDE_PLUGIN_OPTION_serial_port`, `CLAUDE_PLUGIN_OPTION_transport`, and `CLAUDE_PLUGIN_OPTION_bluetoothName`, then re-exports them under `FLIPPER_*` names the Python bridge expects. Decouples the plugin-manifest key naming from the daemon's env-var contract — either side can evolve independently. No `${user_config.KEY}` substitution syntax is used (the plugin only has hook scripts, no MCP/LSP/monitor commands that would consume that form). Field-name casing is mixed: `bluetoothName` (camelCase) vs `serial_port` and `transport` (snake_case).

## Testing

### No tests

No `tests/` directory, no `pytest.ini`, no `conftest.py`, no `[tool.pytest.ini_options]` section in `pyproject.toml`. A refactor would surface regressions only via user-observed misbehavior on the Flipper.

## CI workflow shape

### Single workflow, sparse coverage

`.github/workflows/build-fap.yml` only. Triggers: `workflow_dispatch`, `push` with path filter `flipper-app/**`, and `tags: '*'`. Runs `ufbt build` to compile the Flipper FAP firmware on `ubuntu-latest` with Python 3.11; uploads `.fap` as artifact; on tag pushes attaches it to a GitHub release via `softprops/action-gh-release@v2`. No pytest, no linting, no manifest validation. CI does not exercise `on-session-start.sh` or `on-permission-request.py` — a broken hook script ships green. Caching: none (no `actions/cache`, no `cache: 'pip'`).

### Action-pinning conventions

All actions tag-pinned by major: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`, `softprops/action-gh-release@v2`. No SHA pins.

## Marketplace validation

### No validation

No validation workflow. Marketplace.json and plugin.json are hand-authored — a malformed JSON change would fail only at `claude plugin marketplace add` time on a user's machine.

## Release automation

### Tag-triggered binary build + GH Release with signing

Release is a side-effect of the build workflow's tag-conditional step, not a dedicated workflow. `push: tags: '*'` triggers `ufbt build` to produce `~/.ufbt/build/claude_buddy.fap`; conditional `softprops/action-gh-release@v2` step attaches it. GitHub release notes are auto-generated (no body provided). Tag pattern `*` is permissive — a tag like `test` or `v0.4-backup` would fire a release build. No tag-on-main verification, no tag-matches-version check, no tag-format regex.

### CHANGELOG with non-Keep-a-Changelog custom sections

`flipper-app/CHANGELOG.md` follows a custom `## vX.Y` section format with bullet lists of changes — not Keep-a-Changelog. Not parsed into release notes (the 0.4 release body on GitHub is `null`; earlier releases have empty-string bodies).

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (5163 bytes) — user-facing quickstart with what it does, button reference, install, per-OS setup notes for macOS and Linux, troubleshooting table, support/license. `flipper-app/README.md` exists separately (firmware-oriented); no README inside `plugin/`. The root README covers installation of both components.

### CHANGELOG and ARCHITECTURE absent at root

No root-level `CHANGELOG.md`; no `plugin/CHANGELOG.md`. CHANGELOG is firmware-scoped at `flipper-app/CHANGELOG.md`. No dedicated `architecture.md`; architectural content (three-layer diagram, threading model, protocol, runtime files, platform notes) lives in `CLAUDE.md` at repo root.

### CLAUDE.md as project-config surface

`CLAUDE.md` at repo root only (no per-plugin `CLAUDE.md`). Combines build commands, architecture, threading rules, protocol reference, BLE transport details, runtime files, platform notes, command menu system, and the manual 7-step release procedure (commit clean → update CHANGELOG → `fap_version` → ui.c version string → plugin.json version → pyproject.toml version → commit → tag → push). Architecture content lives here rather than in a separate `architecture.md`.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` at repo root (1064 bytes, MIT). SPDX `MIT` declared in `plugin/.claude-plugin/plugin.json` and `plugin/host-bridge/pyproject.toml`. Single agreement.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, or `.github/PULL_REQUEST_TEMPLATE.md`.

## State persistence

### File-based memory stack with auto-gitignore

Runtime state lives in `/tmp/` with convention-named files: `claude-flipper-bridge.sock` (socket), `claude-flipper-bridge.pid` (daemon PID), `claude-flipper-bridge.refcount` (multi-session counter), `claude-flipper-bridge.log` (daemon log), `claude-flipper-turn-stats.json` (turn statistics), `claude-flipper-bridge.skip-stop.flag` (self-overriding notification coordination), and a BLE name cache.

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Venv at `${CLAUDE_PLUGIN_DATA}/venv` with `.installed-hash` marker. Default fallback `/tmp/flipper-claude-buddy/venv` if the env var is unset.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Hook scripts and Python bridge source under plugin tree (referenced via path relative to the hook's own directory); venv under `${CLAUDE_PLUGIN_DATA}/venv`; runtime IPC files under `/tmp/`. Three storage tiers — code, isolated venv, ephemeral runtime state.

## PATH augmentation and host-project setup

### None (plugin operates standalone)

No PATH modification. Hook scripts resolve via path relative to the hook directory; Python bridge runs from the venv directly.

## Cross-role tools

### Bash

Bash is the runtime for `on-session-start.sh`, `on-stop.sh`, and other shell hooks. Set with `set -euo pipefail`; cross-platform hash fallback in the install path uses bash conditionals.

### Python (stdlib + pip + uv)

Python 3 (system interpreter) bootstraps the venv (`python3 -m venv`); the venv's own `pip` installs the bridge package via `pip install --force-reinstall "$BRIDGE_DIR"`. Bridge package depends on `pyserial`, `pyserial-asyncio`, `bleak` (declared in `pyproject.toml`). No `uv` usage.

### `${CLAUDE_PLUGIN_DATA}`

Venv lives under `${CLAUDE_PLUGIN_DATA}/venv` with default fallback to `/tmp/flipper-claude-buddy`.
