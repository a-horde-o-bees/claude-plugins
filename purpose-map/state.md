# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Status

**v2 evaluation pass — live invention from foundations up. Layers A and B complete. Layer C (Rules) is next.**

The previous pass (v1, snapshot at `purpose-map-v1.db`) revealed that root needs were too broad to support the "is this unmet?" test — n11 had 19 addressers, n13 had 16, making "covered" trivially true for any plausible component. The model was restructured to a tree of needs (`parent_id` on the `needs` table) with enforced wiring rules (no addressing roots, no addressing both an ancestor and a descendant). See `CLAUDE.md` for the new operational protocol and the *Router vs destination* discipline that surfaced from v1's analytical pass.

v2 starts with the 19 v1 root needs as roots (ids preserved: n1–n8, n11–n21), plus 16 pre-refined sub-needs (n22–n37) under the four most-saturated v1 needs (n6, n11, n13, n14). All 19 roots come in validated; the 16 pre-refined sub-needs come in unvalidated (they validate during live invention if they hold up).

**Layer A additions:**

- n1 revised: anchored to "across Claude Code projects" (was platform-agnostic). Two reactive refinements added under it: n38 (reach users other than the originator) and n39 (fit naturally into consumers' existing tooling). Both validated.
- c1 — Claude Code marketplace bundle. Addresses n38 (public github hosting) and n39 (marketplace structural conformance). Validated.
- c2 — OCD plugin packaging. Addresses n39 (plugin structural conformance, distinct mechanism layer from c1) and depends on c1. Validated as "minimum generic plugin" — its OCD-specific identity (the *what* it scopes) is captured in the description but not claimed as a distinctive justification. Sharpening deferred until later layers reveal a concern only this plugin instance can address.

The "convey purpose through name" need (raised during c2 evaluation) is a real candidate refinement under n11, but was deferred — refinement is reactive, and no current component depends on it for justification.

**Rules delivery foundation (added before Layer B so principles can structurally depend on it):**

- n26 refined with n40 (have universal agent guidance present from the start of every agent interaction). Validated.
- c3 — rules delivery mechanism. Templates in `plugins/ocd/rules/` deploy to `.claude/rules/` where Claude Code auto-loads them. Addresses n40, depends on c2. Validated.

**Layer B additions (21 design principles):** Each principle is its own component, depends on c3, and addresses one or more sub-needs through the encoded discipline. The failure-mode framing technique ("what would have had to go wrong for this to be needed?") drove the need wording — see `CLAUDE.md` *Writing needs* for the captured technique.

| Component | Principle | Addresses | New sub-needs introduced |
|-----------|-----------|-----------|--------------------------|
| c4 | Verify Against Reality | n34 (reworded) | — |
| c5 | Epistemic Humility | n35 (reworded) | — |
| c6 | Single Source of Truth | n36 (reworded) | — |
| c7 | Progressive Disclosure | n25 (reworded) | — |
| c8 | Economy of Expression | n41 | n41 (under n15) |
| c9 | Convention as Documentation | n42 | n42 (under n11) |
| c10 | YAGNI | n43 + n51 (multi-edge with c20) | n43 (under n16) |
| c11 | Make Invalid States Unrepresentable | n31 (reworded) | — |
| c12 | Fix Foundations, Not Symptoms | n44 | n44 (under n18) |
| c13 | Determinism by Default | n45 | n45 (under n11) |
| c14 | Idempotency | n46 | n46 (under n2) |
| c15 | Tool Positioning | n28 (reworded; n24 removed as duplicate) | — |
| c16 | Self-Describing Artifacts | n47 | n47 (under n11) |
| c17 | Reuse Before Create | n48 | n48 (under n3) |
| c18 | Agent-First Interfaces | n49 | n49 (under n13) |
| c19 | Confirm Shared Intent | n50 | n50 (under n21) |
| c20 | Principled Pushback | n51 | n51 (under n4) |
| c21 | Trigger Specificity | n33 (reworded) | — |
| c22 | Composability | n52 + n25 (multi-edge with c7) | n52 (under n18) |
| c23 | Separation of Concerns | n53 | n53 (under n18) |
| c24 | Resumability | n54 | n54 (under n2) |

**Pit of Success — finding (no component added):** During evaluation, the principle could not make the unmet pointer. Three of its four bullets are already covered by more specific principles (templates → c11 Make Invalid States Unrepresentable; domain tools → c13 Determinism by Default verbatim; auto-matching conventions → c9 Convention as Documentation + c15 Tool Positioning). The fourth bullet (graceful degradation when a dependency is unavailable) doesn't fit Pit of Success's "easier path" framing at all — it's about *failure mode design*, not ergonomic defaults. Pit of Success itself is a Trigger Specificity violation: it bundles multiple distinct mechanisms under one umbrella.

**Project-level action items (out of scope for the model — for the project rule files):**

1. **Remove Pit of Success from `plugins/ocd/rules/ocd-design-principles.md`.** Distribute its remaining-relevant content (the meta-claim "if doing the right thing is hard, the system is wrong") into existing principles as flavor.
2. **Add a new principle for graceful degradation** to `ocd-design-principles.md`. Working name: *Informative Failure* or *Graceful Degradation*. When the new principle is authored, evaluate it as a future Layer B component with its own sub-need for "prevent dependencies from failing silently or cryptically when unavailable."
3. **Add a new principle for file/component granularity** to `ocd-design-principles.md`. Working name: *File Granularity Follows Governance*. Surfaced during Layer C evaluation when the workflow rule revealed the same heterogeneous-file pattern as the design principles file. Files group by governance (shared load conditions, pattern, depends); components group by contribution. A file with multiple coherent sub-sections is fine when they share governance; split when they need different load conditions. This principle is adjacent to but distinct from Composability (which fires on context-capacity size) and Separation of Concerns (which is about responsibility boundaries within components, not file boundaries). When the principle is authored, evaluate it as a future Layer B component.

**General check that emerged during Layer C:** when evaluating any rule, ask *"is this an override of default behavior or a description of it?"* If the latter, the rule entry is vestigial and should be removed. Default-describing rules don't fire (because they have nothing to override), and they take up context that could be used for actual overrides. Captured in `CLAUDE.md` under *Override vs description*.

**MCP foundation lock-in (post-Layer-C reframe):** The evaluation pass shifted from survey-mode to fix-foundations-mode. Recognized the MCP pattern as the correct shape for process tooling. Locked in the foundation in dependency order: convention delivery (c36) → python.md (c37) → mcp-server.md (c38) → mcp-relational.md (c39) → navigator package (c40, combined backend + MCP server). Then migrated friction, decisions, and stash from rule-based / user-level skill to MCP servers via parallel agents.

**Step 3 migrations complete (subsequently restructured — see Step 4):**

- **c29 (friction rule)** → removed; replaced by **c41 (friction MCP)**. Same addressing edges (n59 signal preservation, n44 multi-edge with c12 Fix Foundations) plus n28/n49 from MCP shape.
- **c34 (decisions rule)** → removed; replaced by **c42 (decisions MCP)**. Same addressing edge (n61 multi-edge with c33 Capture Rationale) plus n28/n49.
- **Stash skill** → replaced by **c43 (stash MCP)**. New sub-need n68 under n2 (*Prevent the agent or user from losing ideas and observations when they can't be acted on immediately*).

**Step 4 — SQLite migration and unified verb standardization:**

All three record-keeping MCP servers (c41, c42, c43) rewritten from markdown-file storage to SQLite with WAL concurrency. Unified verb set (add, list, search, get, update, remove) replaces per-service naming. All records use id-based identity with summary + optional detail_md blob. Navigator (c40) CRUD tools renamed: paths_describe → paths_get (with multi-path support), paths_set → paths_upsert. Case-insensitive regex search across all three services. Old markdown storage (decisions.md, decisions/, .claude/stash/) removed after data migrated. Business logic separated into skill packages (`skills/<name>/_db.py` + `__init__.py`); servers are thin wrappers passing db_path from env vars. Stash uses separate project and user databases instead of scope column.

432 tests total (skill unit + server wiring unit + server integration), registered in `plugins/ocd/.mcp.json` with per-service DB env vars.

**Methodology evolution captured during this work:**

- Verification step (CLAUDE.md protocol step 8) — empirically verify functional claims before validating components
- File Granularity Follows Governance principle (in design principles) — files group by load conditions, components group by contribution
- Override vs description test (CLAUDE.md) — vestigial rule detection
- Capture Rationale principle (c33, in design principles) — rationale as first-class content
- Forward-looking rationale bullet (Capture Rationale) — transitional framing expires, forward-looking framing is permanent

Run `summary` and `needs` for live state.

## Scope and Boundaries

This evaluation is in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must be re-justified through live invention before v1 ships):**

- 22 design principles
- ocd rule files: workflow, friction, system-documentation, decisions, process-flow-notation, navigator
- ocd conventions (after navigator's `governance_match` is in place, since conventions depend on it for loading)
- ocd tools: navigator (facade + MCP server + CLI), plugin hooks (session_start, auto_approval), `run.py` launcher
- ocd skills: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf
- Project-level infrastructure: pytest configs, `scripts/test.sh`, fixtures, plugin manifest

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- `c24` blueprint plugin and its entire component tree
- `c25` adhd plugin (no `plugins/adhd/` directory yet)

**Re-add filter:** components that exist in v1 but cannot make the unmet pointer in v2 are not added to v2. They are removed from the project. The model is the audit; the rebuild has teeth.

## v1 Reference

The v1 database is preserved at `purpose-map-v1.db` (read-only reference). Use it to:

- Look up rationales for components being re-added — the rationale text is often portable (with sharpening for the more-specific sub-need)
- Cross-reference v1 component ids — they may or may not survive re-add. v1 ids are not preserved in v2 unless explicitly assigned (the v2 db assigns its own ids sequentially via `_next_id`).

The v1 db has 43 components, 97 addressing edges, and 19 needs as roots. Querying example:

```bash
python3 -c "import sqlite3; db = sqlite3.connect('purpose-map/purpose-map-v1.db'); [print(r) for r in db.execute('SELECT * FROM components ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)')]"
```

## Pre-refined Sub-trees

These were added before live invention began, based on patterns observed in v1's analytical pass. They are starting points, not exhaustive — refine further as live invention requires.

- **n6** (Prevent the user and agent from making the same mistake twice) → n30, n31, n32, n33
- **n11** (Reduce cognitive load for both user and agent) → n22, n23, n24, n25
- **n13** (Minimize friction between agent and system) → n26, n27, n28, n29
- **n14** (Reduce the gap between assumptions and how things actually behave) → n34, n35, n36, n37

The other 15 root needs (n1–n5, n7, n8, n12, n15–n21) are unrefined. They will be refined during live invention as components require sharper sub-concerns.

## Deferred Edge Reclamations

Carried over from v1. These are sub-needs that v1 incorrectly attached to operational rules (router pattern). When the destination components are re-added in v2, they should claim the relevant sub-needs.

- ~~**n14 sub-needs**~~ — reclaimed by c48 (test infrastructure) via n37 in Layer D.
- **n15** (wasted context tokens) — should be claimed by **navigator components** (the curated query shape). v1 attached this to navigator usage rule c34, also router-pattern.
- **n16** (wasted time) — same as n15. Belongs to navigator's discovery capabilities, not the rule that routes to them.

## Other Open Items

- **`c28` (Tool Positioning) had no recorded path in v1** — when re-adding, anchor target: `plugins/ocd/rules/ocd-design-principles.md#tool-positioning`.
- **Convention loading on read** — stashed in project stash DB (entry #7). Concerns conventions firing when files are *read*, not just modified. Might inform how navigator's `governance_match` is shaped during its evaluation.

## Modeling Decisions (this session)

- **n9 and n10 are gaps in the id sequence** — these were removed during the v1 simplification (refinement-related needs that turned out to be technical requirements, not business concerns). The gap is preserved as historical record; do not reuse the ids.

Durable modeling guidance has been promoted to CLAUDE.md: files-as-containers (*Files are containers, not components*), coverage exclusions (*Coverage exclusions*), cohesive vs parallel path strategy (*Source-Location Paths*), non-preventative needs (*Writing needs*).

## Worklist for Live Invention

Order of component re-add. Process from foundations up. For each candidate, follow the *Evaluating a component* protocol in CLAUDE.md.

### Layer A — Project containers and conceptual roots ✓ COMPLETE

1. ~~**claude-plugins root**~~ — dropped. Project root is implicit, like top-level needs without a parent. No distinctive mechanism survives v2's tighter unmet test.
2. ✓ **Marketplace** — c1, validated. Addresses n38 + n39.
3. ✓ **OCD plugin** — c2, validated as minimum generic plugin. Addresses n39 (distinct mechanism from c1). Depends on c1.

### Layer B — Design principles ✓ COMPLETE (21 of 22 evaluated)

21 principles wired as c4–c24 (see Layer B Additions table above for full mapping). Pit of Success was evaluated but not added — the principle bundles multiple mechanisms already covered by other principles, and surfaced a project-level action to restructure or replace it (see *Project-level action items*).

Graceful Degradation principle (to be authored) will become c25 when added to the rule file.

### Layer C — Rules ✓ COMPLETE

All four rule files fully decomposed into section-level components. Every section is a component; only purpose statements remain as structural metadata. File-as-container principle established: rule files are extensions of c3 (rule delivery), not independent components.

- **ocd-design-principles.md**: c4–c24, c33 (principles), c45 (recurrence heuristic), c46 (bullet form guidance)
- **ocd-workflow.md**: c25–c28 (sections)
- **ocd-system-documentation.md**: c30–c32 (sections), c44 (system boundaries)
- **ocd-process-flow-notation.md**: c35 (single cohesive component)
- Friction, decisions, navigator rules dissolved into MCP servers (c41, c42, c43, c40) during Step 3

### Layer D — Project-level infrastructure ✓ COMPLETE

- c47 — Module launcher (`run.py`). Addresses n70 (prevent per-entry-point bootstrap).
- c48 — Test infrastructure (`pyproject.toml`, `pytest.ini`, `conftest.py`, `test.sh`). Addresses n37 (exercise code through tests).
- c49 — Template sync (`sync-templates.py`). Addresses n71 (deployed/template alignment).
- c50 — Plugin CLI runner (`run-plugin.sh`). Addresses n72 (automate environment setup).
- c51 — AST extraction (`pyextract.py`). Addresses n73 (partial Python file reads).

Test files excluded from `uncovered` tracking — they're derivative of what they test, not independent components.

### Layer E — Navigator ✓ COMPLETE

c40 evaluated as cohesive package (glob path `plugins/ocd/skills/navigator/*` + `plugins/ocd/servers/navigator.py`). Three new edges added: n29 (stale detection), n74 (file-purpose capture — new sub-need under n22), n22→n74 refinement. SKILL.md consumed into c40 via glob; n74 ties its population workflow into the model. Stale rationales fixed (paths_describe → paths_get).

### Layer F — Plugin hooks ✓ COMPLETE

Three components, each with distinct addressing:
- c52 — `install_deps.sh` → n72 (automate environment setup)
- c53 — `session_start.py` → n70 (prevent per-entry-point bootstrap)
- c54 — `auto_approval.py` → n55 (directory enforcement) + n75 (permission prompt interruptions, new sub-need under n19)

`hooks.json` added as path to c2 (plugin packaging).

### Pre-Layer-G infrastructure work ✓ COMPLETE

Governance system changes driven by convention consumption analysis:

1. **Frontmatter rename**: `pattern` → `matches`, `depends` → `governed_by`, new `excludes` field. Clean break — no backward compatibility.
2. **Convention gate hook**: PreToolUse on Read/Edit/Write surfaces applicable conventions via `additionalContext`. Read is informational; Edit/Write is directive ("immediately refactor if non-conforming"). Replaces manual governance_match calls — the design principles bullet was removed.
3. **mcp-server/mcp-relational merge**: Single convention with `excludes: ["__init__.py", "_helpers.py"]`. New sections for standardized verbs, markdown detail storage, domain-specific operations. c39 absorbed into c38.
4. **Pattern matching**: Shared `matches_pattern` function supports basename, `**` prefix, and full-path matching. `mcp-server.md` uses `**/servers/*.py` for depth-independent matching.
5. **System documentation**: README.md + architecture.md for both conventions and rules systems.
6. **Convention consumption tests**: 22 backend tests (governance_match behavior) + 7 agent-level tests (`--run-agent` flag, spawns `claude -p`). All passing.
7. **Clean Break principle** added to design principles.

`governed_by` serves evaluation ordering only — not runtime convention loading. Runtime loading is handled by the convention gate hook.

### Layer G — Conventions ✓ COMPLETE

10 convention files as single components (c57–c64), each with one conformance sub-need under n8 (n77–n84). Simplified sub-need pattern: "Ensure [file type] files follow project standards." Existing n63/n64/n65 aligned to match. Convention dependencies follow `governed_by` chains: c59/c60/c61/c62 depend on c57 (markdown base), c63 depends on c37 (python), c64 depends on c62 (skill-md). c37 and c38 (pre-existing) unchanged.

Convention system documentation (README.md, architecture.md) added as paths to delivery components c3 (rules) and c36 (conventions).

### Layer H — Skills (in progress)

Completed: c65 init, c66 status, c67 commit, c68 push, c69 pdf, c70 evaluate-governance. Navigator already covered as c40.

Remaining: evaluate-skill, evaluate-documentation.

**Methodology refinements during Layer H:**

- **Duplication scan as precision lens** — when the scan surfaces mechanism differences, use the contrast to sharpen need descriptions on both the target need AND related needs exposed in the scan. Codified in CLAUDE.md step 5.
- **Preventative vs enabling framing** — "If we remove everything addressing this need, does something go wrong (preventative) or does something just not exist (enabling)?" Codified in CLAUDE.md writing guidelines.
- **Consequences vs addressing** — addressing edges map to needs directly addressed through primary mechanism, not downstream consequences. Wiring to every consequence dilutes the model. Codified in CLAUDE.md opening section.
- **n72 split** — "Automate environment setup" was too vague; split into n85 (dev invocation config), n86 (runtime dependency provisioning), n87 (governance deployment) using the duplication-scan precision lens.

**System documentation model update:**

Updated system documentation rule to three-document model: README.md + architecture.md (required for every system) + CLAUDE.md/SKILL.md (optional, when agent procedures exist). Document separation enforced — operational docs reference architecture.md, don't duplicate it. Root CLAUDE.md/architecture.md need refactoring to match.

**Evaluate skills redesign:**

evaluate-governance (c70) wired to n93 "Ensure governance artifacts are conformant, followable, and coherent" under n20. Friction items 1-4 document known implementation issues (missing sections, no checkpoint, no --auto, lens duplication). The skill needs redesigning from the ground up — starting from the need, not patching the current implementation. evaluate-skill and evaluate-documentation should follow the same needs-first approach after evaluate-governance is validated.

**Next steps (in order):**

1. Refactor root CLAUDE.md/architecture.md to match new three-document model (move architectural content out of CLAUDE.md)
2. Check all validated system docs conform to the updated model
3. Redesign evaluate-governance from the ground up based on n93
4. Test by spawning an agent to rebuild a doc set and evaluate effectiveness
5. Wire evaluate-skill and evaluate-documentation after evaluate-governance is validated

### Deferred (post-v1, dev branch)

- `c24` blueprint and entire subtree
- `c25` adhd (no plugin directory yet)

## Key Files

- `purpose-map/CLAUDE.md` — tool documentation, schema, operational protocol (read this first)
- `purpose-map/purpose_map.py` — implementation
- `purpose-map/purpose-map.db` — live v2 database
- `plugins/ocd/rules/*.md` — OCD rule files (deployed copies in `.claude/rules/`)
- `plugins/ocd/conventions/*.md` — OCD conventions
- `plugins/ocd/skills/*/SKILL.md` — OCD skills
