# Graceful Degradation

When a dependency is unavailable or a precondition unmet, continue functioning in a reduced state and report what is missing and how to restore it. Silent failure, cryptic cascades, and all-or-nothing behavior force the reader to debug the system to learn what went wrong.

- Missing state is valid — operations on partial or absent data report what is present and what is missing, not refuse the whole request
- Status reporting distinguishes readiness stages (absent, initialized, stale, error) and pairs each with its corrective command
- Error output names the specific missing piece and the specific next action, not a generic failure category
- Before relying on an external tool or environment variable: verify availability and name the corrective command if missing; do not let a downstream call surface an unhelpful error
