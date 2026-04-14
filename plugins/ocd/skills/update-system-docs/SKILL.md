---
name: update-system-docs
description: Maintain project documentation by deriving it from code reality. Canonical docs (README, architecture, CLAUDE, SKILL) are regenerated from a deterministic fact bundle with unverifiable prose ported over from the prior version; non-obvious surfaces (module and function docstrings, CLI help text, MCP tool descriptions, frontmatter descriptions, section purpose statements) use surgical edits. Whole-project scope, bottom-up traversal; git diff is the review gate, unresolved questions bubble up for user judgment.
argument-hint: "--target project"
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - mcp__plugin_ocd_navigator__*
---

# /update-system-docs

Maintain project documentation by deriving it from code reality. Canonical docs (README, architecture, CLAUDE, SKILL) are regenerated from a deterministic fact bundle with unverifiable prose ported over from the prior version; non-obvious surfaces (module and function docstrings, CLI help text, MCP tool descriptions, frontmatter descriptions, section purpose statements) use surgical edits. Whole-project scope, bottom-up traversal; git diff is the review gate, unresolved questions bubble up for user judgment.

## Process Model

Documentation is a consequence of reality. Rather than evaluating docs against reality and surfacing per-finding observations for user triage (the evaluate-* pattern), this skill updates docs in place. The evaluate pattern fits governance because governance changes require intent decisions; documentation changes are mostly consequence-of-reality, and per-finding gates produce fatigue. Git diff is the natural review gate; unresolved questions that require user judgment bubble up to the final Report.

Traversal is bottom-up in waves. Subagents in Claude Code cannot spawn further subagents, so recursive DFS is infeasible at the harness level; instead the skill executor drives wave-by-wave fan-out. Each wave spawns parallel per-system agents. Leaves run first — they have no children to wait on. Each agent writes a bubble-up summary to disk; the next wave's parent agents read those summaries to describe children without re-reading child code. Bottom-up is load-bearing per research (arXiv 2501.07857): LLMs materially drop content when summarizing aggregates, so parent descriptions built from persisted child summaries are the only reliable way to get full coverage at the top.

Canonical docs (README, architecture, CLAUDE, SKILL) are regenerated from the fact bundle on every run. Unverifiable prose from the prior version (motivation, external integrations, historical context, design rationale) is ported over by splicing into matching sections of the regenerated output. Regeneration produces more cohesive prose than incremental patching, and port-over preserves author intent. Non-obvious surfaces (module docstrings, function docstrings, CLI help text, MCP tool descriptions, frontmatter descriptions, section purpose statements) use surgical edits instead — single-entity regeneration has no coherence benefit.

Verification is conservative. Structural matching runs before LLM judgment wherever possible; LLM semantic equivalence skews toward false acceptance (Stanford SSP+24), so the skill biases toward false-alert over silent-pass. Claims whose subjects don't appear in the fact bundle pass through untouched (preserved for canonical docs via port-over, not processed for surfaces).

Architecture.md includes a Contents table — a derived projection listing each section with its purpose statement copied from the section's first paragraph. The table is regenerated on every run from a deterministic section scan; authors maintain section purposes, the skill maintains the table. Purpose statements apply at every scale per design-principles.md (documents, sections, modules, functions); section and function purposes are first-class surfaces.

Hash caching via navigator: each file's fact-bundle contribution and surface verifications are keyed by content hash. Re-runs skip unchanged files whose descendants also haven't changed, dramatically reducing token cost on stable codebases.

## Scope

Full project traversal. Systems discovered via navigator plus heuristics (plugin.json, Python package structure, MCP server layout, hook directory, library package). Skills are not systems per skill-md.md convention — their SKILL.md frontmatter descriptions are covered as non-obvious surfaces within the parent plugin's pass.

Accepted arguments:

- `--target` — required; must be `project`

## Rules

- Structural match before LLM judgment — use fact bundle equality where possible, reserve LLM for abstraction-level claims
- Surgical edits only — Edit tool with exact `doc_excerpt` as `old_string`; never whole-file rewrite
- Unverifiable prose preserved — claims outside the fact bundle's coverage (external integrations, rationale, non-observable properties) pass through untouched
- Required doc creation follows system-documentation.md triggers — README and architecture.md for every system; CLAUDE.md only when agent-facing procedures exist
- Bias toward false-alert over silent-pass — Clover shows LLM semantic equivalence has acceptance-skew; the skill surfaces questionable matches rather than letting stale claims slip

## Route

1. If not --target: Exit to caller — respond with skill description and argument-hint
2. If {target} is not `project`: Exit to caller — v1 supports whole-project only
3. Discover systems — bash: enumerate via `${CLAUDE_PLUGIN_ROOT}/run.py update_system_docs.cli discover --json`
4. If discovery fails: surface error and command to user
5. {systems} = systems list from result
6. {waves} = DAG grouped by depth — leaves are wave 0, roots last
7. Present system map to user — system count, wave structure, file counts per system — confirm
8. {run-id} = `${CLAUDE_SESSION_ID}-$(date +%s)`
9. Create scratch dir: bash: `mkdir -p ${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}`
10. Dispatch Workflow

## Workflow

1. {current-wave} = 0
2. For each {system} in {waves}[{current-wave}]:
    1. {child-pointers} = paths to prior-wave summaries for {system}'s direct children
    2. async Spawn:
        1. Call: `${CLAUDE_PLUGIN_ROOT}/skills/update-system-docs/_per-system-workflow.md`
            - {system} = {system}
            - {child-pointers} = {child-pointers}
            - {run-id} = {run-id}
        2. Return:
            - Summary pointer path
            - Short status: docs regenerated / created / unchanged; surfaces touched; unresolved count
3. Collect wave results
4. Present wave status to user — "Wave {current-wave}/{max-wave} complete"
5. {current-wave} = {current-wave} + 1
6. If {current-wave} <= max wave index: Go to step 2
7. Read root-wave summary and gather aggregated unresolved list
8. Present Report
9. bash: `rm -rf ${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}` — clean up scratch on success

### Report

- **Systems processed** — count per wave, total
- **Canonical docs regenerated** — grouped by kind (README, architecture.md, CLAUDE.md, SKILL.md); full path list with port-over-candidate counts
- **Canonical docs created** — grouped by kind; full path list
- **Canonical docs unchanged** — count (via hash cache; expected majority on stable projects)
- **Non-obvious surfaces** — grouped by surface type (module-docstring, function-docstring, cli-help, tool-description, frontmatter-description, section-purpose): updated / created / verified / total counts
- **Unverifiable prose preserved** — count of port-overs applied; flag port-overs that landed in "Notes" (no matching regenerated section)
- **Unresolved questions** — full list bubbled up from all systems; each with context, question, and scope-needed-to-resolve
- **Status** — `clean` (no changes), `updated` (changes applied), `partial failure at {system}` (if any wave had a failure)
- **Non-obvious surfaces touched** — grouped by surface type (cli-help, docstring, tool-description, frontmatter); counts
- **Preserved unverifiable prose** — count of claims classified unverifiable per system, for user to sanity-check the classifier
- **Status** — `clean` (no changes), `updated` (changes applied), `partial failure at {system}` (if any wave had a failure)

## Error Handling

1. If discovery CLI fails: surface error and command to user for manual debugging; do not proceed
2. If a per-system agent fails within a wave:
    1. Preserve scratch dir `${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/` for inspection
    2. Skip parent-wave processing for that system's parent subtree (parents depend on children summaries)
    3. Continue other subtrees
    4. Report partial failure in final Report
3. If user interrupts mid-run: scratch dir is preserved; next run with same session id can resume by detecting existing pointers (future enhancement)
