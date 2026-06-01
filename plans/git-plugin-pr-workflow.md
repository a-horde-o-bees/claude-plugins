# Git plugin PR workflow

Extend the git plugin's skills to cover the GitHub-collaboration loop: opening, watching, merging, and cleaning up after pull requests. The current plugin stops at push + CI watch; the PR portion of the developer cycle is entirely manual.

## Goal

A single `/git-pr` skill with verbs (`open`, `status`, `merge`, `cleanup`) that closes the loop from a published feature branch to a merged, cleaned-up local state on `main`. Composes cleanly with `/git-checkpoint`: checkpoint ends at the CI gate, `/git-pr` picks up there.

## Driving observations

- Workflow gap: `/git-checkpoint`'s last step is `/git-ci`. The next steps (open PR, watch the PR's review/CI surface, merge, restore local main and prune the merged branch) require manual `gh pr` calls or the GitHub web UI.
- Skill sync only fires when `/checkpoint` runs on `main`. So a feature branch's CI passing isn't the delivery moment — the merge into `main` is, because that's what the marketplace cache + `claude plugins update` will pull next.
- The gap shows up at the end of every feature: the loop never closes inside the plugin's vocabulary.

## Proposed shape

One skill `/git-pr` with verbs, `gh` CLI under the hood. Verbs share preconditions and reporting; one body keeps the merge-related decisions colocated.

- `/git-pr open [--draft] [--base main]` — runs `gh pr create`. Description seed = commit subjects + a bulleted body from message bodies; user reviews before submission. Idempotent: refuses if a PR already exists for the head branch.
- `/git-pr status` — surfaces review state (required reviewers, approvals, changes-requested), CI state on the PR, mergeability (clean / has-conflicts / behind-base), branch protection requirements. One-page summary, no inventing.
- `/git-pr merge [--strategy squash|merge|rebase] [--cleanup]` — gates on green CI + required reviews per branch protection; merges via `gh pr merge`; deletes the remote head branch. Strategy default reads project policy (see methodology file below). With `--cleanup`, also runs the local cleanup verb.
- `/git-pr cleanup` — `git checkout {base} && git pull && git branch -D {head-branch}`. Safe-by-default: refuses if the local branch has unmerged commits that aren't in the just-merged PR.

## Bump-check mechanic (replaces `.github/workflows/auto-bump.yml`)

The current `auto-bump.yml` (server-side push-back after merge) is structurally unsuited to a PR-gated `main`: the bot's push is blocked by branch protection, and even when bypassed the "second commit after merge" pattern decouples the deployment signal from the content change. The fix is to move the bump into the PR itself, with CI enforcing.

`/git-pr` takes over the responsibility, with two complementary pieces:

- **Author-side** (`/git-pr open` and `/git-pr status`): detect plugin code changes in the PR's diff (any `plugins/<name>/` file outside `.claude-plugin/plugin.json` itself). For each affected plugin, ensure `plugin.json` increments its patch version base→head. `open` either applies the bumps automatically and includes them in the PR's commit chain, or surfaces missing bumps as a precondition. `status` reports any missing bump as a blocker before merge.
- **CI-side** (`.github/workflows/bump-check.yml`, replacing `auto-bump.yml`): a `pull_request` job that runs the same detection and fails if any plugin code changed without a corresponding version increment. Becomes a required status check on `main` so branch protection gates on it.

Result: the bump lives in the PR atomically with the change. Merge produces one commit on `main` containing both. `/checkpoint` on `main` syncs immediately. No push-back, no branch-protection conflict, no bypass-actor configuration needed.

**Retirement:** `.github/workflows/auto-bump.yml` deletes when the new mechanic ships. The local `.githooks/pre-commit` bump logic retires too — direct-to-main admin-bypass edge cases either include their own bumps or accept the deployment-signal mismatch (no longer worth carrying the hook for that case alone).

## Open items

- **Skill granularity** — one skill with verbs vs. four skills (`/git-pr-open`, `/git-pr-status`, …). Verbs are more compact; separate skills allow richer per-verb description matching. Current plugin uses one-skill-per-verb (`/git-commit`, `/git-push`); a verbed skill would be a precedent break worth confirming.
- **Merge strategy default** — squash, merge, or rebase? Likely project methodology; pull from a methodology file (see next item) if present.
- **Methodology file** — analog to `.claude/git/release.md`: `.claude/git/pr.md` declaring default strategy, base branch, required-reviewers convention, draft-by-default, optional auto-merge. Skill bootstraps the dialogue when absent.
- **Branch protection interaction** — `gh pr merge` enforces required reviews by default. Should the skill surface the requirement before attempting (so failures are informative) or just attempt and surface `gh`'s error?
- **Conflict / needs-rebase recovery** — when `mergeable` is `CONFLICTING` or the head is behind the base, options: (a) exit-to-user with `git rebase {base}` instructions; (b) attempt the rebase, surface conflicts; (c) trigger GitHub's "Update branch" (merge-base-into-head). Likely (a) by default; (c) opt-in.
- **Integration with `/git-checkpoint`** — should checkpoint optionally chain into `/git-pr open` on first push of a feature branch (i.e. when there is no PR yet for the head)? Or stay strict at commit + push + CI? A `--with-pr` flag is the conservative answer.
- **`/git-release` interaction** — release is on `main`; release-prep PRs themselves are a workflow corner. Probably out of scope for the first version.
- **`allowed-tools` audit** — `Bash(gh *)` needs the explicit allow-list entry; the skill won't run otherwise.

## Related pre-rollout adjustments

- Bootstrap `.claude/git/pr.md` methodology file analog to `.claude/git/release.md`. Skill reads it at runtime for project-specific policy.
- Update `/git-checkpoint`'s description to point at `/git-pr` as the next stage of the loop. The boundary is clear: checkpoint ends at CI, `/git-pr` begins there.

## Out of scope for this plan

- PR review automation — running review checks, summarizing diffs for reviewers. Separate skill, distinct domain.
- Auto-merge policies — already a GitHub feature; the skill could trigger via `gh pr merge --auto`, but the policy lives upstream of the skill.
- Release-tag-after-merge orchestration — composition with `/git-release`, separate concern from the PR loop itself.
