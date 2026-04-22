---
includes: "*"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# System Documentation

Documentation requirements and structure for systems in this project.

## System Boundaries

The project root is always a system. Beyond the root, a system is any structural unit with its own entry point or public interface — a plugin, a library, a service, a standalone package. Identify subsystem boundaries from project structure: own directory with entry points, own package manifest, or own deployment artifact.

## Required Documents

Every system maintains a consumer-facing entry point and a developer-facing design reference at its root. Systems with agent-facing procedures add an operational reference. Together these three documents capture everything needed to use, understand, and operate the system — each from a different perspective.

| Document | Consumer | Question answered |
|----------|----------|-------------------|
| `CLAUDE.md` / `SKILL.md` | Agent | How do I operate this? |
| `README.md` | User | How do I use this? |
| `ARCHITECTURE.md` | Developer | How does this work inside? |

- `README.md` — what it does, how to install, configure, use. Required for systems with substantial internal structure
- `ARCHITECTURE.md` — layers, components, relationships, design patterns, key implementation details. Required for systems with substantial internal structure
- `CLAUDE.md` / `SKILL.md` — operational procedures, workflow rules, tool invocation patterns. Present only when the system has agent-facing procedures. Skills use `SKILL.md`; other systems use `CLAUDE.md`

## Subsystem Doc Consolidation

A subsystem earns its own `README.md` and `ARCHITECTURE.md` when it has substantial internal structure — multiple components, its own schema, its own public interface beyond a single entry point. Libraries, plugins, and substantive services fit this category.

Thin systems — a skill whose `SKILL.md` is its complete operational reference, a thin MCP server adapter over a domain library, a single-file script — do not require their own `README.md` and `ARCHITECTURE.md`. Their purpose is owned at their natural doc location (SKILL.md frontmatter description, module-level docstring, file header) and propagated to the parent's overview.

Purpose statement propagation: every subsystem — whether it has its own docs or consolidates into the parent — owns its purpose statement at one canonical location. Parent documentation quotes from the canonical location rather than independently describing the subsystem, keeping the parent in sync when the subsystem evolves. The canonical locations:

- Library or plugin subsystem with full docs — `README.md`'s opening purpose statement
- Skill — `SKILL.md`'s frontmatter `description` field
- Thin MCP server or other single-file subsystem — module-level docstring of its entry point

## Document Separation

Each document serves one consumer perspective. Architectural content belongs in ARCHITECTURE.md, not duplicated in operational or consumer documents. When an operational document (CLAUDE.md or SKILL.md) needs structural context, it directs the agent to read ARCHITECTURE.md rather than re-explaining the architecture.

- `README.md` excludes technical internals — those belong in ARCHITECTURE.md
- `ARCHITECTURE.md` excludes user-facing content — that belongs in README.md
- `CLAUDE.md` / `SKILL.md` excludes architectural descriptions — it references ARCHITECTURE.md and contains only procedures
- When a procedure requires architectural context to be actionable, the operational document directs the reader to ARCHITECTURE.md rather than embedding the context inline

## Nesting Discipline

Parent documentation describes each subsystem generally and links down; systems describe themselves in detail. Neither layer re-explains content that belongs to the other, so readers can navigate from general to specific without encountering duplicated or conflicting descriptions.

- Parent README describes each subsystem's purpose and links to the subsystem's README for details
- Parent ARCHITECTURE.md describes each subsystem's role in the overall architecture and links to the subsystem's ARCHITECTURE.md for internals
- Neither parent document re-explains content that belongs to the subsystem's own documentation
- A reader navigates from general to specific: project root → system → subsystem
