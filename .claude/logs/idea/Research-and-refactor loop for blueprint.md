# Research-and-refactor loop for blueprint

Candidate capability for the blueprint plugin — a disciplined loop that takes a design goal and produces a project that matches ecosystem convention, not an invented variant of it.

## Motivation

While writing the `claude-marketplace.md` pattern and implementing against it, we diverged from the actual ecosystem convention (invented a `marketplace.stable.json` filename that no real plugin uses). The divergence only surfaced after a user cross-check forced re-examination of the raw docs and real repos. A loop that encodes the right discipline would prevent this class of mistake.

## Proposed loop

1. Establish design goal
2. Research common and correct implementations
3. Build design documentation capturing the findings
4. Refactor the project to match the documentation
5. Reevaluate current project vs the common implementations
6. If diverging: update documentation to fill gaps or correct mistakes; return to 4
7. If matching: done

## Failure modes to guard against

- **Ambiguous research filled with invention.** Step 2 research may return "X does dual channels" without specifying the mechanism. The loop must either force the research to produce citations to exemplar repos (with the mechanism detail visible), or surface the ambiguity so the design decision is made deliberately rather than by filling in a plausible-looking answer.
- **Self-validation at step 5.** If the same agent who wrote step 3 reevaluates at step 5, it anchors on its own reasoning. Step 5 must compare against external artifacts — actually install from an exemplar repo and observe behavior, not compare doc-to-doc.
- **Design decisions without rejected alternatives.** A pattern doc that claims "this is the convention" without naming the alternatives considered and why they were rejected gives step 5 nothing to cross-check. Every non-obvious design choice should carry its rejection reasoning.

## Where this fits

Blueprint is an in-development plugin without a shipped role yet. A research-and-refactor loop would fit as a top-level skill (e.g. `/blueprint:design-and-apply <goal>`) or as an enforcement discipline for `/blueprint:research` combined with a separate `/blueprint:apply` skill. Decision deferred to when blueprint's scope is settled.

## Prerequisites

- A way to require research to produce citations, not just claims (skill-level enforcement).
- A way to perform step 5 via install-from-exemplar-and-observe (may need sandbox integration: spin up a sibling project, install from the exemplar marketplace, inspect cache contents).
- A meta-convention for pattern docs requiring alternatives-and-rejection-reasons on non-obvious decisions — lower-friction precursor that captures part of the discipline before the full loop is built.

## Alternative considered

A meta-convention (`pattern-md.md`) alone, without the full loop. Forces pattern authors to capture rationale up front but doesn't verify against reality. Cheaper to build; would catch this specific class of mistake on future pattern writes but wouldn't help during implementation or when convention shifts.

The loop subsumes the convention — building the convention first as a stepping stone is reasonable.
