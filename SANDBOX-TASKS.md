# SANDBOX-TASKS

Outstanding work for the `sandbox/log-research` feature box. When everything in **Required for unpack** is checked off, the sandbox is ready for `/sandbox unpack log-research`.

## Purpose

Extend the existing `/log` skill with a `research` subcommand so any project using the ocd plugin can analyze its `logs/research/<subject>/samples/` corpora — heading-tree parsing, duplicate detection, cross-sample coverage, and per-section consolidation. The tools are infrastructure for the upcoming Phase A research-corpus retrofit (which uses them to drive observation-and-restructure agents); they are not the retrofit itself.

## Definition of done

- `/log research <verb>` route works end-to-end for `check`, `count-sections`, `consolidate`
- `sample_tools` tests pass under the plugin test suite
- Conventions match the rest of the plugin (system layout, CLI shape, skill workflow fragment, allowed-tools)
- No regressions across the plugin's test suite
- Decision log entry captures the non-obvious design choices

## Done in this sandbox

- [x] `_sample_tools.py` relocated from `logs/research/_scripts/` into `plugins/ocd/systems/log/research/`
- [x] `plugins/ocd/systems/log/__init__.py` facade
- [x] `plugins/ocd/systems/log/__main__.py` CLI dispatch — argparse subparsers for `check`, `count-sections`, `consolidate`; shared `--subject NAME` / `--dir PATH` locator pattern
- [x] `plugins/ocd/systems/log/research/__init__.py` subpackage facade re-exporting `_sample_tools`
- [x] `plugins/ocd/systems/log/_research.md` workflow fragment — strips leading `research` token, dispatches to `ocd-run log research {remainder}`
- [x] `plugins/ocd/systems/log/SKILL.md` — routes `research`, updates description / argument-hint / allowed-tools (`Bash(ocd-run:*)`)
- [x] Tests moved to `tests/plugins/ocd/systems/log/research/test_sample_tools.py`; imports rewritten to `from systems.log.research._sample_tools import ...`
- [x] Empty `__init__.py` placeholders added at `tests/plugins/ocd/systems/log/` and `.../log/research/` — required for pytest `--import-mode=importlib` to resolve `systems.log.research._sample_tools` from the source tree (without them the test-dir `systems/__init__.py` claims `systems` as a regular package and shadows the source)
- [x] `tests/integration/conftest.py` — `_install_research_scripts_on_syspath` workaround removed; `_git_root()` rewritten to use `git -C <conftest_dir>` (works regardless of pytest CWD); `project_root` fixture extracted as the blessed anchor for tests that need the project root
- [x] `tests/integration/test_sample_tools.py` removed (moved into plugin test tree)
- [x] `logs/research/_scripts/` removed (was a one-hour-old aspirational convention; `tools/`-style placement was abandoned in favor of the skill-extension shape)

## Verification status

- [x] 32/32 sample_tools tests pass
- [x] CLI smoke-tested end-to-end against live MCP samples — `ocd-run log research count-sections --dir <samples-dir>` returns chain-key coverage as expected
- [x] Plugin test suite — 402 passed; 49 `ERROR at setup` are pre-existing worktree-compat issues (`project_root` fixture's `.is_dir()` check on `.git` fails when `.git` is a worktree pointer file — not caused by this sandbox)

## Pending — Required for unpack

- [ ] Add `systems/log` to the `testpaths` list in `tests/plugins/ocd/pyproject.toml` so the plugin test suite auto-discovers the new tests instead of requiring an explicit path argument
- [ ] Decision-log entry under `logs/decision/log.md` (or a new `decisions/log/research-skill-extension.md`):
  - Why extend `/log` rather than create a new top-level skill — research is "log analysis," fits the system that already governs the corpora
  - Why empty `__init__.py` files persist in the test subtree — importlib mode + regular-package shadowing
  - Why `--subject` + `--dir` mutually-exclusive locator — `--subject` honors the `logs/research/<name>/samples/` convention; `--dir` for ad-hoc paths
  - YAGNI: this sandbox explicitly excludes retrofit engine, work-queue/log CSV management, and migration-manifest tooling — those land when Phase B defines their actual needs
- [ ] Final lint pass on touched files:
  - `ocd-run check python plugins/ocd/systems/log/`
  - `ocd-run check markdown plugins/ocd/systems/log/`
- [ ] Verify the log system's deployment contract still works (`init()` / `status()` in `_init.py`) with the new `__init__.py` and `__main__.py` co-existing alongside `_init.py` — run the dormancy check or a manual init/status invocation

## Pending — Optional / nice-to-have

- [ ] Fix the worktree-compatibility bug in `tests/plugins/ocd/conftest.py`'s `project_root` fixture: `.git is_dir()` should be `.git exists()` (or a `git -C <dir> rev-parse --show-toplevel` subprocess) so tests pass in worktrees. Out of scope for this feature but the bug surfaces during sandbox dev — fix here or split into a separate small sandbox.
- [ ] Add `/log research deconflict <subject-a> <subject-b>` (or similar) for cross-corpus heading-tree comparison once Phase B reveals whether the use case is real. Defer until felt.

## Out of scope (post-unpack work)

- **Phase A research corpus retrofit** — task #16. Use these tools + the `context-aware-iteration` pattern to restructure MCP and claude-marketplace samples and gather observations. Pre-measure → baseline spawn → calibrated iteration → accumulated per-section observations.
- **Phase B master template design** — human + analytical. Use `count-sections` / `consolidate` plus the observations from Phase A to write `_TEMPLATE.md` prose descriptions. Output: master template + migration manifest (may be empty).
- **Phase C/D retrofit engine** — task #15. Generic retrofit script (likely under `plugins/ocd/systems/log/research/_retrofit.py`). Built only if Phase B's migration manifest requires structural transformation beyond "add missing headings in template order."

## Unpack checklist

When **Required for unpack** is fully checked:

1. From a claude-plugins session on `main`: `/sandbox unpack log-research`
2. Post-unpack verification:
   - Full plugin test suite passes
   - `ocd-run log research --help` resolves cleanly
   - `_research.md` deploys to `.claude/skills/log/` after `ocd-run framework init`
3. Mark task #17 complete in the project tracker
4. Move on to Phase A in a fresh session

## Notes for future maintainers

- The CLI lives in `__main__.py`; the skill workflow fragment in `_research.md` is pure routing — both are thin layers over the analytical primitives in `research/_sample_tools.py`.
- `sample_tools` is intentionally pure-Python with no plugin-internal dependencies, so it can be re-used outside the `/log` skill (e.g., from a future retrofit engine, or as a library import from project-level scripts).
- Heading-tree-as-key (with ` > ` chain separator) is the foundational data model. Any future operation — retrofit, deconflict, migration — should compose on parsed `Section` trees, not re-parse markdown.
