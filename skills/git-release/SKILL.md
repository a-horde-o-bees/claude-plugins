---
name: git-release
description: Use when cutting a tagged release of the current project — explicit signals "cut a release", "tag a version", "ship v...", "release v...", or any context where producing a SemVer tag + CHANGELOG entry + manifest bump is the next action. Reads the project's release methodology, spawns a CHANGELOG synthesizer over commits since the last SemVer tag, gates on human review before any write/commit/tag/push. Does not recurse into submodules by default — each submodule has its own release cadence; pass `--recurse-submodules` to opt in.
argument-hint: "[<version-override>] [--recurse-submodules]"
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash(git *)
  - Skill
  - AskUserQuestion
---

# /git-release

Cut a tagged release. Read methodology, synthesize CHANGELOG + version from commit history, gate on user review, execute on approval.

> Synthesis is non-deterministic and a tagged release is hard to amend; the human review gate is mandatory. Everything after approval is automated.

## Dependencies

- `/concise-prose`, `/author-descriptions`, `/honesty` — the CHANGELOG entry and review presentation are authored under these.

## Variables

- `{version}` — optional positional override; replaces the synthesizer's recommendation when provided

## Rules

- Submodule recursion is opt-out by default — each submodule has its own release cadence. The recursion lives in the sibling git skills (`/git-commit`, `/git-push`, `/git-ci`); cutting a release is a deliberate per-project act. Pass `--recurse-submodules` to opt in (each declared submodule then runs its own `/git-release` flow before the parent records the new pin)
- Intent gate is mandatory — explicit user approval before any release-prep work spends tokens (methodology read, synthesizer spawn). Cheap preconditions run first so failures surface as informative errors, not as "release?" prompts on a dirty tree.
- Review gate is mandatory — synthesized CHANGELOG and final version are presented for approval before any write/commit/tag/push.
- Stage only manifest(s) + `CHANGELOG.md` — satisfies the per-commit auto-bump skip condition (manifest-only commits don't trigger the z-bump hook).
- Annotated tag (`git tag -a`); tag message matches the commit message.
- Push branch + tag together with a single `git push origin {branch} {tag}`.
- Final version strictly greater than current; tag must not already exist.
- Bootstrap dialogue fires only when `.claude/git/release.md` is absent.
- Stage by name (never `git add -A`); never amend; never force-push; never rewrite history.

## Process

1. Preconditions:
    1. {current-branch}: bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} ≠ `main`: Exit process: releases cut from main; currently on {current-branch} — switch to main or rebase the change onto main first
    3. bash: `git diff --quiet`; if non-zero: Exit process: working tree has unstaged changes — clean or commit before releasing
    4. bash: `git diff --cached --quiet`; if non-zero: Exit process: working tree has staged changes — commit or reset before releasing
    5. bash: `git fetch origin main --quiet`
    6. {head-sha}: bash: `git rev-parse HEAD`
    7. {origin-sha}: bash: `git rev-parse origin/main`
    8. If {head-sha} ≠ {origin-sha}: Exit process: local main not aligned with origin/main — pull or push first

2. Intent gate:
    1. {last-tag}: bash: `git tag --sort=-version:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' | head -1` — most recent SemVer-shaped tag, empty if none
    2. {commits-since}: bash: `git rev-list --count {last-tag}..HEAD` if {last-tag} is non-empty, else bash: `git rev-list --count HEAD`
    3. Present: about to cut a tagged release; will read methodology, spawn synthesizer over {commits-since} commits since {last-tag} (or full history if no prior SemVer tag), then review gate before any write/commit/tag/push. Cancel here to avoid the synthesis cost. Apply /concise-prose.
    4. {approval}: AskUserQuestion — approve / cancel. Apply /confirm-shared-intent.
    5. If {approval} is cancel: Exit process: release cancelled

3. Resolve methodology:
    1. {release-md-path}: `.claude/git/release.md`
    2. If {release-md-path} does not exist: Call: `_bootstrap.md` ({release-md-path}: {release-md-path})
    3. {methodology}: Read {release-md-path}

4. {current-version}: per {methodology}, locate manifest path(s) and read
5. Resolve {commit-range}: `HEAD` if {last-tag} is empty, else `{last-tag}..HEAD`
6. Synthesize CHANGELOG + version:
    1. async Spawn: Call: `_synthesize.md` ({commit-range}: {commit-range}, {current-version}: {current-version}, {methodology}: {methodology})
    2. Returns: {recommended-version}, {bump-axis-rationale}, {changelog-entry}

7. {final-version}: {version} if provided (label override in review), else {recommended-version}
8. {tag}: `v{final-version}`
9. Validate:
    1. If {final-version} ≤ {current-version}: Exit process: version {final-version} is not greater than current ({current-version}) — pass a higher version or omit to use the recommendation
    2. {tag-exists}: bash: `git rev-parse --verify --quiet refs/tags/{tag}` exits 0
    3. If {tag-exists}: Exit process: tag {tag} already exists — pass a different version or delete the existing tag if it was created in error

10. Review gate:
    1. Display the following. Apply /concise-prose:
        - {final-version} with source label (recommendation vs override)
        - {bump-axis-rationale} — why the synthesizer chose this axis
        - {changelog-entry} verbatim
        - Proposed manifest changes (paths + version transitions)
    2. {decision}: AskUserQuestion — approve or describe adjustments. Apply /confirm-shared-intent.
    3. If {decision} is approve: proceed to step 11
    4. If version change: update {final-version}, re-validate per step 9, re-render rationale
    5. If CHANGELOG edit: re-spawn synthesizer with revision instructions, or edit inline if mechanical
    6. Go to step 10.1

11. Execute:
    1. Insert {changelog-entry} into CHANGELOG.md above the most recent existing release section (below the `[Unreleased]` pointer)
    2. Bump manifest(s) per {methodology} — Edit each manifest's version field to {final-version}
    3. bash: `git add <manifest-path-1> [<manifest-path-N> ...] CHANGELOG.md`
    4. bash: `git commit -m "release {tag}"`
    5. bash: `git tag -a {tag} -m "release {tag}"`
    6. bash: `git push origin main {tag}`

## Report

Return to caller:

- Tag: {tag}
- Manifest(s) bumped: list of paths and version transitions
- CHANGELOG entry: anchor to the new section
- Push: branch + tag pushed to origin
- GitHub release workflow: fires on tag push per methodology — verifies alignment, runs tests, creates release artifact
