# STATE

Working state for the markdown-authoring scope.

Snapshot (2026-07-23): no work in flight.

## Open decisions

- **Promote indent width to config?** Severity overrides cover most preference divergence, but a different `list-indent` width (e.g. 2-space nesting) currently requires shadowing the whole skill. Promoting it would add the first parameterized rule, against the recorded severity-only decision. Decide-at: the first real installer preference severity can't express.

## Parked

- **Override-path fixture coverage** — `--self-test` disables overrides by design (project config must not warp fixture expectations), so the override machinery has no mechanical check; verified manually 2026-07-23. Revives if the override code grows.
