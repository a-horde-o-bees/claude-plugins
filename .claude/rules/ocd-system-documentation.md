---
pattern: "*"
depends:
  - .claude/rules/ocd-design-principles.md
---

# System Documentation

What documentation each system maintains, how nested systems relate, and when to check or update documentation.

## System Boundaries

The project root is always a system. Beyond the root, a system is any structural unit with its own entry point or public interface — a plugin, a library, a service, a standalone package. Identify subsystem boundaries from project structure: own directory with entry points, own package manifest, or own deployment artifact.

## Required Documents

Every system maintains at its root:

- `README.md` — user/consumer facing: what it does, how to install, configure, use
- `architecture.md` — system facing: layers, components, relationships, design patterns, key implementation details

## Nesting

Systems may contain subsystems. Parent documentation gives a generalized description of each subsystem — what it does and how it relates to the whole. Subsystems describe themselves in their own documentation.

- Parent README describes each subsystem's purpose and links to the subsystem's README for details
- Parent architecture.md describes each subsystem's role in the overall architecture and links to the subsystem's architecture.md for internals
- Neither parent document re-explains content that belongs to the subsystem's own documentation
- A reader navigates from general to specific: project root → system → subsystem

## Decisions

`decisions.md` lives at the project root (not per-system) with detail files in `decisions/`. Decisions are preventative — they record non-obvious choices to prevent backtracking.

`decisions.md` is the index — one line per decision, implicit timeline by insertion order. `decisions/` holds detail files when reasoning is worth preserving.

- Simple: `- **[Title]** — one-line summary`
- With detail: `- **[Title]** — one-line summary → [detail](decisions/file.md)`

Record when alternatives were considered and rejected, or when reasoning is not derivable from code or conventions. Detail files follow:

- **Context** — what problem or question prompted the decision
- **Options Considered** — alternatives evaluated with trade-offs
- **Decision** — what was chosen and why
- **Consequences** — what this enables, constrains, and how to mitigate risks

Do not record implementation details, choices dictated by convention, or standard patterns obvious from reading code. Update existing entries when direction changes. Remove entries and detail files when the decision is no longer relevant.

## Behavioral Triggers

- Before modifying a system, check for its architecture reference
- After significant structural changes (new tables, new layers, changed tool interfaces), update the architecture reference
- After adding or removing subsystems, update the parent system's documentation to reflect the current set
