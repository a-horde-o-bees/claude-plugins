# Rules

Always-on agent behavior guidance loaded into every session automatically.

## How Rules Work

Each rule is a markdown file in `.claude/rules/` with YAML frontmatter. Claude Code auto-loads all files in this directory at session start, making them available as context in every conversation. Rules don't need to be explicitly requested — they're always present.

## Using Rules

Rules are passive context — the agent reads and follows them as part of its operating instructions. No tool call is needed to load them.

## Creating a Rule

1. Create a markdown file in `.claude/rules/` with frontmatter:

```yaml
---
includes: "*"
governed_by:
  - .claude/rules/ocd-design-principles.md
---
```

2. Write behavioral guidance in the body — when to do what, trigger conditions, operational patterns. Rules define agent behavior, not file content standards (those belong in conventions).

3. Run `/ocd-init` to register the rule in the governance database.

## Frontmatter Fields

Same fields as conventions:

- **`includes`** (required) — typically `"*"` for rules since they apply universally. Specific patterns are possible but uncommon for rules.
- **`excludes`** (optional) — patterns to exclude from matching.
- **`governed_by`** (optional) — governance entries this rule builds on. Defines evaluation ordering.

## Current Rules

- **`ocd-design-principles.md`** — foundational principles governing all artifacts and agent behavior. Root of the governance dependency chain — all other rules and conventions build on this.
- **`ocd-workflow.md`** — project-specific operational patterns for day-to-day work.
- **`ocd-system-documentation.md`** — standards for system-level documentation (README.md, architecture.md).
- **`ocd-process-flow-notation.md`** — structured notation for agent workflows used in skill definitions.

## Relationship to Conventions

Rules govern agent behavior (always loaded, universal). Conventions govern file content (loaded on demand, pattern-matched). See `.claude/conventions/README.md` for the conventions system.

Both share the same frontmatter format and governance infrastructure.
