---
includes: "CLAUDE.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/system-docs.md
  - .claude/rules/ocd/markdown.md
---

# CLAUDE.md Conventions

Content standards for `CLAUDE.md` files. Agent-facing operational reference containing procedures, workflow rules, and tool invocation patterns for working with the system.

## Purpose Statement

Opens with the system name or scope and a one-line description of what operational guidance this file provides. A reader encountering the file for the first time understands what procedures are covered.

## Content

Document what an agent needs to operate within the system:

- **Procedures** — step-by-step instructions for recurring operations
- **Workflow rules** — constraints on how work is done (branching, committing, testing)
- **Tool invocation patterns** — how to run system-specific tools and scripts
- **Content routing** — where different types of content belong within the system

Include only procedures and operational guidance. Exclude technical internals (layers, schema, design patterns) — that belongs in architecture.md. Exclude user-facing content (installation, configuration, usage) — that belongs in README.md.

## Architecture Reference

When a procedure requires structural context to be actionable, direct the agent to read architecture.md rather than embedding the context inline. The architecture document is the single source for how the system works; the operational document references it rather than re-explaining.

## Structure

No fixed section template — structure follows the system's operational concerns. Group procedures by topic. Order by frequency of use or workflow sequence.

## Currency

Describes current procedures. Do not reference previous workflows, removed commands, or process history — that information lives in git history and decisions records.
