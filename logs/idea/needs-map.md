# needs-map — forward-looking work

Consolidated idea log for needs-map: unbuilt directions, applications of the underlying methodology beyond component justification, and integrations with other systems. Replaces the earlier per-direction logs (purpose-map reusable analysis tool, audit-governance inversion technique).

## Reusable analysis methodology

The analytical framework needs-map encodes — failure-mode framing, need/rationale split, reactive refinement, override-vs-description check, router-vs-destination check — has applicability beyond component auditing. The current tool is one SQLite-backed implementation; the methodology is the more reusable artifact.

Possible forms:

- **Migration validation** — apply failure-mode framing to validate each piece when moving or restructuring content. Does the destination still answer the same failure mode the origin did?
- **Middle-stage analysis** — any process evaluating "what does this actually contribute?" can use the framework as a middle stage. Pulled out of the component-graph implementation, the questions transfer.
- **Zoomable granularity** — works at file → section → bullet level. The questions don't depend on the size of the unit being evaluated.

Status: speculative. Flag for exploration once needs-map's own audit pass stabilizes.

## audit-governance inversion technique

Strengthen the future evaluate-governance skill by adopting needs-map's failure-mode inversion as a structural soundness check. For each rule or convention, the evaluator would:

1. Invert the entry — what specific failure mode had to exist for this to be written?
2. Check that the governance beneath it (its declared governors) actually supports preventing that failure mode
3. Flag dependency chains that don't tell a coherent story — a convention preventing failure X with governors that don't establish the foundation X depends on, or worse, governors that conflict with preventing X

This goes beyond conformance, friction, and coherence concerns by adding a "does the dependency chain make structural sense as a failure-prevention story from foundations up?" check. Coherence catches contradictions between layers; inversion catches layers that don't justify themselves against what's beneath them.

Prerequisite: evaluate-governance redesign (next on the existing roadmap after evaluate-skill). The inversion check could be a fourth concern held simultaneously, or folded into the coherence stance with sharper guidance.

## Open methodology items

Carried over from the prior `purpose-map/state.md` Methodology Status section.

- **Stale components in the live DB** — c41 (friction server), c42 (decisions server), c43 (stash server) were removed earlier in the v2 build-up. Needs n59 (friction signals) and n68 (ideas/observations) are now gaps. Rewire to the current file-based log system (no MCP server) when those components are formally evaluated.
