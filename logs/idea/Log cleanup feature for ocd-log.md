# Log cleanup feature for /ocd:log

Extend `/ocd:log` with a cleanup-oriented verb (or add cleanup mode to `list`) that surfaces stale entries and drives the per-type lifecycle defined in each `_template.md`. Today `add | list | remove` cover capture; nothing prompts the agent to act on the lifecycle pointer the log-routing rule relies on.

## What the feature would do

- **Review mode** — group outstanding entries per lifecycle cohort (per `rules/log.md`): the **working cohort** (friction / idea / problem) surfaces as queues of pending action; the **reference cohort** (decision / pattern / research) surfaces as the persistent knowledge base. A single review pass lets the agent see both in one place.
- **Cleanup candidates — working cohort** — surface entries likely ready to delete: problem entries referencing artifacts that have since changed, friction entries older than a threshold with no recent updates, idea entries whose acted-on status can be inferred from git history.
- **Reference refresh — reference cohort** — prompt the agent when a reference entry's subject has changed since it was last updated (decision's rationale still current? pattern's methodology still followed? research's samples still reflect the corpus?), nudging an explicit revision rather than silent drift. Decisions in particular degrade silently into settings without rationale checkpoints.

## Why not release-blocking

Logs work today — they accumulate without breaking anything. This is enhancement tooling for dev workflow, not a defect in a shipped artifact.

## Prerequisites

- `/ocd:log` skill exists and owns the verb surface to extend.
- Log type templates define lifecycle in prose; the feature would convert that prose into mechanics the skill can act on.
- Lifecycle cohort definitions live in `rules/log.md`'s "Lifecycle Cohorts" section — the working/reference split is the load-bearing distinction the cleanup feature operates on.
