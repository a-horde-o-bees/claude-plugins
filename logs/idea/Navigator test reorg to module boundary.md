# Navigator test reorg to module boundary

Reorganize `tests/plugins/ocd/systems/navigator/unit/` from per-function file layout to per-module, matching the convention that needs_map and other newer systems already follow.

## Current layout

~17 per-function files: `test_paths_get.py`, `test_paths_list.py`, `test_paths_remove.py`, `test_paths_search.py`, `test_paths_undescribed.py`, `test_paths_upsert.py`, `test_scope_analyze.py`, `test_scan_path.py`, `test_file_metrics.py`, `test_git_hash.py`, `test_mark_parents_stale.py`, `test_pattern_matching.py`, `test_stale.py`, `test_init_db.py`, `test_ready.py`, `test_references.py`, `test_skills.py`.

## Target layout

One test file per source module:

- `test_db.py` ← test_init_db.py (drop `init_` prefix; expand to all _db helpers)
- `test_init.py` ← test_ready.py (extend with init/reset/status contract tests once that work lands)
- `test_scanner.py` ← test_file_metrics + test_git_hash + test_mark_parents_stale + test_pattern_matching + test_scan_path + test_stale
- `test_paths.py` ← test_paths_{get,list,remove,search,undescribed,upsert} + test_scope_analyze
- `test_references.py` (already conforms)
- `test_skills.py` (already conforms)

## Context

Started during the purpose-map sandbox session but cut to keep the migration commit focused. Reorg is purely structural; tests pass either way. The motivation is consistency — needs_map landed with module-boundary organization (test_db.py, test_init.py, test_paths.py, etc.) and navigator's per-function layout is now the outlier.

Companion problem entry captures this as observable inconsistency.
