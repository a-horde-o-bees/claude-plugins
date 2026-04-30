# Sandbox: ocd/research-migration

Phase A of the research-corpus retrofit (mcp samples to heading-tree shape) landed; this branch now carries the structural migration that applies to both subjects: split each topic into a free-form `context/` collection, one or more `{subtopic}-samples/` folders (template-structured), a topic-root `RESEARCH.md` (cross-subtopic synthesis), and a topic-root `ANALYSIS.md` (user-facing takeaways). After mcp is migrated and re-synthesized under the new shape, marketplace gets the same Phase A retrofit and the same structural shape.

## Target structure

```
logs/research/{topic}/
    context/                   — free-form supporting sources (specs, docs, blogs, talks, papers,
                                 datasets, code references, threads); minimal frontmatter
                                 (source / captured / type / relevance), free-form body
    {subtopic}-samples/        — examples of the target; template-structured for cross-sample
                                 tallying. May be one folder; may be many when the research
                                 needs distinct paths of inquiry with different shapes
        _TEMPLATE.md           — canonical heading-tree shape for this subtopic
        _CONSOLIDATED.md       — heading-by-heading accumulation of supporting samples + notes;
                                 mirrors `_TEMPLATE.md`; same compliance contract as samples
        <sample files>
    RESEARCH.md                — agent-facing synthesis across all subtopics; form follows
                                 findings (not bound to any single template)
    ANALYSIS.md                — user-facing takeaways derived from RESEARCH.md
```

## Pointers

- `logs/patterns/sample-corpus-retrofit.md` — read-understand-rewrite-accumulate methodology used across both subjects. Composes with `context-aware-iteration` for batch sizing
- `logs/patterns/context-aware-iteration.md` — trailing-N ratio estimator is now the SOP
- `logs/research/_phase-a-agent-instructions.md` — generalized agent instructions; subject-agnostic. Points at the subject's `_TEMPLATE.md` for canonical vocabulary
- `logs/research/_phase-a-pick-batch.py` — picker; needs subject-parameterizing for marketplace
- `logs/research/_phase-a-mcp-archive/` — completed mcp Phase A artifacts: 10 batch YAMLs, log.csv, `_synthesis.yaml` (per-section aggregation that seeds the from-scratch `repos-samples/_CONSOLIDATED.md`)
- `logs/research/_lessons-from-mcp-phase-a.md` — methodology lessons from the mcp run, applicable to marketplace
- `logs/research/mcp/samples/_TEMPLATE.md` — canonical mcp sample shape (renames to `repos-samples/_TEMPLATE.md` during migration)
- `logs/research/mcp/consolidated.md` — current mcp synthesis; splits during migration: `## Decisions` block becomes sanity-check reference for the new `repos-samples/_CONSOLIDATED.md`; the rest seeds `ANALYSIS.md`
- `logs/research/mcp/context/` — 40 reference-source captures; stays in place under new structure
- `logs/research/claude-marketplace/samples/_TEMPLATE.md` — old bullet-form template; needs revision after Phase A retrofit
- `plugins/ocd/systems/log/research/_compliance.py` — heading-tree-diff against template; recursive order check at every depth; will extend to `_CONSOLIDATED.md` checking
- `ocd-run log research compliance --subject <name>` — corpus audit verb

## Completed (this branch)

- mcp Phase A: 104 samples retrofit complete (10 batches, trailing-N=1.4 work-tok/byte)
- mcp Phase B template: heading-tree-as-spec; pitfalls optional; open-enumeration `<placeholder>` convention
- Compliance tooling in `plugins/ocd/systems/log/research/_compliance.py` (26 tests; CLI verb wired)
- Recursive sub-purpose order check — `_walk_order` traverses template + sample in parallel; `OrderViolation.chain_key` identifies parent context; `<placeholder>` parents skip order checks
- Sample-corpus-retrofit pattern extracted (main worktree, `logs/patterns/sample-corpus-retrofit.md`)
- Context-aware-iteration pattern updated with trailing-N as SOP (main worktree)
- mcp corpus mechanical sweep: section numbering stripped, empty pitfalls headings removed
- Verification sweep over batches 1–4 (late-rule retroactive application)
- Stale `logs/research/_scripts/` removed
- Audit: 104/104 mcp samples clean against template (no outliers, no order violations) under recursive check

## Pending

### A. Cross-cutting structural changes (apply once; both subjects benefit)

- [ ] Update log routing rule + research log template — describe new shape: `context/` (free-form), `{subtopic}-samples/` (template-structured), topic-root `RESEARCH.md` + `ANALYSIS.md`
- [ ] Author `logs/research/_context-template.md` — minimal frontmatter (`source`, `captured`, `type`, `relevance`), free-form body
- [ ] Extend compliance verb to check `_CONSOLIDATED.md` against `_TEMPLATE.md` (same contract as samples; `<placeholder>` skip applies naturally)

### B. mcp migration under new structure

- [ ] Structural migration — rename `samples/` → `repos-samples/`; retire `scripts/`; remove `context/_TEMPLATE.md` and `context/_INDEX.md` ceremony (existing files stay in place); split `consolidated.md` content (`## Decisions` block held for sanity-check reference, rest seeds `ANALYSIS.md`); skeleton `repos-samples/_CONSOLIDATED.md` matching `_TEMPLATE.md` headings; skeleton `RESEARCH.md`. Single commit, no agent spawns
- [ ] Author `repos-samples/_CONSOLIDATED.md` from scratch — per-section synthesis from `_phase-a-mcp-archive/_synthesis.yaml` + raw samples. ~18 agent batches (one per canonical section, excluding Python-specific). After all sections complete: sanity-check against the held `## Decisions` reference; flag divergences as either (a) findings the agent missed or (b) old claims the corpus doesn't support
- [ ] Author `RESEARCH.md` — cross-subtopic synthesis pulling repos-samples + context together; form follows findings
- [ ] Refresh `ANALYSIS.md` — from the migrated old consolidated.md content; update against new RESEARCH.md; prune unsupported claims

### C. Marketplace Phase A retrofit (54 samples)

Apply the locked sample-corpus-retrofit pattern. Methodology stable; marketplace vocabulary differs (Marketplace discoverability, Plugin source binding, Channel distribution, etc. — 18 numbered sections vs mcp's 20).

- [ ] Update `_phase-a-pick-batch.py` to subject-parameterize (currently hardcoded `SUBJECT = "mcp"`)
- [ ] Initialize fresh `_phase-a-claude-marketplace-log.csv` (mcp's archived under `_phase-a-mcp-archive/`)
- [ ] Calibration batch (3–5 samples covering shape variety)
- [ ] Iterate batches until queue empty (~3–5 batches at trailing-N from mcp)
- [ ] Verification sweep over early batches with any late rules
- [ ] Audit: `ocd-run log research compliance --subject claude-marketplace`
- [ ] Aggregate batch YAMLs into `_phase-b-claude-marketplace-synthesis.yaml`
- [ ] Author marketplace `_TEMPLATE.md` (heading-tree-as-spec) and re-run compliance

Estimated cost: ~3–5 agent batches at trailing-N=1.4 work-tok/byte. Marketplace samples are denser (more rich `- **Field**:` bullets per section), so ratio may rise during calibration.

### D. Marketplace migration under new structure

After C: same structural sequence as B against the marketplace corpus.

- [ ] Structural migration — `samples/` → `{subtopic}-samples/` (subtopic name TBD; likely `plugin-marketplaces-samples` or similar based on what the corpus turns out to be); split `consolidated.md`; create skeletons
- [ ] Author `{subtopic}-samples/_CONSOLIDATED.md` from scratch — per-section synthesis
- [ ] Author marketplace `RESEARCH.md`
- [ ] Refresh marketplace `ANALYSIS.md`

Sections B and D dominate context end-to-end and should not compete with other work. Each pending B-section synthesis is bounded (one canonical section across 104 samples fits in one agent context); the `_CONSOLIDATED.md` skeleton develops incrementally.

## Future phases (out of scope this branch)

- **Phase C/D from prior plan** — retire `logs/research/mcp/scripts/_retrofit_samples_to_template.py` (legacy bullet-form retrofit script). Folded into Section B's "retire `scripts/`" step on this branch
- **Generic retrofit engine** — promote per-subject retrofit scripts to a shared engine if the pattern emerges across more research subjects
- **Marketplace name auto-detection in `/checkpoint`** — currently hardcoded as `a-horde-o-bees`; could be parsed from `.claude-plugin/marketplace.json`. Surfaced during `/ocd:git checkpoint` extraction work
