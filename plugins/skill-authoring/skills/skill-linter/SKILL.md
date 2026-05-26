---
name: skill-linter
description: Use when running or extending this project's skill linter — checks skill folders and their plugin manifests against the criteria in criteria.md.
---

# Skill Linter

Lint authored skills against the project's structural and cross-reference criteria, so the pre-commit hook stays minimal and authoring skills carry only judgment. The rules to enforce live in `criteria.md`; this skill realizes them as runnable checks under `scripts/`.

## Workflow

1. Read `criteria.md` — the enforce-list, each criterion tagged ready or pending.
2. For each criterion tagged ready:
   - If a bundled script in `scripts/` covers it: run it over the target plugins or skills.
   - Else: author the check — a script under `scripts/` or a documented manual review — and add it.
3. Skip criteria tagged pending; record them as not-yet-enforced rather than running them.
4. Report per criterion: pass, fail (with locations), or pending.

## Cross-plugin dependency check

`scripts/check_plugin_deps.py [<plugin> ...]` verifies that cross-plugin `/skill` invocations in a plugin's skill bodies resolve through dependencies declared in its `plugin.json`. With no arguments it checks every plugin; run it from the repo root.

Pending research into the resolution model (see `criteria.md`), so it is not wired into pre-commit — run it here on demand.

## Keeping criteria current

`criteria.md` is the source of truth. When it changes, add, retune, or retire the matching check so the linter and the criteria stay matched.
