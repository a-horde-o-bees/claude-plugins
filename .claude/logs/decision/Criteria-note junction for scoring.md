# Criteria-note junction for scoring

## Purpose

Blueprint research relevance scores were set by agents making impressionistic judgments rather than counting explicit criteria.

## Context

Blueprint research relevance scores were set by agents making impressionistic judgments rather than counting explicit criteria. The assessment criteria file defined binary criteria, but the database had no structure to store per-criterion evaluations or link criteria to supporting evidence. Scores were not auditable, "insufficient information" was conflated with "fails criterion," and criteria changes required full re-evaluation with no surgical updates.

## Options Considered

**Cached integer only** — store relevance as a number on the entity, recompute by agent re-evaluation. No audit trail, no partial updates when criteria change, no distinction between "fails" and "not assessed."

**Entity-criteria table** — per-entity assessment with met/not_met/insufficient per criterion. Loses the connection to which notes support the assessment. Agent reasoning not traceable.

**Criteria-note junction** — link criteria definitions to entity notes with a quality (pass/fail). Assessment is computed from the links. Audit trail built into the structure.

## Decision

Criteria-note junction model with two tables:

- `criteria` — stores criterion definitions (id, type, name, gate description)
- `criteria_notes` — junction linking criterion to entity_note with quality (pass/fail)

Entity relationship is implicit: `criteria_notes.note_id` → `entity_notes.entity_id` → `entities`. No direct entity-criteria table needed.

### Resolution Logic

- Any "pass" link for a criterion-entity pair → criterion passed (pass supersedes fail)
- Only "fail" links → criterion failed
- No links → not assessed (absence, not stored)
- Hardline: if any hardline criterion resolves to "fail" → entity should be rejected
- Relevancy: count of distinct relevancy criteria with "pass" = cached relevance score

### ON DELETE CASCADE

`criteria_notes` uses `ON DELETE CASCADE` on both foreign keys. This deviates from other tables in the schema which use manual cascade in Python. Justified because `criteria_notes` is a pure junction table with no dependents — cascade is the correct relational pattern. When a criterion is removed, its links go with it. When a note is deleted (including by stage downgrade), its criteria links cascade automatically.

### Criteria Changes Are Surgical

When a criterion definition changes, only that criterion's links are deleted. All other criteria retain their links and assessments. This means partial criteria updates don't require full re-evaluation — only the changed criteria need reassessment.

### Relevance as Cached Compute

`entities.relevance` remains as a cached value for efficient sorting in `list_entities`. It is recomputed deterministically from criteria-note links by `compute_relevance`. The junction table is the source of truth; the cached field is a materialized view.

## Consequences

- Enables: auditable scoring (trace any score to specific notes), surgical criteria updates, "not assessed" as distinct from "fails," combined mode+criteria assessment in single agent pass
- Constrains: assessment agents must create criterion-note links (more tool calls than setting a number)
- Mitigation: assessment is a dedicated pass with its own reference document; agents link criteria to notes as part of evaluation, not as extra work
