# Centralize Tools — Plan

Plan spec for the `sandbox/centralize-tools` branch. Splits `systems/framework/` into an always-on kernel and an opt-in orchestration system, centralizes shared runtime helpers at project root, and closes drift via the existing pre-commit propagation mechanism plus a content-equality contract test.

## Why

Two concrete triggers surfaced during pdf refactor work:

1. **Drift between `get_project_dir` implementations.** `plugins/ocd/systems/framework/_environment.py` and `tools/testing/_environment.py` are manually maintained copies of the same 20-line function, with three observable drifts already: post-resolve `is_dir()` validation, `subprocess` import location, and error message prose. The same pattern bit this project's monaco* predecessor: a new plugin reinvented project-root resolution via parent-walk instead of using the helper, because neither "use the helper" nor "there's a helper" was discoverable from plugin-local code.
2. **Custom `.git`-walking in places that should delegate.** `tests/plugins/ocd/conftest.py::project_root` (fixed on `sandbox/pdf`) and `plugins/ocd/systems/check/__main__.py::_project_root_from` both walked ancestors looking for a `.git` directory, using `is_dir()`. Both fail in linked worktrees where `.git` is a file pointer. The canonical `framework.get_project_dir()` doesn't have this bug — it shells to `git rev-parse --show-toplevel`.

The root cause of both: no single source of truth for foundational environment resolution, and no enforcement against reinvention.

## Constraints Already Known

- **Shipping boundary.** A plugin installed downstream from the marketplace extracts only `plugins/<name>/` to `~/.claude/plugins/cache/<author>/<name>/<version>/`. Project-root files (`tools/`, `bin/`, `scripts/`) do not ship. Plugins cannot `import` from a project-root module at runtime; each plugin must ship its own copy of any helper it consumes.
- **Non-opt-in consumers exist.** `hooks/auto_approval/__main__.py` calls `framework.get_project_dir()` on every `Bash|Edit|Write` PreToolUse, before any `/ocd:setup` has run, in projects that may not even be git repos. The environment helper is load-bearing on the critical path in "plugin enabled, project uninit" state. It must stay trivial and dependency-free.
- **Existing propagation mechanism.** `.githooks/pre-commit` already copies 17 specific files from `plugins/ocd/` to every other plugin at commit time, opt-in per target subdirectory. Extension, not invention.
- **Marketplace spec stops at per-plugin primitives.** Cross-plugin shared code in a monorepo lives above the marketplace layer. Our solution extends the marketplace, not fights it.

## Target Structure

### Plugin tree (every plugin)

```
plugins/<plugin>/
├── bin/              — entry points
├── hooks/            — event-triggered callbacks
├── tools/            — NEW: always-on helpers, no lifecycle state
│   ├── environment.py    ← vendored from tools/environment.py (project root)
│   └── errors.py         ← vendored from tools/errors.py (project root)
└── systems/          — opt-in, dormant-by-default, user-activated
    └── setup/        — RENAMED from framework/; scoped purely to install/init/status orchestration
        ├── _enabled.py _metadata.py _deployment.py
        ├── _formatting.py _system_discovery.py _orchestration.py
        ├── __main__.py __init__.py
        └── (no _environment, no _errors — moved to plugin tools/)
```

### Project root

```
<project>/
├── bin/project-run       (exists)
├── tools/
│   ├── environment.py    ← CANONICAL — source of truth for get_project_dir, get_plugin_root, get_plugin_data_dir, get_claude_home
│   ├── errors.py         ← CANONICAL — source of truth for NotReadyError
│   ├── setup/            (exists — project bootstrap)
│   └── testing/          (exists — test orchestration; _environment.py consolidates into sibling tools/environment.py)
└── plugins/
```

### Resulting directory taxonomy (per plugin)

Every directory answers the question "when does this run?" without ambiguity:

| Dir | When | Lifecycle gate |
|---|---|---|
| `bin/` | Entry point invoked by the user or the plugin harness | None — direct exec |
| `hooks/` | Event-triggered by Claude Code (SessionStart, PreToolUse) | Fires the moment the plugin is enabled |
| `tools/` | Imported by anything inside the plugin that needs always-on primitives | None — ships with the plugin, no init required |
| `systems/` | Opt-in; dormant by default; activated via `/ocd:setup` | Explicit user activation |

## Axis Decisions

- **A (canonical location):** project root `tools/environment.py` + `tools/errors.py`.
- **B (how copies are produced):** extend existing `.githooks/pre-commit` propagation. New canonical sources replace the current `systems/framework/_environment.py` and `systems/framework/_errors.py` entries in the propagation map. Plugin target subdirectory becomes `tools/` instead of `systems/framework/`.
- **C (drift enforcement):** pre-commit does the work at commit time; add a project-level content-equality test that hashes every vendored copy and asserts bytes equal the canonical source. Catches drift introduced by bypassed hooks or direct branch pushes.
- **D (new-project bootstrap):** out of scope for this branch. Noted below as a follow-up.

## Work Order

1. **Canonical sources at project root.**
   - Move `plugins/ocd/systems/framework/_environment.py` → `tools/environment.py`.
   - Move `plugins/ocd/systems/framework/_errors.py` → `tools/errors.py`.
   - Consolidate the existing `tools/testing/_environment.py` into the new `tools/environment.py`. Delete `tools/testing/_environment.py`; update its one caller (`tools/testing/_sandbox.py`, `tools/testing/_venv.py`, `tools/setup/_orchestration.py`) to import from `tools.environment`.

2. **Vendor into ocd plugin's new `tools/` folder.**
   - `plugins/ocd/tools/environment.py` ← copy of project-root canonical.
   - `plugins/ocd/tools/errors.py` ← copy of project-root canonical.
   - `plugins/ocd/tools/__init__.py` — minimal facade exporting the public surface.

3. **Rename `systems/framework/` → `systems/setup/` in ocd.**
   - `git mv plugins/ocd/systems/framework plugins/ocd/systems/setup` (preserves history).
   - Remove `_environment.py` and `_errors.py` from the renamed `setup/` (they moved to tools/ in step 2).
   - Update `systems/setup/__init__.py` star-imports accordingly — drop env/errors imports.
   - Update `systems/setup/SKILL.md` (if any exists; verify).

4. **Migrate consumers of the old `framework` namespace.**
   - Grep reveals ~15 files doing `import framework` or `from framework._environment import …`. Each either:
     - Needs env helpers → `from tools.environment import get_project_dir, …`
     - Needs orchestration → `from systems.setup import …` (or whatever the new import path resolves to after the rename)
     - Needs both → two imports.
   - Specific call-out: `plugins/ocd/hooks/auto_approval/_settings.py::get_project_dir` currently wraps `framework.get_project_dir()` — rewrite to `from tools.environment import get_project_dir` and drop the wrapper.
   - Specific call-out: `plugins/ocd/run.py` currently adds `plugins/ocd/systems/` to sys.path. Also add `plugins/ocd/` so `from tools.environment import …` resolves. Drop the bare `import framework` idiom; all consumers use explicit package paths.

5. **Extend `.githooks/pre-commit`.**
   - Remove from propagation map: `plugins/ocd/systems/framework/_environment.py:systems/framework` and `plugins/ocd/systems/framework/_errors.py:systems/framework`.
   - Add to propagation map: `tools/environment.py:tools` and `tools/errors.py:tools` with canonical source at project root (not under `plugins/ocd/`).
   - The hook's current copy shape (`git show ":<canonical>" > <dest>`) works unchanged for the new canonical paths.
   - Update the remaining `systems/framework/*` entries to point at `systems/setup/*` after the rename.

6. **Add content-equality contract test.**
   - New `tests/integration/test_shared_file_sync.py` (or similar). Enumerates every entry in the pre-commit propagation map, reads the canonical and every expected vendored copy, asserts content hashes match. Failure message names the drifting file and references `.githooks/pre-commit` as the fix point.

7. **Fix adjacent `.git.is_dir()` walk in check.**
   - `plugins/ocd/systems/check/__main__.py::_project_root_from` currently walks ancestors looking for a `.git` directory. Replace the custom walk with `from tools.environment import get_project_dir` (either direct delegate, or a sibling helper `get_git_root_for(path)` if the seed-from-input-path semantic must be preserved).
   - Worktree decision: the seed-from-input semantic matters when check runs against paths outside the project. Preferred: add `get_git_root_for(path: Path) -> Path` in `tools/environment.py` that shells to `git -C <path> rev-parse --show-toplevel`. Replace the custom walk with this. Delete `_project_root_from`.

8. **Verify.**
   - `bin/project-run tests` passes end-to-end in the main worktree and in a linked worktree (contract test also runs).
   - `/checkpoint` succeeds; plugin cache picks up the reorganized layout.
   - Smoke test: open a Claude session in a different project with ocd plugin enabled but no `/ocd:setup` run; trigger a `Bash` tool use; auto_approval hook loads `tools.environment`, resolves project dir, returns expected answer.

## Per-Consumer Migration Grep Targets

From pdf-branch investigation, consumers of the old `framework` namespace (non-exhaustive, confirm during work):

```
plugins/ocd/hooks/auto_approval/_settings.py
plugins/ocd/hooks/auto_approval/_checking.py          (NotReadyError)
plugins/ocd/hooks/auto_approval/__main__.py           (transitively)
plugins/ocd/systems/framework/_enabled.py             (stays inside rename target)
plugins/ocd/systems/framework/_orchestration.py       (stays inside rename target)
plugins/ocd/systems/governance/_governance.py
plugins/ocd/systems/log/_init.py
plugins/ocd/systems/rules/_init.py
plugins/ocd/systems/conventions/_init.py
plugins/ocd/systems/refactor/_init.py
plugins/ocd/systems/navigator/__init__.py
plugins/ocd/systems/navigator/_references.py
plugins/ocd/systems/navigator/_scanner.py
plugins/ocd/systems/navigator/_skills.py
plugins/ocd/systems/navigator/_init.py
plugins/ocd/systems/navigator/__main__.py
plugins/ocd/systems/sandbox/_cleanup.py
plugins/ocd/systems/sandbox/_worktree.py
plugins/ocd/systems/check/__main__.py
plugins/ocd/systems/check/_dormancy.py
plugins/ocd/systems/permissions/_operations.py
plugins/ocd/systems/setup/__main__.py                 (after rename)
tests/plugins/ocd/conftest.py                         (already updated on sandbox/pdf — will need reconciliation)
tests/plugins/ocd/systems/navigator/integration/test_navigator_integration.py
```

Refactor plugin (`/ocd:refactor`) handles the bulk of rename mechanics.

## Out of Scope

- **New-project bootstrap tool** (axis D). Project-template repo or an `ocd:init-project` skill that scaffolds `bin/project-run`, `tools/`, starter plugin skeleton, pre-commit hook. Natural follow-up once the in-repo canonicalization settles.
- **Blueprint and other plugins' cutover.** They're added to propagation on next commit that touches their `tools/` subdir (existing opt-in model). No forced migration in this branch.
- **Shared-package extraction to private PyPI.** Heavier decoupling; revisit only if the monorepo splits.

## Open Questions

1. **`systems/setup/` vs `systems/install/`** as the post-rename name. Both describe the scope after stripping always-on primitives. `setup` aligns with the existing `/ocd:setup` skill name. Preference: `setup`.
2. **Per-plugin `tools/__init__.py` shape.** Should it re-export env helpers for convenience (`from .environment import *`) or stay empty (forcing explicit `from tools.environment import X`)? Preference: empty — explicit wins, matches the direction of dropping `import framework` bare idiom.
3. **Contract test scope.** Does the content-equality test also assert behavioral equivalence across a fixture matrix (env var set/unset, git repo / not, main/linked worktree), or is hash equality enough? Hash equality is sufficient by construction — if bytes match, behavior matches. Preference: hash-only, with a comment pointing to the rationale.

## Sequencing Note

The `_new.md` precondition relaxation already landed on `main` (pre-this-branch) and enables future sandbox spawns from any location. This plan presumes that change is present.
