---
name: author-skills
description: Use when creating or refining a skill, to apply the project's authoring disciplines together in one pass — prose, descriptions, markdown, rules, process notation, file decomposition, and progressive disclosure.
---

# author-skills

The authoring disciplines that govern a well-formed skill. Invoke this when
creating or refining one to pull them in together, then apply each at its moment.

- **/concise-prose** — all prose in the skill: body, comments, error strings, log lines.
- **/author-descriptions** — the frontmatter `description` (the trigger line a reader uses to engage-or-skip) and any section headings.
- **/author-markdown** — every markdown file opens with an `#` heading naming it, then a description.
- **/author-rules** — any rule, principle, or directive the skill states, so it triggers reliably.
- **/author-processes** — workflow component files whose control flow goes beyond a linear sequence; also where each step's workflow-vs-script placement is decided.
- **/file-decomposition** — whether content belongs in `SKILL.md` or a split-out component file, judged by how an agent loads it.
- **/progressive-disclosure** — layer the skill so the frontmatter triggers, the body navigates, and deep content loads only on dispatch.

`skill-architecture` (skill structure backed by verified platform-behavior assertions) is a pending member — under reconstruction, surfacing no guidance yet; do not load it until the rebuild lands.
