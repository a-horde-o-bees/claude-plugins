# Overview

Index of all blueprint deliverables. Updated as phases complete.

Each file has a template in `${CLAUDE_PLUGIN_ROOT}/templates/`. Templates define:
1. What the file's purpose is
2. What information belongs in it
3. How to organize and format it

Templates do not reference which phases produce or consume them — phase orchestration is the skill's responsibility, not the file's.

## Project Definition (Phase 1)

| File | Purpose |
|------|---------|
| `1-scope.md` | Parent concept, in-scope and excluded areas |
| `2-goals.md` | Project goals and priority order |
| `3-assessment-criteria.md` | Hardline filters and relevancy assessment criteria |
| `4-effectiveness-criteria.md` | Criteria for evaluating discovered patterns and approaches |
| `5-constraints.md` | Implementation realities and environment requirements |
| `6-domain-knowledge.md` | Landscape structure and distilled research findings |

## Research Data (Phase 1-2)

| File | Purpose |
|------|---------|
| `data/state.md` | Phase progress tracker |
| `data/history.md` | Sequential stride log with timestamps |
| `data/research.db` | SQLite database: entities, notes, modes, measures, provenance |

## Analysis (Phase 3)

| File | Purpose |
|------|---------|
| `7-findings.md` | Cross-entity pattern analysis and measure-backed observations |
| `8-interpretation.md` | What findings mean for this project; actionable conclusions |

## Implementation (Phase 4)

| File | Purpose |
|------|---------|
| `9-blueprint.md` | Dependency-ordered implementation plan; final deliverable |
