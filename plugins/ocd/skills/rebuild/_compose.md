# Compose

> Agent brief for the compose phase of rebuild. Read `{extract-path}` and `_rubric.md`; write the rebuilt artifact to `{compose-path}`. The original artifact is set aside and is NOT available to this agent — by design. The extract is the authoritative specification; the rubric is the discipline applied to composition.

### Variables

- {extract-path} — path to the identity specification produced by the extract phase
- {compose-path} — path where the rebuilt artifact is written
- {corrective-guidance} — optional. Identity-defect findings from a prior verify pass on a prior compose attempt. Present only on retry. Each entry names a specific identity gap that must be addressed in this compose

### Authoritative-state cue

Trust the specification at {extract-path} as the true description of what the artifact must be. The original is set aside; you do not have access to it and should not seek it. If you find yourself reasoning about how the original phrased something, abort that line of thought — you do not have access to that phrasing. Compose from the specification.

### Discipline in unison

Load `_rubric.md`. Every pattern in the rubric applies to this composition. The rubric is held in unison — do not satisfy one criterion at a time across sections; compose the entire artifact under all criteria simultaneously. Patch-flow is the failure mode the rubric guards against; applying patterns sequentially is patch-flow in disguise.

### Iron-law framings

- Reading the original at this phase = abort and restart. The extract is the contract. Reaching for the original is not a recovery move; it is the failure.
- Patching an existing draft of the spec rather than composing fresh = abort and restart. The artifact at {compose-path} is the output, not a working file.
- Eliding sections for brevity = never skip, omit, or elide content. Output the complete artifact — every section, every line. No `...`, no `[unchanged]`, no implied continuation.

### Rationalizations to reject

The following thoughts will arise during composition. Each is a sign of patch-flow leaking in, not a valid shortcut:

- "I'll just adjust this one line" → no; if the line needs changing, the whole section recomposes from the spec
- "The original probably said it well; I should match its phrasing" → no; you do not have access to the original; compose from the spec
- "This section is already conformant; I'll keep it as-is" → no; "keep" has no referent when there is no source to keep from; compose
- "Rebuilding will lose tested phrasing" → no; the verify phase scores identity preservation, not surface phrasing; phrasing is not identity
- "I remember roughly how this file looked" → no; memory is not the spec; compose from {extract-path} only

### Output

Write the complete artifact to {compose-path}. Frontmatter, sections, every line — the whole file, not a delta. The verifier will read this file as the candidate replacement; gaps, elisions, or placeholders are failure conditions.

### Corrective-guidance handling

When {corrective-guidance} is present, a prior compose attempt produced an artifact that failed identity preservation. The guidance names the specific gaps. Apply the same iron-law framings to the retry — do not read the prior compose, do not patch it. Compose fresh from {extract-path}, treating the corrective guidance as additional emphasis on which extracted elements must appear in this composition. The guidance is a pointer back into the spec, not a source of content.

### Process

1. Read {extract-path}
2. Read `_rubric.md`
3. If {corrective-guidance} is present: read it as additional emphasis on which extracted elements must appear; do not read the prior compose
4. Compose the entire artifact, applying every rule from the extract and every discipline from the rubric in unison
5. Write the complete result to {compose-path}
6. Return to caller: one-line confirmation that {compose-path} was written
