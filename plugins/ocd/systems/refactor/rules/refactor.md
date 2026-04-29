---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Refactor Usage

When to reach for the `/ocd:refactor` skill versus manual `sed`, `Edit`, or regex sweeps for source transformations.

## Mass Transformations

Prefer `/ocd:refactor` when the change is "replace X with Y across many sites":

- Renaming a Python module, class, or function across a plugin or the project
- Moving a filesystem path with transitive references to update
- Any identifier rename touching more than a handful of files

The skill wraps a scan → plan → apply → verify → test workflow. Pre-scanning reveals the full surface before any edits, classification separates auto-handled identifiers from prose and string literals that need judgment, and AST-aware codemods prevent the false positives a regex sweep produces (e.g. rewriting `"plugin.json"` as a string when renaming the `plugin` module).

## Narrow Edits

Prefer `Edit` directly when the transformation is:

- A single-file change
- Fewer than five call sites, all visible in current context
- A semantic refactor that isn't mechanical substitution (e.g., extracting a function, changing a signature, introducing a wrapper)

The workflow overhead only pays off when the change is wide enough that manual edits risk missing a site or re-introducing a false positive.

## Anti-patterns

- Running `sed -i 's/X/Y/g'` without pre-scanning the categories — hits string literals, misses non-Python references, forces iterative test-fix loops to find what the regex missed
- Iterative identifier discovery — running multiple waves of substitutions because each wave finds patterns the prior didn't target; pre-classification turns three waves into one
- Regex for Python identifier renames when libcst is available — AST-aware tools know the difference between `import plugin` and `"plugin.json"`; regex does not
