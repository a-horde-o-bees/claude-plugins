# Git rm staging persistence across commits

`git rm <path>` stages a deletion that persists in the index across subsequent `git commit` calls until the path is included in a commit's `git add` set or explicitly unstaged. When committing in topical groups via `/ocd:git commit`, an earlier `git rm` can land in a later, semantically unrelated commit if the deletion is not explicitly staged-with or excluded from each commit's file list.

## Reproduction

1. `git rm <fileA>` (e.g. removing a deprecated component)
2. Continue working on unrelated topics
3. Run `/ocd:git commit` (or commit any unrelated group with `git add <other-files>`)
4. Observed: the staged deletion of `fileA` lands in the commit that was supposed to cover only the unrelated topic

## Concrete instance

This session: `git rm .claude/skills/checkpoint/_ci_watch.md` was run early to support the `/ocd:git checkpoint` extraction (intended to land with the git-skill commit). Subsequent commit grouping placed the transcripts-decomposition commit first; `git rm`'s staged deletion was carried into the transcripts commit because nothing explicitly excluded it. Discovered after the fact via `git show --stat`. Topical misgrouping; not amended.

## Suspected root cause

`/ocd:git commit` stages files by name per the design rule ("Stage specific files by name — never use `git add -A` or `git add .`"). But the index already contains the deletion staged by an earlier `git rm`, and `git commit` (without `-o`/`--only`) commits the entire staged index, not just the explicitly-named adds. The grouping intent is honored for adds but not for prior staged-deletes.

## Possible fixes

- **Detect prior staged-deletes before commit grouping.** `/ocd:git commit` could `git diff --cached --name-status --diff-filter=D` at the start, surface any pre-staged deletions to the user, and ask whether each belongs to the current group or should be reset and committed later
- **Use `git commit -o <files>` to commit only the explicitly-named files.** This is `--only` mode — temporarily stashes other staged changes, commits the named ones, restores the stashed staged state. Atomic per-group; staging persistence becomes irrelevant
- **Convention: never `git rm` early; defer until the commit that owns it.** Workflow discipline rather than tooling change. Lower risk but easier to forget

The `-o` mode fix is the strongest because it makes the behavior structurally correct rather than relying on agent vigilance. Worth investigating if `git commit -o` has surprising failure modes (it should not — the mechanism is well-tested).
