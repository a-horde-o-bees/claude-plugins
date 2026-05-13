# ocd

Skill-based plugin. Each former system of the legacy monolithic `ocd` plugin is being migrated into a self-contained skill that bundles its own dependencies (path resolution, error types, PFN, etc.) under `<skill>/scripts/`.

## Status

Migration in progress. Migrated skills land here; the remaining legacy code lives at `plugins/ocd-old/` and is invisible to the marketplace.

Each migrated skill follows the authoring discipline encoded by [`skill-authoring`](../skill-authoring/README.md) (PFN workflow notation, progressive disclosure, skill-level dependency bundling).

## Skills

| Skill | Verbs | Status |
|-------|-------|--------|
| [`git`](skills/git/SKILL.md) | `commit`, `push`, `ci`, `checkpoint`, `release` | Migrated 2026-05-12 — first skill to exercise the AIA-cluster dependency pattern (skill-level + verb-level `dependencies:` frontmatter resolved via `scripts/_deps.py`) |
| [`rebuild`](skills/rebuild/SKILL.md) | (no verbs — single workflow) | Authored 2026-05-12 — re-evaluates an existing artifact against the currently-loaded rule set and rewrites it as if authoring for the first time. Use after a rule has evolved, a rename or split, or when discipline drift has accumulated. |
| [`rules`](skills/rules/SKILL.md) | `list`, `show`, `status`, `install`, `uninstall` | Migrated 2026-05-12 from `plugins/ocd-old/systems/rules/`. Manages always-on agent guidance deployment — `install` copies rule canonicals to `<scope>/rules/dependencies/<name>.md` so Claude Code auto-loads them; `uninstall` removes them. Catalog ships bundled at `<skill>/_dependencies/` (underscore-prefix marks install-source-only storage; excluded from runtime discovery), auto-propagated from project-root `shared/_dependencies/` via pre-commit. |

## Distribution

Skills install per-skill via [`npx skills`](https://skills.sh) from this repository into a target project, at user or project scope as chosen by the installer.
