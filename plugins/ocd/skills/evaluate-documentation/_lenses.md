# Documentation Evaluation Lenses

Domain-specific criteria for each lens when evaluating documentation files.

## Conformity

Evaluate each file against its matched convention:

- **architecture-md** — purpose statement, content sections (layers, components, relationships, schema, patterns), nesting (subsystem summary not re-explanation), structure follows system architecture, currency (current state only)
- **README-md** — purpose statement, content sections (what it does, installation, configuration, usage, dependencies), nesting (subsystem purpose not re-explanation), structure follows user journey, currency

Cite specific convention requirements with each finding.

## Coherence

Cross-file consistency evaluated after all individual files are read.

### Progressive Disclosure

For each parent-child system pair:
- Parent architecture.md describes subsystem role without re-explaining internals — link to child
- Parent README.md describes subsystem purpose without re-explaining usage — link to child
- Each layer is complete at its depth — a reader who stops at any level has coherent understanding

### Cross-Document Consistency

- Same concept described consistently across all docs of the same type
- No contradictions between parent and child descriptions of the same subsystem
- Terminology alignment — same names for same things across documents

### Completeness

- Every system has both required docs (architecture.md and README.md)
- Every subsystem described in parent docs has its own docs
- No orphaned references to docs that don't exist

## Prior Art

- Does the documentation structure follow established patterns (README conventions, architecture decision records, system documentation norms)?
- Are there standard sections that consumers would expect (e.g., Contributing, License, Changelog for README)?
- Does the nesting pattern follow progressive disclosure as practiced in well-documented open-source projects?
- If deviating from standard patterns, is the deviation justified?
