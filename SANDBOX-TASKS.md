# Sandbox: ocd/audit-governance

Lock down the `/ocd:audit-governance` skill — exercise on the full governance chain, decide whether the A/B workflow split should collapse to one, then self-audit via `/ocd:audit-static` once stable.

## Pointers

- (none captured during migration)

## Tasks

- [ ] Exercise on the full governance chain end-to-end; triage observations; decide whether the `_audit-workflow-A.md` vs `_audit-workflow-B.md` A/B is still live or can collapse to one
- [ ] Self-audit via `/ocd:audit-static` once both skills are stable
- [ ] Tighten argument validation or document accepted form: `/ocd:audit-governance` silently accepts undefined `--target` (e.g. `--target project` did not reject or warn)

## Open Questions

- (none yet)
