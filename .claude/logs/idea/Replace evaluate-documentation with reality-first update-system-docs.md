# Replace evaluate-documentation with reality-first update-system-docs

**Priority: high**

## Purpose

Kill `evaluate-documentation` and replace with `update-system-docs`. Documentation is a consequence of reality, not a parallel artifact to validate. Rather than evaluating docs against reality and surfacing per-finding observations for user triage (the evaluate-* pattern), the new skill updates docs directly from observed reality and relies on git diff as the review gate. The evaluate → classify → user-apply cycle fits governance because governance changes require intent decisions; documentation changes are mostly consequence-of-reality, and per-finding user gates produce fatigue more than safety.

## Design Direction

- **Whole-project scope initially.** Per-system scope (`--target`) added once the whole-project traversal is producing the current system map correctly.
- **Correctness over token thriftiness.** Spawn agents as needed — per system, per deep sub-surface. Intelligent spawning is the accuracy lever.
- **DFS with context-aware-iteration, outward-in.** Traverse systems depth-first to leaves; leaf agents process their system completely and push a fixed-shape summary up to the caller; parent agents consume child summaries to update their own docs. Nothing re-reads a system that has already reported up. Matches the Nesting Discipline in `system-documentation.md` — parents describe children generically and link down; children describe themselves in detail.
- **Navigator for traversal.** Respects project exclusions without reinventing ignore logic; indexes paths by purpose.

## Scope of Documentation Surfaces

Not just README / architecture.md / CLAUDE.md / SKILL.md. Also:

- CLI help text
- Module docstrings (file-level `"""..."""`)
- MCP tool descriptions and FastMCP `instructions=` blocks
- Frontmatter `description:` fields on skills, rules, conventions
- Inline header purpose statements in rule/convention files

Supersedes `evaluate-documentation non-obvious surfaces.md` — same surface list, different mechanism (update rather than evaluate).

## Update Discipline

- **Remove content provably incorrect against reality.** Examples of provable: names/paths/files/functions/schemas that don't exist, invariants violated, signatures drifted.
- **Update content that's verifiable and stale** to match reality.
- **Leave alone anything not provably incorrect.** Unverifiable context (historical rationale, external integrations, constraints from outside the repo) survives. The category is narrow — most "purpose/capabilities" content is reality-extractable ("does X" is observable even if "built to solve X" is not).
- **Create missing docs when triggers exist.** README and architecture.md always for a system; CLAUDE.md only when the system has agent-facing procedures (per `system-documentation.md`).

## Key Design Work Before Implementation

1. **Provability criteria** as a shared component file applied by all agents — the definition of "grounded in examinable code/config/structure." Sharpens the update/leave-alone split. Also load-bearing for idempotence: fuzzy criteria → run-to-run drift.
2. **Bubble-up summary schema** — fixed shape each system agent returns to its caller: purpose statement, public interfaces, key internals the parent needs, doc artifacts updated, relative link targets. Lets parents write accurate generic-plus-link summaries without re-reading child code.
3. **System discovery heuristics** — `plugin.json` → plugin, package with `__main__.py`/explicit facade → system, MCP server package → system, hook script with own entry point → system, library package → system. Skills currently sit inside plugins as components; confirm whether they count as separate systems.
4. **Doc creation trigger logic** — detect the CLAUDE.md trigger from code structure, not unconditional creation.

## Risks

- **Write-heavy skill with no preview gate.** If provability criteria are fuzzy, the skill writes bad updates and relies on user noticing in `git diff`. Over-invest in the criteria definition upfront.
- **Cross-system references resolved at LCA.** Claim in navigator's docs about governance's match function is fixed in navigator's pass, after governance's summary has bubbled up. Architecture holds as long as each system's pass is single-shot with no re-entry.
- **Idempotence burden sits on provability criteria.** Second run on stable reality must produce zero diff.

## Blocks and Prerequisites

- Logging convention cleanup pending (separate work).
- System-documentation.md is now the authoritative rule — no re-explanation needed in the skill.
- Navigator's `paths_list` and related tools are the traversal substrate.
