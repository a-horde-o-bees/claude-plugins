---
name: description-authoring
description: Use whenever writing a description of any artifact at any scale — directory, file header, section head, docstring (function/class/module), skill frontmatter, navigator entry, tool help text, commit subject, log entry opener, schema title — where a reader (human or matcher) decides engage-vs-skip from the description alone.
---

# Description Authoring

A description tells a reader what something is and whether to go deeper — required at every structural boundary where a reader makes an include-or-skip decision, from a directory down to a single function.

A description conveys:

- **Scope** — what domain or responsibility it covers
- **Role** — what kind of thing it is (e.g., business logic, CLI, config, rule, section, function)

A description excludes:

- Internal mechanics — how algorithms work, what patterns are used
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

The same scope + role test applies at every size — abstraction level scales, structure does not.

Quality tests:

- If two descriptions are interchangeable: too vague
- If the description would change when internals are refactored but responsibility stays the same: too detailed
- If the same statement would fit at two different scales: one is the wrong granularity

The same artifact described at different boundaries uses the same description — single source of truth.

## Description and body

Description and body are distinct surfaces — one decides engage-vs-skip, the other guides operation. Content appearing in both isn't duplication; the body should re-state its operating principle so a reader landing there has it without re-reading the description.

## Example: skill descriptions

The matcher reads a skill's `description:` field to decide whether to surface the skill — nothing else. For a matcher, scope is the cognitive moment (when to reach for the skill) and the artifact or task type it applies to. Exclusions are unchanged.

- `Use when authoring an artifact another agent will read — SKILL.md, workflow markdown, rule file, description, error message.` — names the cognitive moment + artifact types.
- `Loads concise-prose, description-authoring, and related authoring rules.` — inventories contents; not a trigger.
- `Project authoring disciplines.` — too vague; any authoring task could match.
