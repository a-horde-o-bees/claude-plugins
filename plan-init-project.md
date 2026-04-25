# Addendum — `ocd:init-python-project` Skill

Companion to `plan.md`. The centralize-tools refactor settles the *structure* a Python project using these dev patterns should have (project-root `tools/` with canonical helpers; `bin/project-run` dispatcher; testing harness; content-equality contract test). This addendum scopes the *bootstrap* tool that creates that structure in a fresh Python project — the consumer of the canonical patterns we locked in on this branch.

## Why a Skill, Not Just Documentation

A prose "how to start a Python project with these dev patterns" README decays the moment the reference layout changes. Every new project becomes a tiny divergence — the monaco* failure mode, scaled up. A skill turns the layout into executable scaffolding: run once, get the current canonical structure. Re-run against an existing project for idempotent sync (missing files created, present files left untouched, drifted canonical sources flagged).

Same reasoning as why drift enforcement is a pre-commit hook plus a contract test rather than rules in a style guide: the pattern needs teeth.

## Scope Discipline — Python-Only, No Marketplace Coupling

This skill scaffolds a generic Python project that adopts the project-run + tools/ + testing-harness patterns. It does NOT scaffold a Claude-plugins marketplace, plugins, or any marketplace-specific artifact. The name carries the language coupling explicitly so users on Go/Rust/TypeScript/etc. don't think they need to run it, and so future siblings (`ocd:init-rust-project`, etc.) can compose at the skill-name level rather than as flags on a generic init.

Marketplace setup (the `plugins/` directory, the shared-files propagation map, marketplace standards) is out-of-scope for this skill. If we ever want it, it's a separate skill that layers on top of an already-init'd project (precondition: this skill ran first).

The ocd plugin itself stays language-agnostic — its other skills (rules, conventions, navigator, log, refactor, check, sandbox, governance, pdf) work in projects of any language. Bundling a Python-init skill inside ocd is acceptable because ocd dogfoods these patterns; users on non-Python projects simply don't invoke `/ocd:init-python-project`.

## End-State Definition

After `/ocd:init-python-project` runs against a target directory, the directory has:

```
<target>/
├── .gitignore                    ← seeded with .venv/, __pycache__/, .claude/ocd/ data paths
├── bin/
│   └── project-run               ← canonical project-level dispatcher
├── tools/
│   ├── environment.py            ← canonical env helpers (`tools.environment`)
│   ├── errors.py                 ← canonical error types (`tools.errors`)
│   ├── setup/                    ← `bin/project-run setup` implementation
│   └── testing/                  ← `bin/project-run tests` / `sandbox-tests` implementation
├── tests/
│   └── integration/
│       └── test_shared_file_sync.py   ← content-equality contract test (relevant once the project gains plugins/template directories; harmless before that)
├── pyproject.toml                ← project-level test config
├── ARCHITECTURE.md               ← seeded minimum (scope/role of the project, links to substantive docs once they exist)
├── CLAUDE.md                     ← seeded minimum (development workflow, testing command, editing-rules note)
└── README.md                     ← seeded minimum (what this project is, how to run tests)
```

No `plugins/`, no `.githooks/pre-commit` (no canonical sources to propagate yet — pre-commit infrastructure layers in via a separate skill once the project gains plugins or other propagation targets), no `--with-plugin` flag.

Git config is left alone — user runs `git init` themselves (or invokes init-python-project inside an existing repo).

## Invocation Shape

```
ocd:init-python-project <target> [--force-sync]
```

- `<target>` — required positional. Directory to scaffold into. May be empty, may contain existing files.
- `--force-sync` — optional. Overwrite drifted infrastructure templates with the current canonical version. Default: report drift, don't overwrite.

## Idempotency Rules

End-state semantics like the sandbox-verb redesign. Running twice doesn't fail.

- **Missing → create.** Any scaffolded path that doesn't exist is created from the template.
- **Present + matches canonical → silent pass.** A `tools/environment.py` whose hash equals the template canonical is left alone.
- **Present + drifted from canonical → report, don't overwrite.** List which files diverge; instruct the user to reconcile manually or pass `--force-sync` to overwrite. Never silently clobbers user customization.
- **User-facing scaffolded files (README.md, CLAUDE.md, ARCHITECTURE.md, pyproject.toml, .gitignore) are created only on first run.** These are user-maintained after creation; don't touch on re-run, even with `--force-sync`.

The distinction: infrastructure templates (`tools/environment.py`, `bin/project-run`, testing harness) are sync-on-request; user-maintained files are create-once.

## Template Source of Truth

Templates live inside the ocd plugin at `plugins/ocd/systems/init-python-project/templates/`, with the same path layout as the scaffolded end-state. Each file is the byte-for-byte source of what ends up in the target project.

This project dogfoods its own templates: this repo's `bin/project-run`, `tools/environment.py`, etc. ARE the canonical sources, and the templates under the plugin are propagated copies — same model as the centralize-tools refactor's per-plugin `tools/` vendoring, just with a different destination shape.

### Sync mechanism — extended propagation map

Centralize-tools' `.githooks/pre-commit` propagation map currently uses the shape `canonical:subdir-within-each-plugin` (e.g., `tools/environment.py:tools` copies the canonical into every `plugins/<name>/tools/`). For init-python-project's templates, the destination is a single fixed path, not a per-plugin subdir.

Extend the propagation map to support a second entry shape. One workable form:

```
SHARED_FILES_FIXED=(
    "tools/environment.py:plugins/ocd/systems/init-python-project/templates/tools"
    "tools/errors.py:plugins/ocd/systems/init-python-project/templates/tools"
    "bin/project-run:plugins/ocd/systems/init-python-project/templates/bin"
    # ... other infrastructure files mirrored into templates
)
```

A second loop over this map copies the canonical into the fixed destination when the canonical is staged. The existing `test_shared_file_sync.py` extends to walk this second map and assert byte equality, so drift fails on test invocation regardless of whether the pre-commit hook fired.

Net: one mechanism, two destination shapes, one contract test covering both.

## What init-python-project Does NOT Do

- **Does not install dependencies.** The scaffolded `pyproject.toml` declares them; the user installs with `uv sync` or equivalent. Aligns with existing plugin pattern.
- **Does not init git or set up CI.** Project-local scaffolding only. Users bring their own git + CI discipline.
- **Does not scaffold a marketplace, plugins, or any plugin-specific artifact.** Out-of-scope per *Scope Discipline*.
- **Does not install a `.githooks/pre-commit` hook.** That hook exists to propagate canonical sources across vendored copies — there are no vendored copies in a bare Python project. A future skill that adds plugin/marketplace structure can install the hook then.
- **Does not run for non-Python projects.** Name carries the language coupling. Sibling skills (if ever needed) handle other languages.

## Sequencing

1. centralize-tools lands first (the primary plan on this branch) — canonical templates exist, pre-commit propagation extended, contract test in place.
2. `ocd:init-python-project` branch after merge — skill implementation, template directory under ocd, propagation-map extension for fixed destinations, contract test extension.
3. Downstream: the first external Python project using this scaffolding becomes the real validation that the bootstrap works end-to-end.

Out-of-order risk: scaffolding before centralize-tools means the skill ships templates that don't match what this repo uses, and we have to migrate the templates once the refactor lands. Sequencing avoids it.

## Open Questions

1. **Interactive vs. non-interactive.** Does init-python-project prompt for `project-name` and other seeded values via AskUserQuestion, or take them as flags? Preference: positional `<target>` plus AskUserQuestion fallback for free-form fields — scriptable when automated, interactive when run by hand.
2. **Where to put marketplace/plugin scaffolding when we eventually want it.** Likely candidates: `ocd:init-marketplace` (project-level overlay that adds `plugins/`, the propagation hook, MARKETPLACE-STANDARDS.md) and `ocd:new-plugin <name>` (creates one plugin directory). Both layer on top of `ocd:init-python-project` having already run. Out of scope for this addendum.
