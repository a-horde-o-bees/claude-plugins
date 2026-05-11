# needs-map

Component-needs audit for project evaluation. Answers one question about each component in the project: **is this component justified by a specific unmet concern?** Components that cannot point at a sub-concern that no existing component addresses through any mechanism are candidates for removal, merger, or rewrite.

The tool is the audit surface — a SQLite-backed CLI for maintaining the model. The `/ocd:needs-map` skill drives the evaluation workflow; this README covers the tool mechanics.

## Model

Two entity types connected by two relationship types:

- **Needs** — problems to solve (the "why"), organized as a tree via `parent_id`. Root needs are project-level business concerns; refined sub-needs appear beneath them as discovery requires more specificity.
- **Components** — structural units (the "how"). Any artifact that can address needs: rules, conventions, tools, skills, MCP servers, etc.
- **depends_on** — component → component, structural DAG. "What must exist for this to work."
- **addresses** — component → refined need, with a rationale describing the specific mechanism. Capability claim.

Components carry non-authoritative **source-location paths** pointing at the real artifact. Paths may be files, directories, `file#anchor` references, or glob patterns (e.g. `skills/friction/*`).

Entities use opaque short ids (`c1`, `n1`). Descriptions are the load-bearing meaning — names are deliberately absent so readers engage with the actual statement. See ARCHITECTURE.md for the design rationale.

## Wiring Rules

The CLI enforces three constraints at insertion time so every addressing edge lands where "is this unmet?" has a meaningful answer:

- A component cannot address a root need — must attach at depth ≥ 1
- A component cannot address both a need and any ancestor of that need
- A component cannot address both a need and any descendant of that need

## CLI

Invoke via `ocd-run`:

```
ocd-run needs-map <command> [args...]
```

Hyphens in `needs-map` are rewritten to underscore for Python package resolution; `ocd-run needs_map` works identically.

### Commands

| Category | Commands |
|----------|----------|
| Components | `add-component`, `set-component`, `remove-component` |
| Needs | `add-need`, `refine`, `set-need`, `set-parent`, `remove-need` |
| Dependency edges | `depend`, `undepend` |
| Addressing edges | `address`, `unaddress`, `set-rationale` |
| Paths | `add-path`, `remove-path` |
| Validation | `validate`, `invalidate` |
| Analysis | `dependencies`, `needs`, `addresses`, `where`, `why`, `how`, `compare`, `summary`, `uncovered` |

Run `ocd-run needs-map <command> --help` for per-command argument details.

### Output conventions

| Symbol | Meaning |
|--------|---------|
| `◈` | Component |
| `☆` | Root need |
| `◇` | Refined sub-need |
| `?` prefix | Unvalidated — identity still under question |
| `✓` / `✗` / `○` / (space) | Coverage: covered / gap / unrefined root / abstract interior |

## Installation

needs-map is deployed as part of the ocd plugin. The database location is `.claude/ocd/needs-map/needs-map.db`. Initialize via `/ocd:setup init` (or a direct `ocd-run framework init needs-map`).

Forced reinitialization copies the existing DB to a timestamped backup (`needs-map.db.backup-<ISO>`) before wiping — the content is accumulated evaluation work, not regenerable by scan.

## Status

`ocd-run setup status` reports needs-map's coverage metrics — components, needs, addressing edges, and open gap count.
