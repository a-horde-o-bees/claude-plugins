# Versioning

`x.y.z` semver in each plugin's `.claude-plugin/plugin.json`. Tags live on main; no release branches.

## Pre-commit auto-bump

The pre-commit hook auto-bumps `z` on every commit that stages changes to the plugin tree other than `plugin.json` itself (see `.githooks/pre-commit`). This keeps Claude Code's reload detection firing as dev-channel users track main.

Commits that stage only `plugin.json` (and `CHANGELOG.md`) skip the auto-bump — that's the escape hatch release cuts use.

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
