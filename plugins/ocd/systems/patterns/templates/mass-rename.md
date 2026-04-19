# Mass Rename

Rewrite every occurrence of a symbol, path, or pattern across a codebase in one coordinated pass. Pre-scan reveals the full surface before any edits, classification separates auto-handled cases from ones that need judgment, AST-aware tools catch false positives regex misses, and verification confirms a clean state before tests run.

## Pattern

```
1. {scope} = directory tree to transform (plugin root, system directory, or specific glob)
2. {old} = current form to replace
3. {new} = target form

> Pre-scan: build the full worklist before any edits. Classification in step 4 cannot be correct without an exhaustive inventory.

4. For each context, enumerate occurrences:
    - bash: `grep -rln "\b{old}\b" {scope}` — file list with any occurrence
    - bash: `grep -rn "\b{old}\b" {scope} --include='*.py'` — Python-only, with line numbers
    - bash: `grep -rn "'{old}'\\|\"{old}\"" {scope}` — string-literal occurrences (quoted form)

> Classify each hit by context. A regex sweep on `{old}` would rewrite all of them indiscriminately; classification separates the ones that truly need transformation from incidental matches.

5. Classify findings:
    - **identifier** — Python imports (`import {old}`, `from {old} import`), attribute access (`{old}.attr`), function/class definitions. AST-aware rename handles these cleanly
    - **path-string** — filesystem paths containing {old} as a segment (`plugins/{old}/...`). Substitute via sed or Edit
    - **filename-literal** — string constants like `"{old}.json"` where `{old}` is coincidentally a literal segment. **Leave** — substituting changes runtime behavior
    - **prose** — README, architecture, docs, comments. Decide per-item: edit to reflect current state, or leave as historical mention

> Plan confirmation: present the classified plan and wait for user approval. Surprises during apply cost more than the confirmation prompt.

6. Present plan to user — per-category counts, full lists, proposed disposition for interactive categories
7. AskUserQuestion with options: `["Proceed", "Adjust", "Cancel"]`
8. If cancel: Exit to user: mass rename cancelled
9. If adjust: take refinements, update plan, Go to step 6. Present plan

> Apply: run the right tool for each category. AST-aware tools prevent the false-positive that doomed the ad-hoc sed approach. Regex is the fallback for categories where no AST tool applies (prose, non-Python files, path strings).

10. Apply transformations:
    - **identifier** (Python): bash: `ocd-run refactor rename-symbol --from {old} --to {new} --scope {scope}` — libcst parses each file, skips string literals and comments, rewrites imports and attribute access
    - **path-string**: apply sed or Edit per site. Exclude filename-literal false-positives that incidentally match
    - **prose**: apply Edit per item the user approved

> Verify: re-run the pre-scan. Remaining occurrences must match the documented exceptions (filename literals, leave-overridden prose). Unexpected hits mean a category was missed.

11. Re-scan with the same `grep` calls from step 4
12. {remaining} = re-scan output minus the documented exceptions from classification
13. If {remaining} is non-empty: Exit to user:
    - unexpected occurrences of `{old}` remain after apply
    - {remaining}
    - re-classify and re-invoke

> Test: hand off to the test runner in an isolated worktree. Failures here should expose runtime issues (path resolution, attribute lookup), not missed renames.

14. Exit to user:
    - Total files rewritten, per-category counts
    - Next step: `/ocd:sandbox tests` to verify against a clean ref
```

## When to use

- Renaming a Python module across a plugin (`plugin` → `framework`)
- Moving a filesystem path (`plugins/foo/bar/` → `plugins/foo/baz/`) with transitive references
- Any transformation where the temptation is to run `sed -i` directly and fix test failures iteratively

## When NOT to use

- Single-file edits — use Edit directly
- Transformations with fewer than 5 call sites — surgical Edit is faster than the workflow overhead
- Semantic refactors that aren't "replace X with Y" (e.g., extracting a function, introducing a wrapper) — those need human judgment per site, not mechanical substitution

## Anti-patterns this prevents

- **Sed-and-discover cycles.** Running `sed 's/plugin/framework/g'` without pre-scanning the categories: hits string literals (`"plugin.json"` → `"framework.json"`, breaking the app), misses path-based references in non-Python files, forces iterative test-fix loops to find what regex missed
- **Iterative identifier discovery.** Running three waves of sed because each wave finds patterns the prior didn't target (`plugin.get_*`, then `plugin.deploy_*`, then `plugin.\w+`). Pre-classification with grep + naming every category upfront turns three waves into one
- **Depth-brittle path arithmetic.** File moves that change `__file__.parent.parent` depth — separate concern from mass rename. Prefer marker-anchor walks (see framework.get_plugin_root)
