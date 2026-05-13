# Rubric

> Shared discipline document for the rebuild skill. Loaded by the composer (forward direction: apply each pattern) and the verifier (backward direction: score against each pattern). All patterns apply in unison — no pattern is evaluated in isolation.

## Composition patterns

Patterns the composer applies during composition. The verifier scores whether the composed artifact reflects them.

### Anti-elision

- Discipline: every section, every line of the artifact appears in the output. No `...`, no `[unchanged]`, no implied continuation, no "see original".
- Failure signal: section header present with body missing; section absent that the extract names; truncation marker anywhere in the output.

### Authoritative spec

- Discipline: compose from the identity spec; do not reach for the original. The spec is treated as the complete truth; nothing outside it is consulted.
- Failure signal: phrasing in the fresh artifact that the spec does not justify but appears verbatim or near-verbatim in the original. Indicates original-context leak — either the composer reached for the original, or extracted content over-quoted it.

### Discipline in unison

- Discipline: every loaded rule applies to every section simultaneously. Section 1 reflects all disciplines; section 2 reflects all disciplines. Patches that apply rule A here and rule B there are patch-flow in disguise.
- Failure signal: selective rule application across sections — one section follows description-authoring discipline, another does not; one section is PFN-compliant, another is not.

## Identity-preservation criteria

Criteria the verifier enumerates. Failures here are identity defects (halt the rebuild).

### Callable surface

- Criterion: frontmatter name unchanged unless the user explicitly renamed; every declared variable from the extract appears with its declared shape; declared return shape appears in the fresh artifact.
- Failure: name changed without explicit instruction; variable missing; return shape altered.

### Declared rules

- Criterion: every rule from the extract's "Declared Rules" section appears in the fresh artifact. Phrasing may differ per discipline application; substance is preserved.
- Failure: rule dropped entirely; rule's semantic content changed (not just rephrased).

### Accumulated knowledge

- Criterion: every edge case, bug-fix crystallization, and special-case handling from the extract's "Accumulated Knowledge" section appears in the fresh artifact.
- Failure: edge case absent; workaround dropped because it "looked redundant" to the composer.

## Structural-change criteria

Criteria the verifier checks. Hits here are structural changes (gate on user approval).

### Section structure

- Criterion: section headings present in the original are present in the fresh artifact (possibly renamed if discipline calls for it; renaming is a structural change).
- Flag when: heading renamed; section split into multiple; sections merged.

### Schema or callable-surface shape

- Criterion: changes to variable shapes, return shape, or public interface contract are surfaced even when the names are preserved.
- Flag when: variable type changed; return adds or drops a field; interface contract narrowed or widened.

## Anti-patterns the verifier detects

These manifest as observations or identity defects depending on impact.

### Patch-flow leak

- Symptom: the fresh artifact's section ordering, prose rhythm, or sentence structure closely mirrors the original despite the composer not having access to it.
- Cause: memory leak from training-time exposure, or extract content that over-quoted the original.
- Verdict: observation by default (may be coincidental fit, may indicate spec-leakage to flag for next rebuild). Identity defect only if it correlates with another defect.

### Intent-word reinterpretation

- Symptom: rubric terms ("rebuild", "compose", "preserve identity") or composition-meta language appear in the fresh artifact's own text without being load-bearing for that artifact.
- Cause: composer absorbed the meta-frame into the artifact body.
- Verdict: observation.

### Spec-bypass invention

- Symptom: the fresh artifact contains content not in the extract — new sections, new rules, new variables, new disciplines applied.
- Cause: composer hallucinated additions, applied training-data priors, or filled gaps from its own context rather than the spec.
- Verdict: identity defect if it changes callable surface or declared rules; observation otherwise (but flag — indicates the spec was incomplete or the composer drifted).
