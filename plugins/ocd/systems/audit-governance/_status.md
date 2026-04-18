# In-Flight Status: ocd/audit-governance

Notes migrated from `purpose-map/state.md` when this system was boxed. Accumulates further work as development continues on this branch.

## Open Work

- [ ] Exercise on the full governance chain end-to-end; triage observations; decide whether the `_audit-workflow-A.md` vs `_audit-workflow-B.md` A/B is still live or can collapse to one
- [ ] Self-audit via audit-static once both skills are stable

## Migrated Note: purpose-map/state.md (sandbox findings)

- [ ] **`/ocd:audit-governance` silently accepts undefined `--target`.** SKILL.md argument surface is "none — operates on current project," but passing `--target project` did not reject or warn. Tighten argument validation or document the accepted form explicitly.
