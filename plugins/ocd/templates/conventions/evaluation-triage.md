---
includes: "*/evaluate-*/SKILL.md"
governed_by:
  - .claude/conventions/ocd/evaluation-skill-md.md
  - .claude/rules/ocd/markdown.md
  - .claude/rules/ocd/design-principles.md
---

# Evaluation Triage Criteria

Classification standard for evaluation skills. The skill executor classifies reported findings against this file before deciding what to auto-apply versus what to surface to the user. Evaluation agents never read this file — separation is enforced by file compartmentalization; this file is referenced only in the skill executor's workflow, not in agent component files.

## Classifications

- **Defect** — auto-fix; fix is deterministic, evaluator has verified intent is preserved, and the fix does not change what the target communicates or how it controls execution
- **Observation** — report to user; requires judgment, may be intentional, or evaluator is unsure of intent

## Escalation Rules

Reclassify a Defect as Observation when any of the following hold:

- Fix would change control flow in loops, break conditions, or exit-to-user paths
- Fix would change variable scope across loop boundaries
- Fix would alter what a rule or convention prescribes — any semantic change to governance
- Fix requires choosing between multiple valid alternatives
- Evaluator cannot determine original intent with confidence

## Cross-Concern Interactions

When two findings against the same file conflict — one finding's fix would undo or interfere with another's — both findings are reported as Observations and neither is auto-applied. The skill executor surfaces both with their proposed fixes so the user can choose which to accept.
