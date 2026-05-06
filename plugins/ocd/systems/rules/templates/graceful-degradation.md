---
includes: "*"
---

# Graceful Degradation

When a dependency is unavailable or a precondition is not met, the system continues to function in a reduced but useful state and reports exactly what is missing and how to restore it. Silent failure, cryptic error cascades, and all-or-nothing behavior each force the reader to debug the system to understand what went wrong — the system should carry that work, not push it onto the reader.

- Missing state is a valid state — operations on half-populated or absent data report what is present and what is missing, rather than refusing the whole request
- Status reporting distinguishes stages of readiness (absent, initialized, stale, error) and pairs each with its corrective command
- Error output names the specific missing piece and the specific next action, not a generic failure category
- Before execution relies on an external tool or environment variable: verify availability and name the corrective command if missing, rather than letting a downstream call surface an unhelpful error
