# Checkpoint Bootstrap

> Guided dialogue producing the project's local `.claude/git/checkpoint.md`. Fires the first time `/git-checkpoint` runs in a project without one and with no `--path` override. Detection-first: read repo state, pre-fill a draft, present one batched proposal. Subsequent runs read the written file directly.

## Variables

- {config} — destination path (typically `.claude/git/checkpoint.md`)

## Rules

- Single batched proposal — render the full draft for one-shot review, not section-by-section.
- Write only after approval; create the parent directory if absent.
- Keep the file minimal: a `Path:` line and an optional `## Augmentations` list of project steps. Augmentations are free-form instructions (including script calls) the orchestrator honors — not a fixed schema.

## Process

1. Detect the integration model:
    1. {default-branch}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — fallback `main`
    2. {protection}: bash: `gh api repos/{owner}/{repo}/branches/{default-branch}/protection >/dev/null 2>&1 && echo enforced || echo none`
    3. {path-default}: `pr` if {protection} is `enforced` (branch protection ⇒ PR workflow), else propose a choice between `pr` and `direct`

2. Detect candidate augmentations (suggest, never assume):
    1. {has-bump}: bash: `[ -f scripts/bump-apply.py ] && echo yes || echo no` — if yes, suggest a pre-land bump step
    2. {has-sync}: bash: `[ -f scripts/checkpoint-sync.py ] && echo yes || echo no` — if yes, suggest an on-main delivery step

3. Compose the draft `checkpoint.md`:
    - `Path: {path-default}`
    - `## Augmentations` with the detected suggestions as bullet instructions (omit the section if none detected). Apply /concise-prose.

4. Review gate:
    1. Present the full draft. Apply /confirm-shared-intent.
    2. {decision}: AskUserQuestion — approve / adjust path / adjust augmentations / cancel
    3. If adjust: revise per feedback; go to 4.1
    4. If cancel: Return to caller — bootstrap declined; proceeding this run with `Path: {path-default}` and no augmentations (nothing written)

5. Write {config} (creating `.claude/git/` if absent)

6. Return to caller: wrote {config} — Path: {path}, augmentations: {count}
