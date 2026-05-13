---
name: git
description: Use this skill to commit, push, watch GitHub Actions, run a development checkpoint, or cut a tagged release in the current repository. Trigger on phrases like 'commit', 'commit my changes', 'push my branch', 'check CI', 'is the build green', 'checkpoint', 'cut a release', 'tag a version', or any staging/committing/pushing/releasing context — even when the user doesn't explicitly name a verb. Sandbox-based feature lifecycle (new, pack, open, close, unpack, list) lives under `/ocd:sandbox`, not here.
allowed-tools:
  - Bash(git *)
  - Bash(gh run *)
  - Bash(find *)
---

# git

Manage local git history and tagged releases. Each verb is an atomic workflow loaded on demand.

## Dependencies

1. {dependencies}:
    - [[process-flow-notation]]
2. For each {dependency} in {dependencies}:
    1. {found}: bash: `find ~/.claude <project>/.claude -path "*dependencies/{dependency}.md" -not -path "*/_dependencies/*" -type f 2>/dev/null`
    2. If {found} is empty:
        1. {scope}: `<project>` if `<skill-base>` starts with `<project>`, else `~`
        2. bash: `cp <skill-base>/_dependencies/{dependency}.md {scope}/.claude/dependencies/{dependency}.md`
        3. {path}: the cp target
    3. Else: {path}: first of {found} — prefer user-scope; `rules/dependencies/` over plain `dependencies/`; user-scope skills skip project matches
    4. Read {path} if not in context

## Triggers

| Cognitive moment | Verb |
|---|---|
| "commit", "commit my changes", "stage and commit", "save these edits to git" | `commit` |
| "push", "push my branch", "push to origin" | `push` |
| "check CI", "is the build green", "did CI pass", "watch the build" | `ci` |
| "checkpoint", "commit-push-ci", "save and verify" | `checkpoint` |
| "cut a release", "tag a version", "ship a release", "release v…" | `release` |

## Verbs

| Verb | Workflow | One-line purpose |
|---|---|---|
| `commit` | [`_commit.md`](_commit.md) | Topic-grouped commits from working tree, fully automated |
| `push` | [`_push.md`](_push.md) | Branch-aware push with explicit `--branch` confirmation |
| `ci` | [`_ci.md`](_ci.md) | Report GitHub Actions state for the latest commit on a branch; async watcher when runs are in flight |
| `checkpoint` | [`_checkpoint.md`](_checkpoint.md) | Bundles `commit` + `push` + `ci` into one call |
| `release` | [`_release.md`](_release.md) | Methodology-driven release cut with CHANGELOG synthesis and mandatory review gate |

Internal components reached only via spawn or call:

- [`_ci_watch.md`](_ci_watch.md) — background watcher spawned by `ci` and `checkpoint` when runs are still in progress
- [`_release_bootstrap.md`](_release_bootstrap.md) — first-time methodology dialogue, fires when `.claude/ocd/git/release.md` is absent
- [`_release_synthesize.md`](_release_synthesize.md) — spawned synthesizer that reads commit history and produces a CHANGELOG entry + recommended version

The release methodology template ships at [`assets/release.md`](assets/release.md); the bootstrap dialogue uses it as scaffolding.

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and verb list
2. {verb}: first token of $ARGUMENTS
3. {verb-args}: remainder of $ARGUMENTS after {verb}

> Verb dispatch — each verb lives in its own component file, loaded only when invoked.

4. If {verb} is `commit`: Call: `_commit.md`
5. Else if {verb} is `push`: Call: `_push.md` ({branch}: {verb-args}'s `--branch` value)
6. Else if {verb} is `ci`: Call: `_ci.md` ({branch}: {verb-args}'s `--branch` value, default current)
7. Else if {verb} is `checkpoint`: Call: `_checkpoint.md` ({branch}: {verb-args}'s `--branch` value or current, {no-ci}: `--no-ci` presence)
8. Else if {verb} is `release`: Call: `_release.md` ({version}: first token of {verb-args})
9. Else: Exit to user: unrecognized verb {verb} — expected commit, push, ci, checkpoint, or release

### Report

Each component returns its own report; surface the called component's report verbatim to the user.

## Orientation

Feature-level sandboxing — shelving an in-flight feature onto a dedicated branch, re-activating it, reintegrating it — lives under `/ocd:sandbox`. This skill stays narrow to commit + push + CI orchestration and tagged-release cutting.

Project-level checkpoint skills that need additional steps between commit and push (deployment rectification, template syncs) compose `/ocd:git commit`, `/ocd:git push`, and `/ocd:git ci` piecewise rather than calling the bundled `checkpoint` verb. The bundle is for projects that don't need mid-cycle hooks.
