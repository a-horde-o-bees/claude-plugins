# New

> Workflow component for the `new` verb of skill-creator. Owns the from-scratch skill-authoring flow.

### Rules

- Skills with subjective outputs (writing style, art) often skip test cases — suggest the default per skill type but let the user decide
- Gate on the user before writing files; never scaffold based on incomplete inputs

### Process

1. Interview the user (synthesize from conversation history first, fill gaps via Q):
    1. What should this skill enable Claude to do?
    2. When should it trigger? (user phrases / contexts)
    3. What's the expected output format?
    4. Edge cases worth flagging in the workflow?
    5. Will the skill author content at runtime (commit messages, descriptions, prose) or just dispatch / report? — determines which dep rules belong in frontmatter
    6. Should test cases be set up? (default yes for objectively-verifiable outputs; default no for subjective ones)
    7. Where should the skill live? `user` (~/.claude/skills/), `project` (.claude/skills/), or a custom path.

2. {destination} = the chosen location from step 1.7.

3. {surface} = the cognitive moments this skill carries, derived from the interview. Each moment is a candidate `_<verb>.md` component. Single-workflow skills still extract their workflow into a `_<name>.md` component — SKILL.md is the gating layer regardless of verb count.

4. {runtime-deps} = the runtime disciplines the skill needs loaded at invocation. Common cases:
    - `process-flow-notation` — always (the workflow IS PFN)
    - `description-authoring` — when the skill authors descriptions at runtime
    - `concise-prose` — when it authors prose
    - `honesty` — when it makes claims

   Authoring-only rules (e.g., `agent-first-interfaces`, `workflow-vs-script`) don't go in runtime deps — they apply at draft time, not invocation time.

5. {name} = a chosen skill name, derived from the interview answers (what the skill enables, when it fires). Offer 2–3 lowercase-hyphenated candidates and refine with the user until they settle on one.

6. Confirm the full design with the user before writing — present {name}, frontmatter description draft, {surface}, {runtime-deps}, {destination}; gate on approval.

7. On approval, scaffold `{destination}/{name}/`:
    1. `SKILL.md` from `assets/skill-template.md`, substituting values from the dialogue.
    2. For each cognitive moment in {surface}, `_<verb>.md` from `assets/verb-workflow-template.md`.
    3. For each verb with verb-specific runtime deps, add a `### Dependencies` body section to the component file declaring `[[name]]` references per [[markdown-dependency-resolution]].
    4. Bundle resolver scripts (if needed): `scripts/_environment.py` (copy of project canonical at `shared/scripts/`).
    5. Bundle dep seeds: for each name in skill-level + verb-level `## Dependencies` declarations, copy `shared/_dependencies/<name>.md` into `{destination}/{name}/_dependencies/<name>.md`. The underscore-prefix folder marks install-source storage; the discovery find filter excludes it from runtime resolution per [[markdown-dependency-resolution]].

8. If test cases were chosen (step 1.6 = yes), scaffold `evals/evals.json` with 2–3 prompt entries the user dictates. The embedded source's schema at `sources/anthropics-skills--skill-creator/references/schemas.md` documents the full eval entry shape.

9. Return to caller:
    - Skill scaffolded: `{destination}/{name}/`
    - Files created: SKILL.md, per-verb workflow files, bundled resolver + dep fallbacks, evals.json (if applicable)
    - Next: invoke `refine {name}` to begin the test-evaluate-iterate loop
