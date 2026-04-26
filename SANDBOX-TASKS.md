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

- [x] Add `systems/log` to the `testpaths` list in `tests/plugins/ocd/pyproject.toml` so the plugin test suite auto-discovers the new tests instead of requiring an explicit path argument
- [x] Decision-log entry — `logs/decision/log.md` covers all four points (skill extension over top-level, mutually exclusive locator, empty test `__init__.py` shadowing, YAGNI scope)
- [x] Final lint pass on touched files:
  - `ocd-run check python plugins/ocd/systems/log/` — clean
  - `ocd-run check markdown plugins/ocd/systems/log/` — clean. While running this, the markdown detector itself was fixed to skip YAML frontmatter and to treat fenced code blocks as one structural unit (frontmatter and fence interiors are now opaque to literal-character and blank-line rules); seven false-alarm hits in pre-existing files dropped out as a result, and the remaining sandbox-introduced PFN `{var}` placeholders were backticked
- [x] Verify the log system's deployment contract still works (`init()` / `status()` in `_init.py`) with the new `__init__.py` and `__main__.py` co-existing alongside `_init.py` — `setup init` and `setup status` both report log templates and rules as `current`; `check dormancy` passes for the log system

## Pending — Optional / nice-to-have

- [ ] Fix the worktree-compatibility bug in `tests/plugins/ocd/conftest.py`'s `project_root` fixture: `.git is_dir()` should be `.git exists()` (or a `git -C <dir> rev-parse --show-toplevel` subprocess) so tests pass in worktrees. Out of scope for this feature but the bug surfaces during sandbox dev — fix here or split into a separate small sandbox.
- [ ] Add `/log research deconflict <subject-a> <subject-b>` (or similar) for cross-corpus heading-tree comparison once Phase B reveals whether the use case is real. Defer until felt.

## Out of scope (post-unpack work)

The `logs/research/` corpus refactor — restructuring samples, designing master templates, building the migration retrofit — is intentionally deferred to post-unpack, not omitted. Reasoning: ship the foundation (skill extension, `sample_tools` primitives) before running it against the live corpora. Mixing both in one sandbox would risk unpacking unrunnable infrastructure if the retrofit work hits friction; running the retrofit before the foundation lands means relying on tooling that hasn't been merged or tested.

The phased sequence:

- **Phase A research corpus retrofit** — restructure MCP and claude-marketplace samples and gather observations. Uses the `context-aware-iteration` pattern + `sample_tools` primitives shipped by this sandbox. Pre-measure → baseline spawn → calibrated iteration → accumulated per-section observations.
- **Phase B master template design** — human + analytical. Use `count-sections` / `consolidate` plus the observations from Phase A to write `_TEMPLATE.md` prose descriptions. Output: master template + migration manifest (may be empty if no structural changes are needed).
- **Phase C/D retrofit engine** — generic retrofit script (likely under `plugins/ocd/systems/log/research/_retrofit.py`). Built only if Phase B's migration manifest requires structural transformation beyond "add missing headings in template order." This phase **also retires** `logs/research/mcp/scripts/_retrofit_samples_to_template.py` — the old corpus-specific retrofit (hardcoded section list, fixed `pitfalls observed:` bullet) that lives on main today. It's acknowledged as obsolete and gets deleted as part of Phase C/D, not as part of this sandbox.

### Tracking handoff after unpack

Phase A and Phase C/D were tracked in the originating session's task list (where this sandbox was authored). That tracker doesn't survive the unpack. When the sandbox closes, give the post-unpack phases a durable home:

- Promote each phase to a `logs/idea/` entry on main (or to `logs/decision/` if scope is concrete enough to commit to an approach)
- OR add as ROADMAP entries
- OR open issues in the project's external tracker

Whichever fits the project's workflow — but the post-unpack phases need a location future sessions can find without depending on the sandbox-author's task tracker.

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
