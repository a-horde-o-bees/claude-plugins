# Bubble-Up Summary Schema

Fixed shape each per-system agent writes to `${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/{system-path}/summary.md` and returns a pointer to. Parents read the summary's header sections to populate "describe children generically and link down" text without re-reading child code. Unresolved questions bubble up through parents to the final Report.

## File Location

Nested under run-id by system path:

```
${CLAUDE_PLUGIN_DATA}/update-system-docs/{run-id}/{system-path}/summary.md
```

Example: `${CLAUDE_PLUGIN_DATA}/update-system-docs/1234abc/plugins/ocd/lib/governance/summary.md`

## Schema

```markdown
# System: {path}

## Metadata

- Kind: {plugin | mcp-server | hook-system | library | framework | skill | project-root}
- Purpose: {one-line purpose statement — SSoT with README H1 paragraph and architecture.md H1 paragraph}
- Wave: {wave-index}

## Docs

- Canonical docs present: [list of paths]
- Canonical docs regenerated: [list of paths with port-over-candidate count]
- Canonical docs created: [list of paths]
- Canonical docs unchanged: [list of paths with hash markers]

## Public Interfaces

{one bullet per fact bundle public symbol; parent uses these for dependency descriptions}

- {name} ({kind}): {short signature or summary} — {file:line}

## Subsystems

{one bullet per direct child system, with pointer}

- {child-system-path} ({child-kind}): {child-purpose} — summary: {child-summary-pointer}

## Non-Obvious Surfaces Touched

{grouped by surface type}

- Module docstrings: {updated-count} / {created-count} / {verified-count} / {total}
- Function/method docstrings: {updated-count} / {created-count} / {verified-count} / {total}
- CLI help text: {updated-count} / {total}
- MCP tool descriptions: {updated-count} / {total}
- Frontmatter descriptions: {updated-count} / {total}
- Header purpose statements: {updated-count} / {total}
- Section purpose statements: {updated-count} / {total}

## Unresolved

{list of questions the agent could not resolve within its scope, for bubble-up}

- {question-id}: {one-line summary}
  - Context: {where it arose — file:location or section}
  - Question: {what the agent could not determine}
  - Scope-needed-to-resolve: {e.g., "parent system", "sibling system X", "user judgment"}

## Unverifiable Prose Preserved

{optional; list of port-over candidates surviving regeneration}

- [{doc-path} > {section}]: {one-line summary of content preserved}

## Hash Markers

{file-hash snapshot for re-run optimization}

- {file-path}: {content-hash}

## Run Status

- Contradicted claims: {count}
- Partial claims: {count}
- No-evidence claims: {count}
- Edits applied: {count}
- Edits failed: {count}
- Generation failures: {count}
- Port-over applied: {count}
```

## Parent Consumption

Parent agents read:

- **Metadata.Purpose** — populate "X subsystem: {purpose}" in parent's architecture.md Components section
- **Metadata.Kind** — classify child in parent's descriptions
- **Public Interfaces** — describe "depends on X's {function} for Y" in parent architecture when imports-graph shows a dependency
- **Subsystems** — for transitively building parent's nested description (direct children only; grandchildren summarized by their own parents)
- **Unresolved** — examine each entry; resolve any whose scope-needed is now in parent context; forward remainder with added parent context

Parents do NOT read the rest — detail stays in the child summary for audit and debugging.

## Unresolved-Question Bubbling

Each per-system agent writes `unresolved` entries for:

- Claims with `no-evidence` verdict that don't clearly fit unverifiable-prose
- Sections without a well-formed purpose statement (for Contents table)
- Ambiguous surgical edits the retry loop couldn't uniquify
- Cross-system references to peers the agent can't see
- Missing docstrings on functions where the skill couldn't derive a sensible purpose statement

Parent agents receive child `unresolved` lists along with child summaries. For each child-unresolved:

```
1. If parent scope contains the information needed:
    1. Resolve it (write doc update, answer question, whatever applies)
    2. Drop from unresolved
2. Else:
    1. Annotate with parent context — why parent also can't resolve
    2. Forward to own unresolved list for grandparent / user
```

Project-root agent's final `unresolved` list lands in the skill's Report for user judgment.

## Size Budget

Target: Metadata + Public Interfaces + Subsystems sections combined under 500 words. Parent-readable sections stay tight. Non-Obvious Surfaces Touched, Unresolved, Hash Markers can be larger — only the executor and audit readers consume them.

## Validation

On agent completion, orchestrator validates:

```
1. Summary file exists at expected path
2. H1 matches "System: {path}"
3. Metadata section has all required fields
4. Public Interfaces section has one bullet per expected public symbol
5. Subsystems section has one bullet per direct child in DAG
6. Unresolved entries have all required fields (id, context, question, scope-needed)
```

Validation failure surfaces in the orchestrator's Report as "partial failure at {system}".
