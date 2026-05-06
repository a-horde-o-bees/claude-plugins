---
includes: "*"
---

# Single Source of Truth

One authoritative source for each concept. Derived artifacts validate against their source, not the reverse. When information appears in multiple places, one is the source and the others are projections — make the relationship explicit and the validation automatic.

- Templates are authoritative for file structure; product files conform
- Tool implementations are authoritative for business logic; instructions reference tools by name
- Describe current reality only; do not reference previous states, removed features, or change history
- Rules and conventions are living context, not immutable constraints — flag conflicts and evaluate which should yield; during normal execution, follow rules without re-litigating
- Scattered related content consolidates rather than repeating across locations — pick the canonical home and let other locations point at it (or remove the pointer entirely if the structure already implies the relationship)
- Duplicate logic or documentation signals a need to reorganize — the duplication is the symptom; the missing canonical source is the cause
