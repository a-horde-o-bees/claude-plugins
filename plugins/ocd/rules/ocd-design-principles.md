# Design Principles

Foundational principles governing all artifacts, agent-user collaboration, and agent-facing interfaces.

When something goes wrong on multiple occasions, it likely represents a missing design principle or the need for a clarifying case bullet within an existing principle. Add accordingly so the principles prevent recurrence.

### Areas of Impact

- **Structure** — design of artifacts: code, schemas, tools, files, templates, conventions
- **Collaboration** — agent-user communication: alignment, decisions, pushback, verification
- **Interfaces** — agent-facing design: tools, instructions, output, and error messages consumed by agents (agent-agent and agent-system boundaries)

## Self-Describing Artifacts

Applies to: Structure, Interfaces

Every artifact carries its own purpose, structure, and guard rails. A reader encountering any file, tool, or schema for the first time understands what it is, what belongs in it, and what doesn't — without reading external documentation. Purpose descriptions, structural constraints, and naming conventions are not supplementary; they are the primary interface.

- Files open with a purpose statement that survives implementation unchanged
- Tool names describe their action without needing usage documentation
- Directory layout reveals architecture without a guide
- Architectural decisions are recorded with the reasoning that produced them, not just the outcome

## Make Invalid States Unrepresentable

Applies to: Structure

Enforce correctness through structure, not documentation. When the system's structure prevents incorrect usage, documentation becomes confirmation rather than instruction. Prefer enforcement mechanisms over prose rules at every layer — data, schemas, tool interfaces, file organization.

- Database constraints reject invalid values rather than relying on callers to validate
- Purpose-built interfaces accept only meaningful inputs rather than generic parameters requiring documentation
- Structural and organizational decisions are deterministic — produce the same result regardless of who evaluates them

## Pit of Success

Applies to: Structure, Interfaces

The correct path is the easiest path. If doing the right thing requires extra steps, ceremony, or knowledge that isn't embedded in the system, the system is wrong — not the user. Each improvement should simultaneously make correct usage easier and incorrect usage harder.

- Templates define structure so agents don't invent formats
- Domain tools encode business logic so agents express intent rather than constructing operations
- Conventions auto-match by file pattern rather than requiring manual lookup
- When a dependency is unavailable, the system degrades to a functional state with clear guidance — not silent failure or cryptic errors

## Measure Twice, Cut Once

Applies to: Structure, Collaboration

Verify assumptions before acting on them. Read before writing. Check before building. Align before committing. The cost of verification is always lower than the cost of rework.

- Read existing implementations before writing new functions
- Validate current state before transforming data
- Verify API return formats before writing code that consumes them
- Confirm approach with user before executing multi-step changes

## Fix Foundations, Not Symptoms

Applies to: Structure, Collaboration, Interfaces

When something is wrong, trace to the root cause and correct it — even if that means rebuilding. Bandaids create two problems: the original defect and the workaround that obscures it. A correct foundation that requires changing everything costs less over time than a fragile system held together by exceptions.

- A missing capability in a tool interface is fixed by adding the capability, not by documenting a workaround
- A schema that allows invalid data is migrated, not guarded by application-layer checks
- When a workaround is proposed that changes what's delivered, that signals a gap to address
- Aliases and indirection layers that map short names to real names are symptoms of an incomplete refactor — propagate the real names instead

## Single Source of Truth

Applies to: Structure

One authoritative source for each concept. Derived artifacts validate against their source, not the reverse. When information appears in multiple places, one is the source and the others are projections — make the relationship explicit and the validation automatic.

- Templates are authoritative for file structure; product files conform
- Tool implementations are authoritative for business logic; instructions reference tools by name
- When a refactor touches any name, path, or pattern, every reference is updated as if the old form never existed — no compatibility shims, no split conventions
- Describe current reality only; do not reference previous states, removed features, or change history
- Rules and conventions are living context, not immutable constraints — flag conflicts and evaluate which should yield; during normal execution, follow rules without re-litigating

## Convention as Documentation

Applies to: Structure

Structure communicates intent. When the system's organization makes its design obvious, the need for explanatory documentation decreases proportionally. Names, locations, patterns, and hierarchies encode meaning that should be readable without a guide.

- File numbering encodes dependency order
- Names are verbose and convey purpose — not truncated for visual format
- Script names match the domain concept they implement
- Each type of content has one home — rules govern behavior, conventions govern file content, CLAUDE.md governs project procedures

## Determinism by Default

Applies to: Structure, Interfaces

Automate what can be automated. Reserve agent judgment for decisions that genuinely require intelligence. When an operation can produce the same correct result every time through code, it belongs in a deterministic tool — not in instructions that an agent interprets.

- Deterministic operations belong in scripts and tools; non-deterministic steps stay in workflow instructions
- Validation, normalization, and enforcement are tool responsibilities, not agent responsibilities

## Separation of Concerns

Applies to: Structure

Each component does one thing. Boundaries between components are functional, not arbitrary. When responsibilities are cleanly separated, components can be understood, tested, and modified independently.

- Skills contain workflow decisions; tools contain business logic; schemas contain data rules
- Templates define output format; phase references define process; neither contains the other's concern

## Economy of Expression

Applies to: Collaboration, Interfaces

Completeness without verbosity. Every word must earn its place — if removing a word or phrase does not change meaning, remove it. Complete does not mean verbose; missing information causes incorrect assumptions, but redundant information obscures intent.

- Include examples only when a rule is ambiguous without one
- Examples are generic — use concepts, not project-specific names
- Instructions state what to do, not what not to do, unless the negative case is a common mistake

## Reuse Before Create

Applies to: Structure

Check what exists before building new. The best code is code you don't write. Existing implementations are tested, understood, and maintained — new implementations start with none of those properties.

- Search the codebase before writing a new function
- Adopt well-exercised tools and patterns over custom builds when they fulfill the purpose
- Prefer composition of existing components over new abstractions for one-time operations

## You Aren't Gonna Need It (YAGNI)

Applies to: Structure

Solve the problem in front of you, not hypothetical future problems. Don't build features, abstractions, or infrastructure for requirements that don't exist yet. When the future need materializes, solve it then with actual requirements — not imagined ones.

- Don't add extension points for flexibility no one has asked for
- Don't build abstractions until the pattern repeats — three concrete cases before one generic solution
- Don't design for scale, configurability, or edge cases that haven't occurred

## Resumability

Applies to: Structure

Design systems that can be interrupted and continued from any point. State is explicit, inspectable, and persistent — never locked in memory or a running process. If a session breaks, the system resumes from current state without repeating completed work.

- Phase markers and history logs track progress through multi-step workflows
- Persistent storage is the checkpoint — completed work survives interruption
- State files use simple, inspectable formats (markdown status markers, JSONL logs)

## Composability

Applies to: Structure, Interfaces

Build small pieces that combine naturally. Monolithic components that can't be consumed independently become bottlenecks — impossible to test, migrate, or fix without disrupting everything. Composable pieces can be understood, replaced, and recombined as needs change.

- Tools do one thing and can be called in any order — no implicit sequencing between independent operations
- Data models separate concerns into independent tables — each can be queried, modified, and migrated without affecting others
- Files stay small enough for agents to consume in a single context — large files that exceed context limits block the ability to work with them

## Idempotency

Applies to: Structure, Interfaces

Operations produce the same result whether run once or many times. Agent workflows retry frequently — any operation that changes behavior on repeated invocation causes cascading failures. Design every write operation to be safely re-runnable.

- Init operations detect existing state and skip gracefully
- Upsert over insert — handle the "already exists" case by design
- Diff-based operations (dependency install, template sync) converge to the same state regardless of how many times they run

## Agent-First Interfaces

Applies to: Interfaces

The primary consumer of every tool, output, and error message is an agent. Design for machine consumption: complete context in the interface itself, structured output for parsing, corrective errors for self-correction, and workflow hints for sequencing. An agent encountering any interface for the first time should be able to use it correctly from the interface alone — no external documentation, no trial and error, no user assistance.

- Help text answers — when to call, what output looks like, how to interpret results, what to call next, when to stop
- Error messages include corrective guidance, not just failure description
- Output is structured and consistent — predictable markers, no decorative formatting
- Tool descriptions state their purpose in terms an agent can match to a task

## Principled Pushback

Applies to: Collaboration

The agent is the guardrails. User directives may be based on misunderstanding, incomplete awareness of consequences, or unfamiliarity with the domain. Follow direction only after being certain the user fully understands the implications of a concerning decision. The goal is not blind compliance but collaborative alignment to design principles.

- Push back when a directive would violate a design principle — explain the conflict and consequences
- When the user operates in unfamiliar territory, surface risks they may not see
- Incorporate feedback and directives only after the user has explicitly acknowledged the implications
