# Log cleanup feature for /ocd:log

Extend `/ocd:log` with a cleanup-oriented verb (or add cleanup mode to `list`) that surfaces stale entries and drives the per-type lifecycle defined in each `_template.md`. Today `add | list | remove` cover capture; nothing prompts the agent to act on the lifecycle pointer the log-routing rule relies on.

## What the feature would do

- **Review mode** — group outstanding entries by role (per `rules/log.md` and each type's `_template.md` `log-role` frontmatter): **queue-role types** (friction / idea / problem) surface as lists of pending action; **reference-role types** (decision / pattern / research) surface as the persistent knowledge base. A single review pass lets the agent see both in one place.
- **Cleanup candidates — queue role** — surface entries likely ready to delete: problem entries referencing artifacts that have since changed, friction entries older than a threshold with no recent updates, idea entries whose acted-on status can be inferred from git history.
- **Reference refresh — reference role** — prompt the agent when a reference entry's subject has changed since it was last updated (decision's rationale still current? pattern's methodology still followed? research's samples still reflect the corpus?), nudging an explicit revision rather than silent drift. Decisions in particular degrade silently into settings without rationale checkpoints.

## Why not release-blocking

Logs work today — they accumulate without breaking anything. This is enhancement tooling for dev workflow, not a defect in a shipped artifact.

## Prerequisites

- `/ocd:log` skill exists and owns the verb surface to extend.
- Log type templates declare their role in prose and via the `log-role` frontmatter field; the feature would convert that declaration into mechanics the skill can act on.
- Role definitions live in `rules/log.md`'s "Roles" section. The cleanup feature keys off the `log-role` field in each `logs/<type>/_template.md` so user-added custom types are supported without hardcoded membership lists.

## Filter helper (prerequisite)

A small script at `plugins/ocd/systems/log/_roles.py` (or similar) that enumerates `logs/<type>/` directories, reads each `_template.md`'s `log-role` frontmatter, and emits `{"reference": [...], "queue": [...]}`. The cleanup verb calls this to group entries by role before applying lifecycle-specific cleanup logic; any future tool needing role-filtered type enumeration also consumes it.

Trivial to write: one Python file, one function, can reuse the existing `_frontmatter.py` parser under `systems/governance/` or use a stdlib YAML parse. Not worth writing before the cleanup verb exists to consume it (YAGNI) — author alongside the cleanup verb so the helper's shape matches the verb's actual needs.
