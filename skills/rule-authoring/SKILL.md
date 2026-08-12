---
name: rule-authoring
description: Use when authoring a rule, principle, or directive that governs agent behavior — to raise the odds it binds on the right cases and stays quiet on the wrong ones.
---

# rule-authoring

Use when authoring a rule, principle, or directive that governs agent behavior — to raise the odds it binds on the right cases and stays quiet on the wrong ones.

A rule that governs agent behavior is retrieved, not obeyed: it competes for attention with everything else in context and fails silently when it loses. No wording makes a rule reliable — a guarantee comes only from mechanism. Author under that ceiling: enforce what must hold, then sharpen the wording of what remains.

## Enforce before wording

- When a miss has real cost, escalate past wording: a hook that injects the rule at the moment it applies, a gate that blocks the action until the condition holds, a consumer that fails visibly when the rule was skipped. The authored rule is the fallback for what no mechanism can catch — never the load-bearing layer.
- Compliance is measurable, not assumed: a should-trigger / should-not-trigger prompt set against a cold model turns "does this rule fire?" into a hit rate. A low rate marks the wording as the defect to strengthen — the executor was never given the meaning, only the words.

## One rule per mechanism

Sharing a discipline does not justify sharing a rule; sharing a mechanism does.

- A rule covering two failure modes through different mechanisms is two rules.
- A need that names two distinct concerns is two needs.
- A principle that bundles two **independent** disciplines is two principles. Test independence by asking "is principle A coherent without principle B?" — if each stands without the other, separate them; if removing one leaves the other incomplete, they are facets of one umbrella and live as case-bullets under a single principle.
- Different application moments of the same discipline produce different case-bullets, not different rules.

## Principle, not symptom

- When a draft rule gates on a number, count, or size: ask what fit question the number approximates, then express the rule in terms of that question. Use the number as a supplementary signal, never as the gate.
- A closed list of forms or cases is a symptom too — the agent treats it as the definition and lets through any instance the list didn't name (the disguise that evades the enumeration). State the principle that catches the open set; mark any cases illustrative (`e.g.`), never exhaustive.
- Before deferring to a symptom because it is "easier to apply": ask whether the principle is genuinely harder to recognize, or whether the symptom merely feels concrete because it is numeric.
- Compensate for lost mechanical specificity with concrete examples illustrating the principle in action.

Examples of principle vs symptom:

- **Extraction**: "consumer profile narrows" or "mixed access patterns" — not "exceeds 100 lines / 2,000 tokens"
- **Splitting a rule in two**: "names two distinct mechanisms" — not "covers more than one paragraph"
- **Component reuse**: "referenced from multiple places" — not "more than three callers"

## Self-carrying polarity

A rule carries its own polarity — prescribe or prohibit stated in the line, never inferred from the section heading. The heading names the cluster; sibling rules may supply the clarifying context that keeps a line compact, but neither supplies direction.

## When a rule backfires

- Fix a leaky or backfiring rule — one that misses the right case, or *licenses the behavior it forbids* — by sharpening its own line, never by stacking a second rule to guard the first; the stack compounds (concise-prose § Correction).
- A carve-out that shields content from a cutting rule must gate on what *qualifies* the content, never read as "keep it" or "add it" — ungated, the exception inverts the rule into a mandate to produce the very content the rule bounds.
