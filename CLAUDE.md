# claude-plugins

Project-level navigation hub for the claude-plugins marketplace repository. Read the sibling `ARCHITECTURE.md` before acting on internals.

## Universal triggers

When the user says **"checkpoint"**: skill: `/checkpoint`.

When implementing plugin infrastructure (hooks, MCP servers, dependency management, environment variables), the official Claude Code plugin docs are the primary source: <https://code.claude.com/docs/en/plugins-reference>

## components/

Reference content. Look up the topic; apply its guidance.

- `audit-skill-invocation.md` — pre-flight check before invoking `/audit-*` skills (run `/checkpoint` first when content has shifted)
- `skill-testing-modes.md` — real invocation vs ad-hoc Task agent for skill development
- `plugin-bin-invocation.md` — bare-name (`ocd-run`) vs full-path (`plugins/ocd/bin/ocd-run`) and when to use each
- `versioning.md` — `x.y.z` semver, pre-commit auto-bump, release cuts via `/ocd:git release`, patch releases
- `template-edit-paths.md` — where rule/convention/log templates live; never edit deployed copies under `.claude/`
- `python-dependencies.md` — adding a package to a plugin's `pyproject.toml` and the `SessionStart` reinstall
- `external-tool-dependencies.md` — runtime check pattern for npm globals / system packages skills depend on
- `testing.md` — `bin/project-run tests` flag surface and layout
- `project-tooling.md` — `bin/project-run` commands and `tools/` layout
- `architectural-boundaries.md` — what the plugin layer can control vs what's harness-determined

## workflows/

Top-down procedures. (Currently empty at project root — operational procedures live in skills under each plugin.)

## plans/

Active and upcoming workstreams.

- `system-migrations.md` — overarching plan for migrating each ocd system to the system-structure layout
- `conditional-memory.md` — investigate per-rule trigger-conditioned auto-load to reduce always-on token floor
- `pfn-sweep.md` — convert prose procedural sections to Process Flow Notation
- `subflow-extraction.md` — extract conditional sub-flows into separate workflow/component files
- `init-project-skill.md` — bootstrap tool that creates the canonical project structure in fresh Python projects

## Other top-level docs

- `TASKS.md` — persistent task tracker; pointer-only, links to plans
- `ARCHITECTURE.md` — project-level architecture
- `README.md` — user/contributor-facing overview
- `MARKETPLACE-STANDARDS.md` — marketplace conventions
- `CHANGELOG.md` — release history

## Cold-pickup reading order

When starting from a cleared context:

1. `README.md` — what this project is
2. `ARCHITECTURE.md` — how the pieces fit together
3. `CLAUDE.md` (this file) — navigation index
4. `TASKS.md` — current work surface
5. The relevant `plans/<workstream>.md` for the active task
6. Targeted `components/<topic>.md` lookups as procedures need them
