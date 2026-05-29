# Platform-discovery assertions

How a Bash-invoked skill subprocess discovers calling-session context (project directory, session ID, environment) without requiring downstream hooks.

The motivating problem: user-level-installed skills run as subprocesses with no inherent knowledge of which Claude Code session invoked them or which project the user opened. Some environment variables and on-disk state surfaces are reliable; others are absent in some contexts. Claude Code's documentation doesn't consistently describe which surfaces are populated when. These assertions establish the reliable subset.

## Assertions

| # | Assertion | Status | Why ordered here |
|---|---|---|---|
| 1 | [`project-dir-resolution.md`](./project-dir-resolution.md) — `CLAUDE_CODE_SESSION_ID` + JSONL `cwd` field is authoritative for project-dir lookup | confirmed | Foundational; the resolver chain that other plugins (transcripts, navigator) depend on |

## Canonical patterns confirmed

**Project-dir resolution chain** (verified 2026-05-21, Claude Code v2.1.146):

1. `CLAUDE_PROJECT_DIR` env var — honors explicit override; hook-context only by design, fall through if absent
2. `CLAUDE_CODE_SESSION_ID` → `~/.claude/projects/*/<session-id>.jsonl` → tail-scan latest line with `cwd` field — authoritative, handles non-git projects, mid-session `cd`, sub-agents
3. `git rev-parse --show-toplevel` from cwd — tail safety net for very-early-session probes (before first user-turn JSONL line)
4. Reject paths inside `~/.claude/` — guards against plugin-cache git-checkout trap (every plugin install under `~/.claude/plugins/cache/<author>/<plugin>/<ver>/` is itself a git checkout)

## Untested gaps

| Gap | Why it matters | Priority |
|---|---|---|
| **`CLAUDE_CODE_SESSION_ID` name stability across releases** | If Anthropic renames or removes it, every plugin that resolves project dir via this chain breaks. | Medium — re-verify after each major Claude Code release |
| **macOS / native-Windows behavior** | Verified on Linux + WSL. Other platforms might differ on env-var population or JSONL writes. | Medium — block on first macOS user report or check during cross-platform sweeps |
| **Cross-platform `/proc/$PPID/cwd` alternative** | macOS lacks `/proc`; a portable secondary fallback would harden the chain. | Low — only if the primary chain proves fragile |
| **Sub-agent JSONL behavior** | Sub-agents inherit `CLAUDE_CODE_SESSION_ID`; do they write to the same JSONL as the parent, or a separate one? Affects resolver behavior inside Task-spawned agents. | Low — single-session-id inheritance is the observed behavior |
