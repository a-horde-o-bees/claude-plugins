# Box

Move a feature off main onto a dedicated dev branch, hiding it from holistic testing until the user is ready to reintegrate and unbox. Usually a feature maps to a single plugin system, but a feature can also span multiple paths (e.g. a system plus shared workflow files, or a cross-cutting change touching several subsystems). Box resolves the feature's scope — paths and symbols — through a brief conversation, then cuts structural ties on main and migrates in-flight notes to a `_status.md` on the dev branch.

### Variables

- {verb-arg} — positional value after the verb. Natural-language description of the feature to box; may name a single plugin system directly ("navigator", "ocd:navigator") or describe a cross-cutting feature spanning multiple paths.

### Process

1. Parse {verb-arg}:
    1. {description} = {verb-arg}
    2. {feature-id} = kebab-case slug derived from {description}, confirmed with the user
    3. Propose {default-scope} from {description}:
        1. If {description} clearly names a single plugin system (e.g., "navigator", "ocd:navigator", "box the navigator system"):
            1. {plugin} = plugin name (inferred from description or asked)
            2. {system} = system name
            3. {system-path} = `plugins/{plugin}/systems/{system}`
            4. {default-scope} =
                - paths: [{system-path}]
                - path-refs: [{system-path}]
                - symbols:
                    - `slash`: `/{plugin}:{system}`
                    - `module`: `{system}` — greps `systems[./]{system}(\b|$)`
                    - `bare`: `{system}` — greps backticked name in markdown, or table-row first column under `plugins/`
        2. Else: query navigator to surface candidate paths:
            1. tool: `paths_search` with {description}
            2. If navigator returns its dormant-state message: {default-scope} is empty — user authors scope from scratch in step 4
            3. Else:
                1. {default-scope}.paths = paths from the search result whose indexed purposes align with {description}
                2. {default-scope}.path-refs = {default-scope}.paths
                3. {default-scope}.symbols = empty — user adds specific symbols in step 4 if needed
2. {dev-branch} = `dev/{feature-id}`

> Preconditions — box must run on a clean main checkout; the default scope's paths must exist; no conflicting dev branch may already exist.

3. Verify preconditions:
    1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is not `main`: Exit to user: box requires main checkout; currently on {current-branch}
    3. bash: `git status --short`
    4. If output is non-empty: Exit to user: working tree has changes — commit or stash before boxing
    5. For each {path} in {default-scope}.paths: if {path} does not exist on disk: Exit to user: {path} not found (scope references nonexistent path)
    6. bash: `git show-ref --verify --quiet refs/heads/{dev-branch}`
    7. If exit 0: Exit to user: local branch {dev-branch} already exists
    8. bash: `git ls-remote --exit-code --heads origin {dev-branch}`
    9. If exit 0: Exit to user: remote branch {dev-branch} already exists on origin

> Scope confirmation — present the default scope to the user; invite additions (cross-cutting paths, extra symbols) and removals. The scope is ephemeral — used for this box invocation, then discarded. The dev branch holds everything going forward.

4. Confirm scope with user:
    1. Present {default-scope} — paths, symbols, dev branch name — and ask: "Are there additional paths or symbols this feature covers, or should be scoped narrower?"
    2. AskUserQuestion with options: `["Proceed with default scope", "Add paths/symbols", "Narrow scope", "Cancel"]`
    3. If `Cancel`: Exit to user: box cancelled
    4. If `Add paths/symbols`:
        1. Prompt user for additional paths (relative to project root) and/or symbols (slash-refs, module refs, bare names)
        2. {scope} = {default-scope} ∪ user additions
    5. If `Narrow scope`:
        1. Prompt user for paths/symbols to remove from default
        2. {scope} = {default-scope} ∖ user removals
    6. Else: {scope} = {default-scope}

> Tendril scan — iterate scope elements; grep each across everything outside the scope's paths to find external references. Scope-driven scanning replaces hardcoded patterns keyed to a single system name, which means bare system names in table rows and cross-cutting references get caught by the same mechanism.

5. Scan for external references:
    1. {exclude-pathspec} = pathspec excluding every path in {scope}.paths, e.g. `':(exclude)plugins/ocd/systems/navigator' ':(exclude)plugins/ocd/lib/rules/navigator.md'`
    2. {tendrils} = empty set
    3. For each {path-ref} in {scope}.path-refs:
        1. bash: `git grep -nI -e '{path-ref}' -- . {exclude-pathspec}`; add results to {tendrils}
    4. For each {symbol} in {scope}.symbols:
        1. If {symbol} is `slash`: bash: `git grep -nI -F '{symbol.value}' -- . {exclude-pathspec}`; add results to {tendrils}
        2. If {symbol} is `module`: bash: `git grep -nI -E 'systems[./]{symbol.value}(\b|$)' -- . {exclude-pathspec}`; add results to {tendrils}
        3. If {symbol} is `bare`: bash: `git grep -nI -E '\`{symbol.value}\`|^\| \`?{symbol.value}\`? \|' -- 'plugins/**/*.md' {exclude-pathspec}`; add results to {tendrils} — backticked or table-row-first-column match, scoped to markdown docs under plugins/
    5. Deduplicate {tendrils} by file:line

> Classification — each tendril is auto-handled, migrated, or surfaced for user decision. Classification reads the tendril's file path and surrounding content — no hardcoded keying on "the" system name.

6. Classify tendrils:
    1. {auto-delete} = tendrils that are clearly structural:
        - Rows in `plugins/<plugin>/README.md` skills-table or `plugins/<plugin>/architecture.md` subsystem-table (line starts with `|` inside a markdown table)
        - Path or module imports in code files whose sole content is the reference
    2. {auto-migrate} = tendrils whose source is content about the feature:
        - Bullet entries in `purpose-map/state.md` or project-root `state.md` that describe work on the feature
        - Files in `.claude/logs/**/*.md` whose filename or level-1 heading names any scope symbol
    3. {interactive} = every remaining tendril — prose mentions, illustrative examples, docstring samples, log entries that only mention the feature in passing

> Auto-handle — apply deterministic deletions and accumulate migrated content before touching the index.

7. {status-md-content} = empty accumulator

8. For each {tendril} in {auto-delete}:
    1. Delete the referenced line (or the full table row) from the tendril's file

9. For each {tendril} in {auto-migrate}:
    1. If source is a `state.md`:
        1. Lift the bullet (plus any nested sub-bullets) or heading section from state.md
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

> Verification — confirm the tendril set on main is empty except for explicit `leave` overrides, so boxing doesn't silently leave a path or symbol reference dangling.

11. Re-run the tendril scan from step 5 over the updated tree
12. {remaining} = re-scan output minus any entries the user chose `leave` on
13. If {remaining} is non-empty:
    1. Exit to user:
        - unexpected tendrils still present after auto-handle + interactive
        - {remaining}
        - re-run box once resolved

> Transition — two commits land: one on main with tendril cleanup + scope removal, one on the dev branch that restores the scope's paths and adds the `_status.md` if content was migrated. `_status.md` is written at the scope's primary path (for single-system features, this is inside the system directory; for cross-cutting features, it's the longest common prefix of scope paths).

14. Execute transition:
    1. {pre-box-commit} = bash: `git rev-parse HEAD`
    2. For each {path} in {scope}.paths: bash: `git rm -r {path}`
    3. Stage all modified and deleted tendril files from steps 8–10 — bash: `git add -u`
    4. bash: `git commit -m "box {feature-id}"`
    5. bash: `git checkout -b {dev-branch}`
    6. For each {path} in {scope}.paths: bash: `git checkout {pre-box-commit} -- {path}`
    7. If {status-md-content} is non-empty:
        1. {status-location} = primary path of the scope (single path for single-path scopes; longest common directory prefix for multi-path features)
        2. Write {status-location}/_status.md with a level-1 heading "In-Flight Status: {feature-id}", a one-line purpose statement, then {status-md-content}
    8. bash: `git add` for each scope path
    9. bash: `git commit -m "restore {feature-id}"`
    10. bash: `git push -u origin {dev-branch}`
    11. bash: `git checkout main`
    12. bash: `git push origin main`

15. Return to caller:
    - boxed: {feature-id}
    - scope: {scope}.paths and {scope}.symbols
    - tendrils auto-deleted: count
    - tendrils migrated to `_status.md`: count
    - tendrils handled interactively: count (by disposition)
    - tendrils left on main via override: count
    - main: scope paths removed; HEAD advanced by 1 commit
    - {dev-branch}: scope preserved; `_status.md` present if content migrated; pushed to origin

