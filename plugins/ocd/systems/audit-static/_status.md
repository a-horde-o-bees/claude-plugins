# In-Flight Status: ocd/audit-static

Notes migrated from `purpose-map/state.md` when this system was boxed. Accumulates further work as development continues on this branch.

## Open Work

### audit-static (in development)

Exists on main but isn't locked down. Manual convention audit during v0.1.0 prep surfaced residual issues. To finish:

- [ ] Verify positional argument resolution for every input form (slash-qualified skill, filesystem path, SKILL.md path); exercise on representative targets and triage observations
- [ ] Self-audit once stable

## Migrated Note: purpose-map/state.md (sandbox findings)

- [ ] **`/ocd:audit-static` cannot resolve bare subsystem paths.** `--target systems/navigator/server.py` hit the path-invalid exit because the correct path from repo root is `plugins/ocd/systems/navigator/server.py`. Either add subsystem-path resolution to the skill, or document the full-path requirement.
