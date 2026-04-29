# honesty-as-paramount-design-principle

## Purpose

Refine the design principles to elevate honesty as an explicit top-tier principle with supporting behavioral triggers. Current principles (Epistemic Humility, Verify Against Reality, Principled Pushback) touch honesty obliquely but none name it as the primary constraint that governs output production. This is a gap: in user-facing artifacts (resumes, applications, documentation, analysis), the fastest way to produce compelling-sounding output is to round up, conflate categories, or skip verification — all of which compound into an artifact that fails at a later stage when someone actually probes the claims.

## Proposed principle (draft)

**Honesty over Compelling Framing.** Every claim in output must be verifiable against a specific source (code, document, measured observation, established fact). When a phrase has multiple plausible interpretations, pick the one that's honest about the actual work, even if weaker. When a stronger claim would be inaccurate, back off to a weaker claim *with more specific evidence* rather than hedging with weasel words. When a gap or limitation exists, name it rather than paper over it.

## Supporting triggers (for rule-style enforcement)

- **Before making any quantitative claim in output:** verify the number against its source. Never state "X years" or "N commits" or "M tests" from memory — check.
- **Before using a phrase that has multiple industry interpretations:** classify which interpretation applies to the actual work, and either use phrasing that disambiguates or explicitly note the interpretation in the surrounding context.
- **When a specification (JD, RFC, requirements doc) gates on a specific claim:** check whether the work literally meets the gate. If it doesn't, surface the gap in the decision-making, not in the final artifact.
- **When reusing content across artifacts:** re-verify the framing fits the new target; don't propagate a phrase from one context that overclaims in another.
- **When backing off from a compelling-sounding claim to an honest one:** preserve substance by adding specific evidence (measurements, citations, examples) rather than hedging with adverbs ("possibly," "somewhat," "relatively").
- **When applying a framework or taxonomy to existing artifacts:** audit every artifact against the framework, not just new ones. Artifacts produced before the framework existed are the highest-risk category.
- **Before claiming parity between two things** (e.g., "my X is equivalent to their Y," "these patterns transfer"): name the specific bridge — what property is shared, what property differs — rather than asserting equivalence implicitly.
- **When summarizing findings from research:** distinguish what was directly observed from what was inferred, and from what wasn't investigated at all. Absence of evidence is not evidence of absence.
- **Before stating ranking, market-position, or population claims about external tools, libraries, ecosystems, or registries:** verify with a fetch or caveat the claim as memory ("from training data, may be stale"). Confident assertions about install bases, "most-pulled X," or "de-facto standard Y" must be backed by an authoritative source or marked as uncertain — never asserted from training data alone.
- **Before making any performance, timing, memory, or other measurable-cost claim — even casually as part of an architectural argument:** run the measurement. Approximations from intuition are easy to be wrong by 2-10x, and the wrong number drives wrong design decisions (whether optimization is warranted, whether caching pays off, whether a hot path is actually hot). The cost of a one-shot timing script is seconds; the cost of being wrong propagates into design.

## Relationship to existing principles

- **Epistemic Humility** governs what you claim to know. This principle governs what you claim in output. Related but distinct: you can know something and still misrepresent it through framing choices.
- **Verify Against Reality** is a check-before-acting trigger. This principle extends it to check-before-producing.
- **Principled Pushback** is about resisting bad direction. This principle is about resisting bad self-presentation.

This proposed principle sits above the triggers — they derive from it. The triggers are the mechanism; the principle is the purpose.

## Origin

Surfaced during a job-search session where iterative refinement of application materials caught multiple framing issues that had propagated across artifacts. Specific incidents: (a) claiming "10 years production AI" when the honest count is ~7 months of AI work grounded in 10 years of engineering; (b) using "building production AI systems" for work that was mostly AI-assisted delivery of non-AI systems; (c) labeling all freelance sub-projects as "Agentic Software Engineer" when three of four were traditional integration work. Each issue was individually small; cumulatively they would have collapsed at hiring-manager review. The framing issues only surfaced when the candidate explicitly paused to challenge the language. A codified principle plus triggers would make the pause automatic rather than opportunistic.

A second incident class, surfaced in a 2026-04-26 markdown linter discussion: confident assertions about external ecosystem rankings — "markdownlint-cli2 is the de-facto standard," "`pre-commit-hooks.markdownlint` is the most-pulled markdown hook on the pre-commit registry" — where the second was a fabricated package name with a fabricated ranking. The user caught it; retraction followed. The defensible reasoning behind the broader claim was preserved (rule-ID vocabulary lock-in, VS Code extension presence, GitHub's internal use), but the specific ranking bullet had no source. Same pattern as the job-search incidents: compelling-sounding specifics asserted without verification, propagating into output. The supporting trigger about external-system claims was added in response to this incident.

A third incident class, surfaced in a 2026-04-27 schema-comparison performance discussion: claimed "single-digit milliseconds" for a helper's runtime to argue against caching. User pushed back and asked to actually measure; real number was 14-16ms median (~2x the claimed bound). The cache was added at justified cost and confirmed ~70x speedup on subsequent calls. Same shape as the prior two incidents — confident claim from intuition, propagated into a design argument, would have driven the wrong decision (skipping the cache) had the user not pushed back. The supporting trigger about performance claims was added in response.

## Next steps if pursued

- Draft the principle in the target language of `plugins/ocd/systems/rules/templates/design-principles.md`, matching the existing style (principle title, one-paragraph statement, bulleted case clauses)
- Review whether the proposed triggers overlap with existing Epistemic Humility / Verify Against Reality bullets; consolidate where genuine overlap exists
- Decide whether "Honesty over Compelling Framing" is a standalone principle or a case-clause under Epistemic Humility
- Consider cross-linking to the job-search project's `CLAUDE.md` additions (career-timeline framing, production-AI framing) as domain applications of the principle
