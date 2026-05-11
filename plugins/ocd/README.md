# ocd

Skill-based plugin. Each former system of the legacy monolithic `ocd` plugin is being migrated into a self-contained skill that bundles its own dependencies (path resolution, error types, PFN, etc.) under `<skill>/scripts/`.

## Status

This plugin is currently empty. Migration is in-progress; the legacy code lives at `plugins/ocd-old/` and is invisible to the marketplace.

Each migrated skill follows the authoring discipline encoded by [`progressive-skill-composer`](../progressive-skill-composer/README.md) (PFN workflow notation, progressive disclosure, skill-level dependency bundling).

## Distribution

Skills install per-skill via [`npx skills`](https://skills.sh) from this repository into a target project, at user or project scope as chosen by the installer.
