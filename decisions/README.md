# Decisions

Architecture decisions organized by topic. Each file is the living record of current position — updated when new considerations shift direction, not appended with conflicting entries.

## When to Record

Record decisions where alternatives were considered and rejected, or where the reasoning is not derivable from code or conventions. The test: if an agent arriving fresh would need to re-evaluate from scratch because the WHY is not in the code, record it.

Do not record:
- Choices dictated by convention with no alternatives considered
- Implementation details within a single file
- Standard patterns obvious from reading the code

## Format

One file per topic. Descriptive names, no prefixes. Keep entries concise — scannable, not essays.

Each file contains:

- **Context** — what problem or constraint the decision addresses
- **Options considered** — alternatives with trade-offs; disqualified options note why
- **Decision** — current choice
- **Consequences** — what this enables and constrains

## Updating

When a decision changes: reorganize the file to reflect current understanding. Shift previous choice into options with disqualification rationale, document new factors, update decision and consequences. Complete reorganization is expected — these are living documents, not append-only logs. Git history preserves evolution.
