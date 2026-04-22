# Changelog

All notable changes to plugins in this marketplace are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Tagged releases live on `main`. `main`'s `plugin.json` carries a per-commit auto-bumped patch counter between releases so Claude Code's reload detection fires for dev-channel users tracking main; the counter values are not logged here.

## [Unreleased]

No unreleased changes.

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
