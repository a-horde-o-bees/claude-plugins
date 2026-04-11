---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# System Documentation

Every system maintains documentation that captures the information a consumer or developer needs to work with it, separated by concern across nesting levels and kept current with system state.

## System Boundaries

The project root is always a system. Beyond the root, a system is any structural unit with its own entry point or public interface — a plugin, a library, a service, a standalone package. Identify subsystem boundaries from project structure: own directory with entry points, own package manifest, or own deployment artifact.

## Required Documents

Every system maintains a consumer-facing entry point and a developer-facing design reference at its root. Systems with agent-facing procedures add an operational reference. Together these three documents capture everything needed to use, understand, and operate the system — each from a different perspective.

| Document | Consumer | Question answered |
|----------|----------|-------------------|
| `CLAUDE.md` / `SKILL.md` | Agent | How do I operate this? |
| `README.md` | User | How do I use this? |
| `architecture.md` | Developer | How does this work inside? |

- `README.md` — what it does, how to install, configure, use. Required for every system
- `architecture.md` — layers, components, relationships, design patterns, key implementation details. Required for every system
- `CLAUDE.md` / `SKILL.md` — operational procedures, workflow rules, tool invocation patterns. Present only when the system has agent-facing procedures. Skills use `SKILL.md`; other systems use `CLAUDE.md`

## Document Separation

Each document serves one consumer perspective. Architectural content belongs in architecture.md, not duplicated in operational or consumer documents. When an operational document (CLAUDE.md or SKILL.md) needs structural context, it directs the agent to read architecture.md rather than re-explaining the architecture.

- `README.md` excludes technical internals — those belong in architecture.md
- `architecture.md` excludes user-facing content — that belongs in README.md
- `CLAUDE.md` / `SKILL.md` excludes architectural descriptions — it references architecture.md and contains only procedures
- When a procedure requires architectural context to be actionable, the operational document directs the reader to architecture.md rather than embedding the context inline

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
