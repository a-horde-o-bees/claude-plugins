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

> Confirm target — surface repo root, sibling path, branch, and base commit together so the user catches "wrong project" mistakes (e.g. invoking from a linked worktree or from an unrelated repo) before any filesystem change.

6. Gather target info:
    1. {repo-root} = bash: `git rev-parse --show-toplevel`
    2. {base-commit} = bash: `git log -1 --format='%h %s' origin/main`
7. Present target info to the user — one block showing:
    - Repo: {repo-root}
    - Sibling path: {sibling-path}
    - New branch: {branch}
    - Base: origin/main @ {base-commit}
8. AskUserQuestion — "Create sandbox worktree?"; options: `["Proceed", "Cancel"]`
9. If `Cancel`: Exit to user: new cancelled

> Create — sibling worktree on a new branch from `origin/main`, then push the branch so other sessions/machines can see it.

10. Create sibling worktree:
    1. bash: `ocd-run sandbox worktree-add {sibling-name} --branch {branch} --base-ref origin/main`
11. Push branch to origin:
    1. bash: `git -C {sibling-path} push -u origin {branch}`

12. Return to caller:
    - created: {branch}
    - worktree: {sibling-path}
    - next: `cd {sibling-path} && claude` to begin working in an isolated session; main tree stays on main
