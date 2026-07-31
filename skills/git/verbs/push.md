# git push

Land the current branch on its remote, submodules before the parent that pins them. The driver fetches and rebases onto upstream first, so every push is fast-forward by construction; a rebase conflict stops the flow with nothing pushed.

## Variables

- `{cwd}` — `--cwd <path>`; defaults to `.`
- `{branch}` — `--branch <name>`, required at the top level: naming the branch is the confirmation, and a mismatch with the current branch stops the flow
- `{pin-only}` — `--pin-only <path>` (repeatable): submodules the parent only pins, never direct-pushes — their changes land via their own lifecycle (checkpoint runs it)

## Rules

- A dirty tree is not pushed around — commit first (`/git commit`) or ask the user; never auto-stash.
- Never force-push; the rebase-then-push flow makes non-fast-forward pushes impossible rather than forbidden.

## Process

1. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py push --cwd {cwd} --branch {branch}` with one `--skip <path>` per `{pin-only}` entry.
2. If BLOCKED (branch mismatch, detached HEAD, or a rebase conflict): Exit process: the driver's surface — it has already left the tree safe (conflicted rebases are aborted).
3. Report per repo: branch pushed, upstream set, pin-only skipped, or no-remote skipped.
