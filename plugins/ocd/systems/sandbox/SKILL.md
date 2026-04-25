---
name: sandbox
description: Work on an isolated sandbox of the project — durable feature boxes (new, pack, open, update, close, unpack, list) for in-flight development that parallel sessions can drive without clobbering each other, and ephemeral sandboxes (exercise, cleanup) for fresh-install or interactive validation against the current tree. All substrates share one sibling-path convention, one permission rule, and one cleanup sweep.
argument-hint: "<new <feature-id> | pack <description> | open <feature-id> | update <feature-id> | close <feature-id> | unpack <feature-id> [--direct] | list | exercise [description] | cleanup>"
allowed-tools:
  - AskUserQuestion
  - Bash(git *)
  - Bash(gh *)
  - Bash(env -C *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(rm *)
  - Bash(ls *)
  - Bash(claude *)
  - Bash(ocd-run *)
---

# /sandbox

One umbrella for every isolated-workspace operation. Two verb families:

- **Durable** — a feature-level sandbox that persists across sessions. `new` starts empty, `pack` extracts scope from main, `open` / `close` toggle the sibling worktree on and off without touching the branch, `update` rebases the branch onto current `origin/main` from inside the sibling's session, `unpack` reintegrates back into main. `list` is the inventory.
- **Ephemeral** — a disposable sandbox for validation. `exercise` classifies a change into fresh-install vs interactive concerns and runs both, `cleanup` sweeps leftovers.

## Process Model

Every durable sandbox lives in a **sibling worktree** at `<parent>/<project>--<name>/` on a `sandbox/<feature>` branch. The main tree stays on `main` throughout every durable verb — no checkouts swap files, so parallel sessions can each operate on their own feature without clobbering one another. A new Claude Code session started inside the sibling binds its own `CLAUDE_PROJECT_DIR`, giving MCP servers, hooks, and path-aware tools the correct scope.

Ephemeral sandboxes share the same sibling convention with a `tmp-` name prefix (`<project>--tmp-<topic>/`) and a `sandbox/tmp/<topic>` branch namespace. The `tmp-` prefix distinguishes disposable substrates from durable feature boxes in the inventory and keeps a single `<project>--*` permission glob covering everything.

`exercise` classifies a change description into fresh-install concerns (routed to a sibling project substrate invoked as a `claude -p` subprocess) and interactive concerns (routed to a branched sibling worktree driven by the invoking session). Both substrates are internal mechanics of `exercise` — they are not separately exposed as user verbs.

## Substrate Primitives

Two setup/teardown shapes back the verbs:

### Sibling project (sibling + `claude -p`)

Internal substrate of `exercise` for fresh-install concerns.

- **Setup** — create `<parent>/<project>--tmp-<topic>/`, `git init`, apply fixtures, invoke `env -C <sandbox-path> claude -p "<prompt>"` and capture stdout.
- **Teardown** — `rm -rf <sandbox-path>`, either post-run or via `cleanup`.
- **Prerequisite** — `/checkpoint` must have run so the marketplace-installed plugin reflects current commits; PATH resolves plugin binaries against the cache, not against `--plugin-dir`.

### Branched sibling worktree

Used by durable verbs (`new`, `pack`, `open`, `update`, `close`, `unpack`) and by the interactive bucket of `exercise`.

- **Setup** — `ocd-run sandbox worktree-add <name> --branch <branch> [--base-ref <ref>] [--block-push]`.
- **Teardown** — `ocd-run sandbox worktree-remove <name> [--delete-branch] [--unblock-push]`. Push is always unblocked on exit, since a crashed verb must not leave origin in a broken state.
- **Execution model** — the invoking session drives work directly inside the sibling via `env -C <sibling-path>` for bash and explicit paths for file ops. For sustained feature work, the user starts a fresh session inside the sibling so `CLAUDE_PROJECT_DIR` binds correctly end-to-end.

## Route Selection

Durable vs ephemeral follows from what the user is doing, not from a route matrix. Within ephemeral, `exercise` decides whether a concern is fresh-install or interactive via the Interactivity criterion below and runs both if a description spans them.

### Pick a durable verb when

- Starting a new feature — `new <feature-id>`
- Shelving in-flight scope off main to hide it from holistic testing — `pack <description>`
- Activating or parking an existing feature sandbox — `open <feature-id>` / `close <feature-id>`
- Rebasing a feature branch onto current `origin/main` from inside its sibling session — `update <feature-id>`
- Merging a completed feature back to main — `unpack <feature-id>`
- Surveying what's in flight — `list`

### Pick an ephemeral verb when

- Validating a change end-to-end — `exercise <description>` (single-concern descriptions route to a single bucket; multi-concern descriptions run both)
- Sweeping leftover disposables — `cleanup`

### Interactivity criterion (used by `exercise`)

A concern routes to the interactive bucket if any of the following hold — otherwise it routes to the fresh-install bucket:

1. The skill under test invokes `AskUserQuestion` during its workflow
2. The skill writes to Claude Code's sensitive-file tree (`.claude/**`, `~/.claude/**`, `~/.ssh/**`)
3. The skill emits `Exit to user:` expecting a human follow-up action (observations that need judgment, scope confirmations, re-invocations)
4. The skill interprets natural-language input that needs user confirmation before execution
5. The test requires multi-turn back-and-forth where the parent session steers decisions

If none apply, the concern routes to the fresh-install bucket — pure deterministic execution, MCP tool calls, bash, structured output.

## Rules

- Feature ids starting with `tmp/` or `tmp-` or equal to `tmp` are reserved for the ephemeral namespace — reject them in `new` and `pack`
- Main tree stays on `main` throughout every durable verb — no checkouts on the main tree
- `close` refuses to park a sibling with uncommitted or unpushed work — unpushed work signals the branch has not been end-to-end tested; fix before parking
- `update` runs from inside the sibling's session — rebase conflicts need the sibling-scoped `CLAUDE_PROJECT_DIR` for file-resolution context; invoking from the main tree's session and switching mid-flow for conflict resolution breaks the boundary
- `unpack` is mechanically dumb — branch must already be rebased onto current `origin/main` via `/sandbox update` before unpack; conflicts at unpack time mean origin/main advanced between the precondition check and the merge
- `unpack` defaults to PR-based integration — required status checks gate the merge, the PR diff is the reviewable artifact. `--direct` is an escape hatch that merges on main locally and pushes; use only when the PR flow is unavailable
- `cleanup` scans the parent project's `--tmp-*` sibling namespace and `sandbox/tmp/` branches, plus any detached worktree left at `<project>--tmp-*/` by external test-runner invocations — durable feature boxes are never touched
- `exercise` classifies concerns strictly by the Interactivity criterion — if a concern could plausibly fit either bucket, surface the ambiguity to the user before proceeding

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {verb} = first token of $ARGUMENTS
3. {verb-arg} = remainder of $ARGUMENTS after {verb}

> Verb dispatch — durable verbs operate on feature sandboxes; ephemeral verbs handle disposable testing.

4. If {verb} is `new`:
    1. Call: `_new.md` ({verb-arg} = {verb-arg})
5. Else if {verb} is `pack`:
    1. Call: `_pack.md` ({verb-arg} = {verb-arg})
6. Else if {verb} is `open`:
    1. Call: `_open.md` ({verb-arg} = {verb-arg})
7. Else if {verb} is `update`:
    1. Call: `_update.md` ({verb-arg} = {verb-arg})
8. Else if {verb} is `close`:
    1. Call: `_close.md` ({verb-arg} = {verb-arg})
9. Else if {verb} is `unpack`:
    1. Call: `_unpack.md` ({verb-arg} = {verb-arg})
10. Else if {verb} is `list`:
    1. Call: `_list.md`
11. Else if {verb} is `exercise`:
    1. Call: Exercise
12. Else if {verb} is `cleanup`:
    1. Call: Cleanup
13. Else: Exit to user: unrecognized verb {verb} — expected new, pack, open, update, close, unpack, list, exercise, or cleanup

## Exercise

> Classify a change description into fresh-install and interactive concerns per the Interactivity criterion, present a combined plan, execute both substrates, and compile a unified report. Sibling project substrate and branched sibling worktree substrate are internal mechanics of this verb — not separately exposed.

1. {description} = {verb-arg}
2. If {description} is empty: ask user what they want to exercise end-to-end — AskUserQuestion or free-text prompt
3. Verify working tree is clean and main is pushed — bash: `git status --short`
    1. If uncommitted changes exist: Exit to user: `exercise` routes to the fresh-install bucket which requires `/checkpoint` first; run `/checkpoint` then re-invoke
4. Classify the description into concerns. For each concern, evaluate the Interactivity criterion:
    1. {fresh-bucket} = concerns that route to the fresh-install substrate — deterministic, fresh-install, no user prompts, no `.claude/**` writes, no `Exit to user:` follow-ups
    2. {interactive-bucket} = concerns that route to the branched sibling worktree — anything matching any of the five criterion questions
5. Draft the combined plan:
    1. {fresh-plan} = fresh-bucket setup-steps, invocation for `claude -p`, and verification
    2. {interactive-plan} = interactive-bucket changes (if any), agent instructions, and verification
6. Present the combined plan — show {description}, the per-concern classification, {fresh-plan}, {interactive-plan}. Highlight any concern that's ambiguous and ask the user which bucket it belongs in before proceeding.
7. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
8. If cancel: Exit to user: exercise cancelled
9. If adjust: take user's refinements, update plan, Go to step 6. Present the combined plan
10. Execute fresh bucket (if {fresh-bucket} is non-empty):
    1. {parent-project} = basename of current project directory
    2. {topic} = concise kebab-case slug derived from {description}
    3. {sandbox-path} = bash: `ocd-run sandbox sibling-path tmp-{topic}`
    4. bash: `ocd-run sandbox project setup {sandbox-path}`
    5. Apply {fresh-plan}.setup-steps — create or copy fixture files
    6. bash: `env -C {sandbox-path} claude -p "{fresh-plan}.invocation"`
    7. {fresh-output} = captured stdout
11. Execute interactive bucket (if {interactive-bucket} is non-empty):
    1. {topic} = concise kebab-case slug derived from {description}
    2. bash: `ocd-run sandbox worktree setup {topic}` — creates branched sibling at `<parent>/<project>--tmp-{topic}/`, blocks push
    3. {worktree-path} = bash: `ocd-run sandbox sibling-path tmp-{topic}`
    4. Apply {interactive-plan}.changes — Write/Edit with explicit paths under {worktree-path}
    5. Execute {interactive-plan}.instructions — bash calls use `env -C {worktree-path}`; skill invocations via the Skill tool route prompts to the user. After each instruction, cross-check both {worktree-path} and the main project — main must remain unchanged.
    6. {interactive-output} = per-instruction results and reality-check outcomes
12. Compile results:
    - Summary table: Bucket | Concern | Outcome | Evidence
    - Per-bucket digest: {fresh-output} summarized with filesystem and DB evidence preserved; {interactive-output} summarized with filesystem and interaction evidence preserved
    - Cross-cutting observations: anything that spans both buckets
13. Present the compiled report to the user
14. Ask about cleanup — AskUserQuestion with options: `["Remove both now", "Keep for inspection"]`
15. If remove:
    1. If fresh bucket ran: bash: `ocd-run sandbox project teardown {sandbox-path}`
    2. If interactive bucket ran: bash: `ocd-run sandbox worktree teardown {topic}`
16. Return to caller

17. Error Handling:
    1. If interactive bucket partial state exists: bash: `ocd-run sandbox worktree teardown {topic}` — always unblocks push even on crash
    2. Exit to user: exercise failed — check output for which bucket failed and the cause

## Cleanup

> Find and remove ephemeral sandbox artifacts — sibling projects matching `<project>--tmp-*` and worktrees on `sandbox/tmp/*` branches, plus any detached worktree left at `<project>--tmp-*/` by external test-runner invocations. Durable feature boxes are out of scope — remove those via `unpack`. Always confirms before deletion.

1. bash: `ocd-run sandbox cleanup inventory` — outputs JSON with `siblings` and `worktrees` arrays
2. Parse JSON output
3. If both arrays are empty: Exit to user: nothing to clean up
4. Present inventory to user — sibling paths with sizes, worktree paths with branches
5. Ask user — AskUserQuestion with options: `["Remove all", "Choose which to remove", "Cancel"]`
6. If `Cancel`: Exit to user: cleanup cancelled
7. If `Choose which to remove`:
    1. For each {sibling} in siblings: AskUserQuestion with options: `["Remove", "Keep"]`
    2. For each {worktree} in worktrees: AskUserQuestion with options: `["Remove", "Keep"]`
8. {sibling-args} = `--sibling <path>` for each sibling marked Remove (or all siblings on `Remove all`)
9. {worktree-args} = `--worktree <path>` for each worktree marked Remove (or all worktrees on `Remove all`)
10. If both argument lists are empty: Exit to user: nothing selected for removal
11. bash: `ocd-run sandbox cleanup remove {sibling-args} {worktree-args}`
12. Report what was removed
13. Return to caller
