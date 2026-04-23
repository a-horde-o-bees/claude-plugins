# Alignment Audit

Methodology for comparing a repository's implementation against an observed-conventions research pattern and producing a classified record of where the repo aligns, diverges with justification, or has open work to close the gap. Produces a working artifact (the audit itself) that graduates into a standards doc once the landscape is stable.

## When to use

Produce an alignment audit when:

- A research pattern doc lands (a new purpose-organized study of an ecosystem's observed conventions) and the repo's current state needs to be classified against it.
- An existing pattern doc refreshes with new research waves and the repo's alignment may have drifted.
- Release prep reaches a gate where "are we aligned with ecosystem norms?" is a release-readiness question.
- A major refactor crosses enough surfaces that the alignment delta is worth recording before the next pattern-doc refresh.

Do not produce an alignment audit as a proxy for a standards doc. The audit is the *working artifact*; the standards doc is the *commitment statement*. See *Lifecycle* for how one graduates into the other.

## Inputs

- A research pattern doc organized by purpose (e.g. `claude-marketplace.md`). Each purpose carries observed paths, adoption counts, ★ docs-prescribed markers, and pitfalls.
- The repository being audited — the implementation under comparison.
- Prior audits, if any — to track which items were previously classified and what shifted.

## Artifact shape

The audit file mirrors the pattern doc's purpose structure one-to-one. For every `### Purpose` in the pattern doc, the audit has a `## Purpose` section (the audit's top-level organization, since its purposes aren't nested under a Purposes umbrella).

Per-purpose content is short — no ecosystem encyclopedia, no observed-path enumeration. Three fields, all concise:

- **Chosen path** — what the repo currently does for this purpose. One or two sentences. Concrete — name the file, the shape, the mechanism.
- **Convention match** — one classification symbol from the table below, with a brief citation of the matching cohort (e.g. "✓ Dominant — 14/18").
- **Gap** — if the match is anything other than ✓ or —, what closing it would require, stated as actionable work rather than prose.

Purposes that don't apply to the repo (single-plugin marketplace → multi-plugin purposes absent; no agents shipped → agent-delegation purpose absent) get a one-line "— Not applicable" with a brief reason. Do not omit the section — a reader comparing the audit to the pattern doc should see every purpose accounted for.

## Classification symbols

| Symbol | Meaning |
|---|---|
| ✓ | Dominant — implementation matches the ecosystem's prevailing path for this purpose |
| ⟁ | Partial or outlier-but-defensible — minority pattern with specific justification recorded in the audit |
| ✗ | Outlier requiring action — diverges from convention without current justification; closing the gap is an action item |
| — | Not applicable — this purpose doesn't apply to the repo (with brief reason) |

A ✓ needs no defense. A ⟁ needs a written justification so a future reader understands why the minority path was deliberate. A ✗ implies open work — either close the gap or promote to ⟁ by writing justification. A — signals structural non-applicability, not an unanswered question.

## Summary sections

Append these at the end, after all purpose sections:

- **Action-item summary** — three sub-lists:
  - **Resolved** — items that were ✗ in a prior audit but now ✓ or ⟁. Kept as history so the trail of closed work survives.
  - **Dropped** — items that were ✗ but withdrew from actionable status (pattern-doc correction, priority reassessment, etc.). Record the reason.
  - **Open** — items currently ✗ with their gap description. Graduate these out to roadmap or idea logs as they're scheduled or deferred.
- **Novel-but-defensible choices** — a consolidated list of ⟁ items with their justification. Serves as the repo's public record of deliberate deviation from convention.

## Lifecycle

An alignment audit has four phases:

1. **Authored** when a pattern doc first lands (or significantly refreshes). Every purpose gets classified. Gaps become action items.
2. **Working** — Open items are scheduled (commit, refactor, idea log). As they close, they move from Open to Resolved. Research may refresh the pattern doc; re-audit the affected purposes.
3. **Graduated** — when the Open list is empty and the repo's alignment is stable, the Chosen-path content extracts into a standards doc (see *Standards vs audit*). The audit's comparative structure (match symbols, gap fields) falls away; the commitments remain.
4. **Retired** — once the standards doc has absorbed the audit's content and the roadmap has absorbed any remaining outstanding items, the audit file is removed. Git history preserves the comparison trail; the standards doc carries the commitments forward.

## Standards vs audit

An audit answers "where do we diverge, and what do we do about each divergence?" It's structured as comparison — Chosen path + match symbol + gap. It evolves as gaps close.

A standards doc answers "what do we do?" It's structured as commitment — Standard + Why. It evolves only when the commitment changes.

The audit graduates into the standards doc by lifting every ✓ and ⟁ Chosen-path bullet into a Standard. The match symbols drop away. The Why lines come from the ⟁ justifications and the pattern doc's rationale. Open items don't graduate — they migrate to the roadmap as scheduled work.

Keep both docs simultaneously when the repo is still settling; retire the audit once standards are stable. Trying to maintain a single doc that does both jobs produces a doc that serves neither well — the comparison fields clutter the commitment statement, and the commitment statement crowds out the comparison detail.

## Filename and location

- Audit file: project-root lowercase filename, typically named `<pattern-name>--diff.md` (e.g. `claude-marketplace--diff.md`). Lowercase because it's a working artifact, not an entry point (per the Filename Case rule in `rules/system-docs.md`).
- Standards file that graduates from it: project-root all-caps filename, typically named `<PATTERN>-STANDARDS.md` (e.g. `MARKETPLACE-STANDARDS.md`).
- Research pattern doc: lives under `plugins/<plugin>/systems/patterns/templates/<pattern-name>.md`, deployed to `.claude/patterns/<plugin>/<pattern-name>.md` via auto-init.

## Sibling concerns

- **Pattern research** is a separate discipline — the research doc is the input to an alignment audit, not part of it. Refreshing the research is its own workflow (surveys, sampling, corpus walks).
- **Standards** are the output of a completed audit. Audits produce the commitments; standards docs own them.
- **Roadmap migration** — any Open item that isn't going to close in the current audit cycle migrates to the project's roadmap or idea logs. The audit is not a long-lived TODO list.

## Anti-patterns

- **Audit as TODO list.** The audit classifies every purpose, not just the ones with open work. Dropping ✓ purposes "because there's nothing to do about them" loses the record of intentional alignment and makes it impossible to see what changed when the pattern doc refreshes.
- **Audit without a pattern doc.** The audit's value comes from comparison against observed conventions. An audit authored against inferred-from-gut conventions is just a self-review.
- **Audit as permanent fixture.** Audits are working artifacts. If an audit lives for years without graduating, either the standards doc is missing or the alignment work never completes. Force the graduation.
- **Combining audit and standards in one doc.** The "Chosen path" in an audit can look like a standard, but the match symbol and gap structure make the doc unreadable as a commitment statement. Split them when the repo stabilizes.

## See also

- `rules/system-docs.md` — filename case convention (entry points vs working artifacts).
- `claude-marketplace.md` (pattern template) — example of an ecosystem research doc that an alignment audit would compare against.
- `MARKETPLACE-STANDARDS.md` at project root (once it exists) — example of a standards doc that graduated from an alignment audit.
