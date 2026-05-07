---
tagline: Universal three-document model and folder layout for any system boundary
---

# System Structure

Universal documentation and folder layout for any system. Establishes the three-document model and operational subdirectories that apply at every system boundary. Project-root extensions (workstream tracking, log curation, project-only entry-point files) live in the `project-structure` convention.

## System boundaries

The project root is always a system. Beyond the root, a system is any structural unit with its own entry point or public interface — a plugin, a library, a service, a standalone package. Identify subsystem boundaries from project structure: own directory with entry points, own package manifest, or own deployment artifact.

## Required documents

Every system maintains a consumer-facing entry point and a developer-facing design reference at its root. Systems with agent-facing procedures add an operational reference. Together these three documents capture everything needed to use, understand, and operate the system — each from a different perspective.

| Document | Consumer | Question answered |
|----------|----------|-------------------|
| `CLAUDE.md` / `SKILL.md` | Agent | How do I operate this? |
| `README.md` | User | How do I use this? |
| `ARCHITECTURE.md` | Developer | How does this work inside? |

- `README.md` — what the system does, how to install, configure, and use. Required for systems with substantial internal structure
- `ARCHITECTURE.md` — layers, components, relationships, design patterns, key implementation details. Required for systems with substantial internal structure
- `CLAUDE.md` / `SKILL.md` — operational reference for agents. Present only when the system has agent-facing procedures. Skills use `SKILL.md`; other systems use `CLAUDE.md`

## Operational subdirectories

When a system's operational content grows beyond what `CLAUDE.md` can hold inline, extract by content type into siblings of `CLAUDE.md`:

- `workflows/` — multi-step procedures with discrete actions in order. Consumer pattern: read top-to-bottom, execute each step. One file per procedure.
- `components/` — reference blocks: layouts, rules, schemas, tool surfaces. Consumer pattern: look up a fact, apply it. One file per topic.

Each file inside opens with an L1 heading and purpose statement (per markdown convention), and cross-references related files in sibling folders so a reader landing on one doc can navigate to connected detail without rebuilding context.

The split exists because the access patterns differ: a procedure is consumed top-to-bottom, in order; reference content is queried for a specific fact and applied. Mixing them in one file forces every consumer to scan past content they don't need.

## Extraction criteria

Extraction is driven by consumer fit, not document size. Move content into a separate file when:

- **Consumer profile narrows** — the content's consumer is narrower than the containing doc's. Embedding forces broader consumers to load content they don't need. CLAUDE.md's universal consumer profile makes this the primary trigger for collapsing it to an index.
- **Path-conditional content** — different paths through a workflow need different reference material. The conditional content extracts to a `components/<topic>.md`; the workflow references it where the path branches; paths that don't hit the topic never load it.
- **Multiple-reference DRY** — the same content is referenced from multiple places. Extract to a single source so updates don't desync.
- **Mixed access patterns** — a section's access pattern differs from its container's (procedural top-to-bottom vs reference lookup). Mixing forces consumers to scan past content they don't need to reach what they do.

A system whose content has one consumer profile and one access pattern can keep everything inline without extraction. As consumer profiles or access patterns diverge, the criteria above identify what to pull out.

## Document separation

Each document serves one consumer perspective and one content type. When an operational document needs structural context, it directs the agent to read `ARCHITECTURE.md` rather than re-explaining the architecture.

| Content | Where it lives |
|---|---|
| User-facing install / configure / use | `README.md` |
| Architectural reasoning | `ARCHITECTURE.md` |
| Operational procedures | `workflows/<topic>.md` (or inline in `CLAUDE.md` for small systems) |
| Operational reference | `components/<topic>.md` (or inline in `CLAUDE.md` for small systems) |

- `README.md` excludes technical internals — those belong in `ARCHITECTURE.md`
- `ARCHITECTURE.md` excludes user-facing content — that belongs in `README.md`
- `CLAUDE.md` / `SKILL.md` excludes architectural descriptions — references `ARCHITECTURE.md` and contains either navigation (when subdirs exist) or operational content (for small systems)
- When a procedure requires architectural context to be actionable, the operational document directs the reader to `ARCHITECTURE.md` rather than embedding the context inline

Project-root content extensions (forward-looking strategy, active work tracking, logs) live in the `project-structure` convention.

## Filename case

All-caps filenames signal entry points at a system boundary — docs a reader should find without knowing the system's internals. Lowercase filenames signal content within a structure — navigable only once you're inside the system.

**All-caps — entry points at every system boundary:**

- Three-document-model docs: `README.md`, `ARCHITECTURE.md`, `CLAUDE.md`, `SKILL.md`

Project-root-only entry points (`TASKS.md`, `LICENSE`, `CHANGELOG.md`, etc.) are listed in the `project-structure` convention.

**Lowercase — content within a structure:**

- Workflow procedures (`workflows/<topic>.md`)
- Component references (`components/<topic>.md`)
- Convention, rule, and pattern templates (`design-principles.md`, `architecture-md.md`, `claude-marketplace.md`) — content *of* the governance system
- Component files extracted from a skill's workflow (`_pack.md`, `_open.md`)
- Working state files (`state.md`) and audit artifacts that aren't entry points
- Python files (`.py`) and other code — standard language conventions apply

The rule matches established ecosystem conventions and makes future naming decisions deterministic: the case of the filename answers whether the file is a door or a piece of furniture inside the room.

## Subsystem doc consolidation

A subsystem earns its own three-doc set (`README.md`, `ARCHITECTURE.md`, `CLAUDE.md`/`SKILL.md`) and operational subdirectories (`workflows/`, `components/`, etc.) when it has substantial internal structure — multiple components, its own schema, its own public interface beyond a single entry point. Libraries, plugins, and substantive services fit this category.

Thin systems — a skill whose `SKILL.md` is its complete operational reference, a thin adapter over a domain library, a single-file script — do not require their own structure. Their purpose is owned at their natural doc location (SKILL.md frontmatter description, module-level docstring, file header) and propagated to the parent's overview.

Purpose statement propagation: every subsystem — whether it has its own docs or consolidates into the parent — owns its purpose statement at one canonical location. Parent documentation quotes from the canonical location rather than independently describing the subsystem, keeping the parent in sync when the subsystem evolves. The canonical locations:

- Library or plugin subsystem with full docs — `README.md`'s opening purpose statement
- Skill — `SKILL.md`'s frontmatter `description` field
- Thin MCP server or other single-file subsystem — module-level docstring of its entry point

## Nesting discipline

Parent documentation describes each subsystem generally and links down; subsystems describe themselves in detail. Neither layer re-explains content that belongs to the other, so readers navigate from general to specific without encountering duplicated or conflicting descriptions.

- Parent `README.md` describes each subsystem's purpose and links to the subsystem's `README.md` for details
- Parent `ARCHITECTURE.md` describes each subsystem's role in the overall architecture and links to the subsystem's `ARCHITECTURE.md` for internals
- Parent `CLAUDE.md` or its index points at subsystem operational docs; subsystems own their own `workflows/`, `components/`, etc.
- Neither parent document re-explains content that belongs to the subsystem's own documentation
- A reader navigates from general to specific: project root → system → subsystem
