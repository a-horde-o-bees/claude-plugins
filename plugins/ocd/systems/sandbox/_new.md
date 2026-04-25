# New

Create an empty feature sandbox — a new `sandbox/<feature>` branch checked out in a sibling worktree at `<parent>/<project>--<name>/`. Use when starting a fresh feature from scratch; for features that extract existing code from main, use `pack` instead. Main tree never checks out the dev branch; the sibling is where work happens.

### Variables

- {verb-arg} — positional value: feature id (kebab-case; may be hierarchical with `/` separators like `ocd/audit-static`)

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: new requires a feature id
    2. {feature-id} = {verb-arg}
    3. If {feature-id} starts with `tmp/` or `tmp-` or equals `tmp`: Exit to user: `tmp` namespace reserved for ephemeral sandboxes
2. {sibling-name} = {feature-id} with every `/` replaced by `-` — filesystem-safe flat form
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Preconditions — no branch or path collision with the target. Caller's current branch and working tree are not checked; the new sibling branches directly from `origin/main` and is independent of caller state.

5. Verify preconditions:
    1. bash: `git fetch origin main --quiet`
    2. bash: `git show-ref --verify --quiet refs/heads/{branch}`
    3. If exit 0: Exit to user: local branch {branch} already exists
    4. bash: `git ls-remote --exit-code --heads origin {branch}`
    5. If exit 0: Exit to user: remote branch {branch} already exists on origin
    6. If {sibling-path} exists on disk: Exit to user: path already exists at {sibling-path}

> Confirm target — surface repo root, sibling path, branch, and recent history together so the user catches "wrong project" mistakes (e.g. invoking from a linked worktree or from an unrelated repo) before any filesystem change. Show the last 5 commits rather than just the base commit: rectification commits (`Deployed — rectify …`) on main frequently sit at the tip, and their descriptions are near-identical across projects — the history block above them is what distinguishes one repo from another.

6. Gather target info:
    1. {repo-root} = bash: `git rev-parse --show-toplevel`
    2. {recent-history} = bash: `git log -5 --format='%h %s' origin/main`
7. Present target info to the user — one block showing:
    - Repo: {repo-root}
    - Sibling path: {sibling-path}
    - New branch: {branch}
    - Base: origin/main (tip of recent history below)
    - Recent history (last 5 on origin/main): {recent-history}
8. AskUserQuestion — "Create sandbox worktree?"; options: `["Proceed", "Cancel"]`
9. If `Cancel`: Exit to user: new cancelled

> Create — sibling worktree on a new branch from `origin/main`, then seed `SANDBOX-TASKS.md` at the sibling's project root from the template, commit it, and push the branch so other sessions/machines can see it.

10. Create sibling worktree:
    1. bash: `ocd-run sandbox worktree-add {sibling-name} --branch {branch} --base-ref origin/main`
11. Seed `SANDBOX-TASKS.md` from template:
    1. {template-path} = `{sibling-path}/plugins/ocd/systems/sandbox/templates/SANDBOX-TASKS.md`
    2. {target-path} = `{sibling-path}/SANDBOX-TASKS.md`
    3. Read {template-path}
    4. Substitute the literal `{feature-id}` placeholder in the heading with the actual feature id
    5. Write the substituted content to {target-path}
12. Commit and push:
    1. bash: `git -C {sibling-path} add SANDBOX-TASKS.md`
    2. bash: `git -C {sibling-path} commit -m "Sandbox tasks — initial scope for {feature-id}"`
    3. bash: `git -C {sibling-path} push -u origin {branch}`

13. Return to caller:
    - created: {branch}
    - worktree: {sibling-path}
    - tasks file: {sibling-path}/SANDBOX-TASKS.md — populate Goal, Pointers, and initial Tasks before substantive work begins
    - next: `cd {sibling-path} && claude` to begin working in an isolated session; main tree stays on main
