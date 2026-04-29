---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Workflow

Project-specific operational patterns governing how agents work day-to-day in this project.

## Working Directory

Working directory must remain project root for the entire session. Use absolute paths or tool flags instead of changing directories.

- No `cd`, `pushd`, `popd` — use `git -C <path>` for submodule operations

## Agents

Minimize agent count for ad-hoc work — each sub-agent independently loads context and rediscovers the project, multiplying token cost. Default to a single agent processing tasks sequentially within one context. Skills that prescribe agent spawning have already made the cost decision at design time — follow the prescription without second-guessing the count.

## Push Blocking

Git push can be temporarily blocked for safe ad-hoc execution that might otherwise trigger a push (e.g., worktree-isolated evaluation, hook-tests that exercise git state). The block sets an invalid pushurl on `origin` — any push attempt fails loudly with `fatal: '/dev/null' does not appear to be a git repository`. Separate concern from testing discipline (`testing.md` covers that); Push Blocking is a safety envelope for execution that might push.

- Block: `git config remote.origin.pushurl "file:///dev/null"`
- Unblock: `git config --unset remote.origin.pushurl`
- Check: `git config --get remote.origin.pushurl` — no output means unblocked

When push fails unexpectedly with "does not appear to be a git repository": check whether pushurl is set. A left-over block from a crashed evaluation or interrupted test is the likely cause — unblock with the command above.

## Hook-Registered File Renames

Files registered as hook commands in `.claude/settings.json` have a soft coupling to their path — the command string is resolved at invocation time, and a dangling reference blocks every tool call whose matcher fires the hook. Renaming a hook file before updating its registration triggers a chicken-and-egg lockout: the Edit that would fix `settings.json` is itself blocked by the stale hook.

Correct order — update the registration first, then rename:

1. Edit `.claude/settings.json` to reference the new filename
2. Rename the hook file

Recovery when already locked out: restore the old path as a symlink or copy (`ln -s <new> <old>` or `cp`), update `settings.json`, then remove the temporary. Same discipline applies to any file path baked into `settings.json` — commands, MCP server entries, anything resolved at tool-call time.

