# Target Selection — Subject Definition and Entity Scoping

The first phase of the methodology — define the research subject, identify the candidate population, and select a stratified cross-section to investigate. This phase produces an entity list that the next phase populates per-entity into the corpus the methodology consumes.

## Variables

- {subject} — Research subject (e.g., `mcp`, `marketplace`)
- {subtopic} — Optional grouping within a subject (e.g., for mcp: `repos`, for marketplace: `claude-marketplace`)
- {target-count} — Approximate corpus size; typically 50-150. Smaller corpora can be exhaustive; larger ones benefit from sampling
- {selection-criteria} — Diversity dimensions the corpus must cover (language, scale, governance, ecosystem, …) — drives stratification

## Operating principles

**Diverse over comprehensive.** A 100-entity corpus with broad diversity outperforms a 200-entity corpus biased toward popular entries. Diversity along the dimensions that matter for functional decomposition drives the consolidated tree's coverage; popularity bias produces overweighted central paths and missed long tails.

**Stratified, not random.** Sampling explicitly covers quadrants the subject exhibits. For mcp: vendor vs community, popular vs niche, Python vs JS vs Go vs Rust, hosted-service vs self-hosted, narrow-tool vs broad-tool. Random sampling overweights popular categories and misses long-tail patterns the methodology relies on.

**Capture rejections.** Entities considered but rejected are evidence for what the subject does *not* include. Maintain a rejection log with rationale so future passes can reconsider boundary cases without re-discovering why they were dropped.

**Boundary first, sample second.** Define the subject's boundary explicitly before scanning candidates. The boundary determines what gets sampled; ambiguous boundaries produce inconsistent samples that downstream phases can't reconcile.

## Process

1. **Define subject boundary** — what is in, what is out. Write down the inclusion criteria explicitly. The boundary determines the next steps' scope
2. **Enumerate candidate population** — typically a search query (GitHub, registries, catalogs) or curated list. Aim for completeness at the boundary; pruning to {target-count} happens via stratification
3. **Stratify candidates** along {selection-criteria}. Each stratum gets sampled independently
4. **Sample to {target-count}** — within each stratum, pick representative entities. Mix popular and obscure within each stratum to surface variance
5. **Record selected and rejected** entities with rationale. Selected entries become the input for `02-sample-population`. Rejected entries inform future expansions of the boundary

## Output

- An entity list at `logs/research/{subject}/{subtopic}-picker/_INDEX.md` (or similar — the location convention is the picker workflow's, not the methodology's)
- Per-stratum selection rationale documented
- Rejected entities preserved for traceability

## Notes for downstream phases

- The candidate list does not need to be fixed. If `02-sample-population` discovers that an entity is out of scope or duplicates another, it can be dropped. Conversely, if a Pass 1+ phase surfaces a category the corpus underrepresents, target selection can run again on that category and feed new entities back through `02`
- A picker workflow may be partially automated (search + filter) and partially curated (manual stratum balancing). The methodology doesn't prescribe automation — it prescribes diversity and traceability
