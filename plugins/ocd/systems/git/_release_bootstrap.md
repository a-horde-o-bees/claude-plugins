# Release Bootstrap

> Guided dialogue producing the project's local `.claude/ocd/git/release.md`. Fires the first time `/ocd:git release` runs in a project that has no methodology config. Reads the starter template, detects existing release artifacts (manifests, CHANGELOG, tags, auto-bump hooks), pre-populates suggestions across every section, and presents a single full proposal for batched feedback rather than walking the user section-by-section.

The output is a populated `.claude/ocd/git/release.md` that future invocations of `/ocd:git release` read directly — no repeat dialogue. The doc becomes the project's record of release methodology.

### Variables

- {release-md-path} — destination path for the populated methodology doc (typically `.claude/ocd/git/release.md`)

### Rules

- Detection-first: scan project for existing release artifacts before composing the proposal; pre-populate every section that detection can determine
- Single batched proposal: render the full draft `release.md` content for the user to review in one go, rather than walking section-by-section. The user accepts as-is or calls out section-level adjustments
- Q# format on the single approval question, per project's question-prefix convention
- Write the populated file only after the user approves — no partial writes that leave the file in an inconsistent state

### Process

1. Detect existing release artifacts:
    1. {manifest-candidates} = bash: `find . -maxdepth 4 \( -name "plugin.json" -o -name "package.json" -o -name "Cargo.toml" -o -name "pyproject.toml" -o -name "*.gemspec" \) -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null`
    2. {has-changelog} = bash: `[ -f CHANGELOG.md ] && echo yes || echo no`
    3. {existing-tags} = bash: `git tag --sort=-creatordate 2>/dev/null | head -5`
    4. {tag-format} = derive from {existing-tags} — typically `v<x.y.z>` if first tag matches that pattern
    5. {auto-bump-hook} = bash: `[ -f .githooks/pre-commit ] && grep -l -i "bump\|version" .githooks/pre-commit 2>/dev/null || echo none`
    6. {github-release-workflow} = bash: `[ -f .github/workflows/release.yml ] && echo yes || echo no`

2. Read the starter template at `${CLAUDE_PLUGIN_ROOT}/systems/git/templates/release.md` to anchor the output structure

3. Compose the full draft `release.md` content using the template structure and detection-driven defaults for every section:

    1. **Versioning scheme** — if {existing-tags} match `v\d+\.\d+\.\d+`, fill in semver `x.y.z`; otherwise list semver/calver/custom as choices
    2. **Manifest paths** — fill in {manifest-candidates}; flag in the proposal which are version-bearing best guesses for user confirmation
    3. **Auto-bump behavior** — if {auto-bump-hook} ≠ none, fill in "auto-bump runs in pre-commit hook on every commit; release stages only manifest + CHANGELOG to skip"; otherwise fill in "no auto-bump"
    4. **Bump axis decision rules** — if semver, fill in the template's recommended defaults (breaking → x, new capability → y, fix or auto-bumped → z); for other schemes fill in equivalent rules from the template
    5. **Commit + tag conventions** — if {existing-tags} or {github-release-workflow} suggest a format, fill it in; otherwise fill in `release v<x.y.z>` commit + annotated tag
    6. **CHANGELOG format** — if {has-changelog} = yes, read CHANGELOG.md header and fill in detected format hints; otherwise fill in Keep a Changelog 1.1.0
    7. **Synthesize source** — fill in `git log <last-tag>..HEAD` (or `HEAD` for first release)
    8. **Post-tag-push automation** — if {github-release-workflow} = yes, read its triggers and fill in a summary of what fires
    9. **Preconditions** — fill in the standard set (on default branch, clean tree, aligned with remote, tag doesn't exist, version > current)

4. Present the full draft to the user for batched review:
    1. Render the composed `release.md` content verbatim
    2. Include a detection summary (what was auto-detected vs what is a guess)
    3. Ask user to approve as-is or call out section-level adjustments — Q# format with options

5. If the user requests adjustments:
    1. Apply per their directives (revise sections, swap defaults, add gates)
    2. Re-render the revised draft
    3. Re-present (return to step 4)
    4. Loop until approved

6. On approval, write to {release-md-path}:
    1. Verify parent directory exists; create if absent
    2. Write the composed content via the Write tool

7. Confirm with user that the bootstrap completed and `release.md` is ready for use, then return to caller so the main release flow proceeds

### Report

Return to caller:

- Path written: {release-md-path}
- Sections populated: count of confirmed sections
- Detection summary: what was auto-detected vs what required user input
