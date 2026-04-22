---
includes: "README.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/system-docs.md
  - .claude/rules/ocd/markdown.md
---

# README.md Conventions

Content standards for `README.md` files. User/consumer-facing documentation covering what the system does, how to install, configure, and use it.

## Purpose Statement

Opens with the system name and a one-line description. A reader encountering the file for the first time understands what the system is and whether it's relevant to them.

## Content

Document what a user needs to adopt and use the system:

- **What it does** — capabilities and value proposition
- **Installation** — how to set up from scratch
- **Configuration** — required and optional settings
- **Usage** — how to invoke, common workflows, examples
- **Dependencies** — what must be present for the system to work

Include what a user needs to get started and be productive. Exclude technical internals (layers, schema, design patterns) — that belongs in ARCHITECTURE.md. Exclude agent-facing procedures (workflow rules the agent follows, tool invocation patterns for automation) — that belongs in CLAUDE.md or SKILL.md.

## Nesting

When a system contains systems, describe each subsystem's purpose — what it does and how it relates to the whole. Do not re-explain the subsystem's installation, configuration, or usage details; link to the subsystem's own `README.md`.

A parent README answers "what is this project and what does it contain?" Each subsystem's README answers "how do I use this specific piece?"

## Structure

Structure varies by system type. Common sections:

- Name + description → Setup → Capabilities → Usage (for plugins/tools)
- Name + description → Installation → Configuration → API Reference (for libraries)
- Name + description → Prerequisites → Getting Started → Commands (for CLIs)

Order sections by user journey — what they need first comes first.

## Currency

Describes current capabilities and usage. Do not reference previous versions, deprecated features, or migration history unless users need that information to operate.
