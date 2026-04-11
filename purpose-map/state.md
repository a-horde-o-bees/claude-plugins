# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Scope and Boundaries

This evaluation is in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must be re-justified through live invention before v1 ships):**

- Design principles
- ocd rule files: workflow, friction, system-documentation, decisions, process-flow-notation, navigator
- ocd conventions
- ocd tools: navigator (facade + MCP server + CLI), plugin hooks, `run.py` launcher
- ocd skills: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf
- Project-level infrastructure: pytest configs, `scripts/test.sh`, fixtures, plugin manifest

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- blueprint plugin and its entire component tree
- adhd plugin (no `plugins/adhd/` directory yet)

**Re-add filter:** components that exist in v1 but cannot make the unmet pointer in v2 are not added to v2. They are removed from the project. The model is the audit; the rebuild has teeth.

## Next Steps

1. **Redesign evaluate-governance from the ground up based on n93** — needs-first, not patching the current implementation. This is the prototype for the needs-first skill redesign pattern.
2. **Validate the redesigned evaluate-governance** by spawning an agent to rebuild a doc set and checking effectiveness end-to-end before it becomes the template for other skills.
3. **Redesign evaluate-skill** using the same needs-first approach, cross-referencing the patterns established by evaluate-governance.
4. **Redesign evaluate-documentation** using the same approach. Incorporate the leaves-first traversal insight (parent docs describe subsystems generally; each subsystem's docs carry the detail) and the stashed note (project stash #17) that documentation lives in non-obvious surfaces — CLI help text, module docstrings, MCP tool descriptions, frontmatter `description:` fields, header purpose statements — not just the canonical README/architecture/CLAUDE.md/SKILL.md files.
5. **Check all validated system docs conform to the three-document model** — driven by the rebuilt evaluate-documentation skill, not by hand. This is the mass audit step; it runs skill-driven so drift in non-obvious surfaces is caught the same way drift in canonical documents is caught.

**Rationale for the ordering:** documentation work is backloaded until the evaluate-documentation skill is rebuilt, so the mass audit (step 5) doesn't have to be re-walked when the skill lands.

**Live context for step 1:** evaluate-governance is wired as c70 to n93 ("Ensure governance artifacts are conformant, followable, and coherent" under n20). Known implementation issues from the current build are recorded in the project friction database (items 1–4: missing sections, no checkpoint, no `--auto`, lens duplication). The redesign starts from n93, not from the current implementation. Layer H component evaluation remaining: evaluate-skill and evaluate-documentation — their redesigns in steps 3 and 4 also close out Layer H.

## Open Items

- **Convention loading on read** — project stash entry #7. Concerns conventions firing when files are read, not just modified. Might inform how navigator's `governance_match` is shaped during its evaluation.
- **`purpose-map/skill-migration.md`** — archival planning document for migrating the purpose-map evaluation workflow to a skill. References a stale component id (`c14 (Pit of Success)`) and the now-removed Pit of Success principle. Decide whether to action the migration or delete the document as abandoned planning.

## v1 Reference

The v1 database is preserved at `purpose-map-v1.db` (read-only). Use it to look up rationales for components being re-added — the rationale text is often portable with sharpening for the more-specific sub-need. v1 has 43 components, 97 addressing edges, and 19 roots. v1 ids are not preserved in v2 unless explicitly assigned.

Query example:

```bash
python3 -c "import sqlite3; db = sqlite3.connect('purpose-map/purpose-map-v1.db'); [print(r) for r in db.execute('SELECT * FROM components ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)')]"
```

## Key Files

- `purpose-map/CLAUDE.md` — tool documentation, schema, operational protocol (read this first)
- `purpose-map/purpose_map.py` — implementation
- `purpose-map/purpose-map.db` — live v2 database
- `plugins/ocd/rules/*.md` — OCD rule files (deployed copies in `.claude/rules/`)
- `plugins/ocd/conventions/*.md` — OCD conventions
- `plugins/ocd/skills/*/SKILL.md` — OCD skills
