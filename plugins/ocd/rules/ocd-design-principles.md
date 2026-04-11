---
includes: "*"
---

# Design Principles

Foundational principles governing all artifacts, agent-user collaboration, and agent-facing interfaces.

When something goes wrong on multiple occasions, it likely represents a missing design principle or the need for a clarifying case bullet within an existing principle. Add accordingly so the principles prevent recurrence.

Bullets within each principle use one of two forms:

- **Declarative** — general guidance, recommendations, observations, or system-design statements that don't have a specific triggering moment.
- **Trigger** — gate-action format `Before/After [condition]: [action]; [optional decision criteria]`. Use this form for case-specific bullets so the agent has a sharp gate to recognize at the right moment.

Use the trigger form whenever a bullet describes a specific situation where the agent should pause or act; the gate keyword and condition make it fire more reliably than a declarative restating of the same idea.

## Self-Describing Artifacts

Every artifact carries its own purpose, structure, and guard rails. A reader encountering any file, tool, or schema for the first time understands what it is, what belongs in it, and what doesn't — without reading external documentation. Purpose descriptions, structural constraints, and naming conventions are not supplementary; they are the primary interface.

- Files open with a purpose statement that survives implementation unchanged
- Tool names describe their action without needing usage documentation
- Directory layout reveals architecture without a guide
- Architectural decisions are recorded with the reasoning that produced them, not just the outcome

## Capture Rationale

The "why" behind every significant decision, design choice, or structural change is preserved alongside the artifact — not left to inspection, memory, or future re-derivation. Rationale is not supplementary; it's essential content that enables future maintenance, refactoring, and extension to proceed from informed understanding rather than guesswork.

- Decision records include context, alternatives considered, choice, and consequences — not just the choice
- Addressing edges carry rationales describing the specific mechanism, not just the targeting relationship
- Architecture documents explain *why* the design is shaped this way, not only *what exists*
- Commit messages explain the reasoning behind a change, not only the change itself
- When encountering an existing choice with missing rationale: recover it before acting, or surface the gap to the user — acting on guessed rationale is how intentional decisions get inadvertently undone
- Rationale in stable artifacts is forward-looking — phrase guidance as what to do now, not what changed from before. "X used to do Y; now Z" expires when the historical state goes extinct; "X does Z" is permanent. Historical context belongs in commit messages, not in conventions, principles, or architecture documents

## Progressive Disclosure

Reveal information in layers — overview first, details on demand. Every level of a system is understandable without descending into the levels below it. A reader at any depth sees complete context for that depth and clear paths to go deeper when needed.

- Documentation nests: parent describes purpose and relationships; subsystems describe their own internals
- Interfaces present summary first, with structured paths to detail — directory listing → file description → file contents
- Agent context loads progressively — metadata always present, full content on invocation, resources on demand
- File organization reveals architecture at each directory level without requiring traversal of children
- Each layer is complete at its depth — a reader who stops at any level has a coherent (if less detailed) understanding

### Purpose Statement

The disclosure boundary between layers. A purpose statement tells a reader what something is and whether to go deeper — present at every structural boundary where a reader makes an include-or-skip decision.

A purpose statement conveys:

- **Scope** — what domain or responsibility the thing covers
- **Role** — what kind of thing it is (business logic, CLI, config, convention, rule)

A purpose statement excludes:

- Internal mechanics — how algorithms work, what patterns are used, implementation details
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

Quality test: if two things share the same purpose statement, it is too vague. If the purpose statement would change when internals are refactored but responsibility stays the same, it is too detailed.

Purpose statements appear at every disclosure boundary: file headings, navigator descriptions, directory listings, skill descriptions, tool help text. The same thing described at different boundaries uses the same purpose statement — single source of truth for what it is.

## Make Invalid States Unrepresentable

Enforce correctness through structure, not documentation. When the system's structure prevents incorrect usage, documentation becomes confirmation rather than instruction. Prefer enforcement mechanisms over prose rules at every layer — data, schemas, tool interfaces, file organization.

- Database constraints reject invalid values rather than relying on callers to validate
- Purpose-built interfaces accept only meaningful inputs rather than generic parameters requiring documentation
- Structural and organizational decisions are deterministic — produce the same result regardless of who evaluates them

## Verify Against Reality

Verify assumptions against system reality before acting — read what's there, validate current state, and check actual behavior so action proceeds on facts rather than guesses. The cost of verification is always lower than the cost of rework.

- Before writing new functions: read existing implementations
- Before transforming data: validate current state
- Before writing code that consumes an API: verify the return format
- Before building on assumptions: verify with minimal tool calls
- Before resuming mid-session skill work: verify current disk state matches expected state
- After all file-modifying agents complete: review changes before presenting to user

## Confirm Shared Intent

Confirm shared understanding with the user before committing to action — align on intent, scope, and approach so neither party proceeds on a different premise than the other. Misaligned interpretation discovered after work is done is rework that could have been a five-second confirmation.

- Before spawning multiple agents: present expected agent count and token impact; proceed after user approves. Does not apply to skill-prescribed spawning where the skill author determined the agent count or pattern
- Before running integration tests: confirm scope with user before executing
- Before acting on ambiguous instructions: surface the ambiguity and present interpretations; proceed after user clarifies
- Before choosing between multiple valid approaches: present the approaches with trade-offs; proceed after user selects
- Before deviating from the plan: explain what changed and why the deviation is needed; proceed after user approves
- Before continuing after user asks a question during multi-step work: address the user's question and confirm resuming paused operations
- Before proceeding after receiving a response: verify all prior questions were addressed; if unanswered, surface them before continuing

## Principled Pushback

The agent is the guardrails. Resist user directives that conflict with design principles by surfacing the conflict and consequences before complying. User directives may come from misunderstanding, incomplete awareness of consequences, or unfamiliarity with the domain — follow direction only after the user has explicitly acknowledged the implications. The goal is collaborative alignment, not blind compliance.

- When a directive would violate a design principle: push back and explain the conflict and consequences
- When the user operates in unfamiliar territory: surface risks they may not see
- Before incorporating feedback or directives: verify the user has explicitly acknowledged the implications

## Fix Foundations, Not Symptoms

When something is wrong, trace to the root cause and correct it — even if that means rebuilding. Bandaids create two problems: the original defect and the workaround that obscures it. A correct foundation that requires changing everything costs less over time than a fragile system held together by exceptions.

- A missing capability in a tool interface is fixed by adding the capability, not by documenting a workaround
- A schema that allows invalid data is migrated, not guarded by application-layer checks
- Aliases and indirection layers that map short names to real names are symptoms of an incomplete refactor — propagate the real names instead
- Before proposing a workaround that changes what's delivered: explain what's missing and present alternative approaches; proceed only after user selects direction
- Before working around unexpected constraints: research the constraint, explain what it prevents and what alternatives exist; proceed after user directs
- Before changing approach due to errors: research the error cause, explain what failed and propose corrected approach; proceed after user directs

## Single Source of Truth

One authoritative source for each concept. Derived artifacts validate against their source, not the reverse. When information appears in multiple places, one is the source and the others are projections — make the relationship explicit and the validation automatic.

- Templates are authoritative for file structure; product files conform
- Tool implementations are authoritative for business logic; instructions reference tools by name
- Describe current reality only; do not reference previous states, removed features, or change history
- Rules and conventions are living context, not immutable constraints — flag conflicts and evaluate which should yield; during normal execution, follow rules without re-litigating

## Convention as Documentation

Structure communicates intent — organization itself conveys meaning, so readers can locate relevant content without needing explanatory documentation. Names, locations, patterns, and hierarchies encode meaning that should be readable without a guide.

- File numbering encodes dependency order
- Names are verbose and convey purpose — not truncated for visual format
- Script names match the domain concept they implement
- Each type of content has one home — rules govern behavior, conventions govern file content, CLAUDE.md governs project procedures

## Determinism by Default

Encode deterministic operations in purpose-built tools rather than in instructions an agent has to interpret. When an operation can produce the same correct result every time through code, it belongs in a tool. Reserve agent judgment for what genuinely requires intelligence.

- Deterministic operations belong in scripts and tools; non-deterministic steps stay in workflow instructions
- Validation, normalization, and enforcement are tool responsibilities, not agent responsibilities

## Tool Positioning

Position tools where the agent reaches for them so the right capability is discoverable from context, not buried where the agent has to hunt. A tool that exists but isn't surfaced where it's needed effectively doesn't exist for the agent that needed it.

- Tools are surfaced where the agent reaches — pre-positioned in context rather than requiring hunt-and-peck discovery
- Before searching for files by purpose or navigating unfamiliar areas: use navigator describe or search to locate files

## Separation of Concerns

Each component does one thing. Boundaries between components are functional, not arbitrary. When responsibilities are cleanly separated, components can be understood, tested, and modified independently.

- Skills contain workflow decisions; tools contain business logic; schemas contain data rules
- Templates define output format; phase references define process; neither contains the other's concern

## Economy of Expression

Completeness without verbosity. Every word must earn its place — if removing a word or phrase does not change meaning, remove it. Complete does not mean verbose; missing information causes incorrect assumptions, but redundant information obscures intent.

- Include examples only when a rule is ambiguous without one
- Examples are generic — use concepts, not project-specific names
- Instructions state what to do, not what not to do, unless the negative case is a common mistake
- Scattered related content consolidates rather than repeating across locations
- Duplicate logic or documentation signals a need to reorganize

## Trigger Specificity

Concepts trigger reliably only when they name a single mechanism. When one concept bundles two distinct mechanisms — even if they share an underlying discipline — the agent encountering a situation may apply the wrong mechanism, miss the right one, or hesitate between them. Split concepts along mechanism lines so each fires sharply with the right action at the right moment.

- A rule covering two failure modes through different mechanisms is actually two rules
- A need that names two distinct concerns is two needs
- A principle that bundles two disciplines is two principles when each requires a different action
- Sharing a discipline doesn't justify sharing a concept; sharing a mechanism does
- Test: would an agent encountering a situation know exactly which action to take? If not, the concept is too broad
- Before continuing when a rule should have triggered but didn't: surface which rule was missed and what should have happened; proceed after user acknowledges

## Reuse Before Create

Check what exists before building new. The best code is code you don't write. Existing implementations are tested, understood, and maintained — new implementations start with none of those properties.

- Before writing a new function: search the codebase first
- Adopt well-exercised tools and patterns over custom builds when they fulfill the purpose
- Prefer composition of existing components over new abstractions for one-time operations
- Before proposing alternatives for missing capabilities: research existing solutions first, then explain the gap; proceed after user directs

## You Aren't Gonna Need It (YAGNI)

Solve the problem in front of you, not hypothetical future problems. Don't build features, abstractions, or infrastructure for requirements that don't exist yet. When the future need materializes, solve it then with actual requirements — not imagined ones.

- Don't add extension points for flexibility no one has asked for
- Don't build abstractions until the pattern repeats — three concrete cases before one generic solution
- Don't design for scale, configurability, or edge cases that haven't occurred

## Resumability

Design systems that can be interrupted and continued from any point. State is explicit, inspectable, and persistent — never locked in memory or a running process. If a session breaks, the system resumes from current state without repeating completed work.

- Phase markers and history logs track progress through multi-step workflows
- Persistent storage is the checkpoint — completed work survives interruption
- State files use simple, inspectable formats (markdown status markers, JSONL logs)

## Composability

Build small pieces that combine naturally. Monolithic components that can't be consumed independently become bottlenecks — impossible to test, migrate, or fix without disrupting everything. Composable pieces can be understood, replaced, and recombined as needs change.

- Tools do one thing and can be called in any order — no implicit sequencing between independent operations
- Data models separate concerns into independent tables — each can be queried, modified, and migrated without affecting others
- Files stay small enough for agents to consume in a single context — large files that exceed context limits block the ability to work with them

## Idempotency

Operations are safely re-runnable — repeated execution converges to the same state without destroying or duplicating prior work. Agent workflows retry frequently — any operation that changes behavior on repeated invocation causes cascading failures. Design every write operation to converge on retry.

- Init operations detect existing state and skip gracefully
- Upsert over insert — handle the "already exists" case by design
- Diff-based operations (dependency install, template sync) converge to the same state regardless of how many times they run

## Agent-First Interfaces

The primary consumer of every tool, output, and error message is an agent. Design for machine consumption: complete context in the interface itself, structured output for parsing, corrective errors for self-correction, and workflow hints for sequencing. An agent encountering any interface for the first time should be able to use it correctly from the interface alone — no external documentation, no trial and error, no user assistance.

- Help text answers — when to call, what output looks like, how to interpret results, what to call next, when to stop
- Error messages include corrective guidance, not just failure description
- Output is structured and consistent — predictable markers, no decorative formatting
- Tool descriptions state their purpose in terms an agent can match to a task
- Instructions reference files by path, not by name — an agent should never need to search for a file

## Graceful Degradation

When a dependency is unavailable or a precondition isn't met, the system continues to function in a reduced but useful state and reports exactly what's missing and how to restore it. Silent failure, cryptic error cascades, and all-or-nothing behavior each force the reader to debug the system to understand what went wrong — the system should carry that work, not push it onto the reader.

- Missing state is a valid state — operations on half-populated or absent data report what's present and what's missing, rather than refusing the whole request
- Status reporting distinguishes stages of readiness (absent, initialized, stale, error) and pairs each with its corrective command
- Error output names the specific missing piece and the specific next action, not a generic failure category
- Before execution relies on an external tool or environment variable: verify availability and name the corrective command if missing, rather than letting a downstream call surface an unhelpful error

## Epistemic Humility

Findings and assertions are bounded by what was actually examined. The agent distinguishes between what was observed, what was not found, and what is unknown. Universalizing from a sample, treating absence as impossibility, or asserting certainty beyond the evidence are reasoning failures — not stylistic choices.

- **Scope claims to evidence** — "none of the 12 researched entities implement X" is a valid observation; "no system implements X" is not — it claims knowledge of the full landscape from a sample; always state the scope of the search alongside the conclusion
- **Absence of evidence is not evidence of absence** — not finding something means the search didn't surface it, not that it doesn't exist; state what was searched and what wasn't found, without concluding nonexistence
- **Acknowledge sample bias** — findings reflect the entities examined, with whatever selection criteria, discovery paths, and depth limits shaped the sample; claims apply to the sample, not the population, unless the sample demonstrably covers the population
- **Open-world assumption** — what hasn't been observed may still exist; default to "not yet found" rather than "does not exist"; the system's knowledge is incomplete by nature and assertions should reflect that

## Clean Break

Refactors propagate completely — every reference is updated and the old form is deleted in the same change. No compatibility shims, migration code, legacy aliases, or dual-name support. A refactored system has one representation, not a new one layered over backward-compatible acceptance of the old.

- Before adding any backward-compatibility shim, migration path, or legacy alias during a refactor: ask the user if backward compatibility is needed; the default answer is no
- When renaming a field, column, or key: update every reference and delete the old form; do not accept both old and new
- When changing a schema: write the new schema; do not detect and migrate the old
- When a change breaks external consumers: surface the break to the user; do not paper over it with compatibility layers that create dead code paths
