# Opt-in clean for navigator, log, permissions

The per-system opt-in surface (`/ocd:setup enable|disable`) ships with `clean()` implemented for template-deploying systems (rules, conventions, patterns). Three systems with state beyond template files currently print a warning on `disable` and leave their artifacts in place. A follow-up should add `clean()` so `disable` fully reconciles disk state.

## Per-system semantics

- **navigator** — delete `.claude/<plugin>/navigator/navigator.db` and any parent directories now empty. Navigator tools stop seeing data; re-enable triggers a fresh scan.
- **log** — remove only the type templates (`_template.md` in each type directory). User entries are never cleaned — they are user content, not plugin-deployed. Empty type directories can be removed; directories with user entries stay.
- **permissions** — invoke the existing `permissions clean` flow to remove recommended patterns from whichever scope they were deployed to. `enabled-systems.json` is the opt-in, but the scope the user deployed permissions into is a separate piece of state that clean() needs to recover.

## Why not in v0.1.0

The primary scope-bleed problem the opt-in surface solves (rules loading on non-dev projects) is fixed by `rules.clean()`. The three above are cosmetic — disabling them without clean() does not cause the "agent loads conflicting context" failure the feature was built to stop. Good enough to ship; worth finishing when the need surfaces.
