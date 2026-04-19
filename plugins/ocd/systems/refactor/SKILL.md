---
name: refactor
description: Execute mass source transformations through a scan → plan → apply → verify → test workflow. Wraps AST-aware codemods so identifier renames, module moves, and pattern rewrites land in one coordinated pass instead of iterative sed-and-fix cycles.
argument-hint: "<description>"
allowed-tools:
  - AskUserQuestion
  - Bash(grep *)
  - Bash(ocd-run *)
  - Bash(git *)
---

# /refactor

Execute mass source transformations through a scan → plan → apply → verify → test workflow. Wraps AST-aware codemods so identifier renames, module moves, and pattern rewrites land in one coordinated pass instead of iterative sed-and-fix cycles.

## Process Model

The skill doesn't invent transformations — it orchestrates existing tools under `systems/refactor/`. Today that means `rename-symbol` for Python identifier renames. Future tools under the same system (move-module, pattern-rewrite) plug into the same workflow by exposing a subcommand on `ocd-run refactor`.

The workflow disciplines the **scan → plan → apply → verify → test** cadence so that rename sites are identified up-front (avoiding iterative discovery during test failures), classified deliberately (avoiding false-positive substitutions in string literals, comments, or unrelated tokens), and verified before test runs (so failures expose runtime issues, not missed edits).

## Rules

- Always pre-scan before acting — no substitution passes without a complete inventory of the old identifier's occurrences
- Classify findings explicitly — imports, attribute access, path calculations, string literals, prose mentions. Each category gets a distinct disposition (rename, leave, edit-manually)
- Confirm the plan with user before any file write — AskUserQuestion with the full classified list
- Apply AST-aware tools when available (Python identifier renames) rather than regex. Regex is the fallback for prose/strings/non-Python files
- Re-run the pre-scan after application — remaining hits must match the documented exceptions list only
- Do not invoke the test runner directly — prompt the user to run `/ocd:sandbox tests` so verification happens in an isolated worktree

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. {description} = $ARGUMENTS

> Scope resolution — derive the old/new identifiers from the user's description. If ambiguous, ask before scanning.

3. Parse {description}:
    1. If the description names `<old> → <new>` (or similar unambiguous from/to form): {old} = old identifier, {new} = new identifier
    2. Else: AskUserQuestion with the parsed alternatives or an open prompt to clarify
4. {scope} = `plugins/<plugin>/` if the description names a specific plugin, else current project root — confirm with user if unsure

> Pre-scan — enumerate every occurrence of {old} in the scope. Cover all forms: imports, attribute access, string literals, prose mentions.

5. Scan:
    1. bash: `grep -rln "\b{old}\b" {scope}` — file-level hit list
    2. For a more targeted Python-only scan: bash: `grep -rn "\b{old}\b" {scope} --include='*.py'`
    3. For string-literal check: bash: `grep -rn "'{old}'\|\"{old}\"" {scope}`

> Classify — group findings by context so each category gets the right transformation.

6. Classify findings:
    1. `identifier` — Python imports, attribute access, function/class names. Auto-renameable via `ocd-run refactor rename-symbol`
    2. `path-string` — filesystem paths containing {old} as a segment. Needs sed or Edit
    3. `filename-literal` — strings like `"{old}.json"` that coincidentally match. **Leave** (false positive)
    4. `prose` — README, architecture, logs, comments. Edit manually or leave depending on doc currency expectations

> Plan confirmation — present the classified plan and wait for user approval.

7. Present plan:
    - {identifier} count, list
    - {path-string} count, list
    - {filename-literal} count, list (will be left untouched)
    - {prose} count, list with proposed per-item disposition
8. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
9. If `Cancel`: Exit to user: refactor cancelled
10. If `Adjust`: take user's refinements, update plan, Go to step 7. Present plan

> Apply — run the AST-aware tool for identifiers, sed for path-strings, Edit for prose items the user approved for change.

11. Apply transformations:
    1. If {identifier} non-empty: bash: `ocd-run refactor rename-symbol --from {old} --to {new} --scope {scope}`
    2. If {path-string} non-empty: apply sed to each path-string site
    3. If {prose} items marked for change: apply Edit surgically per item

> Verify — re-run the pre-scan. Remaining hits should be limited to documented exceptions (filename literals, leave-overridden prose).

12. Re-scan:
    1. bash: `grep -rln "\b{old}\b" {scope}`
    2. Compare results against the expected exception set from step 6
13. If unexpected hits remain: Exit to user:
    - unexpected residual occurrences of `{old}` after apply
    - list the unexpected hits
    - re-invoke once resolved

> Test — hand off to the sandbox test runner for isolated verification against a clean ref.

14. Present summary to user:
    - Total files rewritten
    - Per-category counts (identifier, path-string, prose)
    - Next step: run `/ocd:sandbox tests` to verify in a clean worktree
15. Return to caller

16. Error Handling:
    1. If `ocd-run refactor rename-symbol` exits with errors: surface stderr and exit — do not continue to other categories until parse errors are resolved
    2. If the user cancels mid-interactive classification: no file writes occurred yet; safe to exit without cleanup
