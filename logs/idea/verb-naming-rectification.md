# Verb naming rectification

Working queue for the rectification triggered by problem log `Verb naming convention not formally captured.md`. Resolves verb naming across MCP tools, CLI verbs, library functions, system names, and skill argument-hints. Full-project scope; no skips. Convention-first; case-by-case with rule generalization and propagation to all matching patterns until nothing remains unresolved.

Delete this file when every phase is complete and the originating problem log is resolved.

## Resolutions captured so far

- **MCP read verb** is `_query` (single tool per concept). Absorbs `_get` (PK lookup), `_list` (enumeration), `_search` (text-pattern). Input modes are optional parameters: `paths` (PK list), scope/filter args, `text` (substring/fuzzy).
- **MCP write verbs** stay split by operation semantics: `_set` (replace value), `_update` (mutate fields), `_clear` (null out), `_remove` (delete row), `_upsert` (create-or-update). One verb per distinct mutation intent.
- **CLI structure** is noun-verb hierarchical (argparse subparser nesting), e.g. `transcripts sessions query`. CLI verb name = MCP tool name minus the underscore.
- **System-level CLI verbs stay flat** when they act on the whole system (`reset`, `status`, `init`, `enable`, `disable`).
- **Library functions** do not need to mirror MCP tool names 1:1 — many-to-many mapping is allowed (one library function backing multiple MCP tools, or one MCP tool composing multiple functions). Library names follow Python ergonomics; cleanup happens during caller-fan-in evaluation per target.
- **System names** should be nouns where reasonable; verb-shaped names are renamed during this pass.

## Per-target rectification checks

For each target in Phase 3, do *all* of these — not just the rename:

1. **Rename** — apply the new convention.
2. **Caller fan-in** — list every caller of the current function (library, MCP, CLI, tests, docs). Evaluate whether one consolidated function can serve all callers.
3. **Argument refinement** — evaluate if input parameters can collapse via the bucket pattern (like `show=["messages","metrics"]` for transcripts). Output verbosity, mode flags, mutex inputs are common opportunities.
4. **Function cleanup** — any other simplifications surfaced (dead code, redundant wrappers, awkward signatures)?
5. **Apply** — rename + refinement + cleanup in one coherent change.
6. **Tests green** — narrow test pass for the target.
7. **Generalize** — note any rule generalization the case suggests (update convention if the pattern was incomplete).
8. **Propagate** — any other cases matching the EXACT same pattern? Apply the same resolution there.

## Phase 1 — Conventions (author first)

| Status | Action |
|---|---|
| done | New `.claude/conventions/ocd/cli.md` — noun-verb hierarchy, system-level-flat exception, argparse subparser pattern, CLI ↔ MCP naming alignment |
| done | Update `.claude/conventions/ocd/mcp-server.md` — promoted `_query` as unified read verb; documented write-verb split (set/update/clear/upsert/remove); added Input Mode Parameters section covering PK/scope/text inputs and `show` bucket pattern; updated Markdown Detail Storage to deliver `detail_md` via `show=["detail"]`; cross-referenced cli.md from Tool Naming |
| pending | Update `logs/decision/mcp.md` — supersede or delete (blueprint source is gone; legacy `set/add/remove/clear` + `get/list/find` decision is dormant) |

## Phase 2 — System renames

| Status | Current | Proposed | Rationale |
|---|---|---|---|
| pending | `check` | `lint` | `Move check to project root tooling.md` proposes this; verb-shaped system name → noun (linter dimension matches the bulk of operations); also moves to `tools/check/` per that log — separate work, but rename can land independently |
| skip | `refactor` | (keep) | Both verb and noun in English usage; "this is a refactor" is natural noun usage. Keep. |
| skip | `setup` | (keep) | Both verb and noun ("the setup"); widely used as noun. Keep. |

Other systems (`conventions`, `governance`, `log`, `navigator`, `needs_map`, `pdf`, `permissions`, `retrospective`, `rules`, `sandbox`, `transcripts`, `git`) are noun-shaped already.

## Phase 3 — Per-target rectification queue

Order: smallest first to validate the per-target check pattern, then larger to amortize convention edits.

### Target 3.1: `settings_query` (smallest — validates pattern)

- Was: `settings_get` (MCP), `settings` (CLI catch-all)
- File touches: 2

Surfaces:
- MCP: `transcripts/server.py` — rename
- Library: `_settings.get(key)` (single) + `_settings.list_all()` (full block) — evaluate folding
- CLI: `transcripts settings query [key]` (replaces `settings [key]`)
- Tests: `test_settings.py`
- Docs: `transcripts/SKILL.md`, `transcripts/ARCHITECTURE.md`

Per-target checks:
- Caller fan-in: who calls `_settings.get`, `_settings.list_all`? Map.
- Arg refinement: `key=None` covers full block; `key="x"` covers single. Already this shape in CLI.
- Function cleanup: should `get` and `list_all` collapse into one library function?

Status: pending

### Target 3.2: `projects_query`

- Was: `projects_list`
- File touches: 3

Surfaces:
- MCP: `transcripts/server.py` — rename
- Library: `_scope.projects()` — caller fan-in check
- CLI: `transcripts projects query` (replaces `projects`)
- Tests: `test_scope.py::TestProjects`
- Docs: `transcripts/ARCHITECTURE.md`, `transcripts/SKILL.md`

Per-target checks:
- Caller fan-in: who calls `_scope.projects`?
- Arg refinement: should `text` (substring on project name) be added for shape uniformity with `paths_query`?

Status: pending

### Target 3.3: `purposes_update`

- Was: `purposes_set` + `purposes_clear` (MCP), `purposes-set` + `purposes-clear` (CLI), `set_many` + `clear_many` (library)
- File touches: 15

Surfaces:
- MCP: `transcripts/server.py` — 2 → 1
- Library: `_purposes.set_many` + `_purposes.clear_many` — evaluate folding into `update_many(session, set=, clear=)`
- CLI: `transcripts purposes update --set <json> --clear <list>` (mirrors MCP since noun-verb structure makes split cleaner)
- Tests: `test_purposes.py::TestSetMany`, `TestClearMany` → `TestUpdateMany`
- Docs: `transcripts/SKILL.md`, `transcripts/ARCHITECTURE.md`

Per-target checks:
- Caller fan-in: who calls `set_many`/`clear_many`? Likely just CLI + MCP.
- Arg refinement: atomic mixed-mode write — `set` + `clear` in single transaction
- Function cleanup: `set_purpose` + `clear` (singular library helpers) — still used by `set_many`/`clear_many` internally; check if surface APIs need them.

Status: pending

### Target 3.4: `skills_query`

- Was: `skills_list` + `skills_resolve`
- File touches: 11

Surfaces:
- MCP: `navigator/server.py` — 2 → 1
- Library: navigator skills functions — caller fan-in
- CLI: `navigator skills query [--name X]` (replaces `list-skills` + `resolve-skill`)
- Tests: navigator skills tests
- Docs: `navigator/SKILL.md`, `navigator/ARCHITECTURE.md`

Per-target checks:
- Caller fan-in: who calls `skills_resolve`/`skills_list` directly (not via MCP)?
- Arg refinement: `name=None` → full enumeration; `name="x"` → PK lookup. Single param covers both.

Status: pending

### Target 3.5: `paths_query`

- Was: `paths_get` + `paths_list` + `paths_search` + `paths_undescribed`
- File touches: 33 across 4 names (~15 unique files)

Surfaces:
- MCP: `navigator/server.py` — 4 → 1
- Library: 4 navigator path functions — caller fan-in
- CLI: `navigator paths query` (replaces `describe`, `list`, `search`, `get-undescribed`)
- Tests: navigator path tests (multiple files)
- Docs: `navigator/SKILL.md`, `navigator/ARCHITECTURE.md`, MCP server instructions string

Per-target checks:
- Caller fan-in: deepest of the targets — many internal callers in navigator
- Arg refinement:
  - 4 input modes consolidated as optional params: `paths`, `target_path`+`patterns`+`excludes`, `text`, `undescribed`
  - `show` parameter could absorb `sizes` (already a flag), `references`, `governance` — would also fold `scope_analyze` and `references_map`; leave for now per direction
- Mutex check: `paths=[...]` + `text=...` simultaneous — define precedence
- Function cleanup: dedup helpers shared across the 4 functions

Status: pending

## Phase 4 — Other CLI noun-verb migrations (post-target)

After Phase 3 completes, the noun-verb CLI convention applies plugin-wide. Migrate remaining systems:

| Status | System | Current verbs (sample) | Notes |
|---|---|---|---|
| pending | `governance` | `list`, `for`, `order` | `conventions list`, `conventions for <files>`, `conventions order` (rename verb-as-noun to actual noun `conventions`) |
| pending | `log` | `research`, `check`, `consolidate`, `count-sections` | Each has a noun: `research check`, `research consolidate`, etc. — already partly nested |
| pending | `navigator` | `describe`, `list`, `search`, `scan`, `set`, `remove`, `list-skills`, `resolve-skill`, `ready`, `reset`, `get-undescribed` | Most absorbed by Phase 3.4 / 3.5; `scan` becomes `paths scan`; `ready` becomes system-level |
| pending | `needs_map` | many domain verbs | `components add/set/remove`, `needs add/refine/remove`, `dependencies query`, etc. |
| pending | `pdf` | (need to inspect) | |
| pending | `refactor` | `rename-symbol` | `symbols rename` |
| pending | `sandbox` | `project setup/teardown`, `worktree setup/teardown/cleanup` | Already noun-verb; conformant |
| pending | `setup` | `init`, `enable`, `disable`, `status`, `permissions`, `analyze`, `clean`, `deploy` | Mostly system-level (init/status/enable/disable). Permissions sub-tree already noun-verb |
| pending | `check`/`lint` | `dormancy`, `markdown`, `python`, `all` | Could become `lint run --dimension X` or stay as flat dimension verbs (categorical, not noun-verb) — edge case |

## Phase 5 — Convergence sweep

After Phase 4, audit-pass once more:

1. Re-grep for verb suffixes — any leftover `_get`/`_list`/`_search`/`_find` that should be `_query`?
2. Verify `mcp-server.md` rules generalized from Phase 3 are reflected
3. Update problem log `Verb naming convention not formally captured.md` to "resolved by convention update + this rectification"
4. Delete this queue file

## Open questions

- **Library function naming consistency** — case-by-case during caller fan-in evaluation. No global rule.
- **Settings-style fold (single-key + full-block in one tool)** — pattern emerges from Target 3.1; if successful, propagate to similar shapes elsewhere.
