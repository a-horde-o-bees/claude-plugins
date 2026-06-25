---
name: skill-authoring
description: Use when creating or refining a skill, to apply the project's authoring disciplines together in one pass.
---

# skill-authoring

The authoring disciplines a well-formed skill satisfies, and where each one bites. Invoke when creating or refining a skill; apply each discipline at its moment, and hold the `description:` frontmatter to the sharper bar below.

## Applied disciplines

Apply each as it bites while authoring or refining a skill:

- `/markdown-authoring`
- `/description-authoring`
- `/process-authoring`
- `/rule-authoring`
- `/concise-prose`
- `/file-decomposition`

`skill-architecture` (skill structure backed by verified platform-behavior assertions) is a pending member — under reconstruction, surfacing no guidance yet; do not load it until the rebuild lands.

## The `description:` frontmatter

The description is the skill's trigger and the only part always in a reader's context — a dispatcher and an agent decide engage-or-skip from it alone. Author it under `/description-authoring` and `/rule-authoring` as a fluent **what it is + when to fire**, triggering on the right cases within the 1024-char cap. A trigger may name representative cases to fire on; those are *when*, not *what's inside*. Keep two leaks out:

- **Enumeration** — the description says what the skill is for and when it fires, never what's inside it. Listing its parts — features, sections, sub-commands, steps, even framed as a "contract" or overview — is the leak; the reader chooses by responsibility and trigger, not contents.
  - Not: "Lint, format, autofix, and report markdown; supports tables, frontmatter, and link-checking."
  - Yes: "Use when standing up or updating this project's markdown linter."
- **Method** — never describe the skill's mechanics or technique; the reader chooses by what the skill is responsible for, never by how it works inside.
  - Not: "Rank results with TF-IDF scoring over a token index."
  - Yes: "Use when ordering search results by relevance."

## Skill layout

`SKILL.md` holds the entry contract: the triggers, and for a multi-verb skill each verb's signature and routing. Decompose the process a verb runs into a component file once a skill has more than one path — so invoking one verb loads only its own process, not its siblings', and the body routes rather than runs. A single-action skill keeps its process inline.
