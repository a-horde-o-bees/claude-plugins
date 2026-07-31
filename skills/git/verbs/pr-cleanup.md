# git pr cleanup

> Restore local base and tear down a merged head branch. Fully deterministic — the driver runs the whole flow; this verb reports its verdict verbatim. Safe-by-default; idempotent.

## Variables

- `{head}` — `--head <name>`; defaults to the current branch.
- `{base}` — `--base <name>`; defaults to the repo's default branch.

## Rules

- **The PR's merged state is the authority, not git ancestry.** Squash and rebase merges leave the head's commits absent from base, so ancestry wrongly reports "not merged." When the PR is `MERGED`, force-delete is safe — the work is in base under a new SHA. The driver encodes this; never second-guess its refusal or its go-ahead.
- **Safe-by-default** — with no merged PR, the driver refuses to delete a head that has commits not on base. Unmerged work is never silently dropped.
- **Idempotent** — a missing remote or local head branch is a no-op, not an error (merge may have used `--delete-branch`, or cleanup may rerun).

## Process

1. `{result}`: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py pr-cleanup` (append ` --head {head}` / ` --base {base}` when given)
2. If BLOCKED (head is base, detached with no `--head`, or unmerged commits with no merged PR): Exit process — surface the driver's message verbatim; merging or discarding is the user's explicit call.
3. Report from `{result}` — see ## Report.

## Report

Return to caller:

- Base: `{base}` — `{synced (pulled + pruned) | not synced (was not on base)}`
- Remote head: `{deleted | already gone}`
- Local head: `{deleted | already gone}`
- PR-merged authority: `{yes | no — ancestry-safe delete}`
