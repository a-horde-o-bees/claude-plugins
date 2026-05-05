# Release Bootstrap

> Guided dialogue producing the project's local `.claude/ocd/git/release.md`. Fires the first time `/ocd:git release` runs in a project that has no methodology config. Reads the starter template, detects existing release artifacts (manifests, CHANGELOG, tags, auto-bump hooks), pre-populates suggestions, and walks the user through confirmations rather than open-ended fill-in.

The output is a populated `.claude/ocd/git/release.md` that future invocations of `/ocd:git release` read directly — no repeat dialogue. The doc becomes the project's record of release methodology.

### Variables

- {release-md-path} — destination path for the populated methodology doc (typically `.claude/ocd/git/release.md`)

### Rules

- Detection-first: scan project for existing release artifacts before asking questions, then ask only what detection couldn't determine
- Confirmation-style questions: present a detected default and ask "use this, or adjust?" — open-ended only when no default can be detected
- Q# format throughout, per project's question-prefix convention
- Write the populated file at the very end after all questions answered — no partial writes that leave the file in an inconsistent state

### Process

1. Detect existing release artifacts:
    1. {manifest-candidates} = bash: `find . -maxdepth 4 \( -name "plugin.json" -o -name "package.json" -o -name "Cargo.toml" -o -name "pyproject.toml" -o -name "*.gemspec" \) -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null`
    2. {has-changelog} = bash: `[ -f CHANGELOG.md ] && echo yes || echo no`
    3. {existing-tags} = bash: `git tag --sort=-creatordate 2>/dev/null | head -5`
    4. {tag-format} = derive from {existing-tags} — typically `v<x.y.z>` if first tag matches that pattern
    5. {auto-bump-hook} = bash: `[ -f .githooks/pre-commit ] && grep -l -i "bump\|version" .githooks/pre-commit 2>/dev/null || echo none`
    6. {github-release-workflow} = bash: `[ -f .github/workflows/release.yml ] && echo yes || echo no`

2. Read the starter template at `${CLAUDE_PLUGIN_ROOT}/systems/git/templates/release.md` to anchor the output structure

3. Walk the user through each section of the template, using detection results to pre-populate:

    1. **Versioning scheme** — if {existing-tags} match `v\d+\.\d+\.\d+`, propose semver `x.y.z`; otherwise present choices (semver, calver, custom)
    2. **Manifest paths** — propose {manifest-candidates}; ask user to confirm which carry version strings (a project may have multiple manifests, only some versioned)
    3. **Auto-bump behavior** — if {auto-bump-hook} ≠ none, propose "auto-bump runs in pre-commit hook on every commit; release stages only manifest + CHANGELOG to skip"; otherwise propose "no auto-bump"
    4. **Bump axis decision rules** — if semver, propose default rules (y for features, x for breaking, z for patches); ask user to refine for project's specific definition of breaking/feature
    5. **Commit + tag conventions** — if {existing-tags} or {github-release-workflow} suggest a format, propose it; otherwise propose `release v<x.y.z>` commit + annotated tag
    6. **CHANGELOG format** — if {has-changelog} = yes, read CHANGELOG.md header for format hints (Keep a Changelog reference, custom format); propose detected format; otherwise propose Keep a Changelog 1.1.0
    7. **Synthesize source** — propose `git log <last-tag>..HEAD` (or `HEAD` for first release)
    8. **Post-tag-push automation** — if {github-release-workflow} = yes, read its triggers; propose summary of what fires
    9. **Preconditions** — propose standard set (on default branch, clean tree, aligned with remote, tag doesn't exist, version > current); ask if project has additional gates

4. Compose the populated `release.md`:
    1. Use the template structure
    2. Replace each section's placeholder/example content with the user's confirmed answers
    3. Preserve the template's section ordering and headings

5. Write to {release-md-path}:
    1. Verify parent directory exists; create if absent
    2. Write the composed content via the Write tool

6. Confirm with user that the bootstrap completed and `release.md` is ready for use, then return to caller so the main release flow proceeds

### Report

Return to caller:

- Path written: {release-md-path}
- Sections populated: count of confirmed sections
- Detection summary: what was auto-detected vs what required user input
