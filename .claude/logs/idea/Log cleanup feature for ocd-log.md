# Log cleanup feature for /ocd:log

Extend `/ocd:log` with a cleanup-oriented verb (or add cleanup mode to `list`) that surfaces stale entries and drives the per-type lifecycle defined in each `_template.md`. Today `add | list | remove` cover capture; nothing prompts the agent to act on the lifecycle pointer the log-routing rule relies on.

## What the feature would do

- **Review mode** — group outstanding entries per type (friction/idea/problem as queues; decision as persistent) so the agent can see what's pending at a glance.
- **Cleanup candidates** — surface entries likely ready to delete: problem entries referencing artifacts that have since changed, friction entries older than a threshold with no recent updates, idea entries whose acted-on status can be inferred from git history.
- **Decision refresh** — prompt the agent when a decision's subject has changed since the entry was last updated, nudging an explicit revision rather than silent drift.

## Why not release-blocking

Logs work today — they accumulate without breaking anything. This is enhancement tooling for dev workflow, not a defect in a shipped artifact.

## Prerequisites

- `/ocd:log` skill exists and owns the verb surface to extend.
- Log type templates define lifecycle in prose; the feature would convert that prose into mechanics the skill can act on.
