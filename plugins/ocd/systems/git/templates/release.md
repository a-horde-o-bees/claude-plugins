# Release Methodology

Project-specific methodology for cutting tagged releases. Read by `/ocd:git release` to validate inputs, locate manifest(s) to bump, format the CHANGELOG, and execute commit/tag/push correctly. Captured during the bootstrap dialogue and refined over time as the project's release practice evolves.

This is the *local* version (under `.claude/ocd/git/release.md`) — fill in each section with this project's specifics. The plugin ships a starter template at `plugins/ocd/systems/git/templates/release.md`; the bootstrap dialogue uses it as scaffolding.

## Versioning scheme

Document the scheme this project uses. Examples:

- **Semver `x.y.z`** — major.minor.patch; the most common scheme
- **CalVer `YYYY.MM.PATCH`** — calendar versioning when releases tie to dates
- **Custom** — describe the rules

Note any pre-first-release convention (e.g., "track 0.0.z until first 0.1.0 cut") and how the post-first-release series progresses.

## Manifest paths

List every file that carries a version string the release skill must update. The skill reads this list to know what to bump.

- `path/to/primary-manifest.json`
- (additional manifests if present)

If the project uses a glob (e.g., `plugins/*/.claude-plugin/plugin.json` for multi-plugin marketplaces), document the glob and how each match is treated.

## Auto-bump (out of release scope)

If the project has a per-commit auto-bump separate from release-time bumping, document it here so the release skill knows to coordinate.

- Mechanism (e.g., pre-commit hook in `.githooks/pre-commit`)
- Trigger (which commits cause auto-bump; which are skipped)
- Skip rule the release flow relies on (e.g., "commits staging only manifest skip auto-bump")

If no auto-bump exists, state `N/A`.

## Bump axis decision rules

When does each axis bump? Project-specific definitions of breaking, feature, patch.

For semver:
- **`x` (major)** — describe what counts as breaking
- **`y` (minor)** — describe what counts as a feature
- **`z` (patch)** — describe what counts as a patch (or note "auto-incremented per commit; not part of release flow")

For other schemes, document the equivalent.

## Commit + tag conventions

How the release commit and tag are formatted.

- **Commit message format**: e.g., `release v<x.y.z>`
- **Stage rule**: which files to include in the release commit (typically just the manifest + CHANGELOG)
- **Tag format**: e.g., `v<x.y.z>`, annotated, with message matching the commit
- **Push order**: e.g., `git push origin main <tag>` — single command, both refs

## CHANGELOG format

Which CHANGELOG style the project uses.

- **Format reference**: e.g., Keep a Changelog 1.1.0
- **Section heading style**: e.g., `## [<version>] - YYYY-MM-DD`
- **Categories**: e.g., Added / Changed / Fixed / Removed (Keep a Changelog standard)
- **Special rules**: e.g., "do not log auto-bumped patch values between releases"
- **`[Unreleased]` policy**: e.g., "pointer paragraph at release time; not maintained between releases"

## Synthesize source

What git log range the synthesizer should read for the CHANGELOG entry.

- **Default range**: typically `<last-tag>..HEAD`
- **First release**: `HEAD` (no prior tag)
- **Special handling**: any commit-message conventions the synthesizer should leverage (e.g., topic prefix grouping)

## Post-tag-push automation

If pushing a release tag triggers downstream automation, document it here.

- **Workflow file**: e.g., `.github/workflows/release.yml`
- **Triggers**: tag pattern that fires it (e.g., `v*`)
- **What it does**: verification (tag format, manifest version alignment), test execution, GitHub release creation

If no post-tag automation exists, state `N/A`.

## Preconditions

Project-specific gates that must pass before a release can proceed.

- **Branch**: typically `main`
- **Working tree**: clean (no uncommitted changes)
- **Remote alignment**: local branch matches origin
- **Tag uniqueness**: target tag does not yet exist
- **Version monotonicity**: target version > current manifest version
- **Additional**: any other gates (e.g., specific tests that must pass, specific files that must exist)

## Install command for users

How users install/pin to a tagged release. Helps `/ocd:git release` produce a useful post-release report.

Example: `/plugin marketplace add <org>/<repo>@v<x.y.z>`
