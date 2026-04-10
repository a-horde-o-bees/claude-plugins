---
matches: "*"
governed_by:
  - .claude/rules/ocd-design-principles.md
---

# System Documentation

Every system maintains documentation that captures the information a consumer or developer needs to work with it, separated by concern across nesting levels and kept current with system state.

## System Boundaries

The project root is always a system. Beyond the root, a system is any structural unit with its own entry point or public interface — a plugin, a library, a service, a standalone package. Identify subsystem boundaries from project structure: own directory with entry points, own package manifest, or own deployment artifact.

## Required Documents

Every system maintains both a consumer-facing entry point and a developer-facing design reference at its root, so the information needed to understand and work with the system is captured in known locations rather than rediscovered each time.

- `README.md` — user/consumer facing: what it does, how to install, configure, use
- `architecture.md` — system facing: layers, components, relationships, design patterns, key implementation details

## Nesting Discipline

Parent documentation describes each subsystem generally and links down; subsystems describe themselves in detail. Neither layer re-explains content that belongs to the other, so readers can navigate from general to specific without encountering duplicated or conflicting descriptions.

- Parent README describes each subsystem's purpose and links to the subsystem's README for details
- Parent architecture.md describes each subsystem's role in the overall architecture and links to the subsystem's architecture.md for internals
- Neither parent document re-explains content that belongs to the subsystem's own documentation
- A reader navigates from general to specific: project root → system → subsystem

## Documentation Currency

Documentation tracks current system state — modifications to a system trigger corresponding documentation updates so the recorded description doesn't drift from reality.

- Before modifying a system, check for its architecture reference
- After significant structural changes (new tables, new layers, changed tool interfaces), update the architecture reference
- After adding or removing subsystems, update the parent system's documentation to reflect the current set
