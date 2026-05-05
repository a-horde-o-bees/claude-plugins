# Changelog

All notable changes to plugins in this marketplace are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Tagged releases live on `main`. `main`'s `plugin.json` carries a per-commit auto-bumped patch counter between releases so Claude Code's reload detection fires for dev-channel users tracking main; the counter values are not logged here.

## [Unreleased]

Populated at release time by `/ocd:git release <version>`. The verb crawls git history since the last tag, agent-synthesizes a Keep-a-Changelog entry with cross-commit deconfliction, presents a draft + proposed bump for operator review, then on approval bumps the manifest, commits, tags, and pushes. Between releases, in-flight changes live in git history; this section is not maintained manually.

## [0.2.0] - 2026-05-05

First minor release after v0.1.0. Adds three new skills (retrospective, transcripts, needs-map), a transcripts MCP server, an end-to-end release workflow under `/ocd:git`, async CI watching, and substantial expansions to the `/ocd:check` discipline harness, alongside a steady stream of rule, convention, and principle refinements.

### Added

- `/ocd:transcripts` skill and `transcripts` MCP server — query Claude Code session transcripts (projects, sessions, exchanges) as structured data with time accounting, full chat content, and persistent per-exchange purpose summaries; backed by an auto-syncing SQLite DB ingested from `~/.claude/projects/`. Eight verbs cover `projects`, `sessions`, `exchanges`, `purposes-set`, `purposes-clear`, `schema-describe`, `sql-query`, and `report time-blocks`. Same operations available agent-side as MCP tools.
- `/ocd:retrospective` skill — session-end log capture that surfaces open threads first, then walks patterns, friction, ideas, decisions, and user-memory candidates; nothing written without explicit acceptance.
- `/ocd:needs-map` skill and `ocd-run needs-map` CLI — walk components through unmet-concern audits with addressing edges and mechanism rationales. Migrates the project-root `purpose-map` tool into a first-class ocd system at `.claude/ocd/needs-map/needs-map.db`.
- `/ocd:git release` verb — synthesizes a Keep-a-Changelog entry from commit history since the last tag (with cross-commit deconfliction), recommends a version per project methodology, and on approval writes CHANGELOG, bumps the manifest, commits, tags annotated, and pushes main + tag in one operation. Project methodology lives at `.claude/ocd/git/release.md` (bootstrapped via guided dialogue on first invocation).
- `/ocd:git ci` and `/ocd:git checkpoint` verbs — `ci` reports GitHub Actions run state for the latest commit on a branch (synchronous when complete, dispatches a background watcher when in-progress); `checkpoint` bundles commit + push + ci into one call. The project-level `/checkpoint` skill now delegates these generic steps to `/ocd:git`.
- `/ocd:check markdown` dimension — flags unprotected literal characters (`{}`, `<>`, `*`, `_`) in prose, table cells, and list items outside code blocks.
- `/ocd:check python` dimension — file-anchored parent-walking checks for python source.
- `/ocd:sandbox update` verb — in-place rebase of a sandbox onto `origin/main` without unpacking.
- `cli` convention — authoring expectations for plugin CLIs.
- `log-role` YAML frontmatter on log type templates — declares `queue` vs `reference` so cleanup tooling can classify entries; new `patterns` and `research` log types added.
- Filename-case rule — codifies entry-point (all-caps) vs content (lowercase) naming.
- `alignment-audit` pattern — research-driven audit methodology template.
- `Honesty` design principle — verify-before-acting, verify-before-stating, and bound-conclusions-to-what-was-examined trigger set.
- `Q#` question prefix convention — multi-question prompts enumerate questions as `Q1`, `Q2`, ... and options as lettered `A)`, `B)` to avoid collision with the CLI's `1/2/3` rating prompt.
- Roboto variable fonts bundled with `/ocd:pdf` compact preset; per-preset template folder layout for PDF presets.

### Changed

- `Reuse Before Create` principle renamed to `Borrow Before Build` to reflect broader scope across patterns, helpers, and conventions — not just code.
- `/ocd:git release` now treats `<version>` as optional; the synthesizer recommends a version per methodology and the user approves or overrides at review time.
- `/checkpoint` is branch-aware — sandbox and feature pushes skip main-only steps (marketplace refresh, plugin update); CI gate runs asynchronously via a background subagent and delivers outcome via PushNotification.
- `/ocd:sandbox unpack` is PR-based by default with a `--direct` escape hatch; can run from any worktree; sibling-worktree removal is now part of the headline contract.
- `/ocd:sandbox new` branches from `origin/main` with a confirmation step and shows the last 5 commits for orientation.
- `bin/plugins-run` renamed to `bin/project-run` (codifies the `<scope>-run` convention shared with `ocd-run`).
- `tests/` runner gains pytest passthrough; agent-spawning tests are opt-in via `--run-agent`. `scripts/test.sh` retired in favor of `bin/project-run tests`.
- `transcripts.db` is no longer tracked in the repo — it auto-syncs from `~/.claude/projects/` on every read and grew checkpoints to 157 MB. Fresh clones land with no DB and `/ocd:setup init` builds it.
- `tools/db.py` provides a centralized schema-aware DB init contract — systems declare DB location and schema-builder; init is surgical (no-op on healthy, backup-and-rebuild on schema drift). Eliminates the per-checkpoint "reinstall navigator.db" commit churn.
- `/ocd:check all` dispatches generically across registered dimensions; fixtures co-located with their dimension's tests.
- Per-system `reset` CLI verb (`ocd-run navigator reset`, `ocd-run needs-map reset`) is the explicit destructive rebuild path; init is no longer destructive by default.
- Process Flow Notation rule slimmed from 395 to 262 lines without dropping any constructs; step atomicity now explicit (no compound steps, no compound commands inside a single step).
- Testing rule reorganized by phase (authoring, driving, maintaining, deciding).
- Decision logs restructured per-subject with `##` per decision (one file per subject groups related decisions).
- Pre-commit hook gates `plugin.json` auto-bump on commits to `main` only.
- Pre-commit hook auto-bumps the patch version on every commit that stages plugin-tree changes other than `plugin.json` itself.
- Permissions template extended with `project-run`, `gh`, archives, and common process/net utilities. (needs review: confirm new permission entries match what downstream consumers should auto-receive.)
- Many convention and rule template refinements (architecture-md, audit-skill-md, mcp-server, python, readme-md, skill-md; markdown, process-flow-notation, system-docs, testing, workflow, log, refactor) — refer to deployed copies for current text.
- `logs/research/<subject>/` is now a directory with consolidated synthesis, optional per-wave outputs, and a `samples/` subdirectory; `patterns` content migrated out of a dedicated system into `logs/patterns/` and `logs/research/`.
- `ROADMAP.md` reorganized with a High-priority section and `priority:high` tag convention; subsequently renamed to `TASKS.md` to match the operational-next-actions naming convention. (needs review: confirm the rename is not still being referenced externally.)
- `systems/framework` package renamed to `systems/setup` (internal package layout — `/ocd:setup` skill name unchanged).
- `context-resources/` directory renamed to `context/` under log entries.

### Removed

- `scripts/release.sh` retired — bump logic, precondition checks, and operator-instruction echoes consolidated into `/ocd:git release`.
- Integration tests for retired `release.sh` removed; the new flow is exercised via real skill invocation.

### Fixed

- `/ocd:pdf` threads `FontConfiguration` through the WeasyPrint render pipeline so bundled fonts are honored consistently.
- `/ocd:sandbox unpack` captures invoking cwd; teardown collapsed into one `--delete-branch` call.
- Post-commit hook syncs the main index after a partial-commit auto-bump so the working tree stays consistent with the bumped manifest.

## [0.1.0] - 2026-04-22

Initial release of the `ocd` plugin — deterministic enforcement of permissions, rules, and structural conventions for Claude Code, with agent-facing project navigation.

### Added

- PreToolUse hooks: `auto_approval` (permission enforcement with hardcoded structural blocks + dynamic settings evaluation; fail-open wrapper so hook crashes never block tool calls) and `convention_gate` (surfaces applicable conventions from `.claude/conventions/` on Read/Edit/Write, matched to file path via governance frontmatter).
- Rule corpus auto-loaded into `.claude/rules/ocd/` on init: design principles, workflow discipline, testing discipline, process flow notation, system-docs requirements, markdown standards.
- Convention templates matched by file pattern: Python, markdown, SKILL.md, audit SKILL.md, audit triage, MCP server, README.md, CLAUDE.md, ARCHITECTURE.md, governance-file frontmatter.
- Navigator system — SQLite-backed project structure index with human-written descriptions. Skill (`/ocd:navigator`), CLI, and MCP server (`paths_*`, `skills_*`, `references_*`, `scope_*` tools) sharing one library.
- Governance library — match files to applicable rules/conventions, list entries, compute dependency-ordered level grouping (Tarjan's SCC). Standard-library only, reads directly from disk per call.
- Skills under `/ocd:` — `setup`, `git`, `navigator`, `log`, `pdf`, `sandbox`, `refactor`, `check`. Per-system opt-in via `/ocd:setup enable <system>`; state persists in `.claude/ocd/enabled-systems.json`.
- System Dormancy contract — uninitialized systems expose no tools, register no rules, route skills to setup. Enforced by `/ocd:check dormancy`.
- CI / release / validate GitHub Actions workflows; `scripts/release.sh` automates the Option E release cut (tags on main, no release branches).
