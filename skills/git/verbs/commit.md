# git commit

Commit working-tree changes as topic-grouped commits. The gitflow driver runs the deterministic pipeline — submodule recursion, pin detection, conformance checks, staging, committing; judgment enters only at the stop-points below and reaches the repo only as a plan file.

## Variables

- `{cwd}` — `--cwd <path>`; defaults to `.`
- `{paths}` — optional trailing pathspec(s): scope inspection and commit to matching paths, leaving the rest of the tree untouched
- `{on-base}` — `--on-base` present: permit committing onto a protected default branch (intentional admin/base commit; checkpoint passes it in base-mode)
- `{auto}` — `--auto` present: auto-consume submodule pin advances without prompting (checkpoint passes this after landing the submodules deliberately)
- `{pin-only}` — `--pin-only <path>` (repeatable): submodules whose own changes are not committed here; only their pin advance is recorded in the parent

## Rules

- Never amend previous commits unless the user explicitly requests it; never force-push or run destructive operations.
- The driver is the only door in a boxed repo — direct `git`/`gh` are denied there, so every change flows inspect → plan → apply.
- **A plan speaks in whole files.** `apply` resets each repo's index (mixed) before staging, so pre-staged content — including hunk-level staging — folds back into the worktree and commits with whichever group claims its path. Anything no group claims stays pending; it never rides into another group's commit.
- **The whole plan validates before the first commit.** Every group's pathspec is dry-run (staged deletions included), duplicates across groups and no-change groups are rejected, and a failure reports the full problem list with zero commits made — never a partial apply.

## Process

1. `{state}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py inspect --cwd {cwd} --paths {paths}`
2. If `{state}` reports BLOCKED: Exit process: the blockers — resolve them before retrying.
3. If `{state}` reports CLEAN: Exit process: clean working tree within scope.
4. Build the plan from `{state}`'s NEEDS block:
    1. Pin advances: If `{auto}`: consume all. Else: AskUserQuestion per advancing submodule — show its advance log; **consume** or **revert**.
    2. Suspicious untracked files: AskUserQuestion per file — **include**, **exclude**, or **ignore**.
    3. `{groups}` per changed repo (skip repos under `{pin-only}`): partition changed files by topic — tests beside the code they exercise, configuration beside its consumer, files within one directory, a consumed pin advance grouped with the parent change that consumes it. One group when changes are coherent or grouping is ambiguous; multiple only when topics are clearly separable, dependencies before consumers. A single-file change is a valid commit.
    4. `{messages}`: Under concise-prose and description-authoring, draft one message per group — a subject plus body lines of end-state facts visible in the diff or decisions not visible there; no process narration, no restated principles the diff already shows, no project-internal phase labels, no claim the diff or a named decision doesn't carry. Pin-advance lines name the submodule and summarize the consumed commits. Append the co-author trailer when `{inspect}`'s `claude_coauthor` is true (the resolved `user.claude-coauthor` config key, surfaced by the driver because a boxed repo has no other sanctioned way to read it).
    5. If `{state}` shows public-bound: audit `{groups}` and `{messages}` for client/PII leakage — customer names in fixtures, comments, and messages; "for the X migration" phrasing; `user.email` — surface anything suspect and confirm before applying.
5. Write the plan file; Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py apply --plan <plan-file> --cwd {cwd}` (add `--on-base` if `{on-base}`).
6. Report from apply's output: commits per repo (sha + subject), pin dispositions, remaining tree state.
