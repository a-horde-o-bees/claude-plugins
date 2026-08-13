---
name: git
description: Use for any git operation in a repo — e.g. committing or checkpointing work, pushing, watching CI, opening or landing a pull request, cutting a release, or repairing repo health. Bare `/git` lists the verbs; `/git <verb> [args]` runs one.
argument-hint: "[<verb> [args...]]  — commit | push | ci | pr-open | pr-status | pr-merge | pr-cleanup | checkpoint | contribute | release | doctor"
allowed-tools:
  - Skill
  - Read
  - Write
  - Edit
  - Bash(git *)
  - Bash(gh *)
  - Bash(python3 *)
  - Bash(uv run *)
  - Bash(cd *)
  - AskUserQuestion
---

# git

Use for any git operation in a repo — e.g. committing or checkpointing work, pushing, watching CI, opening or landing a pull request, cutting a release, or repairing repo health. Bare `/git` lists the verbs; `/git <verb> [args]` runs one.

The router for this project's git development process. Each verb is a component file under `verbs/` that owns its own gates, submodule recursion, and message authoring; this file binds the verb, forwards the remaining arguments, and returns the verb's report. The verbs call each other — checkpoint sequences commit → push → CI → the PR loop.

## Verbs

| Verb | Component | Routes for |
| --- | --- | --- |
| `commit` | `verbs/commit.md` | stage and commit working-tree changes |
| `push` | `verbs/push.md` | land the current branch on origin |
| `ci` | `verbs/ci.md` | GitHub Actions state for the pushed commit — is the build green |
| `sync` | `verbs/sync.md` | bring another line into the current branch — fetch, merge/rebase/cherry-pick, branch switch, conflict workflow |
| `pr-open` | `verbs/pr-open.md` | open a pull request for the current branch |
| `pr-status` | `verbs/pr-status.md` | what blocks the open PR from merging |
| `pr-merge` | `verbs/pr-merge.md` | land the open PR |
| `pr-cleanup` | `verbs/pr-cleanup.md` | tear down the merged branch and restore base |
| `checkpoint` | `verbs/checkpoint.md` | wrap up this work in one run — commit → push → CI → PR → merge |
| `contribute` | `verbs/contribute.md` | file a PR against an upstream repo we don't own |
| `release` | `verbs/release.md` | cut a tagged release |
| `doctor` | `verbs/doctor.md` | repair repo health — submodules, default branch, CI config, pinned actions |

## Doorway

In a boxed repo, direct `git` and `gh` are denied in project settings and this skill's driver is the only route to them. Box one repo with `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py setup-deny --cwd <repo>`, or every repo at once with `--scope user` (writes `~/.claude/settings.json`; every repo interaction then routes through this skill's verbs — including upstream contributions via `contribute`). Either scope installs two layers: a PreToolUse hook (`scripts/redirect-denied-git.sh`) that denies a raw git/gh call *with a redirect to this skill*, and the bare deny rules as the fail-closed backstop when hooks are off. Judgment steps that inspect history go through `gitflow.py read -- <read-only git>`. The decision, its forces, and the box's limits are recorded in DECISIONS.md — background reading, never needed to run a verb.

## Rules

- **Route, don't re-implement.** This file binds the verb and forwards arguments; every gate, recursion, and report belongs to the verb. Add no behavior here.
- **Each verb is one token** matching its component file — `pr-merge` → `verbs/pr-merge.md`. There is no namespace splitting; the PR-lifecycle verbs are hyphenated names, not a `pr` sub-command.
- **Forward arguments verbatim.** Pass the tokens after the verb straight to the component; the component's own Variables section defines its flags.
- **Unknown or missing verb → the menu, never a guess.** An unrecognized verb shows the menu rather than dispatching to the nearest match.

## Process

1. `{args}`: the invocation arguments. `{verb}`: first token; `{rest}`: the remaining tokens.
2. If `{verb}` is empty or matches no row in ## Verbs: Call: [Menu](#menu) — bind `{verb}` from the user's pick; `{rest}`: empty.
3. `{target}`: the component in `{verb}`'s ## Verbs row.
4. Call: `{target}` `{rest}` — dispatch to the verb, forwarding `{rest}` verbatim.
5. Return the verb's report to the user.

## Menu

Shown for bare `/git` or an unrecognized verb. Lists the verbs, then routes the pick.

1. Present the ## Verbs table (verb + what it routes for), concisely.
2. `{group}`: AskUserQuestion — which area?
    - **Work in progress** — commit, push, ci, sync
    - **Pull request** — open, status, merge, cleanup, or file upstream
    - **Checkpoint** — the all-in-one commit→push→CI→PR→merge (recommended for "wrap up this work")
    - **Maintenance** — release, doctor
3. Narrow to the verb:
    - **Work in progress** → AskUserQuestion: commit / push / ci / sync → bind `{verb}`
    - **Pull request** → AskUserQuestion: pr-open / pr-status / pr-merge / pr-cleanup / contribute (upstream repo we don't own) → bind `{verb}`
    - **Checkpoint** → `{verb}`: `checkpoint`
    - **Maintenance** → AskUserQuestion: release / doctor → bind `{verb}`
4. Return to caller — the chosen `{verb}` and empty `{rest}`.

## Dependencies

The approval gates the verbs run — release, pr-open, pr-merge, doctor — settle with the user per the inlined discipline:

- [/confirm-shared-intent](#confirm-shared-intent)

<!-- flatten-skills START -->

### confirm-shared-intent

Use before an action whose basis isn't on the record — the user hasn't yet picked among live interpretations or approaches, or hasn't yet addressed a problem or risk the agent can see in what they directed. Surfaces the open question or the conflict, gets the user's decision on record, then proceeds. Once the record shows it surfaced and accepted, the gate is spent — no habitual checkpoints, no re-asking what the record already settled.

The standard is the record, not telepathy: the agent cannot know what the user understands, only whether something has been surfaced and answered. The record is the session plus what it stands on — standing rules, approved plans, decisions on file — and anything accepted there holds until the work departs from it. Silence fails in both directions: a silent guess buries the question, silent compliance buries the objection, and either compounds through everything built on it, while putting the matter on the record costs the user a glance. The gate is speaking up, never overriding — no license to refuse, stall, or act against an instruction.

#### No decision on record

The work ahead turns on a choice the record doesn't show the user making. Surface it, get their pick, proceed on it:

- **Ambiguous instruction** — present the live interpretations.
- **Multiple valid approaches** — present them with trade-offs.
- **Missing or unreadable signal** (e.g. an undeclared value, an undeterminable permission) — halt and name the fix; a guessed default is a decision the user never made.
- **Plan deviation** — the work no longer fits the approved plan on record; explain why the plan must change and get acceptance before departing from it.

#### No acknowledgment on record

The directive is clear, but the record doesn't show the user has addressed what the agent can see. Name it and its consequences before complying:

- **A problem in the directive** — a correctness bug, a real risk, or a conflict with the user's stated goal or with sound practice, whether in the directive itself or in an action already running under one.
- **A risk the user is in no position to have addressed** — unfamiliar territory, or a consequence visible only from what the agent has just read.

#### No gate owed

- Surfaced and accepted is spent: once the user clarifies, selects, approves, or acknowledges, they own the call — follow the direction, and never re-gate what the record settles.
- Sound, clearly directed work with nothing unsurfaced proceeds ungated: no habitual mid-phase checkpoints, no manufactured objections — a negligible cost or a matter of taste doesn't qualify.

<!-- flatten-skills STOP -->
