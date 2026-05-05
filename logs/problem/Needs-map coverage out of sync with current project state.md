# Needs-map coverage out of sync with current project state

The needs-map data in `.claude/ocd/needs-map/needs-map.db` has not kept pace with recent project additions. Components and principles added since the last walk are missing or partially represented; the live database no longer reflects the current scope of the project.

## Known gaps

- **Graceful Degradation principle is absent.** All 22 other top-level design principles in `plugins/ocd/systems/rules/templates/design-principles.md` have entries in the `components` table (verified by direct query against needs-map.db: 63 components total, zero matches for Graceful Degradation). Surfaced while pulling per-principle rationales for a LinkedIn post; the principle had to be paraphrased from the principle text rather than the needs-map's failure-mode framing.
- **More gaps suspected.** Graceful Degradation is not believed to be the only missing entry. A full audit pass is needed to enumerate what's stale across components and needs.

## Audit scope

- Walk every level-2 heading in `plugins/ocd/systems/rules/templates/design-principles.md` against the `components` table to identify missing principles.
- Walk every system / hook / skill / library under `plugins/ocd/systems/` against the `components` table to identify missing infrastructure components.
- For each gap, run `/ocd:needs_map` to add the entry with proper failure-mode framing rather than paraphrasing.

## Suspected fix shape

- A `/ocd:needs_map` walk that adds missing components and connects them to existing or new needs.
- Possibly a periodic re-scan discipline (e.g., as part of `/checkpoint`) to detect new components without entries — separate from the data fix itself.

## Origin

Surfaced 2026-05-04 during LinkedIn post #1 drafting in the job-search project. The needs-map was queried for design-principle rationales to ground value-forward summaries on a public-facing post; Graceful Degradation came up missing. Aaron noted the gap is likely broader than this single principle.
