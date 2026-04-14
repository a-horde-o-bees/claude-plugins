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

- `cli.py` → `__main__.py` cleanup (sibling problem entry) should land first — the discovery CLI for this skill would otherwise compound the convention violation.
- Logging convention cleanup (sibling problem entry) — independent but in the same backlog.
- System-documentation.md is now the authoritative rule — no re-explanation needed in the skill.
- Navigator's `paths_list` and related tools are the traversal substrate.

## Implementation Status (2026-04-14)

Skill scaffold committed in 986ddd2 — `plugins/ocd/skills/update-system-docs/` contains SKILL.md plus component files for claim extraction, verification, conservative editing, doc generation (with Contents table), unverifiable prose classification, summary schema (with bubble-up unresolved questions), system discovery, and non-obvious surfaces. `_DESIGN.md` captures the research-backed design and user decisions; `_DRY_RUN.md` captures the lib/governance walkthrough and which findings the user resolved how.

Major design refinements from research and user decisions:

- **Wave-by-wave fan-out, not recursive DFS** — Claude Code subagents cannot spawn subagents (harness constraint). Skill executor drives wave-by-wave; each wave's per-system agents persist summaries to `${CLAUDE_PLUGIN_DATA}` and parents read pointers.
- **Regeneration with port-over for canonical docs, surgical edits for non-obvious surfaces** — full regeneration produces more cohesive prose than incremental patching; surgical edits remain for docstrings/help/frontmatter where regeneration has no coherence benefit.
- **Architecture.md Contents table** — derived projection copying each section's first-paragraph purpose into a table after the H1. Skill owns regeneration.
- **Skills ARE systems** — SKILL.md always; architecture.md only when Document Separation rule would otherwise be violated. No arbitrary complexity trigger.
- **Function/method docstrings in scope** — heavy first-run cost mitigated by hash caching via navigator integration.
- **Unresolved questions bubble up** — anything a per-system agent can't resolve propagates through parents to the final Report for user judgment.
- **Multi-scale Purpose Statement guidance** — design-principles.md updated 986ddd2 to make explicit that purpose statements apply at every scale (document, section, module, function).

## Implementation Follow-ups

Pending implementation work, in dependency order:

1. **`cli.py` → `__main__.py` cleanup** — separate problem; lands first.
2. **Discovery CLI** — `plugins/ocd/skills/update-system-docs/__main__.py` + `_discovery.py`. Deterministic Python: enumerates systems via navigator + heuristics from `_system-discovery.md`, builds parent-child DAG, computes traversal waves, returns JSON. Subcommand `discover --json`.
3. **Fact-bundle builder** — Python module under the skill dir, called by per-system agents via bash. Walks system file inventory, ast-parses each `.py`, extracts module / function / class docstrings, signatures, imports, MCP tool definitions, CLI commands, manifests, frontmatter. Subcommand `fact-bundle --system <path> --child-pointers <list> --json`.
4. **Navigator schema extension for `doc_verified_at`** — adds a per-file content-hash + timestamp marker enabling re-run skip-on-unchanged. Separate navigator-side change. Skill v1 can ship without it and pay the full token cost per run; v1.1 adds caching.
5. **`mark-verified` CLI subcommand** — updates navigator's `doc_verified_at` markers after a per-system agent completes successfully.
6. **End-to-end test on lib/governance** — first real run; manual review of generated docs; calibrate prompts based on observed false-positives / false-negatives.
7. **Delete old `evaluate-documentation` skill** — once `update-system-docs` produces correct output for at least one full project run.

The skill scaffold's prompt templates (claim extraction, verification, conservative edit, doc generation) are designed but unproven — first real runs are the calibration phase.
