# Components Relocation

Relocate everything currently under `components/` to a home that matches its actual trigger. The `components/` folder at project root is a catch-all that conflates workflow-scoped reference content with cross-cutting rules and architectural awareness. Under the "workflows declare what they need" model, each component should live where it is consumed.

## Goal

`components/` empty (and removed) at project root. Each piece of content relocated to a home matching how agents actually reach for it. Project-root `CLAUDE.md` Paths table no longer enumerates components.

## Constraint

Discoverability must hold across each step. A component cannot be removed from `components/` until its replacement home exists and is reachable from the situations where the component used to apply. De-enumeration in `CLAUDE.md` happens last, after all relocations.

## Inventory

| Component | Trigger shape | Target home |
|---|---|---|
| `audit-skill-invocation.md` | Workflow-scoped — fires when `/audit-*` skills are invoked | The `/audit-*` skills declare it |
| `skill-testing-modes.md` | Workflow-scoped — skill development cycle | Skill-development workflow / skill-authoring guidance |
| `plugin-bin-invocation.md` | Workflow-scoped — project-level verification | Project-level testing/verification workflow |
| `versioning.md` | Workflow-scoped — release cuts | `/ocd:git release` skill body |
| `python-dependencies.md` | Workflow-scoped — adding plugin deps | Plugin-development workflow |
| `external-tool-dependencies.md` | Workflow-scoped — skill authoring pattern | Skill-authoring guidance |
| `testing.md` | Workflow-scoped — running tests | Project-level testing workflow |
| `project-tooling.md` | Workflow-scoped — project-level operations | Project-level workflows hub (or testing workflow when narrower) |
| `template-edit-paths.md` | Content-pattern-triggered cross-cutter — fires when an agent goes to edit a deployed template | Convert to a rule (under the rules system) — carries an enforcement intent |
| `architectural-boundaries.md` | Cross-cutting design awareness — fires during design discussions | Inline as a section in project-root `ARCHITECTURE.md` |

## Sequence

1. For each workflow-scoped component:
    1. Identify or author the target workflow / skill body.
    2. Embed the reference content (or link to it) within the workflow.
    3. Verify the workflow is reachable from the original trigger situation.
    4. Delete the file from `components/`.
2. Convert `template-edit-paths.md` to a rule under the rules system (or fold into an existing rule about template authoring).
3. Move `architectural-boundaries.md` content into project-root `ARCHITECTURE.md` as a `Harness Boundary` section.
4. Once `components/` is empty:
    1. Delete the folder.
    2. Update project-root `CLAUDE.md` Paths table — remove the `components/` row and all its enumerated children.

## Open questions

- Several "workflow-scoped" components don't have an existing workflow file (e.g., skill-development, plugin-development, skill-authoring). Do those workflows need to be authored as part of this plan, or is referencing an inline section in a skill body sufficient?
- For `architectural-boundaries.md`: full inline merge into `ARCHITECTURE.md`, or split (boundary + design implications inline; the long known-limitations list elsewhere)?
- `template-edit-paths.md`: new standalone rule, or fold into an existing rule? Closest existing surface is the guard hook itself plus rules around editing in `.claude/`.

## Blocked by

`rules-migration-validation` (precedes any other ocd-system work, and the rule conversion for `template-edit-paths.md` runs through the rules system).
