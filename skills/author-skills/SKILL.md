---
name: author-skills
description: Use when creating or refining a skill, to apply the project's authoring disciplines together in one pass — prose, descriptions, markdown, rules, process notation, file decomposition, and progressive disclosure.
---

# author-skills

The authoring disciplines that compose a well-formed skill. Invoke this when creating or refining one; apply each at its moment.

## The description field

The frontmatter `description:` is special — it is the skill's trigger (the primary mechanism deciding whether the skill fires) and the only part always in context. Author it by composing two disciplines:

- **/author-descriptions** — what the skill is *and* when to use it. Put every "when to use" cue here, never in the body. Third person, within the 1024-char cap.
- **/author-rules** — make it fire on the genuine cases. Scope to the real trigger; lean slightly pushy to counter Claude's tendency to under-trigger, without firing on adjacent tasks.

## The body

Apply each discipline as you would to any artifact:

- **/concise-prose** — all prose: body, comments, error strings, log lines.
- **/author-descriptions** — section headings and any component-file descriptions (the frontmatter field is covered above).
- **/author-markdown** — open every markdown file with an `#` heading naming it, then a description.
- **/author-rules** — any rule or directive the skill states (the description's own triggering is covered above).
- **/author-processes** — workflow component files whose control flow exceeds a linear sequence; also each step's workflow-vs-script placement.
- **/file-decomposition** — whether content belongs in `SKILL.md` or a split-out component, judged by how an agent loads it.
- **/progressive-disclosure** — layer the skill so the frontmatter triggers, the body navigates, and deep content loads only on dispatch.

`skill-architecture` (skill structure backed by verified platform-behavior assertions) is a pending member — under reconstruction, surfacing no guidance yet; do not load it until the rebuild lands.
