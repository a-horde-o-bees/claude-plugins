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

Use before an action whose basis isn't on the session record — the user hasn't yet picked among live interpretations or approaches, or hasn't yet seen a problem or risk the agent can see in what they directed. Surfaces the open question or the conflict, gets the user's decision on record, then proceeds. Once the record shows it surfaced and accepted, the gate is spent — no habitual checkpoints, no re-asking what the session already settled.

The standard is the record, not telepathy: the agent cannot know what the user understands, only whether something has been brought to their attention and accepted in this session. A silent guess buries the question and silent compliance buries the objection; either compounds through the work that follows, and putting it on the record costs a glance. The gate is speaking up, never overriding — no license to refuse, stall, or act against an instruction.

#### When to gate

Each gate names what goes on the record and what releases it.

**No decision on record** — the work ahead turns on a choice the session doesn't show the user making:

- Ambiguous instruction — present the competing interpretations; proceed on their pick.
- Multiple valid approaches — present them with trade-offs; proceed on their pick.
- Missing or unreadable signal (e.g. an undeclared value, an undeterminable permission) — halt and name the fix rather than falling back to a guessed default.
- Plan deviation — the record holds an approved plan the work no longer matches; explain what changed and why, and get the change accepted.

**No acknowledgment on record** — the directive is clear, but the session doesn't show the user has seen what the agent sees:

- A problem in the directive — a correctness bug, a real risk, or a conflict with the user's stated goal or with sound practice, in the directive or in an action already running under one: name the conflict and its consequences before complying.
- A risk invisible from where the user sits — unfamiliar territory, or a consequence visible only from what the agent has just read: surface it even though the directive itself is clear.

#### Released and spent

- Surfaced and accepted is spent: once the user clarifies, selects, approves, or acknowledges, follow the direction — they own the call, and what the record settles is not re-gated.
- Sound, clearly directed work with nothing unsurfaced needs no gate — never habitual mid-phase checkpoints, never manufactured objections; a negligible cost or a matter of taste doesn't qualify.

<!-- flatten-skills STOP -->
