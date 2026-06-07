# PR Bootstrap

> Guided dialogue producing the project's local `.claude/git/pr.md`. Fires the first time `/git pr-open` runs in a project without an existing methodology config.
>
> Detection-first: scan the repo's default branch, protection, allowed merge strategies, CODEOWNERS, and PR template, pre-populate suggestions, then present one batched proposal rather than walking section-by-section. Subsequent PR-verb invocations read the written file directly.

## Variables

- {pr-md-path} — destination path for the populated methodology doc (typically `.claude/git/pr.md`)

## Rules

- Single batched proposal: render the full draft `pr.md` for one-shot review rather than section-by-section.
- Detection records *preferences*, not the live gate — solo-vs-team merge behavior is re-detected at merge time from branch protection. Note this in the file so it isn't mistaken for the authority.
- Q# format on the approval question.
- Write only after the user approves — no partial writes.

## Process

1. Detect PR artifacts:
    1. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — falls back to `main` if unset
    2. {protection}: bash: `gh api repos/{owner}/{repo}/branches/{default-branch}/protection >/dev/null 2>&1 && echo enforced || echo none` — `enforced` signals a team default, `none` a solo default
    3. {allowed-strategies}: bash: `gh api repos/{owner}/{repo} --jq '[if .allow_squash_merge then "squash" else empty end, if .allow_merge_commit then "merge" else empty end, if .allow_rebase_merge then "rebase" else empty end] | join(", ")' 2>/dev/null`
    4. {codeowners}: bash: `for f in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS; do [ -f "$f" ] && echo "$f" && break; done` — empty if none
    5. {pr-template}: bash: `for f in .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md; do [ -f "$f" ] && echo "$f" && break; done` — empty if none

2. {template}: Read `${CLAUDE_SKILL_DIR}/assets/pr.md` — starter structure
3. Compose draft `pr.md` from {template} with detection-driven defaults. Apply /author-markdown and /concise-prose:
    1. **Base branch** — fill in {default-branch}
    2. **Merge strategy** — default to the first of {allowed-strategies} (squash/merge/rebase order); list {allowed-strategies} as the allowed set
    3. **Draft** — default `no` unless the project signals otherwise
    4. **Reviews** — if {protection} is `enforced` or {codeowners} non-empty: fill in "team — required approvals enforced by branch protection / CODEOWNERS at {codeowners}"; else "none configured (solo)"
    5. **Conflict recovery** — default exit-to-user with rebase guidance
    6. **Cleanup** — delete remote head + prune local base on merge: `yes`
    7. If {pr-template} non-empty: note that `gh pr create` will pick up the repo PR template; the authored body augments it

4. Review gate:
    1. Display the composed `pr.md` verbatim + a detection summary (auto-detected vs guessed)
    2. {decision}: AskUserQuestion — approve as-is or call out section-level adjustments. Apply /confirm-shared-intent.
    3. If approve: proceed to step 5
    4. Apply directives; re-render; go to 4.1

5. Write:
    1. Verify {pr-md-path}'s parent directory exists; create if absent
    2. Write composed content to {pr-md-path}

## Report

Return to caller:

- Path written: {pr-md-path}
- Detection summary: default branch, protection (team/solo), allowed strategies, CODEOWNERS, PR template
