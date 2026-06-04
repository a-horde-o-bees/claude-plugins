# Versioning

`x.y.z` semver in each plugin's `.claude-plugin/plugin.json`. Tags live on main; no release branches.

## Version bump (at integration)

Each plugin's `z` is bumped to `z+1` of `main` when a change integrates — applied by `/git-checkpoint`'s pre-land augmentation (`scripts/bump-apply.py --fetch origin/main`, declared in `.claude/git/checkpoint.md`) so the bump rides in the PR, and verified by the required `bump-check` CI. Idempotent: a manual `y`/`x` bump, or a version already ahead of `main`, is respected.

A commit that stages only `plugin.json` (and `CHANGELOG.md`) changes no plugin code, so nothing is bumped — the escape hatch release cuts use. (The former per-commit `.githooks/pre-commit` bump is retired; the bump now happens once, at integration.)

## Release cut

```
/ocd:git release <version>
```

The skill reads project methodology from `.claude/ocd/git/release.md` (bootstraps if absent), synthesizes a CHANGELOG entry from commit history since the last tag, presents the draft + proposed bump for review, then on approval writes CHANGELOG, bumps the manifest, commits, tags annotated, and pushes main + tag.

`.github/workflows/release.yml` fires on tag push to verify tag-commit version alignment, run tests, and create the GitHub release.

## Patch release

Tag a specific main commit as `v<current-version>`. No `plugin.json` edit required — the auto-bump already assigns each commit a unique patch-level version. The tag is the "deliberate release" signal; the commit's `z` value is just its place in the dev sequence.

## Pre-first-release

`plugin.json` stays at `0.0.z` until the first `v0.1.0` release is cut. After that, the release series tracks whatever `y` is at the most recent tag; `z` auto-increments between tags.
