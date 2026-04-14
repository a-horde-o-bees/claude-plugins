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

## V1 Readiness Backlog

All outstanding work before the marketplace goes public. Phased by dependency order. Each phase's items run in parallel internally; phases depend on the prior phase's completion. Check items as completed. Log entries under `.claude/logs/` carry the detail for each item where applicable.

### Phase 0 — Low-hanging fruit

Quick audits and fixes with no dependencies.

- [x] **Cross-skill reference refactor + skill-md convention correction** — A/B probe between `/ocd:status` (folder-derived) and `/ocd:status-alt` (frontmatter `name:`) established: folder-derived names resolve via Skill tool only when qualified; frontmatter-declared names resolve both qualified and unqualified. Concrete failure was `/checkpoint` calling `skill: /commit` and Skill tool returning "Unknown skill". Resolution: (1) convention rewritten — `name:` is now required on every skill, with the rationale embedded in the field description; (2) new Cross-Skill References section in `skill-md.md` mandates `/plugin:skill` form for plugin skill targets; (3) `name:` added to every SKILL.md across ocd, blueprint, and project-local; (4) every `skill:` invocation in Workflow blocks converted to qualified form; (5) PFN rule examples updated to show qualified form. Ocd 0.0.236, blueprint 0.0.64.

### Phase 1 — Foundation cleanups

Must land before code-building phases. These two cleanups correct existing convention violations that would compound if built on.

- [ ] **`cli.py` → `__main__.py` convention cleanup** — see `.claude/logs/problem/cli.py overrides __main__.py convention.md`. Affects `lib/governance/cli.py`, `servers/navigator/cli.py`. Rename and update callers.
- [ ] **Logging convention drop + dead declarations** — see `.claude/logs/problem/Logging convention drop and dead logger declarations.md`. Drop Logging subsection from `python.md`; remove 3 unused logger declarations in navigator files; clean misleading `__all__` comment.

### Phase 2 — Python-related convention lockdowns

Walk each convention against its current consumers and mark locked down. Navigator's completed MCP refactor is the concrete example informing `mcp-server.md` and `python.md`.

- [ ] `python.md` (will incorporate Phase 1 logging drop and `__future__` annotation clarification already committed)
- [ ] `testing.md`
- [ ] `mcp-server.md`
- [ ] `skill-init-py.md`

### Phase 3 — Remaining skill lockdowns

Each skill walked against the locked-down rules and conventions.

- [ ] `commit`
- [ ] `init`
- [ ] `log`
- [ ] `md-to-pdf`
- [ ] `navigator`
- [ ] `push`
- [ ] `status`
- [ ] `checkpoint` (project-local)
- [ ] `sync-templates` (project-local)

### Phase 4 — `update-system-docs` implementation

Scaffold committed in 986ddd2. Implementation work picks up from the scaffold. See `.claude/logs/idea/Replace evaluate-documentation with reality-first update-system-docs.md` for full design and follow-up list.

- [ ] Discovery CLI — `plugins/ocd/skills/update-system-docs/__main__.py` + `_discovery.py`
- [ ] Fact-bundle builder — Python module under skill dir; ast-based; called by per-system agents
- [ ] Navigator schema extension for `doc_verified_at` hash markers
- [ ] `mark-verified` CLI subcommand for post-verification hash updates
- [ ] **`ast.parse` reliability probe** — worktree prototype that ast-parses every `.py` file in the project and reports failures. Confirms the fact-bundle builder's foundation before relying on it.
- [ ] **Idempotence verification** — run the skill twice on unchanged reality; assert second run produces zero diff. Core design promise; must be validated before v1.
- [ ] End-to-end test on `lib/governance`; calibrate prompts based on observed false-positives / false-negatives
- [ ] Iterate until stable

### Phase 5 — Mass documentation audit

Run `update-system-docs` against the full project to create / regenerate all canonical docs and verify non-obvious surfaces. Review, iterate, repeat until stable.

- [ ] First full-project run
- [ ] Review generated docs against intent; tune prompts for observed gaps
- [ ] Re-run until output converges
- [ ] Delete old `evaluate-documentation` skill (replaced by `update-system-docs`)

### Phase 6 — Pre-public release checks

- [ ] Run `evaluate-governance` on full chain — confirms locked-down chain is self-consistent
- [ ] Verify every system has required docs per `system-documentation.md`
- [ ] Marketplace manifest sanity check (`.claude-plugin/marketplace.json` accurate; versions aligned)
- [ ] Update root-level `README.md` and `architecture.md` for external consumers
- [ ] Cut v1.0.0 on plugins; tag release

## Open Items (deferred)

These survive but are not v1 blockers:

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
