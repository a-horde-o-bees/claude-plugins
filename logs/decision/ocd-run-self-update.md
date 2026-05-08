---
log-role: reference
---

# ocd-run Self-Update on Plugin Upgrade

Decision making `ocd-run` self-trigger `install_deps.sh` when it detects a manifest drift between the cached plugin source and the installed venv. Eliminates session-restart-required UX after plugin upgrades.

## Context

Today's flow on plugin upgrade:

1. User updates ocd plugin via marketplace
2. Claude Code installs new cache version (`~/.claude/plugins/cache/.../<new-version>/`)
3. Existing session's MCP servers and venv reference the OLD version
4. New `pyproject.toml` (with potentially-new deps) sits in the new cache, but `install_deps.sh` only fires on SessionStart
5. User must manually restart the session for new deps to install

Mid-session plugin updates are common (the `/checkpoint` workflow on main does this routinely). The session-restart requirement is a recurring papercut.

## Options Considered

**Status quo — restart required** — accept the friction; document it. Rejected: the friction recurs every checkpoint cycle; the architectural fix is small.

**Auto-trigger from a hook on every PreToolUse** — fire `install_deps.sh` from a PreToolUse hook that diffs the manifest. Rejected: PreToolUse runs on every tool call; manifest-diff per call is excessive; install_deps.sh's own diff check would short-circuit but the hook overhead is still per-call.

**ocd-run does the diff check before exec** — when `ocd-run` is invoked, it diffs the cache's `pyproject.toml` against the installed venv's manifest cache; if they differ, runs `install_deps.sh` synchronously, then proceeds. Adopted.

## Decision

`bin/ocd-run` gains a self-update step before its existing venv discovery and exec:

```bash
# Derive data dir (env var if set, otherwise from cache layout)
data_dir="${CLAUDE_PLUGIN_DATA:-$(<derive from cache path>)}"

# Acquire lock to serialize concurrent invocations
exec 9> "$data_dir/.install-lock"
flock 9

# Diff manifest; install if drifted
if [[ -f "$plugin_root/pyproject.toml" && -f "$data_dir/pyproject.toml" ]]; then
    if ! diff -q "$plugin_root/pyproject.toml" "$data_dir/pyproject.toml" >/dev/null 2>&1; then
        CLAUDE_PLUGIN_DATA="$data_dir" CLAUDE_PLUGIN_ROOT="$plugin_root" "$plugin_root/hooks/install_deps.sh"
    fi
fi

# Existing venv discovery + exec
```

The lock file (`flock` on `$data_dir/.install-lock`) prevents concurrent `ocd-run` invocations from racing into double-install. First invocation installs; subsequent ones block on the lock and skip the diff check (no longer drifted) once they acquire it.

`install_deps.sh` itself is already idempotent (its own `diff -q` short-circuits when no install is needed), so the worst case of redundant invocation is a few milliseconds of file-stat work.

## Consequences

- **Enables:** mid-session plugin upgrades become transparent for everything reached through `ocd-run`. No session restart required for agent-side operations
- **Constrains:** every `ocd-run` invocation pays a manifest-diff cost (~1ms when no drift; the install cost on actual drift). Acceptable in exchange for the UX win
- **MCP gap:** MCP servers spawn from `.mcp.json` directly, NOT through `ocd-run`. They reference `${CLAUDE_PLUGIN_DATA}/venv/bin/python3` and run against whatever venv exists at MCP-startup time. A plugin upgrade that adds an MCP-relevant dep does NOT propagate to the running MCP server until the session restarts (Claude Code re-spawns MCPs at session start). Document this as a known limitation
- **Lock cleanup:** the lock file is in the data dir which persists across plugin versions. Stale locks from killed processes resolve via `flock`'s session-scoped semantics (lock released when fd closes, even on process death)
- **Bootstrap:** on first install, `data_dir/pyproject.toml` doesn't exist — the diff check correctly identifies "drift" (one side absent), runs install, and the marker is then in place
