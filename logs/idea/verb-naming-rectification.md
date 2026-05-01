# Verb naming rectification

Working queue for the rectification triggered by problem log `Verb naming convention not formally captured.md`. Resolves verb naming and surface-level fragmentation across MCP tools, CLI verbs, library functions, system names, skill argument-hints, and supporting documentation. Full-project scope; no skips. Convention-first; case-by-case with rule generalization and propagation to all matching patterns until convergence.

This file is the canonical plan. It is designed to be read by a fresh session that has no memory of the conversation that produced it. Read the entire file before starting any work — particularly the *Driving Goals*, *Resolutions captured*, and *Per-target check pattern* sections. Treat resolutions as load-bearing decisions; if a target during execution suggests a resolution is wrong, surface the conflict before proceeding.

Delete this file when every phase is complete and the originating problem log is resolved.

## Driving Goals

The purpose of the rectification is not just to rename things. It is to bring four agent-facing surfaces (MCP tools, CLI verbs, library functions, supporting docs) into a single coherent shape so the agent's mental model of any system is "one concept, one read tool, one write tool, one delete tool" — and so future systems inherit that shape automatically through the conventions.

Goals in priority order (top is most important):

1. **Predictable agent-facing surface.** Three tightly-coupled pillars:
    - **One mental model per concept** — `_query` for all reads, `_update` for all field-modifying writes, `_remove` for deletion. Reads accept input shape variation as parameters (PK list, scope/filter args, text term); writes accept mutation variation as parameters (`set`, `clear`, `add`). The agent learns the pattern once and applies it across systems without per-system re-discovery.
    - **Noun-verb naming** — MCP tools are `<noun>_<verb>`; CLI verbs are `<noun> <verb>`. Readers scan a prefix and find every related operation; new operations attach predictably.
    - **Noun-nesting CLI structure** — argparse subparser nesting (`<system> <noun> <verb> [args...]`) makes the verb tree discoverable via `--help`, mirrors MCP tool grouping, and accommodates new operations on existing nouns without flat-namespace churn.
2. **CLI ↔ MCP alignment.** A reader who knows one surface knows the other; only the separator differs (underscore vs space). When MCP renames, CLI renames in the same change. When CLI restructures, MCP follows.
3. **Convention as source of truth.** Implicit naming patterns become explicit conventions before any rename, so future authors follow them by default. Convention-loading hooks enforce conformance going forward.
4. **Convergence to clean state.** No transitional allowlists, no compatibility shims, no "we'll fix this later" exceptions. Every system, every surface, every doc reference conforms when the rectification ends.
5. **Reduce agent context cost.** Downstream benefit of consolidation: fewer MCP tools means more conversation budget for actual reasoning. Real but lowest priority — prioritizing this over coherence would lead to over-aggressive collapsing that compromises the mental model. The savings should be a *consequence* of getting the surface right, not the driver.

Underlying design principles served (from `.claude/rules/ocd/design-principles.md`):

- **Agent-First Interfaces** — tool surface is designed for agent consumption; tool count and naming patterns optimize agent decision-making
- **Make Invalid States Unrepresentable** — verb selection is structural (one verb per operation kind), not parameter-driven
- **Single Source of Truth** — conventions are authoritative; deployed copies follow templates
- **Fix Foundations, Not Symptoms** — convention update + propagating rectification, not piecemeal renames
- **Reuse Before Create** — consolidating multiple tools into one rather than maintaining variants
- **Convention as Documentation** — naming structure communicates intent without prose docs

## Driving non-goals

To prevent scope creep:

- **Do not redesign business logic.** Rectification is structural. If a tool's domain logic is wrong, log it as a separate problem.
- **Do not add new features.** New tools or capabilities are out of scope; existing capabilities consolidate.
- **Do not change the testing model.** Test files get renamed and re-pointed; testing patterns stay.
- **Do not refactor system architecture.** Library decomposition, plugin framework, init contracts stay as-is.

## Resolutions captured

Treat these as load-bearing. Surface conflicts before deviating.

- **MCP read verb is `_query`.** One tool per concept. Absorbs `_get` (PK lookup), `_list` (enumeration), `_search` (text-pattern). Input modes are optional parameters — `paths` (PK list), scope/filter args, `text` (substring/fuzzy).
- **MCP write verbs are `_update` and `_remove`.** `_update` absorbs `_set`, `_clear`, `_add`, and field-mutation `_update` semantics; supports atomic mixed-mode writes (set + clear in one call); upsert-by-default (creates row if PK absent, modifies if present). `_remove` deletes the entire entry. Modify-vs-delete stays a meaningful semantic boundary; collapsing them into one tool with a `mode=` flag is rejected.
- **Domain-specific verbs are allowed.** When a concept's operation doesn't reduce to query/update/remove, name it descriptively (e.g. `references_map`, `scope_analyze`, `schema_describe`). The `<noun>_<verb>` form still applies.
- **Generic schema-driven write tool is rejected.** A `db_update(table, data)` tool would lose business-logic interception (validation, normalization, application-level invariants schema can't express). Per-concept write tools earn their keep through the business logic they intercept. See `logs/decision/mcp.md` for the original blueprint research decision; the same logic applies project-wide.
- **CLI structure is noun-verb hierarchical** via argparse subparser nesting (`<system> <noun> <verb> [args...]`). CLI verb name = MCP tool name with underscore replaced by space.
- **System-level CLI verbs stay flat** when they act on the whole system (`reset`, `status`, `init`, `enable`, `disable`).
- **Library functions do not need to mirror MCP tool names 1:1.** Many-to-many mapping is allowed (one library function backing multiple tools, or one tool composing multiple functions). Library names follow Python ergonomics; cleanup happens during caller fan-in evaluation per target.
- **System names should be nouns** where reasonable; verb-shaped names rename during this pass.

## Per-target check pattern

For each target in Phase 3 / Phase 4, do *all* of these — not just the rename:

1. **Rename** — apply the new convention.
2. **Cross-surface search** — grep for the old name(s) across:
    - Library code (`.py`)
    - Tests
    - SKILL.md frontmatter (argument-hint, description) and Workflow PFN (`bash:` invocations naming old CLI verbs)
    - MCP server `instructions` strings and tool descriptions
    - README.md, CLAUDE.md, ARCHITECTURE.md
    - Other plugins' docs that may reference cross-system tools
3. **Caller fan-in** — list every caller of the current function (library, MCP, CLI, tests, docs). Evaluate whether one consolidated function can serve all callers.
4. **Business-logic intercept question (writes only)** — does this write tool intercept business logic that a generic schema-driven write would lose (validation, normalization, prefix resolution, type coercion, transaction semantics)? If no, the tool is fragmentation and should fold into the per-noun `_update`. If yes, the tool earns its keep.
5. **Argument refinement** — evaluate if input parameters can collapse via the bucket pattern (like `show=["messages","metrics"]` for transcripts). Output verbosity, mode flags, mutex inputs are common opportunities.
6. **Function cleanup** — any other simplifications surfaced (dead code, redundant wrappers, awkward signatures)?
7. **Apply** — rename + refinement + cleanup in one coherent change per target.
8. **Tests green** — narrow test pass for the target before moving on.
9. **Generalize** — note any rule generalization the case suggests (update convention if the pattern was incomplete or new).
10. **Propagate** — any other cases matching the EXACT same pattern? Apply the same resolution there in this commit so the rule and the practice stay in lockstep.

## Phase 1 — Conventions (author first)

| Status | Action |
|---|---|
| done | New `cli.md` template (`plugins/ocd/systems/conventions/templates/cli.md`) — noun-verb hierarchy, system-level-flat exception, argparse subparser pattern, CLI ↔ MCP naming alignment |
| done | Update `mcp-server.md` template — `_query` as unified read verb; current write-verb table (set/update/clear/upsert/remove); Input Mode Parameters section; Markdown Detail Storage delivers `detail_md` via `show=["detail"]`; Library and Tool Naming Are Independent subsection; Tool Naming cross-references cli.md |
| pending | **Revise `mcp-server.md` again** — collapse write verbs to `_update` + `_remove` only. Drop `set`/`clear`/`upsert` from the standard verb table; document `_update` as absorbing all field modifications + upsert-by-default semantics. Update cli.md Verb Names table to match. Apply BEFORE any Phase 3 work touches the write side. |
| pending | Update `logs/decision/mcp.md` — supersede with a one-line "see mcp-server.md" pointer or delete (blueprint source is gone; the legacy decision is dormant). Decide before Phase 3 starts. |

## Phase 2 — System renames

| Status | Current | Proposed | Rationale |
|---|---|---|---|
| pending | `check` | `lint` | `logs/idea/Move check to project root tooling.md` proposes both promoting check to project tooling and renaming to `lint` (linter dimensions dominate the operations). Verb-shaped system name → noun. |

Other systems (`conventions`, `governance`, `log`, `navigator`, `needs_map`, `pdf`, `permissions`, `retrospective`, `rules`, `sandbox`, `transcripts`, `git`, `setup`, `refactor`) keep their names. `setup` and `refactor` are noun-shaped enough in English usage.

## Phase 3 — Per-target rectification queue

Order: smallest first to validate the per-target check pattern, then larger to amortize convention edits. Each target gets its own commit so the rectification is bisectable.

### Target 3.1: `settings_query` + `settings_update` (smallest — validates pattern)

- Was: `settings_get` + `settings_set` (MCP), `settings` (CLI catch-all)
- File touches: 2 + cross-surface search

Surfaces:
- MCP: `transcripts/server.py` — rename
- Library: `_settings.get(key)` + `_settings.list_all()` + `_settings.set_value(key, value)` — evaluate folding read into one
- CLI: `transcripts settings query [key]` and `transcripts settings update <key> <value>`
- Tests: `test_settings.py`
- Docs: `transcripts/SKILL.md`, `transcripts/ARCHITECTURE.md`

Open questions for this target:
- Caller fan-in: who calls these library functions? Map.
- Library fold: should `get` and `list_all` collapse?
- Settings `_remove` doesn't apply (single-row table); only `_query` and `_update`.

Status: pending

### Target 3.2: `projects_query`

- Was: `projects_list`
- File touches: 3 + cross-surface search

Surfaces:
- MCP: `transcripts/server.py` — rename
- Library: `_scope.projects()` — caller fan-in
- CLI: `transcripts projects query`
- Tests: `test_scope.py::TestProjects`
- Docs: `transcripts/ARCHITECTURE.md`, `transcripts/SKILL.md`

Open questions:
- Should `text` (substring on project name) be added for shape uniformity?
- Projects has no write side (auto-derived from ingest); `_update`/`_remove` not applicable.

Status: pending

### Target 3.3: `purposes_update`

- Was: `purposes_set` + `purposes_clear` (MCP), `purposes-set` + `purposes-clear` (CLI), `set_many` + `clear_many` (library)
- File touches: 15 + cross-surface search

Surfaces:
- MCP: `transcripts/server.py` — 2 → 1
- Library: `_purposes.set_many` + `_purposes.clear_many` → one `update_many(session, set=, clear=)`
- CLI: `transcripts purposes update [--set <json>] [--clear <list>]`
- Tests: `test_purposes.py::TestSetMany`, `TestClearMany` → `TestUpdateMany`
- Docs: `transcripts/SKILL.md`, `transcripts/ARCHITECTURE.md`

Open questions:
- Caller fan-in for `_purposes.set_purpose` / `clear` (singular helpers) — still needed internally? If only used by the batch wrappers, could fold.
- Atomic mixed-mode in single transaction: confirmed working pattern.
- Business-logic intercept: validates non-empty after strip, trims whitespace, sets `purpose_updated_at = CURRENT_TIMESTAMP`, resolves session prefix. Earns its keep — do not fold to generic write.

Status: pending

### Target 3.4: `skills_query`

- Was: `skills_list` + `skills_resolve`
- File touches: 11 + cross-surface search

Surfaces:
- MCP: `navigator/server.py` — 2 → 1
- Library: navigator skills functions — caller fan-in
- CLI: `navigator skills query [--name X]`
- Tests: navigator skills tests
- Docs: `navigator/SKILL.md`, `navigator/ARCHITECTURE.md`

Open questions:
- Caller fan-in for `skills_resolve` / `skills_list` — anyone outside the MCP/CLI surface calling directly?
- `name=None` → enumeration; `name="x"` → PK lookup. Single param covers both.

Status: pending

### Target 3.5: `paths_query` + `paths_update` + `paths_remove`

- Was: `paths_get` + `paths_list` + `paths_search` + `paths_undescribed` (reads); `paths_upsert` (write); `paths_remove` (kept)
- File touches: 33 across 4 read names (~15 unique files) + write surfaces + cross-surface search

Surfaces:
- MCP: `navigator/server.py` — 4 reads → 1; rename `paths_upsert` → `paths_update`; keep `paths_remove`
- Library: navigator path functions — heaviest caller fan-in
- CLI: `navigator paths query` (replaces `describe`, `list`, `search`, `get-undescribed`); `navigator paths update <path> [--purpose ...] [--exclude ...] [--traverse ...]`; `navigator paths remove <path> [--mode ...]`
- Tests: navigator path tests (multiple files)
- Docs: `navigator/SKILL.md`, `navigator/ARCHITECTURE.md`, MCP server instructions string

Open questions:
- 4 input modes: `paths`, `target_path`+`patterns`+`excludes`, `text`, `undescribed` — define precedence when modes overlap
- `show` parameter could absorb `sizes` (currently a flag), `references` (currently `scope_analyze`), `governance` (currently `scope_analyze`). Defer per existing direction; revisit during convergence sweep.
- Business-logic intercept on `paths_update`: timestamps, scan-state coordination, default behavior on optional fields. Earns its keep.
- `paths_undescribed` folds into `paths_query(undescribed=True)` per consolidation.

Status: pending

## Phase 4 — Other CLI noun-verb migrations and surface sweeps

After Phase 3 establishes the per-target pattern, propagate to:

### CLI verb migrations (per system)

| Status | System | Current verbs (sample) | Notes |
|---|---|---|---|
| pending | `governance` | `list`, `for`, `order` | `governance conventions list` / `governance conventions for <files>` / `governance conventions order` (or whatever noun this manipulates) |
| pending | `log` | `research`, `check`, `consolidate`, `count-sections` | Each has a noun layer; partly nested already |
| pending | `navigator` | (verbs not absorbed by 3.4/3.5) `scan`, `ready`, `reset` | `paths scan`; `ready` and `reset` are system-level (flat) |
| pending | `needs_map` | many domain verbs (add-component, refine, depend, ...) | `components update/remove`, `needs update/remove`, `dependencies query`, etc. — heavy refactor; check needs-map.md log for ongoing context |
| pending | `pdf` | (need to inspect) | Single-concept; flat may be acceptable |
| pending | `refactor` | `rename-symbol` | `symbols rename` (noun-verb) |
| pending | `sandbox` | `project setup/teardown`, `worktree setup/teardown/cleanup` | Already noun-verb; verify convention conformance |
| pending | `setup` | `init`, `enable`, `disable`, `status`, `permissions`, `analyze`, `clean`, `deploy` | `init/status/enable/disable` flat; permissions sub-tree noun-verb (already partly nested) |
| pending | `check`/`lint` | `dormancy`, `markdown`, `python`, `all` | Categorical, not noun-verb. Edge case — may stay flat as `lint <dimension>` or restructure. Decide during target. |

### Cross-surface sweeps (independent of named CLI targets)

| Status | Surface | Action |
|---|---|---|
| pending | All `SKILL.md` files | Update argument-hint frontmatter + Workflow PFN `bash:` invocations to use new noun-verb CLI shape |
| pending | All MCP server `instructions` strings | Update embedded tool name references |
| pending | All `README.md` files (system-level + plugin-level + project root) | Update CLI examples, tool name references |
| pending | All `CLAUDE.md` files (project + plugin + project consumers) | Update embedded command examples |
| pending | All test files | Update references to renamed library functions, MCP tool names, CLI verbs (test method names if descriptive of operations) |
| pending | Cross-plugin docs | Search for `paths_get`, `paths_search`, `skills_resolve`, etc. in any plugin docs that reference navigator/transcripts tools |

## Phase 5 — Convergence loop

Iterate until a sweep finds zero new items. Each sweep:

1. Re-grep across the project for legacy patterns:
    - Read verbs: `_get` / `_list` / `_search` / `_find` outside of allowed exceptions
    - Write verbs: `_set` / `_add` / `_clear` / `_upsert` outside of allowed exceptions
    - Verb-first MCP tool names (`update_X`, `delete_X`, `query_X`)
    - CLI flat verbs that should be noun-verb nested
    - Old system names (`check` → `lint`)
2. Inspect surfaces not yet swept (or re-sweep if changes since last):
    - SKILL.md argument-hint and Workflow PFN
    - MCP server instructions and tool descriptions
    - README.md / CLAUDE.md / ARCHITECTURE.md across all systems
    - Test files (broad search)
    - Cross-plugin documentation
3. For each finding, classify:
    - Matches an existing pattern in the queue → add as new target / surface entry
    - Reveals a new pattern not covered by the convention → propose convention update first
    - Suggests a resolution is wrong → surface as conflict (do not silently change)
4. Resolve all findings per the per-target check pattern.
5. Re-run from step 1.
6. **Stop condition:** an iteration produces zero new findings AND zero convention updates.
7. Update problem log `Verb naming convention not formally captured.md` to "resolved by convention update + this rectification."
8. Delete this queue file.

## Conflict detection guidance for fresh sessions

A fresh session executing this plan should pause and surface (not silently change) when:

- A target's caller fan-in reveals a consumer pattern not covered by the convention — generalize the convention first.
- An MCP tool's business logic intercept evaluation is ambiguous — present the operations to the user before deciding fold-or-keep.
- A surface (e.g. a README) seems to conflict with a resolution captured above — verify the resolution still holds against the current evidence; the convention may need refinement.
- A new system has appeared since this plan was written — it must conform; add to Phase 4.
- The Phase 5 stop condition is reached but the convention still feels incomplete — capture the gap as a follow-up problem log; the rectification is done as scoped.
- A test is impossible to update without changing semantics — surface; the rename may be hiding a real semantic question.

When in doubt about scope: this rectification is **structural and naming**, not behavioral. Behavior changes are out of scope; if a rename forces a behavior change, escalate.

## Open questions to settle before execution

These are not blocking the queue's existence, but should be resolved before Phase 3 starts:

- **Phase 1 third revision** — collapse writes to `_update` + `_remove`. Apply now (Phase 1.4 above) so Phase 3 work doesn't have to backtrack.
- **`logs/decision/mcp.md` disposition** — supersede with pointer or delete outright.
- **Allowed exceptions for legacy verbs** — are there any places `_get` / `_list` are still appropriate (e.g. existing public API contracts that can't break)? Default: no, full conformance. Document any exception with rationale.
- **CLI verb structure for categorical commands** — `check dormancy` / `check markdown` / `check python` / `check all`. The dimensions aren't nouns being acted on; they're categories. Decide whether to keep flat or restructure as `lint run --dimension X`.

## Cross-references

- Originating problem log: `logs/problem/Verb naming convention not formally captured.md`
- Related conventions (governing this rectification's outputs):
    - `.claude/conventions/ocd/mcp-server.md` (template at `plugins/ocd/systems/conventions/templates/mcp-server.md`)
    - `.claude/conventions/ocd/cli.md` (template at `plugins/ocd/systems/conventions/templates/cli.md`)
    - `.claude/conventions/ocd/python.md`
- Adjacent log: `logs/idea/Move check to project root tooling.md` (drives the `check` → `lint` rename)
- Decision to revisit/retire: `logs/decision/mcp.md` (blueprint research's read/write naming; dormant, may supersede)

## Execution discipline notes

- **Convention edits go to templates**, not deployed copies. Templates live at `plugins/<plugin>/systems/conventions/templates/<name>.md` and `plugins/<plugin>/systems/rules/templates/<name>.md`. Auto-init deploys to `.claude/conventions/<plugin>/<name>.md`. The convention-deployment hook fires when cwd is inside the plugin repo; cross-repo edits from other working directories bypass it. Always edit the template path.
- **Per-target commits** so the rectification is bisectable.
- **Tests green per target** before moving to the next.
- **Worktree-isolated execution** — this rectification will run in a dedicated git worktree (planned) so the main working tree stays unblocked while it progresses.
