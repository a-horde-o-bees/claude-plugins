# Box

Move a plugin system off main onto a dedicated dev branch, hiding it from holistic testing until explicitly reopened. Cuts structural ties on main and migrates in-flight notes to a `_status.md` on the dev branch.

### Variables

- {verb-arg} — positional value after the verb, expected in `<plugin>:<system>` form

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} does not match `<plugin>:<system>`: Exit to user: box requires `<plugin>:<system>` form
    2. {plugin} = plugin part of {verb-arg}
    3. {system} = system part of {verb-arg}
2. {system-path} = `plugins/{plugin}/systems/{system}`
3. {dev-branch} = `dev/{plugin}/{system}`

> Preconditions — box must run on a clean main checkout with the system present and no conflicting dev branch.

4. Verify preconditions:
    1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is not `main`: Exit to user: box requires main checkout; currently on {current-branch}
    3. bash: `git status --short`
    4. If output is non-empty: Exit to user: working tree has changes — commit or stash before boxing
    5. If {system-path} does not exist: Exit to user: {system-path} not found
    6. bash: `git show-ref --verify --quiet refs/heads/{dev-branch}`
    7. If exit 0: Exit to user: local branch {dev-branch} already exists
    8. bash: `git ls-remote --exit-code --heads origin {dev-branch}`
    9. If exit 0: Exit to user: remote branch {dev-branch} already exists on origin

> Tendril scan — find every external reference to the system so each can be auto-handled or surfaced for user decision.

5. Scan for external references:
    1. {refs-path} = bash: `git grep -nI -e 'plugins/{plugin}/systems/{system}' -- . ':(exclude){system-path}'`
    2. {refs-module} = bash: `git grep -nI -E 'systems[./]{system}(\b|$)' -- . ':(exclude){system-path}'`
    3. {refs-slash} = bash: `git grep -nI -F '/{plugin}:{system}' -- . ':(exclude){system-path}'`
    4. {tendrils} = union of {refs-path}, {refs-module}, and {refs-slash}, deduplicated by file:line

> Classification — each tendril is auto-handled, migrated, or surfaced for user decision.

6. Classify tendrils:
    1. {auto-delete} = tendrils that are clearly structural:
        - Rows in `plugins/{plugin}/README.md` skills-table or `plugins/{plugin}/architecture.md` subsystem-table (line starts with `|` inside a markdown table)
        - Path or module imports in code files whose sole content is the reference (e.g., a bare import line)
    2. {auto-migrate} = tendrils whose source is content about the system:
        - Bullet entries in `purpose-map/state.md` that describe work on the system
        - Files in `.claude/logs/**/*.md` whose filename or level-1 heading names the system
    3. {interactive} = every remaining tendril — prose mentions, illustrative examples, docstring samples, log entries that only mention the system in passing

> Auto-handle — apply deterministic deletions and accumulate migrated content before touching the index.

7. {status-md-content} = empty accumulator

8. For each {tendril} in {auto-delete}:
    1. Delete the referenced line (or the full table row) from the tendril's file

9. For each {tendril} in {auto-migrate}:
    1. If source is `state.md`:
        1. Lift the bullet (plus any nested sub-bullets) from `state.md`
        2. Append to {status-md-content} under the heading "## Open Work"
    2. If source is a log file:
        1. Lift the full file content (minus the level-1 heading) into {status-md-content} under the heading "## Migrated Log: {original filename}"
        2. Delete the original log file

> Interactive — surface remaining tendrils one at a time; the user directs disposition.

10. For each {tendril} in {interactive}:
    1. Present {tendril} to the user with its file, line, and surrounding context
    2. AskUserQuestion with options: `["migrate", "remove", "edit", "leave"]`
    3. If `migrate`:
        1. Prompt the user for what content to migrate (default: the containing paragraph or bullet)
        2. Lift that content into {status-md-content} under the heading "## Migrated Note: {source-file}"
        3. Remove the content from the source file on main
    4. If `remove`:
        1. Delete the referenced line (or the user-specified span) from the source file
    5. If `edit`:
        1. Prompt the user for what the reference should become
        2. Apply the edit to the source file
        3. Re-scan that file; if the tendril remains, re-prompt
    6. If `leave`:
        1. Record the override in the box summary — no file change

> Verification — confirm the tendril set on main is empty except for explicit `leave` overrides, so boxing doesn't silently leave a path or module reference dangling.

11. Re-run the tendril scan (same three greps as step 5)
12. {remaining} = scan output minus any entries the user chose `leave` on
13. If {remaining} is non-empty:
    1. Exit to user:
        - unexpected tendrils still present after auto-handle + interactive
        - {remaining}
        - re-run box once resolved

> Transition — two commits land: one on main with tendril cleanup + system removal, one on the dev branch that restores the system and adds the `_status.md` if content was migrated.

14. Execute transition:
    1. {pre-box-commit} = bash: `git rev-parse HEAD`
    2. bash: `git rm -r {system-path}`
    3. Stage all modified and deleted tendril files from steps 8–10 — bash: `git add -u`
    4. bash: `git commit -m "box {plugin}:{system}"`
    5. bash: `git checkout -b {dev-branch}`
    6. bash: `git checkout {pre-box-commit} -- {system-path}`
    7. If {status-md-content} is non-empty:
        1. Write {system-path}/_status.md with a level-1 heading "In-Flight Status: {system}", a one-line purpose statement, then {status-md-content}
    8. bash: `git add {system-path}`
    9. bash: `git commit -m "restore {plugin}:{system}"`
    10. bash: `git push -u origin {dev-branch}`
    11. bash: `git checkout main`
    12. bash: `git push origin main`

15. Return to caller:
    - boxed: {plugin}:{system}
    - tendrils auto-deleted: count
    - tendrils migrated to `_status.md`: count
    - tendrils handled interactively: count (by disposition)
    - tendrils left on main via override: count
    - main: system removed; HEAD advanced by 1 commit
    - {dev-branch}: system preserved; `_status.md` present if content migrated; pushed to origin
