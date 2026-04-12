# Conventions Architecture

How the convention system discovers, matches, and delivers file-type-specific guidance.

## Governance Infrastructure

Conventions and rules share a governance infrastructure implemented in the governance library (`lib/governance/`). The library reads directly from disk on every call — no database, no caching. It scans `.claude/rules/` and `.claude/conventions/` directories, parses YAML frontmatter from each governance file, and performs in-memory pattern matching via `matches_pattern` for basename, `**` prefix, and full-path modes.

## Pattern Matching

`governance_match` takes a list of file paths and returns the conventions that apply to each. For each convention file, it parses the frontmatter for include/exclude patterns, tests each input path against the normalized patterns, and groups results by file.

Rules are excluded from the match result by default because they are already in agent context. Passing `include_rules=True` adds every registered rule path to every file's match list — used by governance evaluation workflows where rules themselves are the evaluation target.

The return value includes per-file matches and a deduplicated `conventions` list across all files.

## Runtime Loading

Conventions are not auto-loaded. A convention gate hook (PreToolUse on Read/Edit/Write) surfaces applicable conventions via `additionalContext` on every file-touching tool call. Read invocations receive the conventions as informational context; Edit and Write invocations receive a directive to refactor immediately if the file does not conform.

The hook calls `governance_match` with the target file path and injects the matched convention paths into the tool-call context, so the agent sees exactly the governance that applies to the file it is about to touch — no manual lookup, no stale context across file boundaries.

## Evaluation Ordering

The `governed_by` frontmatter field declares which governance entries a convention builds on. It is consumed at evaluation time by skills that walk the governance dependency chain root-first — it is not consumed by runtime convention loading.

## Template and Deployment

Convention files exist in two locations:

- **Templates** — `plugins/ocd/conventions/` in the plugin source (flat, no subfolder)
- **Deployed copies** — `.claude/conventions/ocd/` in the user's project (per-plugin subfolder)

Edit deployed copies. The `sync-templates.py` script propagates deployed → template changes before commits. `/init` deploys templates to the project.

