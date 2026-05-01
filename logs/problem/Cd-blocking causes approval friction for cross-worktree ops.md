# Cd-blocking causes approval friction for cross-worktree ops

The project's `workflow.md` rule blocks `cd` / `pushd` / `popd` in agent Bash invocations to prevent session-cwd drift. The rule is correct in spirit — drift would corrupt every subsequent Bash call's project context — but it forces every cross-worktree operation through `git -C <path>`, `CLAUDE_PROJECT_DIR=<path> ...`, or absolute-path script invocations. Many of those alternative forms are not in the standard allowlist patterns and trigger approval popups, slowing operations that `cd` could have legitimately resolved without persisting state.

## Reproduction

From a session whose cwd is sandbox worktree A:

1. Need to run `python3 scripts/auto_init.py` against main worktree at /path/to/main
2. Approved patterns include `Bash(python3 scripts/auto_init.py)` (relative path, runs in cwd)
3. Workarounds:
    - `CLAUDE_PROJECT_DIR=/path/to/main python3 /path/to/main/scripts/auto_init.py` — env-var prefix + absolute path; not in allowlist; popup
    - `python3 -c "import os; os.chdir('/path/to/main'); ..."` — convoluted; popup
    - `cd /path/to/main && python3 scripts/auto_init.py` — would match the allowlist but blocked by the rule

`cd` in a single Bash invocation is process-local — the next Bash call gets a fresh shell at the session root. There is no actual drift to prevent within one command. The rule blocks it anyway.

## Suspected middle ground

The rule's concern is **persistent** drift across Bash calls, which is impossible because each Bash call is a fresh shell. Two possible refinements:

- **Allow `cd` only in compound commands.** Pattern like `cd <path> && <command>` is single-invocation and cannot drift. The session-cwd convention remains: every Bash call starts at session root, the rule only blocks bare `cd` or `pushd`/`popd` (which would matter in a persistent shell, but Claude Code's Bash isn't persistent anyway). Practically: the rule could be loosened to "no bare `cd`; compound `cd <path> && <cmd>` is allowed because each Bash call is a fresh shell"
- **Add allowlist entries for cross-worktree forms.** `Bash(git -C *:* )`, `Bash(CLAUDE_PROJECT_DIR=* python3 *)`, etc. Reduces popups for the workarounds without touching the cd rule

## Concrete instance

This session: `/checkpoint` against main from a sandbox session required hand-rolling `git -C /path/to/main commit -m "..."` for every commit (8 commits) and `CLAUDE_PROJECT_DIR=/path/to/main python3 /path/to/main/scripts/auto_init.py` for auto-init. Multiple of these triggered approval popups despite each being a single-shell, single-shot operation with no drift risk.

## Investigation notes

- The current rule is in `plugins/ocd/systems/rules/templates/workflow.md` § Working Directory
- The auto-approval hook at `.claude/hooks/auto_approval.py` (or wherever the cd-block lives) needs review for the compound-command exception
- Consider whether Claude Code's Bash tool genuinely uses a fresh shell per invocation in all cases — if any caching/persistence exists, the compound-command exception fails
