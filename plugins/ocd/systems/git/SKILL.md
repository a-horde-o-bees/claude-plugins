---
name: git
description: Manage local git history — commit topic-grouped changes, push a branch to origin, watch GitHub Actions, and bundle the full commit-push-CI cycle as a checkpoint. Sandbox-based feature lifecycle (new, pack, open, close, unpack, list) lives under /ocd:sandbox.
argument-hint: "<commit | push --branch <branch-name> | ci [--branch <branch-name>] | checkpoint [--branch <branch-name>] [--no-ci]>"
allowed-tools:
  - Bash(git *)
  - Bash(gh run *)
---

# /git

Manage local git history. Four verbs:

- `commit` records topic-grouped changes
- `push` sends a branch to the remote
- `ci` watches GitHub Actions runs for the latest commit on a branch
- `checkpoint` bundles commit + push + ci into one call

Each verb's sub-flow is in its own component file (`_commit.md`, `_push.md`, `_ci.md`, `_checkpoint.md`). The dispatch below loads only the component for the requested verb, keeping invocation context minimal.

Feature-level sandboxing — shelving an in-flight feature onto a dedicated branch, re-activating it, reintegrating it — lives under `/ocd:sandbox` via the `new`, `pack`, `open`, `close`, `unpack`, and `list` verbs. Use that skill for feature lifecycle; this one stays narrow to commit + push + CI orchestration.

Project-level `/checkpoint` skills that need additional steps between commit and push (deployment rectification, template syncs) call `/ocd:git commit`, `/ocd:git push`, and `/ocd:git ci` piecewise rather than the bundled `checkpoint` verb. The bundle is for projects that don't need mid-cycle hooks.

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-args} = remainder of $ARGUMENTS after {verb}

> Verb dispatch — each verb lives in its own component file, loaded only when invoked.

4. If {verb} is `commit`: Call: `_commit.md`
5. Else if {verb} is `push`: Call: `_push.md` ({branch} = {verb-args}'s `--branch` value)
6. Else if {verb} is `ci`: Call: `_ci.md` ({branch} = {verb-args}'s `--branch` value, default current)
7. Else if {verb} is `checkpoint`: Call: `_checkpoint.md` ({branch} = {verb-args}'s `--branch` value or current, {no-ci} = `--no-ci` presence)
8. Else: Exit to user: unrecognized verb {verb} — expected commit, push, ci, or checkpoint

### Report

Each component returns its own report; surface the called component's report verbatim to the user.
