---
log-role: reference
---

# Decision

Non-obvious choices where alternatives were considered and rejected, or where the reasoning is not derivable from code or conventions. Preserves rationale so future sessions don't re-explore rejected alternatives.

Decisions are grouped by subject — one file per subject, multiple decisions within. A subject is typically a plugin system (`navigator.md`, `sandbox.md`, `framework.md`) but can be a cross-cutting topic (`database.md`, `mcp.md`, `skill-authoring.md`) when decisions span systems.

## What Qualifies

A choice worth preserving for a future session that will not have access to the conversation where it was made.

## What Does Not Qualify

- Implementation details visible in the code
- Choices dictated by convention
- Standard patterns obvious from reading the source

If a fresh agent can derive the answer from the code, it is not a decision.

## File Structure

Each subject file opens with:

- Level-1 heading (`# <Subject>`) naming the subject in prose form.
- A short purpose paragraph stating what decisions this file collects.

Then one `## ` heading per decision, titled as a short descriptive phrase. Under each decision:

- `### Context` — what prompted the decision
- `### Options Considered` — alternatives with trade-offs
- `### Decision` — what was chosen and why
- `### Consequences` — what this enables and constrains

A decision without rationale devolves into a setting — future agents cannot tell whether the conditions still hold.

## Adding to an Existing Subject

When capturing a new decision for a subject that already has a file, append the decision as a new `## ` section. Order decisions within a file by logical dependency — foundational decisions first, applied/derived decisions later — so a reader sees rationale accumulate coherently rather than chronologically.

When a new decision extends or amends an earlier one, place it near the related decision with an explicit cross-reference (`See also: ## <Related Decision>`).

## Adding a New Subject

Create a new `logs/decision/<subject>.md`. Subject filenames use kebab-case (`skill-authoring.md`, not `Skill-Authoring.md`); the level-1 heading inside uses prose capitalization (`# Skill Authoring`).

Pick a subject name that reads well as a compact label and scopes naturally — a plugin system name when decisions cluster around one system, a cross-cutting topic when the decisions span systems. Cross-cutting subjects include the technical domain (`database`, `mcp`) rather than the system where the decision first materialized.

## Lifecycle

Kept current with project state. Update entries when direction changes. Subjects grow as new decisions land; prune when a decision is subsumed by a later one, or preserve both with a note indicating which is current if the historical trail matters.
