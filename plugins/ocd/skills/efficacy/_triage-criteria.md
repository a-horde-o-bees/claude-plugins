# Triage Criteria

Classifies evaluation findings for Auto workflow. Orchestrator applies these criteria to each finding from evaluation agent report.

Straightforward — fix is deterministic from document and referenced conventions; no new design decisions or external context required:
- PFN notation errors
- Unbound or unassigned variables
- Missing flow control steps
- Wording that contradicts its own context
- Redundant content where duplication serves no distinct purpose
- Internal consistency (cross-references, terminology)

Complex — fix requires design decisions, new conventions, external context, or evaluator may be wrong:
- Structural changes to how workflows operate
- Changes to control flow within loops, STOP/EXIT paths, or variable scope across loop boundaries
- Issues that cascade beyond immediate file
- Issues where proposed fix conflicts with prior decisions
- Judgments about whether something is actually a problem
