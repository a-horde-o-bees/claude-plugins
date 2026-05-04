# Sample Population — Per-Entity Research

For each entity in the target list, capture observable facts about the entity's components and the purpose each serves. Output is one sample file per entity that the methodology's downstream phases consume.

The methodology derives the consolidated tree from these samples. The sample-population phase doesn't prescribe the consolidated's shape — it captures raw evidence at the right depth so downstream phases have something to synthesize.

## Variables

- {subject} — Research subject name
- {subtopic} — Optional grouping
- {entity} — One entity from the target list
- {research-objectives} — A flat checklist of dimensions to investigate per entity (subject-specific). For mcp: server runtime, transport, authentication, distribution channel, capability surface, deployment posture, repo layout, license, …

## Operating principles

**Functional decomposition is the goal — capture what each component IS and what purpose it serves, not the implementation details of how it works.** A 10-page transport-architecture explainer collapses to one short paragraph: "Streamable HTTP, single-tenant per process, OAuth-2.1 required for browser callback." Implementation depth happens later — ad-hoc, post-methodology, when the user implements their own version.

**Distinguishing variance, not exhaustive coverage.** Apply the "would this distinguish?" test to every fact: would this fact distinguish this sample from a hypothetical sibling that took a different path? "Has OAuth" fails (universally true of OAuth samples). "OAuth 2.1 + PKCE per-user, HTTP-only because browser callback can't reach stdio, 1-hour token TTL" passes (the constraints differentiate from OAuth-2.0-client-credentials samples).

**Capture proper nouns and version pins; skip prose.** Concrete distinguishing markers carry high information per byte: `FastMCP 2.x`, `@modelcontextprotocol/sdk`, AGPL-3.0, `--keep-connection`, `OAUTH_MODE=jwt`. Conceptual descriptions of well-known mechanisms carry low information; an OAuth flow diagram in a sample is noise.

**One short paragraph per component.** ~3-5 sentences per dimension. If a researcher needs more, either (a) cut implementation detail, or (b) split the dimension into multiple components. The first is research-discipline; the second is a methodology question — surface as a defer-marker.

**Defer-marker for "might matter."** When something could distinguish but the researcher can't tell from one entity's vantage point, leave a `↗` marker noting "deeper look pending Pass 2" rather than expanding inline. Pass 2 normalize and the depth pass resolve whether it was actually distinguishing.

**Cap-then-link, never inline external prose.** Long external documentation gets a link, not a transcription. The sample's job is the categorization-relevant delta — the consolidation phases never depend on prose imported from the entity's own docs.

**The research-objective checklist is flat.** Use a list of dimensions to investigate ("transport, auth, distribution, …") with no prescribed nesting. Per-sample structure is a thinking aid for the researcher, not a contract with downstream phases. Pass 2 normalize will rewrite samples to mirror the converged consolidated tree anyway, so initial structure is throwaway scaffolding.

> **Critical anti-pattern to avoid.** A nested heading-tree template (e.g., `## Transport > ### Wire protocol > #### Selection mechanism`) encourages researchers to keep filling deeper headings even when there's nothing distinguishing to say. The original mcp `_TEMPLATE.md` (now archived) functioned as both checklist AND schema, conflating the two roles. Keep the checklist flat; the structure is for downstream synthesis to determine.

## Process

1. For each {entity} in the target list:
    1. Investigate the dimensions in {research-objectives}
    2. Capture observable facts; leave gaps where evidence is unavailable
    3. Apply the "would this distinguish?" test to each fact
    4. Cap at one short paragraph per dimension; defer-mark anything that wants to expand
    5. Write to `logs/research/{subject}/{subtopic-or-discovered}-samples/{entity}.md`
    6. Verify with `plugins/ocd/bin/ocd-run log research check <sample-path>`

> **Default: sequential dispatch.** Each researcher (agent or human) handles one entity at a time. Sequential lets each researcher benefit from prior calibration data — what dimensions tend to surface, where defer-markers are commonly needed, what depth feels right. Batch-parallel is opt-in when wall-clock matters more than calibration consistency.

## Output

One sample file per entity at `logs/research/{subject}/{subtopic-or-discovered}-samples/{entity}.md`. Structure within each sample is loose — what matters is that the {research-objectives} dimensions were investigated. Pass 1 gather handles whatever shape emerges.

## Re-iteration

If `10-gap-audit` (run later, opt-in) identifies that a specific sample × dimension pair was researched too shallowly, that pair can be re-routed through this phase for targeted re-research. The researcher receives the gap-audit's specific scope (sample, dimension, what's missing) and updates the existing sample. Downstream phases re-run incrementally on the changed sample.
