# git release

Cut a tagged release: read the methodology, synthesize CHANGELOG + version from commit history, gate on user review, execute on approval.

> Synthesis is non-deterministic and a tagged release is hard to amend; the human review gate is mandatory. Everything after approval is the driver's single cut.

## Dependencies

- concise-prose and description-authoring govern the CHANGELOG entry and review presentation; every entry traces to actual commits in the range (the synthesizer's own rule).
- `partials/release-synthesize.md` — the spawned CHANGELOG synthesizer's directive.

## Variables

- `{version}` — optional positional override; replaces the synthesizer's recommendation when provided
- `{recurse}` — `--recurse-submodules`; run each declared submodule's release before the parent's
- From the preflight JSON: `{default-branch}`, `{last-tag}`, `{commit-range}`, `{commits-since}`, `{submodules}`

## Rules

- Submodule recursion is off by default — each submodule releases on its own cadence, by its own `/git release`; cutting a release is a deliberate per-project act. `--recurse-submodules` opts in: each declared submodule runs this whole verb from its own root (its own methodology, gates, and cut — every gate fires per repo, never batched), the parent commits each advanced pin through the commit verb, and the pins push before the parent's own release so its preflight sees an aligned tree and its CHANGELOG range includes the pin advances.
- Intent gate is mandatory — explicit user approval before any release-prep work spends tokens (methodology read, synthesizer spawn). The driver's preflight runs first so failures surface as informative errors, not as "release?" prompts on a dirty tree.
- Review gate is mandatory — synthesized CHANGELOG and final version are presented for approval before any write/commit/tag/push.
- The cut is the driver's: it stages only the named manifest(s) + `CHANGELOG.md` (satisfying the per-commit auto-bump skip condition), commits `release {tag}`, creates the annotated tag with the same message, and pushes branch + tag together. Never amend; never force-push; never rewrite history.
- Final version strictly greater than current; tag must not already exist — validated by the driver before review and again at the cut.
- The [Bootstrap](#bootstrap) dialogue fires only when `.claude/git/release.md` is absent.

## Process

1. `{pre}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-preflight` — BLOCKED (not on default branch, dirty tree, not aligned with origin): Exit process: the driver's message verbatim. Bind `{default-branch}`, `{last-tag}`, `{commit-range}`, `{commits-since}`.
2. Intent gate:
    1. Present concisely: about to cut a tagged release; will read methodology, spawn synthesizer over `{commits-since}` commits since `{last-tag}` (or full history if no prior SemVer tag), then review gate before any write/commit/tag/push. When `{recurse}` and `{submodules}` is non-empty, also present the recursion scope: each of `{submodules}` runs this whole release flow first (own gates, own cut), its pin advance is committed and pushed in this repo, and only then does this repo release. Cancel here to avoid the synthesis cost.
    2. `{approval}`: AskUserQuestion — approve / cancel; never proceed without the explicit approval (confirm-shared-intent).
    3. If `{approval}` is cancel: Exit process: release cancelled

3. Submodule recursion — only when `{recurse}` and `{submodules}` is non-empty:
    1. For each `{sub}` in `{submodules}`:
        1. Run this whole verb again from `{sub}`'s root (`{cwd}`: `{sub}` — every driver command in that run takes `--cwd {sub}`, and its methodology resolves at `{sub}/.claude/git/release.md`; forward `--recurse-submodules` so nested submodules recurse the same way). If that run exits without a cut (cancelled, or nothing to release), continue to the next `{sub}` — an unchanged pin needs no commit.
        2. Call: verbs/commit.md — record the advanced pin in this repo: the plan's only content is `pins: {"{sub}": "consume"}`; the pin-advance message names `{sub}` and summarizes the consumed commits (its new release tag is the summary's anchor).
    2. If any pin was committed: Call: verbs/push.md — the parent's preflight requires alignment with origin, and the pin advances belong in the release's commit range.
    3. Re-run step 1 (`release-preflight`) — re-bind `{commit-range}` and `{commits-since}`; the range now includes the pin advances the synthesizer should narrate.

4. Resolve methodology:
    1. `{release-md-path}`: `.claude/git/release.md`
    2. If `{release-md-path}` does not exist: Call: [Bootstrap](#bootstrap)
    3. `{methodology}`: Read `{release-md-path}`

5. `{current-version}`: per `{methodology}`, locate manifest path(s) and read
6. Synthesize CHANGELOG + version:
    1. Spawn async agent to: read and follow `${CLAUDE_SKILL_DIR}/partials/release-synthesize.md` (`{commit-range}`: `{commit-range}`, `{current-version}`: `{current-version}`, `{methodology}`: `{methodology}`)
    2. Returns: `{recommended-version}`, `{bump-axis-rationale}`, `{changelog-entry}`
7. `{final-version}`: `{version}` if provided (label override in review), else `{recommended-version}`; `{tag}`: `v{final-version}`
8. Validate: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-validate --version {final-version} --current {current-version}` — BLOCKED (not greater, or tag exists): surface verbatim; a version override goes back through this step.
9. Review gate:
    1. Display concisely:
        - `{final-version}` with source label (recommendation vs override)
        - `{bump-axis-rationale}` — why the synthesizer chose this axis
        - `{changelog-entry}` verbatim
        - Proposed manifest changes (paths + version transitions)
    2. `{decision}`: AskUserQuestion — approve or describe adjustments; never cut without the explicit approval (confirm-shared-intent).
    3. If `{decision}` is approve: go to step 10
    4. If version change: update `{final-version}`, re-validate per step 8, re-render rationale
    5. If CHANGELOG edit: re-spawn synthesizer with revision instructions, or edit inline if mechanical
    6. Go to step 9.1

10. Execute:
    1. Insert `{changelog-entry}` into CHANGELOG.md above the most recent existing release section (below the `[Unreleased]` pointer)
    2. Bump manifest(s) per `{methodology}` — Edit each manifest's version field to `{final-version}`
    3. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-cut --version {final-version} --current {current-version}` with one `--manifest <path>` per manifest — stages, commits, tags, and pushes in one run; its progressive output names what completed if a step fails

## Report

Return to caller:

- Tag: `{tag}`
- Manifest(s) bumped: list of paths and version transitions
- CHANGELOG entry: anchor to the new section
- Push: branch + tag pushed to origin (the driver's cut output)
- When `{recurse}` ran: each submodule's tag and the parent pin-advance commits recorded for it
- GitHub release workflow: fires on tag push per methodology — verifies alignment, runs tests, creates release artifact

## Bootstrap

Guided dialogue producing the project's local `.claude/git/release.md`. Fires the first time this verb runs in a project without an existing methodology config; subsequent invocations read the written file directly.

> Detection-first: scan project artifacts (manifests, CHANGELOG, tags, auto-bump hooks) and pre-populate suggestions, then present one batched proposal rather than walking the user section-by-section.

### Rules

- Single batched proposal: render the full draft `release.md` content for one-shot user review rather than walking section-by-section
- Q# format on the approval question
- Write only after the user approves — no partial writes that leave the file in an inconsistent state

### Process

1. Detect existing release artifacts: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py release-bootstrap-detect` — bind `{manifest-candidates}`, `{has-changelog}`, `{existing-tags}`, `{tag-format}`, `{auto-bump-hook}`, `{github-release-workflow}`
2. `{template}`: Read `${CLAUDE_SKILL_DIR}/assets/release.md` — starter template anchoring output structure
3. Compose draft `release.md` using `{template}` structure and detection-driven defaults for every section, under markdown-authoring and concise-prose:
    1. **Versioning scheme** — if `{existing-tags}` match `v\d+\.\d+\.\d+`, fill in semver `x.y.z`; otherwise list semver/calver/custom as choices
    2. **Manifest paths** — fill in `{manifest-candidates}`; flag version-bearing best guesses for user confirmation
    3. **Auto-bump behavior** — if `{auto-bump-hook}`: fill in "auto-bump runs in pre-commit hook on every commit; release stages only manifest + CHANGELOG to skip"; else "no auto-bump"
    4. **Bump axis decision rules** — if semver, fill in template's recommended defaults (breaking → x, new capability → y, fix or auto-bumped → z); for other schemes fill in equivalent rules from `{template}`
    5. **Commit + tag conventions** — if `{existing-tags}` or `{github-release-workflow}` suggest a format, fill it in; otherwise `release v<x.y.z>` commit + annotated tag
    6. **CHANGELOG format** — if `{has-changelog}`: read CHANGELOG.md header and fill in detected format hints; else Keep a Changelog 1.1.0
    7. **Synthesize source** — `git log <last-tag>..HEAD` (or `HEAD` for first release)
    8. **Post-tag-push automation** — if `{github-release-workflow}`: Read `.github/workflows/release.yml` and summarize what fires
    9. **Preconditions** — standard set (on default branch, clean tree, aligned with remote, tag doesn't exist, version `>` current)
4. Review gate:
    1. Display: the composed `release.md` content verbatim, and a detection summary (what was auto-detected vs guessed)
    2. `{decision}`: AskUserQuestion — approve as-is or call out section-level adjustments; never write without the explicit approval (confirm-shared-intent).
    3. If `{decision}` is approve: go to step 5
    4. Apply the user's directives (revise sections, swap defaults, add gates); re-render the revised draft
    5. Go to step 4.1
5. Write:
    1. Verify `{release-md-path}`'s parent directory exists; create if absent
    2. Write composed content to `{release-md-path}`
6. Return to caller: path written, sections populated, detection summary (auto-detected vs user-supplied)
