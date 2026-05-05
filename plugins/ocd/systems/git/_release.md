# Release

> Cut a tagged release. Reads project versioning methodology from `.claude/ocd/git/release.md` (bootstraps if absent), synthesizes a CHANGELOG entry from commit history since the last tag, presents the draft + proposed bump for user review, then on approval writes CHANGELOG, bumps the manifest(s), commits, tags, and pushes.

The version arg is the operator's "deliberate release" signal. The synthesizer reads commits since the last tag and proposes the entry. Review is mandatory — synthesis is non-deterministic and a tagged release is hard to amend, so the human gate stays in the loop. After approval everything else is automated.

### Variables

- {version} — target version passed via positional arg; required

### Rules

- Review gate is mandatory — synthesized CHANGELOG and proposed bump are presented for approval before any write/commit/tag/push action
- Stage rule: only manifest(s) + `CHANGELOG.md`. This satisfies the auto-bump skip condition (commits with only plugin.json don't get z-bumped) when the project relies on a per-commit auto-bump hook
- Tag is annotated (`git tag -a`), not lightweight; message matches the commit message
- Push is `git push origin {branch} {tag}` — single command, both refs together
- Version must be strictly greater than current manifest version; tag must not already exist
- Bootstrap dialogue fires only when `.claude/ocd/git/release.md` is absent — subsequent runs read it directly
- Never amend, force-push, or rewrite history

### Process

1. If not {version}: Exit to user: release requires `<version>` positional arg
2. Preconditions:
    1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} ≠ `main`: Exit to user: releases cut from main; currently on {current-branch}
    3. Run `git diff --quiet && git diff --cached --quiet` — if non-zero exit: Exit to user: working tree has uncommitted changes — clean before releasing
    4. bash: `git fetch origin main --quiet`
    5. If `git rev-parse HEAD` ≠ `git rev-parse origin/main`: Exit to user: local main not aligned with origin/main — pull or push first
    6. {tag} = `v{version}`
    7. If `git rev-parse --verify --quiet refs/tags/{tag}` exits 0: Exit to user: tag {tag} already exists
3. Resolve project methodology:
    1. {release-md-path} = `.claude/ocd/git/release.md`
    2. If {release-md-path} does not exist:
        1. Call: `_release_bootstrap.md` ({release-md-path} = {release-md-path})
    3. Read {release-md-path} into context — used by subsequent steps for manifest paths, bump rules, CHANGELOG format
4. Validate {version}:
    1. Per methodology in {release-md-path}, identify manifest path(s) and current version
    2. If {version} ≤ current: Exit to user: version {version} is not greater than current
5. Find last release tag:
    1. {last-tag} = bash: `git describe --tags --abbrev=0 2>/dev/null` — empty string if no tags exist
    2. If {last-tag} is empty: {commit-range} = HEAD; else: {commit-range} = `{last-tag}..HEAD`
6. Spawn synthesizer agent:
    1. async Spawn: Call: `_release_synthesize.md` ({commit-range} = {commit-range}, {version} = {version}, {methodology} = content of {release-md-path})
    2. {changelog-entry} = synthesizer's returned Keep-a-Changelog formatted markdown section
7. Present review gate:
    1. Display proposed {version} and the bump axis interpretation per methodology (e.g., "y-bump from 0.1.46 → 0.2.0 — feature release per project rules")
    2. Display {changelog-entry} verbatim
    3. Display proposed manifest changes (which files, what version transition)
    4. Ask user to approve or describe adjustments — Q# format with options
    5. If user requests adjustments:
        1. If version change: re-validate per step 4, re-derive bump axis interpretation
        2. If CHANGELOG edit: apply user's directives — re-spawn synthesizer with revision instructions, or edit inline if change is mechanical
        3. Re-present (go to step 7.1)
    6. Loop until approved
8. On approval, execute the release:
    1. Update CHANGELOG.md — insert {changelog-entry} above the most recent existing release section, below the `[Unreleased]` pointer paragraph
    2. Bump manifest(s) per methodology — agent edits each manifest file's version field directly using the Edit tool
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
