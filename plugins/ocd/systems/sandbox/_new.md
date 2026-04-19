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

> Preconditions — main must be up-to-date with origin; no name, branch, or path collision.

5. Verify preconditions:
    1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is not `main`: Exit to user: new requires main checkout; currently on {current-branch}
    3. bash: `git status --short`
    4. If output is non-empty: Exit to user: working tree has changes — commit or stash before creating a new sandbox
    5. bash: `git fetch origin main --quiet`
    6. bash: `git rev-list --count main..origin/main`
    7. If non-zero: Exit to user: main is behind origin/main — pull before creating a new sandbox
    8. bash: `git show-ref --verify --quiet refs/heads/{branch}`
    9. If exit 0: Exit to user: local branch {branch} already exists
    10. bash: `git ls-remote --exit-code --heads origin {branch}`
    11. If exit 0: Exit to user: remote branch {branch} already exists on origin
    12. If {sibling-path} exists on disk: Exit to user: path already exists at {sibling-path}

> Create — sibling worktree on a new branch from main, then push the branch so other sessions/machines can see it.

6. Create sibling worktree:
    1. bash: `ocd-run sandbox worktree-add {sibling-name} --branch {branch} --base-ref main`
7. Push branch to origin:
    1. bash: `git -C {sibling-path} push -u origin {branch}`

8. Return to caller:
    - created: {branch}
    - worktree: {sibling-path}
    - next: `cd {sibling-path} && claude` to begin working in an isolated session; main tree stays on main
