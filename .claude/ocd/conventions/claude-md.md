# CLAUDE.md Conventions

CLAUDE.md is agent-facing project instructions loaded into system prompt. Defines startup behavior, discovery procedures, preferences, and project-specific conventions. Overrides Claude's default behavior — instructions are followed exactly as written.

## Standard Sections

| Section | Description |
|---------|-------------|
| `## On Startup` | Commands or skills to run when conversation begins |
| `## Discovery` | How to find and load available patterns, conventions, and procedures |
| `## Tools` | CLI commands available and their usage |
| `## After Changes` | Post-modification tasks: sync project navigator |
| `## Rules` | Behavioral rules: when to stop, how to handle ambiguity, coding style |

Sections appear in this order. Not all sections are required for every project — include what is relevant.
