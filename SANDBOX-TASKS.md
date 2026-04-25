# Sandbox: ocd/audit-static

Lock down the `/ocd:audit-static` skill — verify positional argument resolution across every input form, then self-audit once stable.

## Pointers

- (none captured during migration)

## Tasks

- [ ] Verify positional argument resolution for every input form (slash-qualified skill, filesystem path, SKILL.md path); exercise on representative targets and triage observations
- [ ] Self-audit once stable
- [ ] Add subsystem-path resolution or document the full-path requirement: `/ocd:audit-static` cannot resolve bare subsystem paths like `systems/navigator/server.py` (correct form from repo root is `plugins/ocd/systems/navigator/server.py`)

## Open Questions

- (none yet)
