# Triage Criteria

Shared classification system for evaluation findings. All evaluate-* skills reference this file.

## Classifications

- **Defect** — auto-fix; fix is deterministic, evaluator has verified intent is preserved, and the fix does not change what the target communicates or how it controls execution
- **Observation** — report to user; requires judgment, may be intentional, or evaluator is unsure of intent

## Escalation Rules

Reclassify a Defect as Observation when:
- Fix would change control flow in loops, Break loop, or Exit to user paths
- Fix would change variable scope across loop boundaries
- Fix would alter what a rule or convention prescribes (semantic change)
- Fix requires choosing between multiple valid alternatives
- Evaluator cannot determine original intent with confidence

## Cross-Lens Interactions

When a finding from one lens conflicts with a finding from another lens:
- Document both findings with their lens source
- Do not auto-fix either — classify the pair as an Observation
- Include both recommended actions so the user can choose
