---
includes: "*"
tagline: Completeness without verbosity — every word must earn its place
---

# Economy of Expression

Completeness without verbosity. Every word must earn its place — if removing a word or phrase does not change meaning, remove it. Complete does not mean verbose; missing information causes incorrect assumptions, but redundant information obscures intent.

- Include examples only when a rule is ambiguous without one
- Examples are generic — use concepts, not project-specific names
- Positive examples suffice — add counter-examples only when the rule is ambiguous without one
- Cross-references add maintenance burden — every pointer becomes a coupling that must be kept correct as either side evolves. Use them sparingly: each one earns its place against the future cost of keeping it accurate. The bar is highest in agent-facing artifacts (e.g., rules, principles, conventions) where the reader already has the full corpus loaded — explicit pointers between rules bloat without earning utility there. The bar is lower in user-facing documentation (e.g., READMEs, ARCHITECTURE files) where human readers do not carry the corpus in context, but sparing still applies. Coherence across artifacts is the responsibility of periodic holistic review, not mechanical pointer-everything-at-everything
