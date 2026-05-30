# New

> Workflow component for the `new` verb of skill-creator. Owns the from-scratch skill-authoring flow.

## Rules

- Skills with subjective outputs (writing style, art) often skip test cases — suggest the default per skill type but let the user decide
- Gate on the user before writing files; never scaffold based on incomplete inputs

## Process

1. Interview the user (synthesize from conversation history first, fill gaps via Q):
    1. {goal}: What should this skill enable Claude to do?
    2. {triggers}: When should it trigger? (user phrases / contexts)
    3. {output-format}: What's the expected output format?
    4. {edge-cases}: Edge cases worth flagging in the workflow?
    5. {runtime-vs-dispatch}: Will the skill author content at runtime (commit messages, descriptions, prose) or just dispatch / report? — determines which dep rules belong in frontmatter
    6. {test-cases}: Should test cases be set up? (default yes for objectively-verifiable outputs; default no for subjective ones)
    7. {destination}: Where should the skill live? `user` (~/.claude/skills/), `project` (.claude/skills/), or a custom path

2. {surface}: cognitive moments this skill carries, derived from {goal} + {triggers}. Each moment is a candidate `_<verb>.md` component. Single-workflow skills still extract their workflow into a `_<name>.md` component — SKILL.md is the gating layer regardless of verb count.
3. {runtime-deps}: runtime disciplines the skill needs loaded at invocation. Common cases:
    - `process-flow-notation` — always (the workflow IS PFN)
    - `description-authoring` — when the skill authors descriptions at runtime
    - `concise-prose` — when it authors prose
    - `honesty` — when it makes claims

    > Authoring-only rules (e.g., `agent-first-interfaces`, `workflow-vs-script`) don't go in runtime deps — they apply at draft time, not invocation time.

4. {name}: 2–3 lowercase-hyphenated candidates from {goal} + {triggers}; refine with the user until one is settled
5. {approval}: AskUserQuestion — confirm the full design: present {name}, frontmatter description draft, {surface}, {runtime-deps}, {destination}
6. If {approval} is cancel: Exit to user: skill creation cancelled
7. Scaffold `{destination}/{name}/`:
    1. Write `SKILL.md` from `<skill-base>/assets/skill-template.md`, substituting values from the dialogue
    2. For each cognitive moment in {surface}, write `_<verb>.md` from `<skill-base>/assets/verb-workflow-template.md`

8. If {test-cases} is yes: scaffold `evals/evals.json` with 2–3 prompt entries the user dictates. The embedded source's schema at `sources/anthropics-skills--skill-creator/references/schemas.md` documents the full eval entry shape.

## Report

Return to caller:

- Skill scaffolded: `{destination}/{name}/`
- Files created: SKILL.md, per-verb workflow files, bundled dep seeds, evals.json (if applicable)
- Next: invoke `refine {name}` to begin the test-evaluate-iterate loop
