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

## Governance Lockdown (2026-04-13)

Systematic walkthrough of the governance chain supporting evaluate-skill and evaluate-governance. All foundational rules and conventions locked down through direct walkthrough, then both evaluation skills aligned against them.

**Rules locked down:**

- design-principles.md
- process-flow-notation.md (major rewrite: Call/Spawn/Error Handling, reorder, keyword formatting)
- markdown.md (promoted from convention to rule; added Special Characters)
- log-routing.md
- system-documentation.md (Documentation Currency moved to evaluate-documentation skill responsibility)
- workflow.md

**Conventions locked down:**

- skill-md.md (major simplification; Body Structure at top; String Substitution → Environment Variables)
- evaluation-skill-md.md (restructured to Executor Rules + Agent Rules with compartmentalization framing)
- evaluation-triage.md
- architecture-md.md, claude-md.md, readme-md.md
- governance-md.md

**Skills aligned:**

- evaluate-skill SKILL.md (Call/Spawn syntax, Exit to caller, path-tracing for exercisable routes)
- evaluate-governance SKILL.md (aligned with new conventions, graph anomaly artifact removed — misalignments now flow as ordinary findings)
- Component files (_evaluation-workflow.md for both skills) aligned

## Unevaluated Against Locked-Down Governance

Skills and Python-related conventions that exist but have not been walked through against the new rules and conventions. Mark each as locked down after refactor verification.

**Skills** (ocd plugin unless noted):

- [ ] commit
- [ ] init
- [ ] log
- [ ] md-to-pdf
- [ ] navigator
- [ ] push
- [ ] status
- [ ] checkpoint (project-local)
- [ ] sync-templates (project-local)
- [ ] evaluate-documentation (tracked separately under Next Steps; redesign, not just align)

**Python-related conventions:**

- [ ] python.md
- [ ] testing.md
- [ ] mcp-server.md
- [ ] skill-init-py.md

The navigator MCP refactor is complete, so the navigator skill and mcp-server.md / python.md can use that as the concrete example informing the updated conventions.

## Next Steps

1. **Run evaluate-governance** against the locked-down chain to validate the governance graph topologically.
2. **Redesign evaluate-documentation** using the same approach as evaluate-skill. Incorporate the leaves-first traversal insight (parent docs describe subsystems generally; each subsystem's docs carry the detail) and the observation that documentation lives in non-obvious surfaces — CLI help text, module docstrings, MCP tool descriptions, frontmatter `description:` fields, header purpose statements — not just the canonical README/architecture/CLAUDE.md/SKILL.md files. The skill now also owns Documentation Currency enforcement (formerly in system-documentation.md).
3. **Check all validated system docs conform to the three-document model** — driven by the rebuilt evaluate-documentation skill, not by hand. This is the mass audit step; it runs skill-driven so drift in non-obvious surfaces is caught the same way drift in canonical documents is caught.

**Rationale for the ordering:** governance validation first to confirm the locked-down chain is self-consistent; then documentation work after evaluate-documentation is rebuilt, so the mass audit (step 3) runs against the new skill rather than being re-walked by hand.

## Open Items

- **Convention loading on read** — conventions fire when files are read, not just modified. Governance reads from disk on every call (no database), so this is purely about hook behavior.
- **`purpose-map/skill-migration.md`** — archival planning document for migrating the purpose-map evaluation workflow to a skill. References a stale component id (`c14 (Pit of Success)`) and the now-removed Pit of Success principle. Decide whether to action the migration or delete the document as abandoned planning.
- **Purpose-map stale components removed, needs orphaned** — c41 (friction server), c42 (decisions server), c43 (stash server) removed from DB. Needs n59 (friction signals) and n68 (ideas/observations) are now gaps. These needs remain valid but need rewiring to new file-based log system components once those are evaluated and rebuilt.

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
- `plugins/ocd/templates/rules/*.md` — rule templates (deployed to `.claude/rules/ocd/`)
- `plugins/ocd/templates/conventions/*.md` — convention templates (deployed to `.claude/conventions/ocd/`)
- `plugins/ocd/templates/patterns/*.md` — pattern templates (deployed to `.claude/patterns/ocd/`)
- `plugins/ocd/templates/logs/` — log type templates (deployed to `.claude/logs/`)
- `plugins/ocd/skills/*/SKILL.md` — skills
- `plugins/ocd/servers/navigator/` — navigator MCP server package
- `plugins/ocd/lib/governance/` — governance library (disk-only)
- `plugins/ocd/plugin/` — plugin framework (propagated to all plugins)
- `plugins/ocd/hooks/` — auto-approval and convention gate hooks
- `scripts/sync-templates.py` — template → deployed copy sync
