# Triage Criteria

Maps evaluator classifications to Auto workflow actions. Evaluating agents classify each finding as Defect or Observation in their report.

- Defect — auto-fix; fix is deterministic and evaluator has verified intent is preserved
- Observation — report to user; requires judgment, may be intentional, or evaluator is unsure

Orchestrator rejects any Defect fix that would change control flow within loops, Break loop/Exit to user paths, or variable scope across loop boundaries — reclassify as Observation.
