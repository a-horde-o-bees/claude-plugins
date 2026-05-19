# Rules-to-skills pivot — abandon dep framework, all rules become project skills

Date: 2026-05-15

## Decision

Every former always-on rule becomes a project-level skill at `.claude/skills/<name>/SKILL.md` with an empty description (so it doesn't auto-fire via matcher). Each rule's body content is preserved verbatim. The dep file framework (`shared/_dependencies/`, co-located `_read_deps.py`, pre-commit propagation, deployed `<scope>/rules/dependencies/`) is set aside "for the moment" — preserved on disk but not actively maintained.

Cross-references between skills will happen via direct `/<skill>` invocation when authoring new content, not via `## Dependencies` block declarations.

## Rejected alternatives

- **Keep dep system + lazy-load via skill router** — explored as the "skill-graph-router" pattern (see [logs/idea/skill-router.md](../idea/skill-router.md)). Pattern is valid (Firecrawl ships it in production) but at our scale (5–22 skills) the matcher's native description-budget is sufficient. Routing earns its keep at ~50+ skills or when description discrimination starts failing measurably.
- **Demote rules to user-scope only** — leaves the dep framework intact but moves the always-on burden. Doesn't solve the core problem (rule layer duplicates skill content; cross-reference notation duplicates dep declarations).
- **Build a single router skill bundling 8 disciplines** — the previous draft (`agent-authoring` router). Concentrates context cost into one heavier load per match, but loses the per-skill matcher discrimination we need to refine each discipline independently.

## Why

- **Cross-reference duplication.** Each body `[[name]]` wikilink also requires the name in the `## Dependencies` declaration. Two surfaces to keep in sync.
- **Rule-graph constraint inertia.** Demoting one rule to a skill forces every rule depending on it to either also demote or drop the dep edge. Refactor inertia for what should be a small change.
- **Duplicate content.** When a discipline exists as both rule and skill, its body lives in two places (rule deployment + skill SKILL.md). Pre-commit propagation kept them in sync but added a commit-gate dependency.
- **Skills already do dep-style loading.** When a skill fires, its body loads into context. No separate resolver needed. Skill ↔ skill cross-references are just `/<name>` invocations.
- **Setting aside, not deleting.** The framework is preserved at [`architecture/skill-dependency-system/`](../../architecture/skill-dependency-system/) with full reference (README + `_read_deps.py` + `pre-commit`). Reconstruction takes hours if the skill-call substitute proves insufficient.

## Implications

- **Workflows that declare `## Dependencies` still work** via `_read_deps.py` tier 5 (plugin bundled copies in `plugins/<plugin>/skills/*/_dependencies/<name>.md`). The bundled copies retain their old rule body content. Workflows in `plugins/ocd/skills/git/_commit.md` and similar continue to resolve `concise-prose` etc.
- **The always-on context budget drops to zero** for rule content. Previously 22 rules × hundreds of tokens each, loaded into every agent. Now: zero unless the skill is invoked.
- **Matcher reliability becomes load-bearing.** Where rules guaranteed loading, skills guarantee loading only when their descriptions match. Each description must be sharp enough to fire on real moments — measured, not predicted.
- **Phase H of the architecture refactor is largely subsumed.** "Conventions as situational-load skill" assumed a single user-facing skill loading any convention; what landed is one skill per convention, matcher-fired. See `TASKS.md` for follow-up.

## Verification of the new state

23 project skills at `.claude/skills/`:

```
agent-first-interfaces  borrow-before-build  checkpoint  clean-break
composability  concise-prose  confirm-shared-intent  description-authoring
file-decomposition  fix-foundations-not-symptoms  graceful-degradation
honesty  markdown  markdown-dependency-resolution  principled-pushback
progressive-disclosure  structure-as-documentation  test-authoring
test-driven-development  test-maintenance  testing-decisions
trigger-specificity  workflow-vs-script
```

`.claude/rules/` removed entirely. `architecture/skill-dependency-system/` contains the saved working model.
