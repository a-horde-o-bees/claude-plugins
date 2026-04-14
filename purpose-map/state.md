# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Scope and Boundaries

This evaluation is in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must be re-justified through live invention before v1 ships):**

- Design principles
- ocd rule files: design-principles, workflow, system-documentation, process-flow-notation, log-routing, markdown
- ocd conventions
- ocd patterns
- ocd servers: navigator (thin MCP adapter under `servers/navigator.py`)
- ocd libraries: navigator (under `lib/navigator/`), governance (disk-only)
- ocd log templates and deployed entries (file-based, no MCP)
- ocd skills: init, status, navigator, log, audit-static, audit-governance, commit, push, md-to-pdf, update-system-docs
- Plugin infrastructure: plugin framework, hooks, `run.py` launcher, sync-templates
- Project-level infrastructure: pytest configs, `scripts/test.sh`, fixtures, plugin manifest

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- blueprint plugin and its entire component tree
- adhd plugin (no `plugins/adhd/` directory yet)

**Re-add filter:** components that exist in v1 but cannot make the unmet pointer in v2 are not added to v2. They are removed from the project. The model is the audit; the rebuild has teeth.

## V1 Readiness Backlog

Phased by dependency order. Each phase's items run in parallel internally; phases depend on prior phase completion. Detail for completed phases lives in git history and in `.claude/logs/` entries; this file holds only the resumable work.

### Phase 0 — Low-hanging fruit — ✓ done

Skill-name qualification ruleset: `name:` frontmatter required; every agent-emitted plugin-skill reference uses `/plugin:skill`. Rule lives in `design-principles.md` Agent-First Interfaces.

### Phase 1 — Foundation cleanups — ✓ done

lib/servers architectural split (domain libraries under `lib/`, thin MCP adapters under `servers/`). Logging convention dropped. Dead logger declarations removed.

### Phase 2 — Python-related convention lockdowns — ✓ done

Atomicity pass across `python.md`, `testing.md`, `mcp-server.md`. `skill-init-py.md` merged into `python.md` *Init/Status Contract*. Trigger section removed from skill-md convention and all 10 consumer skills. Consumer audit: qualified-reference sweep; `paths_remove` refactored to `mode` parameter; Error Handling rule rewritten with purpose embedded.

### Phase 3 — Remaining skill lockdowns

Each skill audited via `/ocd:audit-static` against the locked-down rules and conventions.

- [ ] `commit`
- [ ] `init`
- [ ] `log`
- [ ] `md-to-pdf`
- [ ] `navigator`
- [ ] `push`
- [ ] `status`
- [ ] `audit-governance`
- [ ] `audit-static` (self-audit after rewrite)
- [ ] `checkpoint` (project-local)
- [ ] `sync-templates` (project-local)

### Phase 4 — `update-system-docs` implementation

Scaffold committed in 986ddd2. Implementation work picks up from the scaffold. See `.claude/logs/idea/Replace evaluate-documentation with reality-first update-system-docs.md` for full design and follow-up list. (evaluate-documentation skill itself was deleted alongside the audit-* family rename.)

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

### Phase 6 — Pre-public release checks

- [ ] Run `audit-governance` on full chain — confirms locked-down chain is self-consistent
- [ ] Verify every system has required docs per `system-documentation.md`
- [ ] Marketplace manifest sanity check (`.claude-plugin/marketplace.json` accurate; versions aligned)
- [ ] Update root-level `README.md` and `architecture.md` for external consumers
- [ ] Cut v1.0.0 on plugins; tag release

## Open Items (deferred)

Non-v1-blocking:

- **Convention loading on read** — conventions fire when files are read, not just modified. Governance reads from disk on every call, so this is purely about hook behavior.
- **`purpose-map/skill-migration.md`** — archival planning doc referencing a now-removed principle. Decide whether to action the migration or delete as abandoned planning.
- **Purpose-map stale components removed, needs orphaned** — c41 (friction server), c42 (decisions server), c43 (stash server) removed. Needs n59 (friction signals) and n68 (ideas/observations) are now gaps. Remain valid; rewire to new file-based log system components when those are evaluated and rebuilt.
- **Logged problems awaiting action** — governance test-coverage thin vs navigator; `test_convention_agent.py` lacks git worktree isolation. See `.claude/logs/problem/`.
- **Print() usage review** — deferred from Phase 1 logging drop. See the logging log entry.

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
- `plugins/ocd/servers/navigator.py` — navigator MCP adapter (thin wrapper over `lib/navigator/`)
- `plugins/ocd/lib/navigator/` — navigator domain library (facade + CLI + internals)
- `plugins/ocd/lib/governance/` — governance library (disk-only)
- `plugins/ocd/plugin/` — plugin framework (propagated to all plugins)
- `plugins/ocd/hooks/` — auto-approval and convention gate hooks
- `scripts/sync-templates.py` — template → deployed copy sync
