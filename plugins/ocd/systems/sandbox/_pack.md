# Pack

Move a feature off the current branch onto a dedicated `sandbox/<feature>` branch in a sibling worktree, hiding it from holistic testing until the user is ready to reintegrate and unpack. The source branch is whatever cwd is on — usually `main`, but can be another `sandbox/*` branch when splitting a sub-feature out of an in-flight sandbox. Usually a feature maps to a single plugin system, but a feature can also span multiple paths (a system plus shared workflow files, or a cross-cutting change touching several subsystems). Pack resolves the feature's scope — paths and symbols — through a brief conversation, then cuts structural ties on the source branch and migrates in-flight notes to a `_status.md` in the sibling worktree.

When the source is not `main`, the new sandbox's history will contain the source branch's commits — surface this to the user before proceeding so they understand the unpack ordering implication.

### Variables

- {verb-arg} — positional value: natural-language description of the feature to pack; may name a single plugin system directly ("navigator", "ocd:navigator") or describe a cross-cutting feature spanning multiple paths.

### Process

1. Parse {verb-arg}:
    1. {description} = {verb-arg}
    2. {feature-id} = kebab-case slug derived from {description}, confirmed with the user. May be hierarchical with `/` for plugin-scoped features (e.g. `ocd/audit-static`).
    3. If {feature-id} starts with `tmp/` or `tmp-` or equals `tmp`: Exit to user: `tmp` namespace reserved for ephemeral sandboxes — choose a different feature id
    4. Propose {default-scope} from {description}:
        1. If {description} clearly names a single plugin system (e.g., "navigator", "ocd:navigator", "pack the navigator system"):
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
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`
5. {source-branch} = bash: `git rev-parse --abbrev-ref HEAD`

> Preconditions — pack runs on any clean working tree; the default scope's paths must exist; no conflicting branch or sibling may already exist. Source branch must not be detached.

6. Verify preconditions:
    1. If {source-branch} is `HEAD`: Exit to user: pack requires a named source branch; cwd is on detached HEAD
    2. bash: `git status --short`
    3. If output is non-empty: Exit to user: working tree has changes — commit or stash before packing
    4. For each {path} in {default-scope}.paths: if {path} does not exist on disk: Exit to user: {path} not found (scope references nonexistent path)
    5. bash: `git show-ref --verify --quiet refs/heads/{branch}`
    6. If exit 0: Exit to user: local branch {branch} already exists
    7. bash: `git ls-remote --exit-code --heads origin {branch}`
    8. If exit 0: Exit to user: remote branch {branch} already exists on origin
    9. If {sibling-path} exists on disk: Exit to user: sibling path {sibling-path} already exists

> Source confirmation — when source is not main, the sub-feature's history will carry the source's commits when unpacked. Surface to the user.

7. If {source-branch} ≠ `main`:
    1. AskUserQuestion:
        - question: "Packing off `{source-branch}` (not main). The new sandbox `{branch}` will branch from `{source-branch}`'s tip and inherit its commits. When unpacked into main, those commits go with it — usually fine if `{source-branch}` is also being unpacked, surprising otherwise. Proceed?"
        - options: `["Proceed", "Cancel"]`
    2. If `Cancel`: Exit to user: pack cancelled

> Scope confirmation — present the default scope to the user; invite additions (cross-cutting paths, extra symbols) and removals.

8. Confirm scope with user:
    1. Present {default-scope} — paths, symbols, branch name, sibling path — and ask: "Are there additional paths or symbols this feature covers, or should be scoped narrower?"
    2. AskUserQuestion with options: `["Proceed with default scope", "Add paths/symbols", "Narrow scope", "Cancel"]`
    3. If `Cancel`: Exit to user: pack cancelled
    4. If `Add paths/symbols`:
        1. Prompt user for additional paths (relative to project root) and/or symbols (slash-refs, module refs, bare names)
        2. {scope} = {default-scope} ∪ user additions
    5. If `Narrow scope`:
        1. Prompt user for paths/symbols to remove from default
        2. {scope} = {default-scope} ∖ user removals
    6. Else: {scope} = {default-scope}

> Tendril scan — iterate scope elements; grep each across everything outside the scope's paths to find external references.

9. Scan for external references:
    1. {exclude-pathspec} = pathspec excluding every path in {scope}.paths, e.g. `':(exclude)plugins/ocd/systems/navigator' ':(exclude)plugins/ocd/lib/rules/navigator.md'`
    2. {tendrils} = empty set
    3. For each {path-ref} in {scope}.path-refs:
        1. bash: `git grep -nI -e '{path-ref}' -- . {exclude-pathspec}`; add results to {tendrils}
    4. For each {symbol} in {scope}.symbols:
        1. If {symbol} is `slash`: bash: `git grep -nI -F '{symbol.value}' -- . {exclude-pathspec}`; add results to {tendrils}
        2. If {symbol} is `module`: bash: `git grep -nI -E 'systems[./]{symbol.value}(\b|$)' -- . {exclude-pathspec}`; add results to {tendrils}
        3. If {symbol} is `bare`: bash: `git grep -nI -E '\`{symbol.value}\`|^\| \`?{symbol.value}\`? \|' -- 'plugins/**/*.md' {exclude-pathspec}`; add results to {tendrils}
    5. Deduplicate {tendrils} by file:line

> Classification — each tendril is auto-handled, migrated, or surfaced for user decision.

10. Classify tendrils:
    1. {auto-delete} = tendrils that are clearly structural:
        - Rows in `plugins/<plugin>/README.md` skills-table or `plugins/<plugin>/ARCHITECTURE.md` subsystem-table (line starts with `|` inside a markdown table)
        - Path or module imports in code files whose sole content is the reference
    2. {auto-migrate} = tendrils whose source is content about the feature:
        - Bullet entries in `purpose-map/state.md` or project-root `state.md` that describe work on the feature
        - Files in `logs/**/*.md` whose filename or level-1 heading names any scope symbol
    3. {interactive} = every remaining tendril — prose mentions, illustrative examples, docstring samples, log entries that only mention the feature in passing

> Auto-handle — apply deterministic deletions and accumulate migrated content before touching the index.

11. {status-md-content} = empty accumulator

12. For each {tendril} in {auto-delete}:
    1. Delete the referenced line (or the full table row) from the tendril's file

13. For each {tendril} in {auto-migrate}:
    1. If source is a `state.md`:
        1. Lift the bullet (plus any nested sub-bullets) or heading section from state.md
        2. Append to {status-md-content} under the heading "## Open Work"
    2. If source is a log file:
        1. Lift the full file content (minus the level-1 heading) into {status-md-content} under the heading "## Migrated Log: {original filename}"
        2. Delete the original log file

> Interactive — surface remaining tendrils one at a time; the user directs disposition.

14. For each {tendril} in {interactive}:
    1. Present {tendril} to the user with its file, line, and surrounding context
    2. AskUserQuestion with options: `["migrate", "remove", "edit", "leave"]`
    3. If `migrate`:
        1. Prompt the user for what content to migrate (default: the containing paragraph or bullet)
        2. Lift that content into {status-md-content} under the heading "## Migrated Note: {source-file}"
        3. Remove the content from the source file on the source branch's working tree
    4. If `remove`: delete the referenced line (or user-specified span) from the source file
    5. If `edit`:
        1. Prompt the user for what the reference should become
        2. Apply the edit to the source file
        3. Re-scan that file; if the tendril remains, re-prompt
    6. If `leave`: record the override in the pack summary — no file change

> Verification — confirm the tendril set on the source branch is empty except for explicit `leave` overrides.

15. Re-run the tendril scan from step 9 over the updated tree
16. {remaining} = re-scan output minus any entries the user chose `leave` on
17. If {remaining} is non-empty:
    1. Exit to user:
        - unexpected tendrils still present after auto-handle + interactive
        - {remaining}
        - re-run pack once resolved

> Transition — two commits land: one on the source branch with tendril cleanup + scope removal, one on the sibling branch that carries the `_status.md` if content was migrated. The sibling is branched from the source's tip BEFORE the scope-removal commit, so the scope paths are already present in the sibling without needing manual restoration. The source worktree (cwd) stays on its branch throughout; no checkouts.

18. Execute transition:
    1. bash: `ocd-run sandbox worktree-add {sibling-name} --branch {branch} --base-ref {source-branch}`
    2. On the source worktree (cwd): remove scope paths
        1. For each {path} in {scope}.paths: bash: `git rm -r {path}`
        2. Stage tendril modifications from steps 12–14: bash: `git add -u`
        3. bash: `git commit -m "pack {feature-id}"`
    3. In the sibling (if {status-md-content} non-empty):
        1. {status-location} = primary path of the scope (single path for single-path scopes; longest common directory prefix for multi-path features)
        2. Write `{sibling-path}/{status-location}/_status.md` with a level-1 heading "In-Flight Status: {feature-id}", a one-line purpose statement, then {status-md-content}
        3. bash: `git -C {sibling-path} add {status-location}/_status.md`
        4. bash: `git -C {sibling-path} commit -m "restore {feature-id}"`
    4. Push both branches:
        1. bash: `git -C {sibling-path} push -u origin {branch}`
        2. bash: `git push origin {source-branch}`

19. Return to caller:
    - packed: {feature-id}
    - source: {source-branch}
    - scope: {scope}.paths and {scope}.symbols
    - tendrils auto-deleted: count
    - tendrils migrated to `_status.md`: count
    - tendrils handled interactively: count (by disposition)
    - tendrils left on {source-branch} via override: count
    - source: scope paths removed; HEAD advanced by 1 commit; pushed
    - sibling: {sibling-path} on {branch}; scope preserved; `_status.md` present if content migrated; pushed
    - next: `cd {sibling-path} && claude` to continue feature work
