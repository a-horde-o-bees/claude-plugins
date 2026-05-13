# Release

> Cut a tagged release: read methodology, synthesize a CHANGELOG entry + version recommendation from commit history, gate on user review, execute on approval.

> Synthesis is non-deterministic and a tagged release is hard to amend; the human review gate is mandatory. Everything after approval is automated.

### Dependencies

1. {dependencies}:
    - [[confirm-shared-intent]]
    - [[description-authoring]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context

### Variables

- {version} — optional positional override; when provided, replaces the synthesizer's recommendation. When absent, the recommendation drives.

### Rules

- Intent gate is mandatory — explicit user approval is required before any release-prep work spends tokens (methodology read, synthesizer spawn, etc.). Cheap preconditions run first so failures surface with informative errors, not "do you want to release?" prompts on a dirty tree
- Review gate is mandatory — synthesized CHANGELOG and recommended (or override) version are presented for approval before any write/commit/tag/push action
- Stage rule: only manifest(s) + `CHANGELOG.md`. This satisfies the auto-bump skip condition (commits with only plugin.json don't get z-bumped) when the project relies on a per-commit auto-bump hook
- Tag is annotated (`git tag -a`), not lightweight; message matches the commit message
- Push is `git push origin {branch} {tag}` — single command, both refs together
- Final version (recommended or override) must be strictly greater than current manifest version; tag must not already exist
- Bootstrap dialogue fires only when `.claude/ocd/git/release.md` is absent — subsequent runs read it directly
- Never amend, force-push, or rewrite history

### Process

1. Preconditions:
    1. {current-branch}: bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} ≠ `main`: Exit to user: releases cut from main; currently on {current-branch}
    3. bash: `git diff --quiet` — if non-zero exit: Exit to user: working tree has unstaged changes — clean before releasing
    4. bash: `git diff --cached --quiet` — if non-zero exit: Exit to user: working tree has staged changes — clean before releasing
    5. bash: `git fetch origin main --quiet`
    6. {head-sha}: bash: `git rev-parse HEAD`
    7. {origin-sha}: bash: `git rev-parse origin/main`
    8. If {head-sha} ≠ {origin-sha}: Exit to user: local main not aligned with origin/main — pull or push first
2. Intent gate — confirm with user before any prep work spends tokens:
    1. {last-tag-preview}: bash: `git describe --tags --abbrev=0 2>/dev/null` — empty string if no tags exist
    2. {commits-since}: bash: `git rev-list --count {last-tag-preview}..HEAD` if {last-tag-preview} is non-empty; else bash: `git rev-list --count HEAD`
    3. Present: about to cut a tagged release. Will read project methodology, spawn a synthesizer agent over {commits-since} commits since {last-tag-preview} (or full history when no prior tag) to draft a CHANGELOG entry and recommend a version bump, then present for review before any write/commit/tag/push. Cancel here to avoid the synthesis cost.
    4. Ask user to approve (Q# format) — proceed on approval, Exit to user with "release cancelled" on decline
3. Resolve project methodology:
    1. {release-md-path}: `.claude/ocd/git/release.md`
    2. If {release-md-path} does not exist:
        1. Call: `_release_bootstrap.md` ({release-md-path}: {release-md-path})
    3. Read {release-md-path} into context — used by subsequent steps for manifest paths, bump rules, CHANGELOG format
4. Identify current version:
    1. Per methodology in {release-md-path}, locate manifest path(s) and read {current-version}
5. Find last release tag:
    1. {last-tag}: bash: `git describe --tags --abbrev=0 2>/dev/null` — empty string if no tags exist
    2. If {last-tag} is empty: {commit-range}: HEAD; else: {commit-range}: `{last-tag}..HEAD`
6. Spawn synthesizer agent:
    1. async Spawn: Call: `_release_synthesize.md` ({commit-range}: {commit-range}, {current-version}: {current-version}, {methodology}: content of {release-md-path})
    2. Synthesizer returns: {recommended-version}, {bump-axis-rationale}, {changelog-entry}
7. Resolve final version:
    1. {final-version}: {version} if --version provided (note override in review), else {recommended-version}
    2. {tag}: `v{final-version}`
8. Validate {final-version}:
    1. If {final-version} ≤ {current-version}: Exit to user: version {final-version} is not greater than current ({current-version})
    2. If `git rev-parse --verify --quiet refs/tags/{tag}` exits 0: Exit to user: tag {tag} already exists
9. Review gate:
    1. Display:
        - {final-version} with source label (recommendation vs override)
        - {bump-axis-rationale} — why the synthesizer chose this axis
        - {changelog-entry} verbatim
        - Proposed manifest changes (which files, what version transition)
    2. {decision}: AskUserQuestion — approve or describe adjustments (Q# format)
    3. If {decision} is approve: proceed to step 10
    4. If version change: update {final-version}, re-validate per step 8, re-render bump axis interpretation
    5. If CHANGELOG edit: re-spawn synthesizer with revision instructions, or edit inline if change is mechanical
    6. Go to step 9.1
10. On approval, execute the release:
    1. Update CHANGELOG.md — insert {changelog-entry} above the most recent existing release section, below the `[Unreleased]` pointer paragraph
    2. Bump manifest(s) per methodology — agent edits each manifest file's version field to {final-version} directly using the Edit tool
    3. Stage: bash: `git add <manifest-path-1> [<manifest-path-N> ...] CHANGELOG.md`
    4. Commit: bash: `git commit -m "release {tag}"`
    5. Tag annotated: bash: `git tag -a {tag} -m "release {tag}"`
    6. Push: bash: `git push origin main {tag}`

### Report

Return to caller:

- Tag created: {tag}
- Manifest(s) bumped: list of paths and version transitions
- CHANGELOG entry: link or anchor reference to the new section
- Push: `main` and `{tag}` to origin
- GitHub release workflow: per methodology, `release.yml` (or equivalent) fires on tag push to verify alignment + run tests + create release artifact
