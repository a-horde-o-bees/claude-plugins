---
name: progressive-disclosure
description:
---

# Progressive Disclosure

Triggers whenever an author writes a SKILL.md, a workflow component, a help-text root, or any entry-point doc agents load via a fuzzy trigger before deciding whether to drill deeper. The entry point loads when the trigger fires; deep content loads only once the entry confirms the trigger and dispatches inward.

Three-tier loading model:

1. **Metadata** — frontmatter `name` + `description` (per /description-authoring). Always in context. Sized to fire the trigger reliably across phrasings.
2. **Entry point** — SKILL.md body or top-level doc. Loads when metadata fires. Body is navigation only: a triggers table (more precise than the description-level match), topography pointing at component files, and orientation. Not the workflow itself.
3. **Deep content** — `_<verb>.md` component files, `scripts/` modules, bundled references. Loads only when the entry point dispatches inward via `Call:`, `Spawn:`, or `bash:` invocation.

Why the gating layer matters: metadata triggers are fuzzy (description-text match against natural language). The entry point gets a second pass — the precise triggers section says "this is what I cover; is your situation actually one of these?" A false-positive description match exits at the entry point without paying for the workflow. Inline workflows in SKILL.md pay that cost on every false-positive trigger.

Reading-cost discipline:

- SKILL.md body stays narrow — triggers + topography + orientation, typically 30–200 lines. If body steps encode workflow content, those steps belong in a component file.
- Single-workflow skills (no verbs to dispatch on) still extract the workflow into a `_<name>.md` component. SKILL.md dispatches via `Call: _<name>.md`. Cost: one file. Benefit: false-positive triggers don't pay the workflow.
- Component files load only when the entry point dispatches them. Agents rarely reach into a component directly from outside the parent skill.
- Scripts are encapsulated operations the workflow invokes; they don't load into the agent's context at all.

Antipatterns:

- **Workflow inline in SKILL.md** — false-positive triggers pay the workflow cost; the entry point loses its gating role.
- **"It's only one workflow, no point in splitting"** — single workflow still benefits from the gating layer; the discipline is uniform across single- and multi-verb skills.
- **Eagerly loading bundled references** — references load on demand from the workflow, not from the entry point.
- **Dispatch dressed as content** — sections that *look like* topography (triggers + a table pointing at components) but include execution steps below them; the workflow has leaked into the entry point.

Tell whether the entry point is at the right size by asking: if a user triggers this skill by accident (their phrasing matched the description but they meant something else), do they pay only for navigation cost, or for the full workflow? See /file-decomposition for the general split-vs-merge discipline; progressive disclosure is its specific application to entry-point and deep-content layouts.
