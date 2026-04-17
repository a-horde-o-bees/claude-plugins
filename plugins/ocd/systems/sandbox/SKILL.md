---
name: sandbox
description: Exercise changes in an isolated test environment — a sibling project for fresh-install scenarios, a git worktree for interactive validation, or a combined test that routes concerns to both. Presents a test plan, confirms, executes, compiles results, and offers cleanup.
argument-hint: "<project | worktree | test | cleanup> [description]"
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

Exercise changes in an isolated test environment — a sibling project for fresh-install scenarios, a git worktree for interactive validation, or a combined `test` verb that classifies concerns and routes them to both substrates. Presents a test plan, confirms, executes, compiles results, and offers cleanup.

## Process Model

Testing in isolation uses one of two substrates depending on what's being exercised:

- **Sibling project** (`project` verb) — a brand new directory created at `<parent-project>-test-<topic>/`, separate filesystem, fresh git repo, fresh plugin cache. Tests "from nothing" scenarios: fresh install, bootstrapping, first-time-user behavior.
- **Git worktree** (`worktree` verb) — a disposable branch checked out at `.claude/worktrees/<topic>/`, shares plugin cache with current session, isolated from main working tree. Tests changes against existing project state without risking the main tree.

The skill executor reasons about what the user is testing (from their natural-language description) and proposes a concrete plan. User confirms or adjusts before any filesystem changes happen. After execution, results are presented; cleanup is offered immediately or deferred until the next `cleanup` invocation.

## Route Selection

The verbs pick different execution mechanisms. Each concern under test routes to `project` or `worktree` based on interactive characteristics — the test verb orchestrates both buckets automatically; the direct verbs route one bucket at a time.

| Capability | `project` (external) | `worktree` (internal) |
|---|---|---|
| Mechanism | Fresh `claude -p` subprocess | In-session agent via `Spawn (isolation: "worktree"):` |
| Plugin load | Fresh session — SessionStart fires, venv deps install, MCP servers initialize | Inherits parent session's plugin state |
| Cache / PATH | Assembled at subprocess start (requires `/checkpoint` first) | Parent session's existing cache and PATH |
| Permission prompts | Auto-decline — no back-channel to parent | Route through parent session to the user |
| Sensitive-file gate (`.claude/**`) | Blocks even under `--dangerously-skip-permissions` | User approves interactively |
| `AskUserQuestion` | Exits immediately | Works normally |
| `Exit to user:` follow-ups | No user available — skill ends without the follow-up happening | User acts on the exit message interactively |

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
- Skills that `Exit to user:` expecting follow-up — `<plugin>:audit-governance`, `<plugin>:audit-static`, observations-pending flows
- Multi-turn interactions where the parent session approves / steers
- Changes to repository state that shouldn't affect the main working tree — destructive refactors, commit-graph experiments

### Pick `test` when

- Validating a change end-to-end and either don't know or don't care which substrate each concern fits
- A single change touches both fresh-install and interactive surface area — `test` classifies concerns automatically and runs both buckets in sequence

Neither direct route is a replacement for the other. Fresh-install tests cannot pause for user input; interactive tests cannot exercise SessionStart cold-start behavior. `test` is the union — not a shortcut to skip classification, but a wrapper that keeps both halves visible.

## Rules

- Never create, modify, or delete outside the sandbox substrate — the invoking project is never touched
- Never proceed with creation until user has confirmed the plan — presenting the plan is not authorization to execute
- Cleanup scans only the parent project's namespace — siblings matching `<parent>-test-*` and all non-main worktrees reported by `git worktree list`; never touches unrelated directories
- `project` verb and the project bucket of `test` require `/checkpoint` first — the spawned `claude -p` subprocess inherits PATH from the harness, and PATH resolves `<plugin>-run` binaries against the marketplace-cached install, not `--plugin-dir`. Reliable plugin-behavior tests need the marketplace version to reflect current commits; `--plugin-dir` alone is insufficient because PATH lookup shadows it with older cached versions
- Empty description is a valid invocation for `project`, `worktree`, and `test` — skill asks what to test instead of guessing
- `test` classifies concerns strictly by the Interactivity criterion — if a concern could plausibly fit either bucket, surface the ambiguity to the user before proceeding rather than routing silently

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint

> Verb dispatch — project creates a sibling, worktree creates a branch checkout, test routes concerns to both substrates, cleanup removes what remains.

2. If {verb} is `project`:
    1. Call: Project
3. Else if {verb} is `worktree`:
    1. Call: Worktree
4. Else if {verb} is `test`:
    1. Call: Test
5. Else if {verb} is `cleanup`:
    1. Call: Cleanup
6. Else: Exit to user: unrecognized verb {verb} — expected project, worktree, test, or cleanup

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
11. If cancel: Exit to user: test cancelled
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

> Spawn an agent inside a disposable git worktree via the Agent tool's `isolation: "worktree"` modifier. Permission prompts route through the parent session so interactive skills work; the worktree system handles creation and cleans up automatically when the agent makes no changes. Agent changes that stick return a path and branch in the result for later cleanup.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to test
3. {topic} = concise kebab-case slug derived from {description}
4. Draft test plan:
    1. {changes} = file changes the agent should apply inside the worktree, or none
    2. {instructions} = what the agent should do — which skill(s) to invoke, what to verify, what to return
    3. {verification} = what output or filesystem state confirms the test passed
5. Present plan to user — show {topic}, {changes}, {instructions}, {verification}
6. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
7. If cancel: Exit to user: test cancelled
8. If adjust: take refinements, update plan, Go to step 5. Present plan to user
9. Block push — bash: `git config remote.origin.pushurl "file:///dev/null"`
10. Execute plan:
    1. Spawn (isolation: "worktree"):
        1. If {changes}: apply the described changes to files in the worktree
        2. Follow {instructions} — invoke skills, exercise the target workflow
        3. Return to caller:
            - Test output
            - Verification outcome against {verification} — pass, fail, inconclusive
            - Worktree path and branch (if changes were committed and the worktree persists)
    2. {output} = returned content
11. Unblock push — bash: `git config --unset remote.origin.pushurl`
12. Present results — {output}
13. Return to caller

14. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. Exit to user: worktree sandbox failed — check output for details

## Test

> Classify a comprehensive test description into project-bucket and worktree-bucket concerns per the Interactivity criterion, present a combined plan, execute both substrates, and compile a unified report. Use when validating an end-to-end change that touches both fresh-install and interactive surface area.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to test end-to-end — AskUserQuestion or free-text prompt
3. Verify working tree is clean and main is pushed — bash: `git status --short`
    1. If uncommitted changes exist: Exit to user: `test` routes to the `project` bucket which requires `/checkpoint` first; run `/checkpoint` then re-invoke
4. Classify the description into concerns. For each concern, evaluate the Interactivity criterion (see Route Selection):
    1. {project-bucket} = concerns that route to `project` — deterministic, fresh-install, no user prompts, no `.claude/**` writes, no `Exit to user:` follow-ups
    2. {worktree-bucket} = concerns that route to `worktree` — anything matching any of the five criterion questions
5. Draft the combined plan:
    1. {project-plan} = project-bucket setup-steps, invocation for `claude -p`, and verification — following the Project workflow shape
    2. {worktree-plan} = worktree-bucket changes (if any), agent instructions, and verification — following the Worktree workflow shape
6. Present the combined plan — show {description}, the per-concern classification, {project-plan}, {worktree-plan}. Highlight any concern that's ambiguous and ask the user which bucket it belongs in before proceeding.
7. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
8. If cancel: Exit to user: test cancelled
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
    1. Block push — bash: `git config remote.origin.pushurl "file:///dev/null"`
    2. Spawn (isolation: "worktree"):
        1. If {worktree-plan}.changes: apply the described changes to files in the worktree
        2. Follow {worktree-plan}.instructions — invoke skills, exercise the target workflow
        3. Return to caller:
            - Test output
            - Verification outcome against {worktree-plan}.verification — pass, fail, inconclusive
            - Worktree path and branch (if changes were committed and the worktree persists)
    3. {worktree-output} = returned content
    4. Unblock push — bash: `git config --unset remote.origin.pushurl`
12. Compile results:
    - Summary table: Bucket | Concern | Outcome | Evidence
    - Per-bucket digest: {project-output} summarized with filesystem and DB evidence preserved; {worktree-output} summarized with filesystem and interaction evidence preserved
    - Cross-cutting observations: anything that spans both buckets (naming mismatches, doc drift, unexpected behavior not tied to a single concern)
13. Present the compiled report to the user
14. Ask about cleanup — AskUserQuestion with options: `["Remove sandbox project now", "Keep for inspection"]` (worktree auto-cleans if no agent commits; persisted worktrees appear in the next `cleanup` invocation)
15. If remove and project bucket ran: bash: `rm -rf {sandbox-path}`
16. Return to caller

17. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. Exit to user: test sandbox failed — check output for which bucket failed and the cause

## Cleanup

> Find and remove sandbox projects and leftover git worktrees. Sibling projects match the parent-project prefix convention; worktrees are everything `git worktree list` reports except the main checkout — Agent-tool-managed worktrees that persisted across runs (because the agent committed changes) land here alongside any legacy paths. Always confirms before deletion.

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
