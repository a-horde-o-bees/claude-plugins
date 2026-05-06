---
includes: "CLAUDE.md"
---

# CLAUDE.md Conventions

Content standards for `CLAUDE.md` files. Agent-facing operational reference for systems whose operational content is not packaged as a slash skill (skills use `SKILL.md`). `CLAUDE.md` is loaded by every agent on every spawn; its content is paid by every consumer regardless of task.

## Purpose Statement

Opens with the system name or scope and a one-line description of what operational guidance this file provides. A reader encountering the file for the first time understands the system's identity and what procedures are covered.

## Two Modes

A `CLAUDE.md` is one of two shapes depending on the system's structure:

### Inline mode (small systems)

For systems whose operational content fits cleanly in a single file, `CLAUDE.md` carries the procedures inline. Group sections by topic; order by workflow sequence or frequency of use.

Inline mode contains:

- **Procedures** — step-by-step instructions for recurring operations
- **Workflow rules** — constraints on how work is done
- **Tool invocation patterns** — how to run system-specific tools
- **Content routing** — where different types of content belong within the system

### Navigation-hub mode (systems with operational subdirectories)

When `workflows/`, `components/`, or `plans/` subdirectories exist, `CLAUDE.md` collapses to an index. Topic-specific content has narrower consumers and lives where those consumers reach for it; the hub stays small because every spawned agent pays its cost.

The index follows a fixed structure:

1. L1 heading and purpose statement
2. `workflows/` — list with one-line purpose per file
3. `components/` — list with one-line purpose per file
4. `plans/` — list with one-line purpose per file (when any exist)
5. Other top-level docs — `TASKS.md`, decision records, semantic specs, etc.
6. Cold-pickup reading order — the sequence an agent should follow when starting from a cleared context

The hub-mode `CLAUDE.md` does not duplicate detail from the files it indexes. Each entry is a single line: filename plus one-line purpose. Detail lives in the indexed file.

## Architecture Reference

When operational guidance requires structural context to be actionable, direct the agent to read `ARCHITECTURE.md` rather than embedding the context inline. The architecture document is the single source for how the system works; the operational document references it rather than re-explaining.

## Exclusions

- Technical internals (layers, schema, design patterns) — those belong in `ARCHITECTURE.md`
- User-facing content (installation, configuration, usage) — those belong in `README.md`
- Detail from indexed files — in navigation-hub mode, the hub points; the file describes

## Currency

Describes current procedures. Do not reference previous workflows, removed commands, or process history — that information lives in git history and decision records.
