---
name: sandbox
description: Exercise changes in an isolated test environment — a sibling project for fresh-install scenarios, or a git worktree for in-repo change isolation. Presents a test plan, confirms, executes, and offers cleanup.
argument-hint: "<project | worktree | cleanup> [description]"
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

Exercise changes in an isolated test environment — a sibling project for fresh-install scenarios, or a git worktree for in-repo change isolation. Presents a test plan, confirms, executes, and offers cleanup.

## Process Model

Testing in isolation uses one of two substrates depending on what's being exercised:

- **Sibling project** (`project` verb) — a brand new directory created at `<parent-project>-test-<topic>/`, separate filesystem, fresh git repo, fresh plugin cache. Tests "from nothing" scenarios: fresh install, bootstrapping, first-time-user behavior.
- **Git worktree** (`worktree` verb) — a disposable branch checked out at `.claude/worktrees/<topic>/`, shares plugin cache with current session, isolated from main working tree. Tests changes against existing project state without risking the main tree.

The skill executor reasons about what the user is testing (from their natural-language description) and proposes a concrete plan. User confirms or adjusts before any filesystem changes happen. After execution, results are presented; cleanup is offered immediately or deferred until the next `cleanup` invocation.

## Rules

- Never create, modify, or delete outside the sandbox substrate — the invoking project is never touched
- Never proceed with creation until user has confirmed the plan — presenting the plan is not authorization to execute
- Cleanup operates on the parent project's namespace only — matches `<parent>-test-*` siblings and worktrees under `.claude/worktrees/`; never touches unrelated directories
- `project` verb testing requires `/checkpoint` first — the spawned `claude -p` subprocess inherits PATH from the harness, and PATH resolves `<plugin>-run` binaries against the marketplace-cached install, not `--plugin-dir`. Reliable plugin-behavior tests need the marketplace version to reflect current commits; `--plugin-dir` alone is insufficient because PATH lookup shadows it with older cached versions
- Empty description is a valid invocation for `project` and `worktree` — skill asks what to test instead of guessing

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint

> Verb dispatch — project creates a sibling, worktree creates a branch checkout, cleanup removes either.

2. If {verb} is `project`:
    1. Call: Project
3. Else if {verb} is `worktree`:
    1. Call: Worktree
4. Else if {verb} is `cleanup`:
    1. Call: Cleanup
5. Else: Exit to user: unrecognized verb {verb} — expected project, worktree, or cleanup

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

> Create a disposable git worktree on a new branch, propose a test plan, confirm, execute, report, offer cleanup.

1. {description} = remaining arguments after the verb
2. If {description} is empty: ask user what they want to test
3. {topic} = concise kebab-case slug derived from {description}
4. {worktree-path} = `.claude/worktrees/{topic}`
5. {branch} = `sandbox/{topic}`
6. Draft test plan:
    1. {changes} = file changes to apply in the worktree, or none
    2. {invocation} = exact command to run in {worktree-path}
    3. {verification} = what output or filesystem state confirms the test passed
7. Present plan to user — show {worktree-path}, {branch}, {changes}, {invocation}, {verification}
8. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
9. If cancel: Exit to user: test cancelled
10. If adjust: take refinements, update plan, Go to step 7. Present plan to user
11. Block push — bash: `git config remote.origin.pushurl "file:///dev/null"`
12. Execute plan:
    1. bash: `git worktree add -b {branch} {worktree-path}`
    2. Apply {changes} to files in {worktree-path}
    3. bash: `env -C {worktree-path} {invocation}`
    4. {output} = captured output
13. Unblock push — bash: `git config --unset remote.origin.pushurl`
14. Present results — {output}, branch state, verification outcome against {verification}
15. Ask user about cleanup — AskUserQuestion with options: `["Remove worktree now", "Keep for inspection"]`
16. If remove:
    1. bash: `git worktree remove {worktree-path} --force`
    2. bash: `git branch -D {branch}`
17. Return to caller

18. Error Handling:
    1. Unblock push — bash: `git config --unset remote.origin.pushurl`
    2. Exit to user: worktree sandbox failed — check output for details

## Cleanup

> Find and remove sandbox projects and worktrees belonging to the current project. Always confirms before deletion.

1. {parent-project} = basename of current project directory
2. {parent-dir} = parent directory of current project
3. {project-siblings} = directories matching `{parent-dir}/{parent-project}-test-*`
4. {worktrees} = output of `git worktree list` filtered to paths under `.claude/worktrees/`
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
    1. bash: `git worktree remove {worktree} --force`
    2. If {worktree}'s branch has `sandbox/` prefix: bash: `git branch -D {branch}`
13. Report what was removed
14. Return to caller
