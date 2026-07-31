# DECISIONS

The counterfactual record for markdown-authoring's shape — why the lint lives here and why the override surface is severity-only.

## Markdown lint lives inside this skill, not as a sibling

**Decision.** The lint capability is bundled into markdown-authoring itself rather than shipped as a separate project-tooling skill; lint-markdown, the prior form, is retired.

**Forces.** The authoring rule must fire at write time everywhere, not only in projects that stood up a linter — mechanical enforcement over attentional compliance.

**Rejected.**

- *Folding markdown-authoring into description-authoring*: description-authoring is scale-general (commit subjects, tool help, docstrings), not markdown-specific; the merge blurs its scope.
- *A separate project-tooling skill* (lint-markdown, the prior form): enforcement reached only projects that ran the stand-up, the rules split across two homes (its criteria list vs. the authoring skill), and the cluster spent a second listing entry.

## Overrides are severity-only config; different rules are a skill shadow

**Decision.** The override surface is exactly two layers — severity retuning by project config, and full replacement by skill shadow — with no parameterized rules.

**Forces.** Installers of the suite hold real formatting preferences (hard-wrapped paragraphs, other indent widths), so the bundled script must not force a fork over a severity disagreement — but the config must not grow into a second source of truth beside `lint-spec.md`.

**Rejected.**

- *Parameterized rules* (e.g. a configurable indent width): every knob doubles the surface to keep matched — spec, schema, and test matrix — while severity covers the common disagreements and the shadow layer covers the rest at zero code.
- *An override file inside the skill folder*: suite updates would clobber user edits; the project's own `.claude/` survives them.
- *Config passed as a CLI flag*: every call site (skills, hooks, users) would have to know and repeat the flag; nearest-ancestor discovery makes the preference ambient to the files it governs.
