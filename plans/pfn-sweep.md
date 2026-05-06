# Prose → PFN sweep

Convert prose workflow descriptions in READMEs, ARCHITECTUREs, and SKILL.md files to Process Flow Notation. PFN compresses ~30–50% versus prose for procedural content while sharpening the structure agents parse.

## Goal

Every procedural section in the project's documentation reads as PFN — numbered steps, indentation-scoped blocks, mechanism-prefixed invocations. Prose is reserved for orientation, rationale, and reference content; procedure goes through the notation.

## Output

Per-document edits across the surface:

- Operational sections of `README.md` files
- Workflow descriptions in `ARCHITECTURE.md` execution-flow sections
- Procedures in `CLAUDE.md` and `SKILL.md` files that drift into prose paragraphs
- Per-system `workflows/<topic>.md` files (these should be PFN by convention but may have legacy prose)

## Sequence

1. Audit pass — identify procedural prose across the project tree. Likely candidates: skill workflows that mix PFN with prose, ARCHITECTURE files with execution-flow narrative, READMEs with multi-step setup instructions
2. Convert in batches by file type: skills first (highest leverage — every invocation pays), then ARCHITECTURE files, then READMEs
3. Update `process-flow-notation.md` rule if the sweep surfaces new patterns or needs

## Decisions

- Conversion targets only true procedures — content with discrete sequential steps. Reference content (tables, decision matrices, rule lists) stays as prose or structured prose
- The PFN spec loads once per session as a memory rule; converting more procedures amortizes that cost across more workflows

## Open questions

- Are there documents whose prose form is load-bearing (e.g., agent-facing reading orders that work better as narrative)? Identify during the audit pass
- Should this sweep happen during each system migration (PFN-on-conversion) or as a separate pass after migrations? Per-system probably wins — content is fresh and the migrator already has the system loaded

## Status

Not started. Lands naturally during system migrations; a focused sweep can fill any remaining prose-procedure gaps afterward.
