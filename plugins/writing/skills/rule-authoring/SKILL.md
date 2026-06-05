---
name: rule-authoring
description: Use when authoring a rule, principle, or directive that governs agent behavior, so it triggers reliably rather than firing on the wrong cases or missing the right ones.
---

# Rule Authoring

A rule that governs agent behavior fires reliably only when it names a single mechanism at the right level — the underlying principle, not a downstream symptom. A rule that bundles two mechanisms, or hooks on a surface threshold, fires unreliably: the agent applies the wrong thing, misses the right one, or hesitates. Scope each rule to one mechanism and express it as its principle so it triggers sharply.

## Single mechanism

- A rule covering two failure modes through different mechanisms is two rules.
- A need that names two distinct concerns is two needs.
- A principle that bundles two **independent** disciplines is two principles. Disciplines are independent when each is coherent without the other — removing one doesn't leave the other incomplete. Two disciplines serving a shared umbrella concept live as case-bullets under one principle, not as separate principles.
- Independence test: "is principle A coherent without principle B?" If yes, separate them. If removing one leaves the other incomplete, they're facets of one umbrella — keep them together with sharp case-bullets.
- Different application moments of the same discipline produce different case-bullets, not different rules.
- Sharing a discipline does not justify sharing a rule; sharing a mechanism does.

## Right level — principle, not symptom

- When a draft rule gates on a number, count, or size: ask what fit question the number approximates, then express the rule in terms of that question.
- Use size, count, or cost as supplementary signals, never as the gate.
- A numeric threshold is a signal to look for the principle hiding behind it.
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
