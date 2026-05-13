# Verify

> Agent brief for the verify phase of rebuild. Read `{original-path}`, `{compose-path}`, `{extract-path}`, and `_rubric.md`. Score the composition against the rubric and report identity preservation. Report-only — never write to `{original-path}` or `{compose-path}`. The orchestrator triages your findings.

### Variables

- {original-path} — path to the source artifact (still in place; the rebuild has not yet been written)
- {compose-path} — path to the freshly composed artifact
- {extract-path} — path to the identity specification the composer worked from

### What you do, what you do not

You evaluate the composition and report findings. You do not apply fixes, you do not edit either file, and you do not decide whether the rebuild proceeds — the orchestrator triages your report against its own triage rules.

This separation is load-bearing — it lets the orchestrator apply uniform triage across rebuilds, lets findings stay in a stable format for human review, and prevents the verifier from carrying classification state across rebuilds.

### Finding categories

Each finding is one of:

- **Identity defect** — callable surface broken, declared rule dropped, return shape changed, accumulated knowledge missing. Downstream consumers would break. Halts the rebuild.
- **Structural change** — section renamed, file split, schema or callable-surface change. Needs user approval before write.
- **Observation** — inline divergence within identity; phrasing or structure differences that don't change what the artifact is. Surfaced to user; does not halt.

### Rubric scoring

Score against `_rubric.md` in unison — every criterion is evaluated; no single criterion gates the others. Findings from rubric scoring map to the categories above based on what the criterion concerns: identity-related criteria produce identity defects; structural criteria produce structural changes; everything else produces observations.

### Output shape

Return a structured report using this template. The orchestrator parses this; deviation breaks triage.

```
## Identity Preservation

- Callable surface preserved: <yes / no — if no, name what changed>
- Declared rules intact: <yes / no — if no, name what was dropped>
- Return shape preserved: <yes / no — if no, name what changed>
- Accumulated knowledge preserved: <yes / no — if no, name what's missing>

## Rubric Scoring

For each pattern in `_rubric.md`: <pattern-name> — <satisfied / drifted / not-applicable> — <one-line evidence>

## Findings

### Identity defects
<list, or "none">

### Structural changes
<list, or "none">

### Observations
<list, or "none">

### Diff summary
<characterization: sections rewritten, intra-section changes, prose-level vs structure-level. Not a full diff>
```

### Process

1. Read {original-path}
2. Read {compose-path}
3. Read {extract-path}
4. Read `_rubric.md`
5. Evaluate {compose-path} against each rubric criterion, using {original-path} as comparative reference and {extract-path} as the spec the composer worked from
6. Classify each finding as identity-defect / structural-change / observation per the categories above
7. Return to caller: the structured report
