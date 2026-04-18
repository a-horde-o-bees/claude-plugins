---
name: sandbox
description: Exercise changes or run the test suite in an isolated environment — a sibling project for fresh-install scenarios, a git worktree for interactive validation, an exercise that routes change concerns to both substrates, or a test run against a clean ref. Presents a plan, confirms, executes, reports, and offers cleanup.
argument-hint: "<project [description] | worktree [description] | exercise [description] | test [--ref <ref>] | cleanup>"
allowed-tools:
  - AskUserQuestion
  - Bash(git *)
  - Bash(env -C *)
  - Bash(mkdir *)
  - Bash(cp *)
  - Bash(rm *)
  - Bash(ls *)
  - Bash(claude *)
---

# /sandbox

Operate in an isolated environment so changes, interactive tests, or the project test suite can run without contaminating main. Five verbs:

- `project` — sibling project for fresh-install scenarios (`claude -p` subprocess)
- `worktree` — disposable git worktree for interactive/in-session validation (executor-driven)
- `exercise` — orchestrator that classifies a change description into `project` and `worktree` concerns and runs both
- `test` — run the project test suite against a clean ref (default main HEAD) in a worktree
- `cleanup` — find and remove leftover sandboxes and worktrees

## Process Model

Testing in isolation uses one of two substrates depending on what's being validated:

- **Sibling project** (`project` verb, and the project bucket of `exercise`) — a brand new directory created at `<parent-project>-test-<topic>/`, separate filesystem, fresh git repo, fresh plugin cache. Tests "from nothing" scenarios: fresh install, bootstrapping, first-time-user behavior. Executed as a `claude -p` subprocess.
- **Git worktree** (`worktree` verb, the worktree bucket of `exercise`, and the `test` verb) — a disposable checkout at `.claude/worktrees/<topic>/`, shares plugin cache with current session, isolated from the main working tree. Tests changes or runs the suite against existing project state without risking main. **Executor-driven**: the invoking session drives the steps directly (using `env -C` for bash calls and explicit worktree paths for file ops) so `AskUserQuestion`, the Agent tool, Skill invocation, and the parent's permission context all remain available. The worktree itself provides filesystem isolation and push blocking, not execution isolation.

`exercise` and `project`/`worktree` take a natural-language description; the skill executor drafts a concrete plan, the user confirms, then the plan runs. `test` takes no description — it always answers "do the tests pass on this ref?" After execution, results are presented; cleanup is offered immediately or deferred until the next `cleanup` invocation.

## Substrate Primitives

Three setup/teardown shapes recur across the verbs. Each verb composes one or more. Kept here as a single reference so the shapes read consistently wherever they appear in the workflow.

### Project substrate (sibling + `claude -p`)

Consumed by `project` and the project bucket of `exercise`.

- **Setup** — create `{parent-dir}/{parent-project}-test-{topic}/`, `git init`, apply setup-step file copies/writes, invoke `env -C {sandbox-path} claude -p "<prompt>"` and capture stdout.
- **Teardown** — `rm -rf {sandbox-path}`, either offered post-run or surfaced by `cleanup`.
- **Prerequisite** — `/checkpoint` must have run so the marketplace-installed plugin reflects current commits; PATH resolves plugin binaries against the cache, not against `--plugin-dir`.

### Branched worktree (disposable branch on parent `.git`)

Consumed by `worktree` and the worktree bucket of `exercise`.

- **Setup** — `git config remote.origin.pushurl "file:///dev/null"` to block push, then `git worktree add -b sandbox/{topic} .claude/worktrees/{topic}`.
- **Teardown** — `git worktree remove --force`, `git branch -D sandbox/{topic}`, `git config --unset remote.origin.pushurl`. Error handling always unblocks push, since a crashed verb leaves the origin broken.
- **Execution model** — the invoking session drives steps directly. Bash uses `env -C`; file ops use explicit paths under the worktree; Skill invocations and `AskUserQuestion` route through the parent session to the user.

### Detached worktree (read-only snapshot at a ref)

Consumed by `test`.

- **Setup** — `git worktree add --detach .claude/worktrees/test-{short-sha} {ref-sha}`. No branch, no push blocking.
- **Teardown** — `git worktree remove --force`. No branch to delete.
- **Execution model** — same executor-driven model as branched worktree; `env -C {worktree-path} {project-venv} -m pytest ...` for suite runs.

## Route Selection

The verbs pick different execution mechanisms. The `exercise` verb classifies concerns per the Interactivity criterion and routes each to `project` or `worktree`; the direct verbs route one bucket at a time.

| Capability | `project` (external) | `worktree` (internal) |
|---|---|---|
| Mechanism | Fresh `claude -p` subprocess | Executor-driven; invoking session operates inside `.claude/worktrees/<topic>/` via `env -C` |
| Plugin load | Fresh session — SessionStart fires, venv deps install, MCP servers initialize | Parent session's plugin state |
| Cache / PATH | Assembled at subprocess start (requires `/checkpoint` first) | Parent session's existing cache and PATH |
| Permission prompts | Auto-decline — no back-channel to parent | Route through parent session to the user (executor is the parent session) |
| Sensitive-file gate (`.claude/**`) | Blocks even under `--dangerously-skip-permissions` | Applies under parent's permission context; prompts route to user |
| `AskUserQuestion` | Exits immediately | Works normally — parent session tool |
| `Exit to user:` follow-ups | No user available — skill ends without the follow-up happening | User acts on the exit message interactively |
| MCP tool context | Sandbox's own MCP servers bind to the sandbox project dir | Parent's MCP servers remain bound to parent `CLAUDE_PROJECT_DIR` — MCP-tool calls see main project's state, not the worktree's |
| Nested `Spawn:` inside skills | Skill's own subagents inherit the fresh subprocess context | Nested subagents hit tool-surface limits (no `AskUserQuestion`, no further agent-spawn); executor should drive those skills' workflows manually rather than invoking them as black boxes |

### Interactivity criterion

A concern routes to `worktree` if any of the following are true — otherwise it routes to `project`:

1. The skill under test invokes `AskUserQuestion` during its workflow
2. The skill writes to Claude Code's sensitive-file tree (`.claude/**`, `~/.claude/**`, `~/.ssh/**`)
3. The skill emits `Exit to user:` expecting a human follow-up action (observations that need judgment, scope confirmations, re-invocations)
4. The skill interprets natural-language input that needs user confirmation before execution
5. The test requires multi-turn back-and-forth where the parent session steers decisions

If none apply, the concern routes to `project` — pure deterministic execution, MCP tool calls, bash, structured output, fresh-install semantics.

### Pick `project` directly when testing

- Fresh-install behavior — `install_deps.sh`, plugin initialization, navigator DB creation, paths.csv aggregation
- Dependency self-installation — `requirements.txt` changes pulled into the venv on SessionStart
- Cross-session behavior — anything that depends on a clean session start rather than an in-flight session
- CLI output and exit codes — `<plugin>-run`, shell invocations, deterministic skill outputs
- PATH resolution — plugin wrapper scripts against the marketplace cache layout
- Non-interactive skills: `<plugin>:navigator` (scan + MCP tools), `<plugin>:git commit` on clean files, `<plugin>:pdf`/`<plugin>:md-to-pdf`

### Pick `worktree` directly when testing

- Skills that use `AskUserQuestion` — `<plugin>:setup guided`, permissions subflow
- Skills that write to `.claude/**` — `<plugin>:log`, defect auto-application in audit skills
- Skills that `Exit to user:` expecting follow-up — observations-pending flows
- Multi-turn interactions where the parent session approves / steers
- Changes to repository state that shouldn't affect the main working tree — destructive refactors, commit-graph experiments

Worktree residuals to keep in mind:

- **MCP-backed state testing is limited.** MCP servers bound at parent-session start continue to see the main project's `CLAUDE_PROJECT_DIR`. Tools like `paths_upsert` / `paths_get` query main's navigator DB, not the worktree's. Use `project` for tests where MCP tool state must reflect the sandbox rather than main.
- **Nested `Spawn:` inside skills still hits the subagent tool-surface limit.** Skills whose workflows invoke their own subagents cannot be run as black boxes in the worktree — the nested subagent lacks `AskUserQuestion` and further agent-spawn capability. The executor drives those skills' workflows manually, step-by-step, using the parent session's tools.

### Pick `exercise` when

- Validating a change end-to-end and either don't know or don't care which substrate each concern fits
- A single change touches both fresh-install and interactive surface area — `exercise` classifies concerns automatically and runs both buckets in sequence

Neither direct substrate is a replacement for the other. Fresh-install tests cannot pause for user input; interactive tests cannot exercise SessionStart cold-start behavior. `exercise` is the union — not a shortcut to skip classification, but a wrapper that keeps both halves visible.

### Pick `test` when

- Need to know whether the existing test suite passes on a baseline — default main HEAD, or an explicit `--ref`
- No change is being exercised — the question is "do the tests pass?", not "is this change safe?"
- Before invoking `unbox` on a dev branch (verify the branch passes tests before merging into main)
- After pulling sibling-session commits to validate nothing regressed
- Periodic regression checks as a quality gate

## Rules

- Never create, modify, or delete outside the sandbox substrate — the invoking project is never touched
- Never proceed with creation until user has confirmed the plan — presenting the plan is not authorization to execute. `test` has no plan to confirm (deterministic verb) and runs immediately
- Cleanup scans only the parent project's namespace — siblings matching `<parent>-test-*` and all non-main worktrees reported by `git worktree list`; never touches unrelated directories
- `project` verb and the project bucket of `exercise` require `/checkpoint` first — the spawned `claude -p` subprocess inherits PATH from the harness, and PATH resolves `<plugin>-run` binaries against the marketplace-cached install, not `--plugin-dir`. Reliable plugin-behavior tests need the marketplace version to reflect current commits; `--plugin-dir` alone is insufficient because PATH lookup shadows it with older cached versions
- Empty description is a valid invocation for `project`, `worktree`, and `exercise` — skill asks what to test instead of guessing. `test` and `cleanup` take no description
- `exercise` classifies concerns strictly by the Interactivity criterion — if a concern could plausibly fit either bucket, surface the ambiguity to the user before proceeding rather than routing silently

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint

> Verb dispatch — project and worktree create substrates directly, exercise classifies a change into both, test runs the suite, cleanup removes what remains.

2. If {verb} is `project`:
    1. Call: Project
3. Else if {verb} is `worktree`:
    1. Call: Worktree
4. Else if {verb} is `exercise`:
    1. Call: Exercise
5. Else if {verb} is `test`:
    1. Call: Test
6. Else if {verb} is `cleanup`:
    1. Call: Cleanup
7. Else: Exit to user: unrecognized verb {verb} — expected project, worktree, exercise, test, or cleanup

## Project

> Create a sibling project, propose a setup plan for what the user is testing, confirm, execute, report, offer cleanup. Plugin-behavior tests require the marketplace install to reflect current commits — prompt for `/checkpoint` first if the user's last push is ahead of the latest uncommitted work.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to test — AskUserQuestion or free-text prompt
3. If the test exercises plugin behavior (install, skills, MCP tools, hooks):
    1. Verify the working tree is clean and main is pushed — bash: `git status --short`
    2. If uncommitted changes exist: Exit to user: plugin-behavior sandbox tests require `/checkpoint` first so the marketplace-installed plugin reflects current code; run `/checkpoint` then re-invoke
4. {parent-project} = basename of current project directory
5. {parent-dir} = parent directory of current project
6. {topic} = concise kebab-case slug derived from {description}
7. {sandbox-path} = `{parent-dir}/{parent-project}-test-{topic}`
8. Draft test plan:
    1. {setup-steps} = files to create, fixtures to copy from current project, any pre-existing state the test needs
    2. {invocation} = exact `claude -p` prompt to run in {sandbox-path}
    3. {verification} = what output or filesystem state confirms the test passed
9. Present plan to user — show {sandbox-path}, {setup-steps}, {invocation}, {verification}
10. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
11. If cancel: Exit to user: sandbox cancelled
12. If adjust: take user's refinements, update plan, Go to step 9. Present plan to user
13. Execute plan:
    1. bash: `mkdir -p {sandbox-path}`
    2. bash: `git -C {sandbox-path} init`
    3. Apply {setup-steps} — create or copy fixture files
    4. bash: `env -C {sandbox-path} claude -p "{invocation}"`
    5. {output} = captured stdout
14. Present results:
    - {output}
    - Filesystem state if relevant (list key files created/modified)
    - Verification outcome against {verification} — pass, fail, or inconclusive
15. Ask user about cleanup — AskUserQuestion with options: `["Remove sandbox now", "Keep for inspection"]`
16. If remove: bash: `rm -rf {sandbox-path}`
17. Return to caller

## Worktree

> Create a disposable git worktree on a new branch; the invoking session drives tests directly inside it. `AskUserQuestion`, the Agent tool, Skill invocation, and parent permission context all remain available because the executor is the parent session, not a subagent. The worktree provides filesystem isolation (main tree untouched) and push blocking (`/dev/null` pushurl) for the duration.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to test
3. {topic} = concise kebab-case slug derived from {description}
4. {worktree-path} = `.claude/worktrees/{topic}`
5. {branch} = `sandbox/{topic}`
6. Draft test plan:
    1. {changes} = file changes to apply inside the worktree, or none
    2. {instructions} = test steps the executor will run — skill invocations, per-step reality checks, verifications against both the worktree and main
    3. {verification} = what output or filesystem state confirms the test passed
7. Present plan to user — show {worktree-path}, {branch}, {changes}, {instructions}, {verification}
8. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
9. If cancel: Exit to user: sandbox cancelled
10. If adjust: take refinements, update plan, Go to step 7. Present plan to user
11. Block push — bash: `git config remote.origin.pushurl "file:///dev/null"`
12. Create worktree — bash: `git worktree add -b {branch} {worktree-path}`
13. Apply {changes} — Write/Edit with explicit paths under {worktree-path}
14. Execute {instructions} — bash calls use `env -C {worktree-path}`; skill invocations via the Skill tool route prompts to the user; for skills whose own workflow invokes `Spawn:` subagents, drive the steps manually. After each instruction, cross-check both {worktree-path} and the main project — main must remain unchanged.
15. {output} = per-instruction results and reality-check outcomes
16. Unblock push — bash: `git config --unset remote.origin.pushurl`
17. Present results — {output}, verification outcome against {verification}
18. Ask user about cleanup — AskUserQuestion with options: `["Remove worktree now", "Keep for inspection"]`
19. If remove:
    1. bash: `git worktree remove {worktree-path} --force`
    2. bash: `git branch -D {branch}`
20. Return to caller

21. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. bash: `git worktree remove {worktree-path} --force`
    3. bash: `git branch -D {branch}`
    4. Exit to user: worktree sandbox failed — check output for details

## Exercise

> Classify a comprehensive change description into project-bucket and worktree-bucket concerns per the Interactivity criterion, present a combined plan, execute both substrates, and compile a unified report. Use when validating an end-to-end change that touches both fresh-install and interactive surface area.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to exercise end-to-end — AskUserQuestion or free-text prompt
3. Verify working tree is clean and main is pushed — bash: `git status --short`
    1. If uncommitted changes exist: Exit to user: `exercise` routes to the `project` bucket which requires `/checkpoint` first; run `/checkpoint` then re-invoke
4. Classify the description into concerns. For each concern, evaluate the Interactivity criterion (see Route Selection):
    1. {project-bucket} = concerns that route to `project` — deterministic, fresh-install, no user prompts, no `.claude/**` writes, no `Exit to user:` follow-ups
    2. {worktree-bucket} = concerns that route to `worktree` — anything matching any of the five criterion questions
5. Draft the combined plan:
    1. {project-plan} = project-bucket setup-steps, invocation for `claude -p`, and verification — following the Project workflow shape
    2. {worktree-plan} = worktree-bucket changes (if any), agent instructions, and verification — following the Worktree workflow shape
6. Present the combined plan — show {description}, the per-concern classification, {project-plan}, {worktree-plan}. Highlight any concern that's ambiguous and ask the user which bucket it belongs in before proceeding.
7. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
8. If cancel: Exit to user: exercise cancelled
9. If adjust: take user's refinements, update plan, Go to step 6. Present the combined plan
10. Execute project bucket (if {project-bucket} is non-empty):
    1. {parent-project} = basename of current project directory
    2. {parent-dir} = parent directory of current project
    3. {topic} = concise kebab-case slug derived from {description}
    4. {sandbox-path} = `{parent-dir}/{parent-project}-test-{topic}`
    5. bash: `mkdir -p {sandbox-path}`
    6. bash: `git -C {sandbox-path} init`
    7. Apply {project-plan}.setup-steps — create or copy fixture files
    8. bash: `env -C {sandbox-path} claude -p "{project-plan}.invocation"`
    9. {project-output} = captured stdout
11. Execute worktree bucket (if {worktree-bucket} is non-empty):
    1. {worktree-path} = `.claude/worktrees/{topic}`
    2. {worktree-branch} = `sandbox/{topic}`
    3. Block push — bash: `git config remote.origin.pushurl "file:///dev/null"`
    4. Create worktree — bash: `git worktree add -b {worktree-branch} {worktree-path}`
    5. Apply {worktree-plan}.changes — Write/Edit with explicit paths under {worktree-path}
    6. Execute {worktree-plan}.instructions — bash calls use `env -C {worktree-path}`; skill invocations via the Skill tool route prompts to the user; for skills whose own workflow invokes `Spawn:` subagents, drive the steps manually. After each instruction, cross-check both {worktree-path} and the main project — main must remain unchanged.
    7. {worktree-output} = per-instruction results and reality-check outcomes
    8. Unblock push — bash: `git config --unset remote.origin.pushurl`
12. Compile results:
    - Summary table: Bucket | Concern | Outcome | Evidence
    - Per-bucket digest: {project-output} summarized with filesystem and DB evidence preserved; {worktree-output} summarized with filesystem and interaction evidence preserved
    - Cross-cutting observations: anything that spans both buckets (naming mismatches, doc drift, unexpected behavior not tied to a single concern)
13. Present the compiled report to the user
14. Ask about cleanup — AskUserQuestion with options: `["Remove both now", "Keep for inspection"]`
15. If remove:
    1. If project bucket ran: bash: `rm -rf {sandbox-path}`
    2. If worktree bucket ran:
        1. bash: `git worktree remove {worktree-path} --force`
        2. bash: `git branch -D {worktree-branch}`
16. Return to caller

17. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. If worktree bucket partial state exists:
        1. bash: `git worktree remove {worktree-path} --force`
        2. bash: `git branch -D {worktree-branch}`
    3. Exit to user: exercise failed — check output for which bucket failed and the cause

## Test

> Run the project test suite against a clean ref in a worktree. Deterministic verb — no plan, no classifier, no change description. Answers "do the existing tests pass on this baseline?" Default ref is `main` HEAD; `--ref <commit-or-branch>` selects another. Cleans up worktree on completion regardless of pass/fail.

1. Parse arguments after the verb:
    1. If `--ref <value>` present: {ref} = {value}
    2. Else: {ref} = `main`
2. Resolve ref to commit SHA — bash: `git rev-parse {ref}`
    1. If fail: Exit to user: ref {ref} could not be resolved
    2. {ref-sha} = the resolved SHA
    3. {short-sha} = first 7 chars of {ref-sha}
3. {worktree-path} = `.claude/worktrees/test-{short-sha}`
4. {branch-detached} = true — worktree is created detached (no branch)
5. Verify worktree path available:
    1. If {worktree-path} already exists: Exit to user: {worktree-path} already in use — run `/ocd:sandbox cleanup` first or pick a different ref
6. Resolve test venv:
    1. {project-venv} = parent project's `.venv/bin/python3`, absolute path
    2. If missing: Exit to user: project `.venv/bin/python3` not found — bootstrap the project venv before running `test`
7. Create worktree — bash: `git worktree add --detach {worktree-path} {ref-sha}`
8. Discover test surfaces:
    1. {project-tests} = `{worktree-path}/tests/` if present
    2. {plugin-suites} = each `{worktree-path}/plugins/*/pytest.ini` (the plugin directory containing it is a suite)
9. Run suites:
    1. {results} = empty accumulator
    2. If {project-tests} exists:
        1. bash: `env -C {worktree-path} {project-venv} -m pytest tests/ -v`
        2. Append {passed, failed, failures} to {results} under "project"
    3. For each {suite} in {plugin-suites}:
        1. {plugin-name} = basename of the plugin directory
        2. bash: `env -C {worktree-path} {project-venv} -m pytest plugins/{plugin-name}/ -c plugins/{plugin-name}/pytest.ini -v`
        3. Append {passed, failed, failures} to {results} under {plugin-name}
10. Compile report:
    - Per-suite: passed/failed counts, failure summary (first line of each failing test's output)
    - Overall: total passed, total failed, ref + short SHA identifying the baseline
11. Cleanup worktree:
    1. bash: `git worktree remove {worktree-path} --force`
12. Return to caller:
    - ref: {ref} ({short-sha})
    - per-suite counts and failure summaries
    - overall pass/fail verdict
    - worktree cleaned up

13. Error Handling:
    1. If worktree was created: bash: `git worktree remove {worktree-path} --force`
    2. Exit to user: test run failed — check output for cause (venv missing, ref unresolvable, suite setup error)

## Cleanup

> Find and remove sandbox projects and leftover git worktrees. Sibling projects match the parent-project prefix convention. Worktrees match `.claude/worktrees/*` — the path the `worktree`, `exercise`, and `test` verbs create under. Any additional non-main worktrees reported by `git worktree list` (leftover from earlier runs, manual creations, other tools) are also surfaced so nothing disposable is missed. Always confirms before deletion.

1. {parent-project} = basename of current project directory
2. {parent-dir} = parent directory of current project
3. {project-siblings} = directories matching `{parent-dir}/{parent-project}-test-*`
4. {worktrees} = `git worktree list` rows whose path is not the current project directory
5. If no siblings and no worktrees: Exit to user: nothing to clean up
6. Present inventory:
    - Sibling projects — path, size, last-modified time for each
    - Worktrees — path, branch, status (clean/dirty) for each
7. Ask user — AskUserQuestion with options: `["Remove all", "Choose which to remove", "Cancel"]`
8. If cancel: Exit to user: cleanup cancelled
9. If choose:
    1. For each {item} in {project-siblings} and {worktrees}:
        1. AskUserQuestion with options: `["Remove", "Keep"]`
10. {to-remove} = items marked for removal
11. For each {sibling} in {to-remove} matching {project-siblings}: bash: `rm -rf {sibling}`
12. For each {worktree} in {to-remove} matching {worktrees}:
    1. bash: `git worktree remove {worktree.path} --force`
    2. If {worktree.branch} is safe to delete (not main, not current, not tracked elsewhere): bash: `git branch -D {worktree.branch}`
13. Report what was removed
14. Return to caller
