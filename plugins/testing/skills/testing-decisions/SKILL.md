---
name: testing-decisions
description:
---

# Testing Decisions

Deciding whether or how much to test a given component. Routes between traditional unit tests, property tests, snapshots, exhaustive boundary enumeration, and evaluation protocols, by failure mode.

For any callable or deterministic component:

1. Does it have at least one test? If no, write one — untested callables are the first gap.
2. If deterministic:
    1. Contract agents depend on (output format, exit codes, help text): snapshot
    2. Invariants exist: property test
    3. Idempotent by design: test idempotency
    4. Security boundary: exhaustive adversarial cases
    5. Silent failure causes downstream malfunction: test regardless of simplicity
    6. Integration test duplicates unit coverage with no new failure mode: skip
    7. Test merely restates configuration: skip
3. Else: evaluate through protocols, don't unit test
