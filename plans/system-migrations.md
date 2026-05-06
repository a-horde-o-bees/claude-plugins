# System migrations

Migrate each ocd plugin system to the system-structure layout established by the rules-system exemplar. Tracks per-system status; each migration is its own commit.

## Goal

Every system in `plugins/ocd/systems/` conforms to `plugin-system.md` (top-level `__init__.py` with the four facade functions, `workflows/install.md`, `workflows/uninstall.md`) and `system-structure.md` (three-doc set when substantive, navigation-hub `CLAUDE.md`/`SKILL.md` when subdirs exist). Setup orchestration discovers every system uniformly; un-migrated systems remain invisible until they migrate.

## Output

Each system migration lands as a commit containing:

- `<system>/__init__.py` exposing `purpose`, `status`, `install`, `uninstall` (or `SKILL.md` for skill-only systems that don't appear in `/ocd:setup`)
- `<system>/workflows/install.md` and `<system>/workflows/uninstall.md` for setup-managed systems
- `<system>/README.md`, `<system>/ARCHITECTURE.md`, `<system>/CLAUDE.md` (or `SKILL.md`) when substantive
- Tests for the new facade and per-scope install paths
- Updated doc references in plugin-level `ARCHITECTURE.md`, `README.md`

## Sequence

Order by independence and risk. Smallest/cleanest first to firm the template; larger systems last.

1. ~~rules — exemplar~~ (done in prior commit)
2. permissions — small migration; already partly scope-aware via `--scope` flag
3. refactor — small; ships one rule template, no DB
4. log — moderate; deploys log-type templates to project root `logs/`, project-only scope
5. conventions — moderate; merged-from-governance system; ships templates + matching CLI; both scopes
6. needs_map — DB-backed; project-only scope
7. navigator — DB-backed; project-only scope; operational CLI + MCP server (introduces operational gating)
8. transcripts — DB-backed; **scope migration to user** (see plans/scope-per-system-install.md if extracted)
9. Skill-only systems (check, pdf, sandbox, retrospective, git) — no facade; system-structure layout only

## Decisions

- Setup-managed vs skill-only — systems with deployable artifacts (templates, DB, patterns) are setup-managed and need the facade. Skills with no deployable state are skill-only and just adopt the directory layout
- Re-deployment of conventions during conventions migration — `.claude/conventions/ocd/` is currently empty; user picks which to install via the new setup flow once the system migrates
- Operational CLI gating — added to systems that have non-setup CLI verbs (navigator, transcripts, conventions, needs_map). Pattern from `plugin-system.md` *Operational CLI Gating*
- Scope decisions per system are made during that system's migration — not centrally

## Open questions

- transcripts user-scope DB location: `~/.claude/ocd/transcripts/transcripts.db` or under `get_plugin_data_dir()`? Resolve when transcripts migrates.
- Do conventions deploy templates (the on-demand convention files agents see) and matching infrastructure (the Python/CLI for `governance_match`/`governance_list`) need to install as one unit, or can the user pick which? Resolve when conventions migrates.
- Operational CLI gating: should `status()` count `divergent` files as installed for gate purposes? Probably yes — they're deployed, just need refresh. Confirm during navigator migration.
