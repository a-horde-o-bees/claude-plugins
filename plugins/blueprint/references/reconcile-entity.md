# Entity Reconciliation Procedure

Universal procedure for updating entity notes, description, and relevance. Applied any time agent touches entity — discovery, research, dedup reconciliation, or reassessment.

## Notes

### Decision Procedure

For each existing note, classify against new information:
- Still accurate, not superseded — keep
- Contains outdated value — replace via `set_note({note_id: "N_ID", text: "corrected fact"})`
- Disproven, redundant, or no longer relevant — remove via `remove_notes({entity_id: "ID", note_ids: ["N_ID"]})`

Then add genuinely new observations not already captured: `add_notes({entity_id: "ID", notes: ["new fact"]})`

### Contradiction Resolution

When existing notes conflict with new information:
- Prefer recent over old
- Prefer specific over general
- Replace contradicted note in place — do not append competing note

### Incorrect Facts

When agent has evidence note is wrong: remove or replace with correct fact. Do not reference old incorrect value. Do not write correction-style notes ("was X, now Y"). Do not preserve inaccurate information in any form. Notes state current understanding only.

### Quality

Each note is single atomic fact that stands alone. Include specific names, numbers, and context so note is meaningful without reference to other notes. Do not summarize or editorialize. Accuracy matters more than completeness.

### Guards

- Do not write notes about where entity was found (e.g., "listed on X", "also referenced on Y") — provenance tracked in `url_provenance` table
- Do not add note restating existing note with updated values — replace existing note instead
- Do not write notes referencing previous incorrect values ("was X, now Y") — state current understanding only

## Description

One sentence stating what entity is and its primary approach or distinguishing characteristic. Notes hold all specific facts — description never lists features, counts, or claims.

Good: "Distributed task queue with priority scheduling and dead-letter recovery"
Bad: "Relevant tool with good adoption" (too vague, no identity)
Bad: "Platform with 30 modules, 16 plugins, 7 modes, claims 2x speed" (feature inventory belongs in notes)

If current description is vague, lists features, or references stale information — rewrite it. Same current-understanding-only rule as notes.

## Relevance

Reassess against assessment criteria (from `blueprint/2-assessment-criteria.md`) with full picture of combined knowledge. If assessment warrants different score, update it. Do not preserve previous score out of deference — latest assessment with most information is authoritative.

## Adjacent Entity Discovery

While examining any entity, if links to other relevant entities not yet in database are encountered, register them with mode `unclassified` and use current entity URL as `source_url` for provenance:

```
register_entity({name: "Name", url: "https://...", description: "One sentence", relevance: 0, modes: ["unclassified"], source_url: "https://current-entity-url"})
```

Valid modes: `example`, `directory`, `context`, `unclassified`. Adjacent discoveries always use `unclassified` — the orchestrator classifies them after the research wave completes via classify-modes agent (`${CLAUDE_PLUGIN_ROOT}/references/classify-modes.md`).

**One-hop limit:** Adjacent discoveries are bare registrations only — do not apply this reconciliation procedure, do not visit their pages, do not follow their links. Capture only what is visible from page already being read. Discovered entity enters database at stage `new` for future processing.
