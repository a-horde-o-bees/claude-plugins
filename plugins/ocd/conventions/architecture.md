# Conventions Architecture

How the convention system discovers, matches, and loads file-type-specific guidance.

## Governance Infrastructure

Conventions and rules share a governance infrastructure implemented in the navigator skill package. The navigator database stores governance entries, their patterns, and their dependency relationships. Three database tables support this:

- **`governance`** — each entry's path, `matches` pattern, optional `excludes` pattern, and auto-loaded flag (rules = 1, conventions = 0)
- **`governs`** — directed edges from governor to governed, derived from `governed_by` frontmatter. Used by `governance_order` for topological evaluation ordering
- **`entries`** — the navigator's general file index; governance files appear here like any other file

## Registration Flow

`governance_load` scans `.claude/rules/` and `.claude/conventions/` for markdown files with governance frontmatter. For each file found:

1. Parse `matches`, `excludes`, and `governed_by` from YAML frontmatter
2. Insert or update the governance table with the file's path, patterns, and auto-loaded flag
3. For each `governed_by` entry, insert a `governs` edge (governor → governed)

Registration is idempotent — safe to rerun. Called during `/ocd-init` and can be triggered manually via the navigator CLI's `governance-load` command.

## Pattern Matching

`governance_match` is the runtime entry point. Given a list of file paths, it returns which conventions apply.

For each governance entry and each input file:

1. Normalize the governance entry's `matches` field into a list of fnmatch patterns
2. Test the file's **basename** against each pattern, and also the file's **full project-relative path**. Either matching is sufficient
3. If matched, check the `excludes` patterns the same way. If excluded, skip
4. Rules (auto_loaded = 1) are filtered out by default since they're already in agent context. Pass `include_rules=True` for governance evaluation workflows

The return value includes per-file matches and a deduplicated `conventions` list across all files.

## Loading Discipline

Conventions are not auto-loaded. The agent calls `governance_match` before creating or modifying files, reads the returned conventions, and follows them. This on-demand loading keeps session context focused — only guidance relevant to the current work is loaded.

The `governance_match` tool accepts batch input (multiple file paths). The agent should batch all target files in one call rather than calling per-file to avoid redundant lookups.

## Evaluation Ordering

`governance_order` returns a topological sort of all governance entries based on `governed_by` relationships. Level 0 entries have no governors; level N entries are governed only by levels 0..N-1. This ordering determines which conventions to evaluate first when checking conformity across the governance chain.

`governance_graph` returns the raw dependency edges, roots, and leaves for visualization.

## Template and Deployment

Convention files exist in two locations:

- **Templates** — `plugins/ocd/conventions/` in the plugin source
- **Deployed copies** — `.claude/conventions/` in the user's project

Edit deployed copies. The `sync-templates.py` script propagates deployed → template changes before commits. `/ocd-init` deploys templates to the project.

## Scan-Time Governance

During filesystem scans, the scanner also populates the `governs` table with file-to-governance relationships. For each non-governance file on disk, the scanner checks which governance entries match it and records the edge. This enables `governance_unclassified` to report files with no governance coverage.
