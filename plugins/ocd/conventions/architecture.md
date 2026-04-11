# Conventions Architecture

How the convention system discovers, matches, and delivers file-type-specific guidance.

## Governance Infrastructure

Conventions and rules share a governance infrastructure implemented in the navigator skill package. The navigator database separates the two along domain lines, with conventions normalized into include/exclude pattern tables:

- **`conventions`** — one row per convention file: `entry_path`, raw `matches` and `excludes` text, and `git_hash`
- **`convention_includes`** — one row per normalized include pattern, keyed by `entry_path` (CASCADE on delete)
- **`convention_excludes`** — one row per normalized exclude pattern, keyed by `entry_path` (CASCADE on delete)
- **`rules`** — one row per rule file: `entry_path` and `git_hash`. Rules carry no patterns because they apply universally
- **`entries`** — the navigator's general file index; governance files appear here like any other file

Patterns are stored exactly as written in frontmatter. The runtime performs matching through the custom `path_match(path, pattern)` SQL function, registered on every connection and delegating to `matches_pattern` for basename, `**` prefix, and full-path modes.

## Self-Refresh

Every governance query calls `_ensure_current` first, which reconciles the `rules` and `conventions` tables against disk state. Reconciliation compares each file's current `git_hash` against the stored hash and re-parses only changed files. Deleted files are removed; new files are inserted with their include and exclude patterns. This means callers never need to run a separate load step — queries always see current disk state.

`governance_load` is exposed as a standalone function for initialization flows and for the navigator CLI's `governance-load` command, but it runs the same reconciliation logic as `_ensure_current`.

## Pattern Matching

`governance_match` takes a list of file paths and returns the conventions that apply to each. The query joins files against `convention_includes` via `path_match`, anti-joins against `convention_excludes`, and groups results by file.

Rules are excluded from the match result by default because they are already in agent context. Passing `include_rules=True` adds every registered rule path to every file's match list — used by governance evaluation workflows where rules themselves are the evaluation target.

The return value includes per-file matches and a deduplicated `conventions` list across all files.

## Runtime Loading

Conventions are not auto-loaded. A convention gate hook (PreToolUse on Read/Edit/Write) surfaces applicable conventions via `additionalContext` on every file-touching tool call. Read invocations receive the conventions as informational context; Edit and Write invocations receive a directive to refactor immediately if the file does not conform.

The hook calls `governance_match` with the target file path and injects the matched convention paths into the tool-call context, so the agent sees exactly the governance that applies to the file it is about to touch — no manual lookup, no stale context across file boundaries.

## Evaluation Ordering

The `governed_by` frontmatter field declares which governance entries a convention builds on. It is consumed at evaluation time by skills that walk the governance dependency chain root-first — it is not consumed by runtime convention loading.

## Template and Deployment

Convention files exist in two locations:

- **Templates** — `plugins/ocd/conventions/` in the plugin source
- **Deployed copies** — `.claude/conventions/` in the user's project

Edit deployed copies. The `sync-templates.py` script propagates deployed → template changes before commits. `/ocd-init` deploys templates to the project.

## Unclassified Coverage

`governance_unclassified` reports file entries that no convention covers. The query excludes files registered as rules or conventions (those are governance files, not governed files), then filters out files matched by any `convention_includes` pattern that is not also blocked by a `convention_excludes` pattern. Results are grouped by file extension so gaps are actionable at the file-type level.
