---
log-role: reference
---

# Log

Decisions governing the `/log` skill — capture verbs (`add`/`list`/`remove`), the `research` subcommand surface, and the supporting Python package layout under `plugins/ocd/systems/log/`.

## Research analysis lives under `/log`, not a new top-level skill

### Context

`logs/research/<subject>/samples/` corpora are the system-of-record for long-form ecosystem investigations. Operating on them — counting heading-tree coverage, consolidating per-section content across samples, checking duplicate-heading invariants — is "log analysis" applied to one specific log type. The sandbox needed somewhere to put that surface area: a CLI dispatcher (`ocd-run … …`), a skill workflow fragment (`_*.md`), and a Python package the analytical primitives can live in.

### Options Considered

**Top-level `/research` skill.** Treats research analysis as its own domain. Rejected: the corpora are governed by the log system already (routing, lifecycle, role declaration, template rules all live in `plugins/ocd/systems/log/`). A peer skill would have to re-read those rules to know what a research entry even is, and any future log-type analyzers (cross-corpus deconfliction, queue-log review) would need their own peer skills for the same reason. The split is cosmetic; the cohesion is not.

**Project-local `tools/` script.** Keeps the analytical primitives close to the corpora that use them. Rejected: the primitives are reusable infrastructure (any project consuming the ocd plugin gets a `logs/research/` corpus and would benefit), and `tools/` is reserved for project-level operational scripts that do not ship to downstream consumers.

**Subcommand under the existing `/log` skill.** `research` becomes a verb the skill dispatches like `add`/`list`/`remove`. The skill's domain is already "operate on `logs/`"; analysis is a natural extension of that domain. Accepted.

### Decision

Extend `/log` with a `research <verb>` subcommand. The skill workflow gates on the leading token (`research` → `_research.md` → `ocd-run log research <remainder>`); legacy verbs (`add`/`list`/`remove`) remain skill-level workflow fragments because they are context-only operations with no Python runtime. The CLI lives at `plugins/ocd/systems/log/__main__.py` and dispatches into `research/_sample_tools.py` for the analytical primitives.

### Consequences

- **Enables:** future log-type analyzers (e.g. `/log queue review`, cross-corpus deconfliction) compose under the same skill without proliferating top-level commands
- **Enables:** `_sample_tools.py` is pure-Python with no plugin-internal dependencies and re-importable from a future retrofit engine or project-level script
- **Constrains:** the `/log` SKILL.md description must keep enumerating its verb set as the surface grows; once a fourth or fifth verb-group lands, this may exceed what one description paragraph can usefully convey, at which point splitting (e.g. extracting `research` into its own skill that the `/log` workflow delegates to) is reconsidered

## Mutually exclusive `--subject` / `--dir` samples-directory locator

### Context

`count-sections` and `consolidate` both operate on a samples directory. Two access patterns exist: the conventional one (`logs/research/<name>/samples/` for an in-project corpus) and the ad-hoc one (an arbitrary path, e.g. another checkout, a temp directory during template development, or a corpus pulled from elsewhere for one-off comparison). Both must be reachable; neither composes meaningfully with the other.

### Options Considered

**Single positional path.** `ocd-run log research count-sections <path>`. Rejected: in the common case, the user types `<project>/logs/research/<subject>/samples/` — five path segments to invoke the most frequent verb. The convention deserves a shorthand.

**`--subject NAME` only, `<path>` discouraged.** Rejected: forecloses ad-hoc use entirely. Template-development and cross-corpus inspection would have to symlink into `logs/research/`, polluting the canonical location.

**Both flags, optional, default-resolution rules.** `--subject` resolves to convention, `--dir` overrides, neither required. Rejected: requires a default (probably current directory, probably wrong), and "neither given" silently produces a useless answer or a confusing error. The locator is required information, not a tunable.

**Mutually exclusive group, exactly one required.** Argparse enforces "exactly one" structurally. Both verbs share the same factored `_add_samples_location_args` helper so the surface is identical. Accepted.

### Decision

`--subject NAME` resolves to `<cwd>/logs/research/<name>/samples/`; `--dir PATH` accepts any directory; the two are mutually exclusive and one is required. Both `count-sections` and `consolidate` use the same helper so users learn one dialect.

### Consequences

- **Enables:** common case is `--subject mcp` — terse and convention-aligned; ad-hoc case stays first-class via `--dir`
- **Enables:** `make-invalid-states-unrepresentable` — neither "both given" nor "neither given" can be expressed at the CLI; argparse rejects them before the dispatcher runs
- **Constrains:** `--subject` is bound to current-working-directory resolution. Running the skill from outside the project root would resolve against the wrong tree. Acceptable: project-root cwd is enforced everywhere else in this project, so the binding matches the operating envelope

## Empty `__init__.py` files persist in the test subtree

### Context

The plugin test suite uses pytest with `--import-mode=importlib` and a `pythonpath` of `["../../../plugins/ocd", "../../../plugins/ocd/systems"]`. Tests import the system under test as `from systems.log.research._sample_tools import ...` — they consume the source tree as a package, which is what makes the imports identical to production code paths.

When the test directory at `tests/plugins/ocd/systems/` contains its own `__init__.py`, that file marks `tests/plugins/ocd/systems/` as a regular Python package — and a regular package on `sys.path` shadows the namespace package at `plugins/ocd/systems/`. Test imports of `systems.log.research._sample_tools` then resolve into the test directory, fail to find the source modules, and report `ModuleNotFoundError`.

### Options Considered

**Delete every test `__init__.py`.** Removes the shadowing. Rejected: pytest's `--import-mode=importlib` discovery still benefits from package directories (each test subdirectory becomes importable, allowing relative-import patterns and shared fixtures via `conftest.py` chains).

**Rename the test directory tree to avoid collision.** E.g. `tests/plugins/ocd/system_tests/log/...`. Rejected: the test tree's structure mirroring the source tree is the convention — it makes the mapping between test and code obvious to a reader and lets coverage tools align them automatically. Renaming for an importlib quirk is the wrong layer to fix.

**Keep `__init__.py` empty in every test subdirectory.** Empty files do not contribute names, but their presence still marks the directory as a package for pytest's importlib mode. The shadowing problem is specifically about `tests/plugins/ocd/systems/__init__.py` competing with the source `systems/` namespace — but pytest's `pythonpath` is set to the source directories, not to `tests/plugins/ocd/`, so the test-tree `__init__.py` files are not visible as competing top-level packages. They only serve as in-tree pytest collection markers. Accepted.

### Decision

Empty `__init__.py` placeholders live at every level of the test mirror: `tests/plugins/ocd/systems/log/__init__.py`, `.../log/research/__init__.py`. They are required for pytest's importlib mode to discover tests as importable modules; they are empty because the test packages re-export nothing. The shadowing concern is contained because `pythonpath` does not include the test root.

### Consequences

- **Enables:** test imports follow source imports symbolically (`from systems.log.research._sample_tools import …`) — agents reading the test file understand the production import path immediately
- **Enables:** future test additions in this subtree (e.g. CLI smoke tests for `__main__.py`) drop in without import-config changes
- **Constrains:** any move of the test tree relative to the source tree must preserve the `pythonpath` invariant — adding `tests/plugins/ocd/` to `pythonpath` would re-introduce the shadowing problem

## Sandbox scope excludes retrofit engine, work-queue tooling, and migration manifests

### Context

The same session that authored this sandbox also identified follow-on phases: a research-corpus retrofit (Phase A), a master template design pass (Phase B), and a generic retrofit engine (Phase C/D) that could replace `logs/research/mcp/scripts/_retrofit_samples_to_template.py` with corpus-agnostic infrastructure. The sandbox could have bundled some of that work — building the retrofit engine alongside `sample_tools` was particularly tempting because the same heading-tree primitives underpin both.

### Options Considered

**Bundle retrofit engine and sample_tools in one sandbox.** Ships infrastructure together. Rejected: retrofit engine requirements are unknown until Phase B produces a master template and migration manifest. Building it now means designing for hypothetical migrations that may not exist — directly violating YAGNI. If Phase B's manifest is empty (no structural transformations needed), the entire engine is dead code on first day.

**Bundle work-queue/log CSV management.** A future capability for tracking research observations across iteration cycles. Rejected: the use case is speculative; no live workflow needs it yet, and the data shape will be shaped by Phase A's actual observations rather than design-time guesses.

**Ship only the foundation: skill extension + analytical primitives.** Phase A retrofit consumes them as a library. Phase B sees the corpora through them. Phase C/D engine, if needed, builds on them. Accepted.

### Decision

This sandbox ships `sample_tools` (heading-tree parsing, duplicate detection, cross-sample coverage, per-section consolidation) and the `/log research` surface that exposes them. It explicitly excludes:

- A generic retrofit engine — Phase C/D, contingent on Phase B producing a non-empty migration manifest
- Work-queue or observation-log CSV management — a Phase A artifact whose schema is determined by what Phase A observes
- Master template design — Phase B, which uses `count-sections` / `consolidate` outputs as inputs to human + analytical synthesis
- Deletion of `logs/research/mcp/scripts/_retrofit_samples_to_template.py` — corpus-specific retrofit kept until the generic replacement actually exists

### Consequences

- **Enables:** unpacking this sandbox lands runnable, tested infrastructure with no half-built downstream
- **Enables:** Phase A starts immediately on main with the primitives available
- **Constrains:** post-unpack work needs a durable home (logs/idea, ROADMAP, or external tracker) since the originating session's task list does not survive unpack; this is captured in `SANDBOX-TASKS.md` under "Tracking handoff after unpack"
- **Constrains:** if Phase A or Phase B reveal that retrofit-engine design needs primitives `sample_tools` does not provide, those land in a future sandbox rather than being retrofitted into this one
