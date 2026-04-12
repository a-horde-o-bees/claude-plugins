# Evaluate-governance inversion technique from purpose-map

## Purpose

Add a structural soundness check to evaluate-governance by adopting purpose-map's failure-mode inversion technique.

## Context

Purpose-map's core evaluation move is: for each component, reverse-engineer what failure mode had to exist for this thing to be needed. This technique could strengthen evaluate-governance's holistic reading.

For each rule or convention being evaluated, the agent would:

1. Invert the governance entry — what specific failure mode had to exist for this to be written?
2. Check that the governance beneath it (its declared governors) actually supports preventing that failure mode
3. Flag when the dependency chain doesn't tell a coherent story — a convention that prevents failure X but whose governors don't establish the foundation X depends on, or worse, prescribe something that conflicts with preventing X

This goes beyond the current three concerns (conformance, friction, coherence) by adding a "does the dependency chain make structural sense as a failure-prevention story from foundations up?" check. Coherence catches contradictions between layers; inversion catches layers that don't justify themselves against what's beneath them.

Prerequisite: evaluate-governance would need to be redesigned (it's next on the state.md list after evaluate-skill). The inversion check could be a fourth concern held simultaneously, or it could be folded into the coherence stance with sharper guidance in _evaluation-criteria.md.
