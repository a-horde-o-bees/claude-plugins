# evaluate-documentation Still on Old Lenses Model

evaluate-documentation SKILL.md uses the pre-redesign pattern: separate lens passes, agent-side triage, agent applies fixes directly.

The agent reads `evaluation-triage.md` and applies defects itself (lines 55-56, 80-81), violating the report-only agent architecture that evaluate-skill and evaluate-governance now follow. It also references `_lenses.md` instead of `_evaluation-workflow.md`.

Needs the same redesign evaluate-skill got (commit 7329acb): report-only agent, holistic reading, orchestrator-owned triage, `_evaluation-workflow.md` with prescribed section structure per evaluation-skill-md.md convention.
