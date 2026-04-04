---
pattern: "architecture.md"
depends:
  - .claude/rules/ocd-design-principles.md
  - .claude/rules/ocd-system-documentation.md
  - .claude/conventions/markdown.md
---

# architecture.md Conventions

Content standards for `architecture.md` files. System-facing technical reference documenting layers, components, relationships, design patterns, and key implementation details.

## Purpose Statement

Opens with a one-line description of what the system does, followed by a brief statement of what this document covers. A reader encountering the file for the first time understands the system's identity and scope immediately.

## Content

Document the system's internal structure:

- **Layers** — execution flow from entry point to data store; how components communicate
- **Components** — distinct functional units with their responsibilities
- **Relationships** — how components depend on and interact with each other
- **Schema** — data models, database tables, API contracts
- **Design patterns** — non-obvious patterns and why they were chosen
- **Key implementation details** — concurrency model, error handling strategy, performance constraints

Include what a developer needs to modify the system safely. Exclude user-facing content (installation, configuration, usage) — that belongs in README.md.

## Nesting

When a system contains subsystems, describe each subsystem's role in the overall architecture — what it does, how it connects to other components, what interface it exposes. Do not re-explain the subsystem's internal structure; link to the subsystem's own `architecture.md` for technical internals.

A parent architecture.md answers "how do these pieces fit together?" Each subsystem's architecture.md answers "how does this piece work internally?"

## Structure

No fixed section template — structure follows the system's actual architecture. Common patterns:

- Purpose → Layers → Components → Schema → Constraints (for database-backed systems)
- Purpose → Layers → Modules → Entry Points → File Organization (for plugin/library systems)
- Purpose → Components → Interfaces → Data Flow (for service systems)

Section depth follows component depth. Flat systems have flat documents.

## Currency

Describes current state. Do not reference previous states, removed features, or change history — that information lives in git history and decisions.md.
