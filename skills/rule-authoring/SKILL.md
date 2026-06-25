---
name: rule-authoring
description: Use when authoring a rule, principle, or directive that governs agent behavior, so it triggers reliably rather than firing on the wrong cases or missing the right ones.
---

# rule-authoring

A rule that governs agent behavior fires reliably only when it names a single mechanism at the right level — the underlying principle, not a downstream symptom. A rule that bundles two mechanisms, or hooks on a surface threshold, fires unreliably: the agent applies the wrong thing, misses the right one, or hesitates. Scope each rule to one mechanism and express it as its principle so it triggers sharply.

## Single mechanism

- A rule covering two failure modes through different mechanisms is two rules.
- A need that names two distinct concerns is two needs.
- A principle that bundles two **independent** disciplines is two principles. Test independence by asking "is principle A coherent without principle B?" — if each stands without the other, separate them; if removing one leaves the other incomplete, they're facets of one umbrella and live as case-bullets under a single principle, not as separate principles.
- Different application moments of the same discipline produce different case-bullets, not different rules.
- Sharing a discipline does not justify sharing a rule; sharing a mechanism does.

## Right level — principle, not symptom

- When a draft rule gates on a number, count, or size: ask what fit question the number approximates, then express the rule in terms of that question. Use the number as a supplementary signal, never as the gate.
- A closed list of forms or cases is a symptom too — the agent treats it as the definition and lets through any instance the list didn't name (the disguise that evades the enumeration). State the principle that catches the open set; mark any cases illustrative (`e.g.`), never exhaustive.
- Fix a leaky or backfiring rule — one that misses the right case, or *licenses the behavior it forbids* — by sharpening its own line, never by stacking a second rule to guard the first; the stack compounds (`/concise-prose` § Correction).
- A carve-out that shields content from a cutting rule must gate on what *qualifies* the content, never read as "keep it" or "add it" — ungated, the exception inverts the rule into a mandate to produce the very content the rule bounds.
- Compensate for lost mechanical specificity with concrete examples illustrating the principle in action.
- Before deferring to a symptom because it is "easier to apply": ask whether the principle is genuinely harder to recognize, or whether the symptom merely feels concrete because it is numeric.

Examples of principle vs symptom:

- **Extraction**: "consumer profile narrows" or "mixed access patterns" — not "exceeds 100 lines / 2,000 tokens"
- **Splitting a rule in two**: "names two distinct mechanisms" — not "covers more than one paragraph"
- **Component reuse**: "referenced from multiple places" — not "more than three callers"

## Self-carrying polarity

- A rule carries its own polarity — prescribe or prohibit stated in the line, never inferred from the section heading. The heading names the cluster; the rule states the direction.
- A rule may lean on sibling rules for clarifying context, staying compact — but never on the heading to signal whether it prescribes or prohibits.

## When a rule is missed

- When a rule should have triggered but did not: surface which rule was missed and what should have happened; proceed after the user acknowledges.
