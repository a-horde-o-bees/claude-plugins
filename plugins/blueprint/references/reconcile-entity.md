# Entity Reconciliation Procedure

## File Map

### Dependencies
```
.claude/skills/blueprint/blueprint_cli.py
docs/2-assessment-criteria.md
```

Universal procedure for updating entity notes, description, and relevance. Applied any time an agent touches an entity — discovery, research, dedup reconciliation, or reassessment.

## Notes

### Decision Procedure

For each existing note, classify against new information:
- Still accurate, not superseded by new findings — keep
- Contains outdated value — replace in place via `update note --note-id N_ID --note "corrected fact"`
- Disproven, redundant, or no longer relevant — remove via `remove notes --entity-id ID --note-ids N_ID`

Then add genuinely new observations not already captured: `upsert notes --entity-id ID --notes "new fact"`

### Contradiction Resolution

When existing notes conflict with new information:
- Prefer recent over old
- Prefer specific over general
- Replace contradicted note in place — do not append competing note

### Incorrect Facts

When agent has evidence note is wrong: remove it or replace with correct fact. Do not reference old incorrect value. Do not write correction-style notes ("was X, now Y"). Do not preserve inaccurate information in any form. Notes state current understanding only.

### Quality

Each note is single atomic fact that stands alone. Include specific names, numbers, and context so note is meaningful without reference to other notes. Do not summarize or editorialize. Accuracy matters more than completeness.

### Guards

- Do not write notes about where entity was found (e.g., "listed on X", "also referenced on Y") — provenance is tracked in `url_provenance` table
- Do not add note that restates existing note with updated values — replace existing note instead
- Do not write notes that reference previous incorrect values ("was X, now Y") — state current understanding only

## Description

One sentence stating what entity is and its primary approach or distinguishing characteristic. Notes hold all specific facts — description never lists features, counts, or claims.

Good: "Distributed task queue with priority scheduling and dead-letter recovery"
Bad: "Relevant tool with good adoption" (too vague, no identity)
Bad: "Platform with 30 modules, 16 plugins, 7 modes, claims 2x speed" (feature inventory belongs in notes)

If current description is vague, lists features, or references stale information — rewrite it. Same current-understanding-only rule as notes.

## Relevance

Reassess against assessment criteria (from `docs/2-assessment-criteria.md`) with full picture of combined knowledge. If agent's assessment warrants different score, update it. Do not preserve previous score out of deference — latest assessment with most information is authoritative.

## Adjacent Entity Discovery

While examining any entity, if you encounter links to other relevant entities not yet in the database, register them using the registration flow from your agent prompt. Use the current entity's URL as `--source-url` for provenance.

**One-hop limit:** Adjacent discoveries are bare registrations only — do not apply this reconciliation procedure to them, do not visit their pages, do not follow their links. Capture only what is visible from the page you are already reading. The discovered entity enters the database at stage `new` for future processing.
