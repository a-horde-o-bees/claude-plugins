---
name: git
description: Router for the whole git development process — dispatches to one verb and runs its integrated flow. Use for any git operation in a repo: committing working-tree changes ("commit", "save these edits"), pushing to a remote ("push"), checking GitHub Actions CI ("is the build green", "did CI pass"), the pull-request lifecycle ("open a PR", "is the PR ready", "merge the PR", "clean up the branch"), the all-in-one development checkpoint ("checkpoint", "ship it" — commit→push→CI→PR→merge), cutting a tagged release ("cut a release", "tag a version"), or diagnosing and repairing repo health ("fix submodules", "audit my CI", "pin my actions"). Bare `/git` lists the verbs; `/git <verb> [args]` runs one directly; natural-language requests route to the matching verb.
argument-hint: "[<verb> [args...]]  — commit | push | ci | pr-open | pr-status | pr-merge | pr-cleanup | checkpoint | release | doctor"
allowed-tools:
  - Skill
  - Read
  - Write
  - Edit
  - Bash(git *)
  - Bash(gh *)
  - Bash(python3 *)
  - Bash(uv run *)
  - Bash(sh *)
  - Bash(test *)
  - Bash(cd *)
  - AskUserQuestion
---

# /git

The router for this project's git development process. One trigger fronts ten verbs; each verb is a component file under `verbs/` that owns its own gates, submodule recursion, and message authoring. This file only routes — it parses the verb, forwards the remaining arguments, and returns the verb's report. The value is the integrated process: the verbs call each other (checkpoint sequences commit → push → CI → the PR loop; commit and push pre-check via doctor), so they live together rather than as isolated skills.

## Verbs

| Verb | Component | Routes for |
| --- | --- | --- |
| `commit` | `verbs/commit.md` | commit, stage and commit, save these edits |
| `push` | `verbs/push.md` | push, push my branch, push to origin |
| `ci` | `verbs/ci.md` | check CI, is the build green, did CI pass, watch the build |
| `pr-open` | `verbs/pr-open.md` | open a PR, create a pull request, submit for review |
| `pr-status` | `verbs/pr-status.md` | is the PR ready to merge, PR status, what's blocking the PR |
| `pr-merge` | `verbs/pr-merge.md` | merge the PR, land it, ship the PR |
| `pr-cleanup` | `verbs/pr-cleanup.md` | clean up the branch, delete the merged branch, restore main |
| `checkpoint` | `verbs/checkpoint.md` | checkpoint, ship it, wrap up this work (commit→push→CI→PR→merge) |
| `release` | `verbs/release.md` | cut a release, tag a version, ship vX |
| `doctor` | `verbs/doctor.md` | fix submodules, audit my CI, pin my actions, pre-commit health check |

## Rules

- **Route, don't re-implement.** This file binds the verb and forwards arguments; every gate, recursion, and report belongs to the verb. Add no behavior here.
- **Each verb is one token** matching its component file — `pr-merge` → `verbs/pr-merge.md`. There is no namespace splitting; the PR-lifecycle verbs are hyphenated names, not a `pr` sub-command.
- **Forward arguments verbatim.** Pass the tokens after the verb straight to the component; the component's own Variables section defines its flags.
- **Unknown or missing verb → the menu, never a guess.** An unrecognized verb shows the menu rather than dispatching to the nearest match.

## Process

1. {args}: the invocation arguments. {verb}: first token; {rest}: the remaining tokens.
2. If {verb} is empty: Call: Menu — bind {verb} (and {rest}, empty) from the user's pick.
3. If {verb} matches a row in ## Verbs: {target}: that row's component.
4. Else (unrecognized {verb}): Call: Menu — bind {verb} from the pick; {rest}: empty.
5. Call: {target} {rest} — dispatch to the verb, forwarding {rest} verbatim.
6. Return the verb's report to the user.

## Menu

Shown for bare `/git` or an unrecognized verb. Lists the verbs, then routes the pick.

1. Present the ## Verbs table (verb + what it routes for). Apply /concise-prose.
2. {group}: AskUserQuestion — which area?
    - **Work in progress** — commit, push, ci
    - **Pull request** — open, status, merge, cleanup
    - **Checkpoint** — the all-in-one commit→push→CI→PR→merge (recommended for "wrap up this work")
    - **Maintenance** — release, doctor
3. Narrow to the verb:
    - **Work in progress** → AskUserQuestion: commit / push / ci → bind {verb}
    - **Pull request** → AskUserQuestion: pr-open / pr-status / pr-merge / pr-cleanup → bind {verb}
    - **Checkpoint** → {verb}: `checkpoint`
    - **Maintenance** → AskUserQuestion: release / doctor → bind {verb}
4. Return to caller — the chosen {verb} and empty {rest}.
