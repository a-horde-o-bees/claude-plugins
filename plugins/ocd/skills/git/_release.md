# Release

> Cut a tagged release. Read project methodology, synthesize CHANGELOG + version from commit history, gate on user review, execute on approval.

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

- {version} — optional positional override; replaces the synthesizer's recommendation when provided

### Rules

- Intent gate is mandatory — explicit user approval before any release-prep work spends tokens (methodology read, synthesizer spawn). Cheap preconditions run first so failures surface with informative errors, not "release?" prompts on a dirty tree
- Review gate is mandatory — synthesized CHANGELOG and final version are presented for approval before any write/commit/tag/push
- Stage only manifest(s) + `CHANGELOG.md` — satisfies the per-commit auto-bump skip condition (manifest-only commits don't trigger the z-bump hook)
- Annotated tag (`git tag -a`); tag message matches the commit message
- Push branch + tag together with a single `git push origin {branch} {tag}`
- Final version strictly greater than current; tag must not already exist
- Bootstrap dialogue fires only when `.claude/ocd/git/release.md` is absent
- Never amend, force-push, or rewrite history

### Process

1. Preconditions:
    1. {current-branch}: bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} ≠ `main`: Exit to user: releases cut from main; currently on {current-branch} — switch to main or rebase the change onto main first
    3. bash: `git diff --quiet`; if non-zero: Exit to user: working tree has unstaged changes — clean or commit before releasing
    4. bash: `git diff --cached --quiet`; if non-zero: Exit to user: working tree has staged changes — commit or reset before releasing
    5. bash: `git fetch origin main --quiet`
    6. {head-sha}: bash: `git rev-parse HEAD`
    7. {origin-sha}: bash: `git rev-parse origin/main`
    8. If {head-sha} ≠ {origin-sha}: Exit to user: local main not aligned with origin/main — pull or push first

2. Intent gate:
    1. {last-tag-preview}: bash: `git describe --tags --abbrev=0 2>/dev/null` — empty if no tags
    2. {commits-since}: bash: `git rev-list --count {last-tag-preview}..HEAD` if {last-tag-preview} is non-empty, else bash: `git rev-list --count HEAD`
    3. Present: about to cut a tagged release; will read methodology, spawn synthesizer over {commits-since} commits since {last-tag-preview} (or full history if no prior tag), then review gate before any write/commit/tag/push. Cancel here to avoid the synthesis cost.
    4. {approval}: AskUserQuestion — approve / cancel (Q# format)
    5. If {approval} is cancel: Exit to user: release cancelled

3. Resolve methodology:
    1. {release-md-path}: `.claude/ocd/git/release.md`
    2. If {release-md-path} does not exist: Call: `_release_bootstrap.md` ({release-md-path}: {release-md-path})
    3. {methodology}: Read {release-md-path}

4. {current-version}: per {methodology}, locate manifest path(s) and read

5. Find last tag:
    1. {last-tag}: bash: `git describe --tags --abbrev=0 2>/dev/null` — empty if no tags
    2. {commit-range}: `HEAD` if {last-tag} is empty, else `{last-tag}..HEAD`

6. Synthesize CHANGELOG + version:
    1. async Spawn: Call: `_release_synthesize.md` ({commit-range}: {commit-range}, {current-version}: {current-version}, {methodology}: {methodology})
    2. Returns: {recommended-version}, {bump-axis-rationale}, {changelog-entry}

7. {final-version}: {version} if --version provided (note override in review), else {recommended-version}

8. {tag}: `v{final-version}`

9. Validate:
    1. If {final-version} ≤ {current-version}: Exit to user: version {final-version} is not greater than current ({current-version}) — pass a higher version or omit --version to use the recommendation
    2. {tag-exists}: bash: `git rev-parse --verify --quiet refs/tags/{tag}` exits 0
    3. If {tag-exists}: Exit to user: tag {tag} already exists — pass a different --version or delete the existing tag if it was created in error

10. Review gate:
    1. Display:
        - {final-version} with source label (recommendation vs override)
        - {bump-axis-rationale} — why the synthesizer chose this axis
        - {changelog-entry} verbatim
        - Proposed manifest changes (which files, what version transition)
    2. {decision}: AskUserQuestion — approve or describe adjustments (Q# format)
    3. If {decision} is approve: proceed to step 11
    4. If version change: update {final-version}, re-validate per step 9, re-render bump-axis interpretation
    5. If CHANGELOG edit: re-spawn synthesizer with revision instructions, or edit inline if mechanical
    6. Go to step 10.1

11. Execute:
    1. Insert {changelog-entry} into CHANGELOG.md above the most recent existing release section (below the `[Unreleased]` pointer)
    2. Bump manifest(s) per {methodology} — Edit each manifest's version field to {final-version}
    3. bash: `git add <manifest-path-1> [<manifest-path-N> ...] CHANGELOG.md`
    4. bash: `git commit -m "release {tag}"`
    5. bash: `git tag -a {tag} -m "release {tag}"`
    6. bash: `git push origin main {tag}`

### Report

Return to caller:

- Tag: {tag}
- Manifest(s) bumped: list of paths and version transitions
- CHANGELOG entry: anchor to the new section
- Push: branch + tag pushed to origin
- GitHub release workflow: fires on tag push per methodology — verifies alignment, runs tests, creates release artifact
