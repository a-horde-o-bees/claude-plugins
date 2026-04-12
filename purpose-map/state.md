# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Scope and Boundaries

This evaluation is in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must be re-justified through live invention before v1 ships):**

- Design principles
- ocd rule files: design-principles, workflow, system-documentation, process-flow-notation, log-routing
- ocd conventions
- ocd patterns
- ocd servers: navigator (MCP server + CLI)
- ocd libraries: governance (disk-only, no MCP)
- ocd log templates and deployed entries (file-based, no MCP)
- ocd skills: init, status, navigator, log, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf
- Plugin infrastructure: plugin framework, hooks, `run.py` launcher, sync-templates
- Project-level infrastructure: pytest configs, `scripts/test.sh`, fixtures, plugin manifest

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- blueprint plugin and its entire component tree
- adhd plugin (no `plugins/adhd/` directory yet)

**Re-add filter:** components that exist in v1 but cannot make the unmet pointer in v2 are not added to v2. They are removed from the project. The model is the audit; the rebuild has teeth.

## Next Steps

1. **Move template content under `templates/`** — `rules/`, `conventions/`, `patterns/`, `logs/` are all template content that deploys to `.claude/`. Move into `plugins/ocd/templates/{rules,conventions,patterns,logs}/` to separate "content that deploys" from "code that runs." Update deploy_* functions, sync-templates, guard-templates, CLAUDE.md, architecture.md, and purpose-map component paths. Delete sub-level docs (`rules/README.md`, `rules/architecture.md`, `conventions/README.md`, `conventions/architecture.md`) — governance explanation belongs at plugin root level. Lowercase all governance filenames. Delete empty `references/` directory. Delete `tools/auto_convergence.py` (YAGNI — `--auto` feature does not exist).
2. **Update purpose-map component paths** — multiple refactors have made component paths stale. Update paths as encountered during evaluation, not as a bulk sweep.
3. **Redesign evaluate-skill** using the same needs-first approach as evaluate-governance, cross-referencing the patterns established by the governance skill's holistic single-pass model.
4. **Redesign evaluate-documentation** using the same approach. Incorporate the leaves-first traversal insight (parent docs describe subsystems generally; each subsystem's docs carry the detail) and the observation that documentation lives in non-obvious surfaces — CLI help text, module docstrings, MCP tool descriptions, frontmatter `description:` fields, header purpose statements — not just the canonical README/architecture/CLAUDE.md/SKILL.md files.
5. **Check all validated system docs conform to the three-document model** — driven by the rebuilt evaluate-documentation skill, not by hand. This is the mass audit step; it runs skill-driven so drift in non-obvious surfaces is caught the same way drift in canonical documents is caught.

**Rationale for the ordering:** template reorganization first so all subsequent work references correct paths. Documentation work backloaded until the evaluate-documentation skill is rebuilt, so the mass audit (step 5) does not have to be re-walked when the skill lands.

## Open Items

- **Convention loading on read** — conventions fire when files are read, not just modified. Governance reads from disk on every call (no database), so this is purely about hook behavior.
- **`purpose-map/skill-migration.md`** — archival planning document for migrating the purpose-map evaluation workflow to a skill. References a stale component id (`c14 (Pit of Success)`) and the now-removed Pit of Success principle. Decide whether to action the migration or delete the document as abandoned planning.
- **Purpose-map stale components removed, needs orphaned** — c41 (friction server), c42 (decisions server), c43 (stash server) removed from DB. Needs n59 (friction signals) and n68 (ideas/observations) are now gaps. These needs remain valid but need rewiring to new file-based log system components once those are evaluated and rebuilt.
- **Governance evaluation paused at Level 1** — Level 0 clean, Level 1 observations applied but not verified. Conventions are stale from refactoring — consider redesigning evaluate-documentation or evaluate-skill before continuing governance evaluation so conventions can be updated systematically first.

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
- `plugins/ocd/rules/*.md` — rule templates (deployed to `.claude/rules/ocd/`)
- `plugins/ocd/conventions/*.md` — convention templates (deployed to `.claude/conventions/ocd/`)
- `plugins/ocd/patterns/*.md` — pattern templates (deployed to `.claude/patterns/ocd/`)
- `plugins/ocd/logs/` — log type templates (deployed to `.claude/logs/`)
- `plugins/ocd/skills/*/SKILL.md` — skills
- `plugins/ocd/servers/navigator/` — navigator MCP server package
- `plugins/ocd/lib/governance/` — governance library (disk-only)
- `plugins/ocd/plugin/` — plugin framework (propagated to all plugins)
- `plugins/ocd/hooks/` — auto-approval and convention gate hooks
- `scripts/sync-templates.py` — template → deployed copy sync
