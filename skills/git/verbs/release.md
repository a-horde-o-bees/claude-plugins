# git release

Cut a tagged release. Read methodology, synthesize CHANGELOG + version from commit history, gate on user review, execute on approval.

> Synthesis is non-deterministic and a tagged release is hard to amend; the human review gate is mandatory. Everything after approval is the driver's single cut.

## Dependencies

- `/concise-prose`, `/description-authoring` — the CHANGELOG entry and review presentation are authored under these; every entry traces to actual commits in the range (the synthesizer's own rule).
- `partials/release-bootstrap.md`, `partials/release-synthesize.md` — methodology bootstrap + the spawned CHANGELOG synthesizer.

## Variables

- `{version}` — optional positional override; replaces the synthesizer's recommendation when provided
- From the preflight JSON: `{default-branch}`, `{last-tag}`, `{commit-range}`, `{commits-since}`

## Rules

- Submodule recursion is opt-out by default — each submodule has its own release cadence. The recursion lives in the other git verbs; cutting a release is a deliberate per-project act. Pass `--recurse-submodules` to opt in (each declared submodule then runs its own `/git release` flow before the parent records the new pin)
- Intent gate is mandatory — explicit user approval before any release-prep work spends tokens (methodology read, synthesizer spawn). The driver's preflight runs first so failures surface as informative errors, not as "release?" prompts on a dirty tree.
- Review gate is mandatory — synthesized CHANGELOG and final version are presented for approval before any write/commit/tag/push.
- The cut is the driver's: it stages only the named manifest(s) + `CHANGELOG.md` (satisfying the per-commit auto-bump skip condition), commits `release {tag}`, creates the annotated tag with the same message, and pushes branch + tag together. Never amend; never force-push; never rewrite history.
- Final version strictly greater than current; tag must not already exist — validated by the driver before review and again at the cut.
- Bootstrap dialogue fires only when `.claude/git/release.md` is absent.

## Process

1. `{pre}`: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-preflight` — BLOCKED (not on default branch, dirty tree, not aligned with origin): surface the driver's message verbatim and stop. Bind `{default-branch}`, `{last-tag}`, `{commit-range}`, `{commits-since}`.
2. Intent gate:
    1. Present: about to cut a tagged release; will read methodology, spawn synthesizer over `{commits-since}` commits since `{last-tag}` (or full history if no prior SemVer tag), then review gate before any write/commit/tag/push. Cancel here to avoid the synthesis cost. Apply /concise-prose.
    2. `{approval}`: AskUserQuestion — approve / cancel. Apply /confirm-shared-intent.
    3. If `{approval}` is cancel: Exit process: release cancelled

3. Resolve methodology:
    1. `{release-md-path}`: `.claude/git/release.md`
    2. If `{release-md-path}` does not exist: Call: partials/release-bootstrap.md (`{release-md-path}`: `{release-md-path}`)
    3. `{methodology}`: Read `{release-md-path}`

4. `{current-version}`: per `{methodology}`, locate manifest path(s) and read
5. Synthesize CHANGELOG + version:
    1. async Spawn: Call: partials/release-synthesize.md (`{commit-range}`: `{commit-range}`, `{current-version}`: `{current-version}`, `{methodology}`: `{methodology}`)
    2. Returns: `{recommended-version}`, `{bump-axis-rationale}`, `{changelog-entry}`

6. `{final-version}`: `{version}` if provided (label override in review), else `{recommended-version}`; `{tag}`: `v{final-version}`
7. Validate: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-validate --version {final-version} --current {current-version}` — BLOCKED (not greater, or tag exists): surface verbatim; a version override goes back through this step.
8. Review gate:
    1. Display the following. Apply /concise-prose:
        - `{final-version}` with source label (recommendation vs override)
        - `{bump-axis-rationale}` — why the synthesizer chose this axis
        - `{changelog-entry}` verbatim
        - Proposed manifest changes (paths + version transitions)
    2. `{decision}`: AskUserQuestion — approve or describe adjustments. Apply /confirm-shared-intent.
    3. If `{decision}` is approve: proceed to step 9
    4. If version change: update `{final-version}`, re-validate per step 7, re-render rationale
    5. If CHANGELOG edit: re-spawn synthesizer with revision instructions, or edit inline if mechanical
    6. Go to step 8.1

9. Execute:
    1. Insert `{changelog-entry}` into CHANGELOG.md above the most recent existing release section (below the `[Unreleased]` pointer)
    2. Bump manifest(s) per `{methodology}` — Edit each manifest's version field to `{final-version}`
    3. bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-cut --version {final-version} --current {current-version}` with one `--manifest <path>` per manifest — stages, commits, tags, and pushes in one run; its progressive output names what completed if a step fails

## Report

Return to caller:

- Tag: `{tag}`
- Manifest(s) bumped: list of paths and version transitions
- CHANGELOG entry: anchor to the new section
- Push: branch + tag pushed to origin (the driver's cut output)
- GitHub release workflow: fires on tag push per methodology — verifies alignment, runs tests, creates release artifact
