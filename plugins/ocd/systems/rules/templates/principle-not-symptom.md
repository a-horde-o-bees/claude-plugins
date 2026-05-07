---
includes: "*"
tagline: Trigger rules on the underlying principle, not a numeric or downstream symptom
---

# Principle, Not Symptom

When authoring a rule, convention, or extraction criterion, the trigger should be the underlying principle that drives the desired behavior, not a downstream symptom of the principle. Symptom-based rules feel concrete and easier to apply, but they fire in the wrong cases — small files with mixed concerns slip through; large files with appropriately bundled concerns get falsely flagged. A rule that names its principle stays applicable as the framework evolves; a rule pinned to a specific threshold needs recalibration when surrounding norms shift.

- When a draft criterion gates on a number, count, or size: ask what fit question the number is approximating, then express the rule in terms of the fit question
- Use size, count, or cost as supplementary signals or recognition aids, never as the gate itself
- When reviewing a rule that uses a numeric threshold: treat that as a signal to look for the principle hiding behind it
- Compensate for the loss of mechanical specificity with concrete examples that illustrate the principle in action
- Before deferring to a downstream symptom because it is "easier to apply": consider whether the principle is genuinely harder to recognize, or whether the symptom merely feels concrete because it is numeric

Examples of principle vs symptom in this framework:

- **Extraction**: "consumer profile narrows" or "mixed access patterns" — not "exceeds 100 lines / 2,000 tokens"
- **Splitting concepts into separate rules**: "names two distinct mechanisms" — not "covers more than one paragraph"
- **Component reuse**: "referenced from multiple places" — not "more than three callers"

Each principle-based criterion applies cleanly to small instances where mixed concerns matter just as well as to large ones, and avoids triggering on cases where the symptom is present but no real fit issue exists.
