---
status: confirmed
last-verified: 2026-05-21
---

# Project-directory resolution via CLAUDE_CODE_SESSION_ID + JSONL cwd field

## Hypothesis

When a skill is invoked at user-level (e.g. installed under `~/.claude/skills/` or a user-scope plugin) and its scripts run as a Bash subprocess from a Claude Code session, the calling project's directory can be resolved without requiring the downstream user to install a `SessionStart` hook by:

1. Reading the `CLAUDE_CODE_SESSION_ID` environment variable that Claude Code sets in every Bash subprocess (regardless of invocation mode — interactive UI, headless `claude -p`, sub-agents)
2. Globbing `~/.claude/projects/*/<session-id>.jsonl` to locate the session's transcript
3. Tail-scanning that JSONL for the latest line carrying a `cwd` field (set on every `user`-type message line)

The `cwd` field is authoritative — it reflects whichever directory Claude Code is currently tracking, not the parent-shell cwd at process spawn.

## Why it matters

Drives the project-dir resolver chain for any plugin whose user-level installation needs to know the calling project:

- `plans/transcripts.md` Workstream A1 (transcripts DB moves to user-level; per-project filtering needs project resolution)
- Pending navigator state-location move (same resolver chain)
- Any future plugin facing the same surface

Alternatives are worse:

- **Requiring a `SessionStart` hook** in downstream `settings.json` is invasive distribution overhead — defeats the "install one plugin, it just works" UX
- **`git rev-parse --show-toplevel`** from cwd fails in non-git projects and after mid-session `cd`
- **Decoding `~/.claude/projects/<encoded-cwd>` directory names** is lossy (`/` and `.` both collapse to `-`) — unsafe
- **`/proc/$PPID/cwd`** is Linux-only

## Test design

### Probe A — Env-var presence in interactive context

```bash
printenv | grep -i claude | sort
```

**Expected output** includes at least:

```
CLAUDECODE=1
CLAUDE_CODE_ENTRYPOINT=cli
CLAUDE_CODE_EXECPATH=<path>
CLAUDE_CODE_SESSION_ID=<uuid>
```

`CLAUDE_PROJECT_DIR` is **absent** unless the user has a hook setting it. Confirms `CLAUDE_CODE_SESSION_ID` is set by Claude Code in interactive Bash subprocesses.

### Probe B — Env-var presence in headless context with parent env stripped

```bash
cd /tmp && env -u CLAUDE_CODE_SESSION_ID -u CLAUDE_PROJECT_DIR claude -p \
  'You are running inside a Claude Code headless session. Without using `pwd`, `git`, or any cwd-based heuristic, determine the project directory the calling user opened Claude Code in. You may only use: (a) environment variables set by Claude Code, and (b) JSONL transcript files under ~/.claude/projects/. Use the Bash tool. Report concisely: (1) which env var you used, (2) the JSONL file path you read, (3) the resolved project directory. If you cannot resolve it, say so and why.'
```

Strips `CLAUDE_CODE_SESSION_ID` and `CLAUDE_PROJECT_DIR` from the parent environment so the probe verifies what the child `claude -p` instance sets, not what leaks from the invoking shell.

**Expected:** the headless session sets its own `CLAUDE_CODE_SESSION_ID` to a NEW UUID (not inherited from parent), writes a JSONL at `~/.claude/projects/-tmp/<new-uuid>.jsonl`, and an unprimed agent locates it via env+glob and extracts `cwd=/tmp`.

### Probe C — JSONL `cwd` field presence

```bash
JSONL="$(ls -t ~/.claude/projects/*/$CLAUDE_CODE_SESSION_ID.jsonl 2>/dev/null | head -1)"
grep -o '"cwd":"[^"]*"' "$JSONL" | tail -1
```

**Expected:** prints the latest `cwd` recorded for the session, e.g. `"cwd":"/home/dev/projects/claude-plugins"`.

### Detection method

For Probe A and C: shell exit code zero + non-empty stdout matching the expected pattern.

For Probe B: parse the headless agent's response for three required claims:
- Env var name = `CLAUDE_CODE_SESSION_ID`
- JSONL path containing `~/.claude/projects/-tmp/`
- Resolved project directory = `/tmp`

Run procedure: execute Probe A first to confirm the basic env contract holds in the running session; then run Probe C to confirm the JSONL is hot and the field present; then run Probe B to confirm the env-var-name + JSONL contract holds for a fresh headless session with parent env stripped (this is the load-bearing test for "no downstream hook needed").

## Expected outcomes

| Observed | Interpretation |
|---|---|
| All three probes succeed; env var present; JSONL discoverable; `cwd` field present | Hypothesis **confirmed** — resolver chain works without downstream hook |
| Probe A: `CLAUDE_CODE_SESSION_ID` absent | Claude Code version no longer sets this var; resolver mechanism broken — investigate replacement env var or migration path |
| Probe B: headless `claude -p` does not set the env var | Headless mode behaves differently from interactive; resolver needs a separate code path for headless contexts (or hypothesis refuted for headless) |
| Probe B: agent fails to resolve `/tmp` from session-id alone | JSONL not yet written by the time the agent probes; mechanism has a race — investigate timing |
| Probe C: no `cwd` field in JSONL | JSONL schema changed; resolver needs to consult a different field or different file |
| JSONL filename ≠ `<session-id>.jsonl` | Naming convention changed; resolver needs updated glob pattern |

## Historical results

| Date | Claude Code version | Probe A | Probe B | Probe C | Notes |
|---|---|---|---|---|---|
| 2026-05-21 | v2.1.146 | ✓ (`CLAUDE_CODE_SESSION_ID=b539017b-…`) | ✓ (fresh session-id `309edae8-…`; JSONL at `~/.claude/projects/-tmp/309edae8-…jsonl`; `cwd=/tmp` extracted) | ✓ | Initial verification. Headless agent resolved unprimed with no coaching — confirms the chain is also discoverable by an unprimed LLM, not just by code. |

## Quirks worth knowing

- **Encoded-directory names lose information.** `~/.claude/projects/<encoded-cwd>` collapses `/` and `.` to `-`. `claude-plugins--centralize-tools` could in principle mean `claude/plugins-/centralize/tools` or other combinations. Never reverse-decode. Always go through the session-id glob.
- **First-line cwd absence.** The first line of a session's JSONL is `permission-mode` metadata without `cwd`. A probe issued before any user turn returns nothing from the JSONL; the tail-scan needs to skip to the next line with `cwd`. In practice, by the time a skill is invoked, a user turn has landed.
- **Plugin-cache git-checkout trap.** Every plugin install under `~/.claude/plugins/cache/<author>/<plugin>/<ver>/` is itself a git checkout, so `git rev-parse` from a script's own directory returns the wrong root. The reject-if-inside-`~/.claude/` guard catches it.
- **Sub-agents inherit `CLAUDE_CODE_SESSION_ID`.** Task-spawned sub-agents see the parent session's id, so they resolve to the parent's project dir naturally. No special handling needed inside sub-agents.
- **Read-frequency cost.** Each project-dir resolution by the JSONL path involves a glob + tail-scan. Cheap, but if hit in a hot loop, cache the result within the subprocess lifetime.

## Cross-references

- [`confirmed-facts.md`](../../confirmed-facts.md) § "Platform discovery" — digest entry pointing back here
- [`architecture.md`](../../architecture.md) § "Project-directory resolution" — the recommendation derived from this assertion
- `plans/transcripts.md` Workstream A1 — first consumer of the verified mechanism
