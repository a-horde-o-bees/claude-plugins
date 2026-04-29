# Navigator unit tests use per-function layout instead of per-module

Navigator's unit tests live at `tests/plugins/ocd/systems/navigator/unit/` with ~17 files organized one-per-function (`test_paths_get.py`, `test_paths_list.py`, `test_scan_path.py`, `test_file_metrics.py`, etc.). Every other system with a meaningful test surface uses one-test-file-per-source-module: needs_map's `test_db.py` / `test_init.py` / `test_paths.py` / `test_edges.py` / `test_entities.py` / `test_queries.py` is the canonical shape.

## What's wrong

- A reader looking for "the tests that exercise `_paths.py`" has to scan ~7 file names and infer membership instead of opening one file
- New tests added to navigator follow no clear rule — should a new `_db.py` test go in `test_init_db.py`, a new file, or somewhere else? The current layout doesn't answer
- Inconsistency between systems is friction for cross-system refactors (e.g., applying a test pattern from needs_map to navigator means re-deriving where each test class belongs)

## Suspected fix

Mechanical merge per the mapping in `logs/idea/Navigator test reorg to module boundary.md`. Tests pass either way; the change is purely structural.
