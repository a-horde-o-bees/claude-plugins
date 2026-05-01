---
log-role: reference
---

# Principles

Decisions governing the design-principles rule template — how the umbrella principles are structured and what evidence drove their trigger sets.

## Honesty principle trigger set

### Context

The Honesty principle in `design-principles.md` carries a substantial trigger set covering quantitative claims, performance claims, external-tool ranking claims, parity claims, weasel-word avoidance, framework-audit completeness, and verification-before-acting. The trigger count is unusual for a single principle and warrants explicit rationale so future sessions don't simplify the set without understanding which incidents each trigger prevents.

### Options Considered

**Minimal trigger set** — one or two general bullets ("verify before claiming"). Rejected: agents reading a general rule don't reliably catch domain-specific failure modes; the trigger only fires when the agent recognizes the moment, and recognition is sharper with situation-specific gates.

**Full trigger set, origin captured separately** — the principle file stays prescriptive; rationale lives in this decision log. Adopted.

### Decision

The Honesty principle's trigger set is driven by three incident classes, each producing one or more triggers:

- **User-facing artifact framing incidents** — repeated overclaiming in application materials (quantitative durations, "production AI" framing, role-title labeling). Drove triggers around quantitative claims, content reuse across artifacts, parity claims, weasel-word avoidance, framework-audit completeness, and industry-phrase disambiguation.
- **External-ecosystem ranking incident** — confident assertion of a market position about a tool that turned out to be a fabricated package name. Drove the trigger about ranking/market-position claims and the requirement to fetch or caveat-as-memory.
- **Performance-claim incident** — claimed "single-digit milliseconds" for a helper to argue against caching; real measurement was ~15ms. Drove the trigger about performance/timing/cost claims requiring measurement.

Each trigger names a specific situation where the agent's default would be to assert without verification. The set is incident-driven, not exhaustive — additional triggers may be added when new incident classes are observed.

### Consequences

- **Enables:** future sessions facing similar moments find a sharp gate that fires reliably; new incident classes can be added as triggers without redesigning the principle
- **Constrains:** the trigger set will grow over time as new failure modes are observed; periodic consolidation may be needed if triggers start overlapping
- **Audit signal:** if the same incident pattern recurs across multiple sessions and no trigger fires, the trigger set is incomplete — add the missing case bullet rather than treating each instance as procedural noise
