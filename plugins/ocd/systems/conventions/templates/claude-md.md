---
tagline: Content standards for CLAUDE.md — agent-facing operational reference
---

# CLAUDE.md Conventions

Content standards for `CLAUDE.md` files. Agent-facing operational reference for systems whose operational content is not packaged as a slash skill (skills use `SKILL.md`). `CLAUDE.md` is loaded by every agent on every spawn; its content is paid by every consumer regardless of task.

## Purpose Statement

Opens with the system name or scope and a one-line description of what operational guidance this file provides. A reader encountering the file for the first time understands the system's identity and what procedures are covered.

## Required Sections

Every `CLAUDE.md` includes these sections in order:

1. L1 heading and purpose statement
2. Optional inline sections — project-specific triggers, external-doc pointers, inline procedures (see *Two Modes* below)
3. Paths — filesystem layout reference (see *Paths* below)
4. Cold-pickup — one-line direction to the system's persistent work surface (see *Cold-pickup* below)

## Two Modes

A `CLAUDE.md` is one of two shapes depending on the system's structure:

### Inline mode (small systems)

For systems whose operational content fits cleanly in a single file, `CLAUDE.md` carries the procedures inline as part of the optional inline sections. Group sections by topic; order by workflow sequence or frequency of use.

Inline content typically includes:

- **Procedures** — step-by-step instructions for recurring operations
- **Workflow rules** — constraints on how work is done
- **Tool invocation patterns** — how to run system-specific tools
- **Content routing** — where different types of content belong within the system

### Navigation-hub mode (systems with operational subdirectories)

When `workflows/`, `components/`, or `plans/` subdirectories exist, `CLAUDE.md` collapses to an index. Topic-specific content has narrower consumers and lives where those consumers reach for it; the hub stays small because every spawned agent pays its cost. The hub-mode `CLAUDE.md` does not duplicate detail from the files it indexes — Paths points; the indexed file describes.

## Paths

Default section listing every path at the system's root that an agent might need to read or reason about — folders and files — with a one-line purpose. Enumeration discipline for folders:

- Folder owns its own `CLAUDE.md` / `SKILL.md` → list the folder, do not enumerate. The subsystem's index owns its scope.
- Folder has no sub-index → enumerate contents only when both: (a) the folder's purpose alone does not tell the agent when its contents apply, AND (b) the contents are something an agent operating in this system should broadly know.
- Otherwise → list the folder once with its purpose; agents navigate inside on demand.

## Cold-pickup

One-line direction to whatever surface tracks the system's in-flight work — typically `TASKS.md` when present. `CLAUDE.md` is auto-loaded on every spawn, so it does not appear in its own reading order. `README.md` is user-facing. `ARCHITECTURE.md` is on-demand for tasks that touch internals. Other paths load as the work calls for them; do not list them in cold-pickup — they belong in Paths.

## Architecture Reference

When operational guidance requires structural context to be actionable, direct the agent to read `ARCHITECTURE.md` rather than embedding the context inline. The architecture document is the single source for how the system works; the operational document references it rather than re-explaining.

## Exclusions

- Technical internals (layers, schema, design patterns) — those belong in `ARCHITECTURE.md`
- User-facing content (installation, configuration, usage) — those belong in `README.md`
- Detail from indexed files — in navigation-hub mode, the hub points; the file describes

## Currency

Describes current procedures. Do not reference previous workflows, removed commands, or process history — that information lives in git history and decision records.
