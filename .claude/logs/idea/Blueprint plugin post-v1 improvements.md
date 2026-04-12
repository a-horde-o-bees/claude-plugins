# Blueprint plugin post-v1 improvements

## Purpose

Identified during best-practices research session. Deferred to post-v1.

1. **External research ingestion** — add --source route to /blueprint-research for parsing existing documents into entity registrations
2. **Conditional measure clearing** — only clear measures when criteria changed, not when entities added
3. **PFN formalization gaps** — missing numbered steps in Phase 1 and Phase 3 workflows
4. **Static content directory recipe** — add GitHub README/curated list recipe to directory-traversal.md
5. **Duplicate resolution timing** — find-duplicates should only run within deep research resolve-duplicates workflow
6. **Phase 1 gate criteria** — surface metrics at Phase 1 gate for data-backed readiness check
