---
name: skill-authoring
description: Use when creating or refining a skill, to apply the authoring disciplines together in one pass.
---

# skill-authoring

The bar a well-formed skill meets, and the authoring disciplines that get it there.

## Applied disciplines

Apply each as it bites while authoring or refining a skill:

- `/markdown-authoring`
- `/description-authoring`
- `/procedure-authoring`
- `/rule-authoring`
- `/concise-prose`
- `/file-decomposition`

## The trigger frontmatter

The `description:` is the skill's trigger and the only part always in context: the model decides engage-or-skip from it alone, and every skill's entry sits in the listing for the whole session, competing with every other instruction there. Author it per `/description-authoring` — what the skill does and when to use it, woven fluently, third person — plus the facts specific to this surface:

- **Key use case first.** The listing truncates an entry at 1,536 characters, front-first — the opening clause must carry the decision.
- **One distinctive use-condition.** A trigger matches on one vocabulary collision with the live request, not many. Synonym runs and quoted lists of example phrasings add no matching power and widen unintentional auto-invocation; name distinct cases (`e.g.`-marked) when they cover genuinely different territory, never rephrasings of one case.
- **Weave idiom vocabulary into the prose.** When requests arrive in an idiom that shares no tokens with the responsibility statement ("prepping a handoff" vs. "reconcile system docs"), fold that vocabulary in as a fluent subordinate clause — the description stays one readable thought and still carries the collision surface. Never as a quoted phrasing list.
- **The listing is a shared budget.** Every entry is permanent per-session context, and each addition taxes every other skill's chance of firing. Trim at the source first; beyond that, `skillOverrides: "name-only"` lists a low-priority skill without its description, and `skillListingMaxDescChars` / `skillListingBudgetFraction` (or `SLASH_COMMAND_TOOL_CHAR_BUDGET`) tune the caps.
- **Intentionally unused fields.** The suite sets no `when_to_use` (the woven description is the whole trigger surface; the field is appended into the same listing entry under the same 1,536-char cap, adding only a second surface to audit) and no `disable-model-invocation` / `user-invocable` (every skill stays model- and user-invocable at the defaults). Deviate only as a deliberate, recorded exception.

The general exclusions — describe responsibility, never method; never enumerate the skill's contents or verbs — are description-authoring's; the skill listing is where those leaks cost most, since a leaked description both misfires as a trigger and bloats every session. Test a contested trigger cold with should-trigger / should-not-trigger prompts (rule-authoring § Enforce before wording) rather than arguing the wording.

## Skill layout

`SKILL.md` holds the entry contract: the triggers, and for a multi-verb skill each verb's signature and routing. Decompose the process a verb runs into a component file once a skill has more than one path — so invoking one verb loads only its own process, not its siblings', and the body routes rather than runs. A single-action skill keeps its process inline.

## Audits

Close an authoring pass with two audits of the finished skill, each judged by reading the affected files whole. Well-formedness is the thing under audit, so match-line context is never enough — the conventions that make a snippet legible cannot be assumed.

**Reference audit.** A slash-reference is an invocation — every mechanical consumer treats `/name` as "load and apply here": apply-over-queue's flatten inlines the referenced skill's whole tree, and a reading agent is pressed to invoke it. Cite a skill for any other reason — provenance, comparison, a shared constant's origin — by bare name.

1. **Probe**: write a one-line operation file `/skill-name`; bash: `python3 ${CLAUDE_SKILL_DIR}/../apply-over-queue/scripts/flatten.py --operation-file {probe} --skills-root ${CLAUDE_SKILL_DIR}/.. --out {payload}` (sibling paths — the suite installs as one unit). The printed unit list is the reading list; the payload's byte count is the true cost — deduplicated and frontmatter-stripped, so per-file sums overstate it.
2. **Read every listed unit end-to-end**, and classify each reference with the whole file in view:
    - *operational* — the referenced discipline shapes execution at that point: keep the slash.
    - *citation* — rationale, provenance, comparison: bare name.
    - *definitional example* — the slash syntax is itself the content: keep it; its payload cost is accepted knowingly.
3. **Judge the shape**: a branch-free leaf is safe to reference from fan-out operations. A router (verb dispatch, param-conditional components) is fine for normal dispatch, which loads one branch — but flatten inlines the union of every branch, so operations must reference a router's leaf units, and each leaf must stand alone.

**Mechanization audit.** For every process step, ask: judgment or mechanism? A step whose outcome is fully determined by its inputs — parse, count, walk, diff, rename — belongs in a script the step invokes; prose walking an agent through mechanical work drifts and re-bills every invocation (rule-authoring: route load-bearing behavior to mechanical enforcement rather than wording).
