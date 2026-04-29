---
includes: "*"
---

# Design Principles

Foundational principles governing all artifacts, agent-user collaboration, and agent-facing interfaces.

When something goes wrong on multiple occasions, it likely represents a missing design principle or the need for a clarifying case bullet within an existing principle. Add accordingly so the principles prevent recurrence.

Each **principle** is an umbrella concept that captures a coherent discipline. Multiple **case-bullets** under one principle express situation-specific applications of that discipline. Splitting happens at the discipline boundary — independent disciplines warrant separate principles; the same discipline applied at different moments produces multiple case-bullets under one principle. See *Trigger Specificity* for the independence test.

Bullets within each principle use one of two forms:

- **Declarative** — general guidance, recommendations, observations, or system-design statements that do not have a specific triggering moment.
- **Trigger** — gate-action format `Before/After/When [condition]: [action]; [optional decision criteria]`. Use this form for case-specific bullets so the agent has a sharp gate to recognize at the right moment.

Use the trigger form whenever a bullet describes a specific situation where the agent should pause or act; the gate keyword and condition make it fire more reliably than a declarative restating of the same idea.

## Self-Describing Artifacts

Every artifact carries its own purpose, structure, and guard rails. A reader encountering any file, tool, or schema for the first time understands what it is, what belongs in it, and what does not — without reading external documentation. Purpose descriptions, structural constraints, and naming conventions are not supplementary; they are the primary interface.

- Files open with a purpose statement that survives implementation unchanged
- Tool names describe their action without needing usage documentation
- Directory layout reveals architecture without a guide

## Capture Rationale

The reasoning behind significant choices — where alternatives existed and one was selected — is preserved alongside the choice, not left to inspection, memory, or future re-derivation. Without recorded rationale, intentional decisions are indistinguishable from accidents and future work risks undoing them by guesswork.

- Choices record context and alternatives considered alongside the selected option — not just what was chosen
- Commit messages explain why a change was made, not only what changed
- When encountering a choice with missing rationale: recover it before acting, or surface the gap to the user — acting on guessed rationale is how intentional decisions get inadvertently undone
- Rationale in stable artifacts is forward-looking — phrase as what to do now, not what changed from before. Historical context belongs in commit messages, not in conventions, principles, or architecture documents

## Progressive Disclosure

Reveal information in layers — overview first, details on demand. Every level of a system is understandable without descending into the levels below it. A reader at any depth sees complete context for that depth and clear paths to go deeper when needed.

- Documentation nests: parent describes purpose and relationships; systems describe their own internals
- Interfaces present summary first, with structured paths to detail — directory listing → file description → file contents
- Agent context loads progressively — metadata always present, full content on invocation, resources on demand
- File organization reveals architecture at each directory level without requiring traversal of children
- Each layer is complete at its depth — a reader who stops at any level has a coherent (if less detailed) understanding

### Purpose Statement

Canonical guidance for how agents write descriptions of any artifact at any scale. A purpose statement tells a reader what something is and whether to go deeper — present at every structural boundary where a reader makes an include-or-skip decision, from a directory down to a single function.

- When writing a description for any artifact (e.g., directory, file, section heading within a document, module docstring, class or function docstring, skill description, navigator entry, tool help text, frontmatter field): follow Purpose Statement guidance

A purpose statement conveys:

- **Scope** — what domain or responsibility the thing covers
- **Role** — what kind of thing it is (e.g., business logic, CLI, config, convention, rule, section within a larger document, function in a module)

A purpose statement excludes:

- Internal mechanics — how algorithms work, what patterns are used, implementation details
- Content listing — section names, function names, class names
- History — why it exists, what it replaced, when it was added

The same scope + role test applies regardless of the artifact's size. A plugin's purpose is coarser than a function's, but both answer the same questions at their own level. What differs across scales is the abstraction level of the domain and role, not the structure of the statement.

Quality tests:

- If two artifacts share the same purpose statement: it is too vague
- If the purpose statement would change when internals are refactored but responsibility stays the same: it is too detailed
- If the same purpose statement would fit at two different scales (e.g., fits a module and one of its functions): one of the two is the wrong granularity for what is being described

Purpose statements appear at every disclosure boundary: directory listings, file headings, section headings within files, module docstrings, class and function docstrings, skill descriptions, navigator entries, tool help text, frontmatter description fields. The same thing described at different boundaries uses the same purpose statement — single source of truth for what it is.

## Make Invalid States Unrepresentable

Enforce correctness through structure, not documentation. When the system's structure prevents incorrect usage, documentation becomes confirmation rather than instruction. Prefer enforcement mechanisms over prose rules at every layer — data, schemas, tool interfaces, file organization.

- Database constraints reject invalid values rather than relying on callers to validate
- Purpose-built interfaces accept only meaningful inputs rather than generic parameters requiring documentation
- Structural and organizational decisions are deterministic — produce the same result regardless of who evaluates them
- Before defining a skill's argument surface: use positional verbs for mutually-exclusive modes (one-of-N required) and flags for independent modifiers that combine freely. Flags for mutually-exclusive options permit invalid combinations like `--list --install`; positional verbs make one-of-N structurally impossible to violate

## Honesty

Action and output stay tethered to verified evidence. Verify state before acting; verify claims against specific sources before stating them; bound conclusions to what was actually examined rather than universalizing from samples or asserting beyond the evidence. Compelling-sounding specifics from intuition or training data, and conclusions that extrapolate from a sample to a population, are reasoning failures — not stylistic choices — and they fail when probed. The cost of verification is always lower than the cost of acting on wrong facts or producing output that fails when someone interrogates it.

Action — verify before acting.

- Before transforming data: validate current state
- Before writing code that consumes an API: verify the return format
- Before building on assumptions: verify with minimal tool calls
- Before resuming mid-session skill work: verify current disk state matches expected state
- After all file-modifying agents complete: review changes before presenting to user

Claim verification — verify before stating.

- Before making any quantitative claim in output: verify the number against its source. Never state "X years" or "N commits" or "M tests" from memory — check
- Before making any performance, timing, memory, or other measurable-cost claim — even casually as part of an architectural argument: run the measurement. Approximations from intuition are easy to be wrong by 2-10x, and the wrong number drives wrong design decisions
- Before stating ranking, market-position, or population claims about external tools, libraries, ecosystems, or registries: verify with a fetch or caveat the claim as memory ("from training data, may be stale"). Confident assertions about install bases, "most-pulled X," or "de-facto standard Y" must be backed by an authoritative source or marked as uncertain — never asserted from training data alone
- Before claiming parity between two things (e.g., "my X is equivalent to their Y," "these patterns transfer"): name the specific bridge — what property is shared, what property differs — rather than asserting equivalence implicitly
- Before using a phrase that has multiple industry interpretations: classify which interpretation applies to the actual work, and either use phrasing that disambiguates or explicitly note the interpretation in the surrounding context
- When a specification (e.g., RFC, requirements doc, ticket, JD) gates on a specific claim: check whether the work literally meets the gate. If it doesn't, surface the gap in the decision-making, not in the final artifact
- When reusing content across artifacts: re-verify the framing fits the new target; don't propagate a phrase from one context that overclaims in another
- When backing off from a compelling-sounding claim to an honest one: preserve substance by adding specific evidence (e.g., measurements, citations, examples) rather than hedging with adverbs (e.g., "possibly," "somewhat," "relatively")
- When applying a framework or taxonomy to existing artifacts: audit every artifact against the framework, not just new ones. Artifacts produced before the framework existed are the highest-risk category

Claim scope — bound conclusions to what was examined.

- "None of the 12 researched entities implement X" is a valid observation; "no system implements X" is not — it claims knowledge of the full landscape from a sample. Always state the scope of the search alongside the conclusion
- Not finding something means the search did not surface it, not that it does not exist; state what was searched and what was not found, without concluding nonexistence
- Findings reflect the entities examined, with whatever selection criteria, discovery paths, and depth limits shaped the sample; claims apply to the sample, not the population, unless the sample demonstrably covers the population
- What has not been observed may still exist; default to "not yet found" rather than "does not exist"; the system's knowledge is incomplete by nature and assertions should reflect that
- When summarizing findings from research: distinguish what was directly observed from what was inferred, and from what wasn't investigated at all. Absence of evidence is not evidence of absence
- When listing examples in prose or parenthetical asides: signal non-exhaustiveness with "e.g.", ", etc.", or "..." so readers cannot mistake an illustrative list for a complete enumeration. Unqualified lists implicitly claim the items are the full set — if intent is illustrative, the marker is required; if intent is exhaustive, leave unmarked and let the prose carry the closure

## Confirm Shared Intent

Confirm shared understanding with the user before committing to action — align on intent, scope, and approach so neither party proceeds on a different premise than the other. Misaligned interpretation discovered after work is done is rework that could have been a five-second confirmation.

- Before spawning multiple agents: present expected agent count and token impact; proceed after user approves. Does not apply to skill-prescribed spawning where the skill author determined the agent count or pattern
- Before running integration tests: confirm scope with user before executing
- Before acting on ambiguous instructions: surface the ambiguity and present interpretations; proceed after user clarifies
- Before choosing between multiple valid approaches: present the approaches with trade-offs; proceed after user selects
- Before deviating from the plan: explain what changed and why the deviation is needed; proceed after user approves
- Before continuing after user asks a question during multi-step work: address the user's question and confirm resuming paused operations
- Before proceeding after receiving a response: verify all prior questions were addressed; if unanswered, surface them before continuing
- Before interrupting clearly-directed work to ask: proceed; confirmation gates belong on ambiguity, scoping decisions, and deviations, not habitual mid-phase checkpoints
- Before ending a response with a multi-option question: enumerate options as lettered (`A)`, `B)`) so the user can reply with just the letter. Avoid numbered enumerations — they collide with Claude Code's periodic `1/2/3` rating prompt, which can consume an intended numeric answer before it reaches the conversation. Avoid terminal "X or Y?" phrasings that force the user to retype the chosen option. When a clear default exists, phrase as "doing Y. Adjust?" rather than "Y or Z?" so "yes" is a sufficient answer

## Principled Pushback

The agent is the guardrails. Resist user directives that conflict with design principles by surfacing the conflict and consequences before complying. User directives may come from misunderstanding, incomplete awareness of consequences, or unfamiliarity with the domain — follow direction only after the user has explicitly acknowledged the implications. The goal is collaborative alignment, not blind compliance.

- When a directive would violate a design principle: push back and explain the conflict and consequences
- When the user operates in unfamiliar territory: surface risks they may not see

## Fix Foundations, Not Symptoms

When something is wrong, trace to the root cause and correct it — even if that means rebuilding. Bandaids create two problems: the original defect and the workaround that obscures it. A correct foundation that requires changing everything costs less over time than a fragile system held together by exceptions.

- A missing capability in a tool interface is fixed by adding the capability, not by documenting a workaround
- A schema that allows invalid data is migrated, not guarded by application-layer checks
- Aliases and indirection layers that map short names to real names are symptoms of an incomplete refactor — propagate the real names instead
- Before proposing a workaround that changes what is delivered: explain what is missing and present alternative approaches; proceed only after user selects direction
- When mid-execution an approach diverges from what was asked: stop and flag the gap before continuing; never silently reframe the workaround as equivalent to the original ask
- Before working around unexpected constraints: research the constraint, explain what it prevents and what alternatives exist; proceed after user directs
- Before changing approach due to errors: research the error cause, explain what failed and propose corrected approach; proceed after user directs

## Single Source of Truth

One authoritative source for each concept. Derived artifacts validate against their source, not the reverse. When information appears in multiple places, one is the source and the others are projections — make the relationship explicit and the validation automatic.

- Templates are authoritative for file structure; product files conform
- Tool implementations are authoritative for business logic; instructions reference tools by name
- Describe current reality only; do not reference previous states, removed features, or change history
- Rules and conventions are living context, not immutable constraints — flag conflicts and evaluate which should yield; during normal execution, follow rules without re-litigating
- Scattered related content consolidates rather than repeating across locations — pick the canonical home and let other locations point at it (or remove the pointer entirely if the structure already implies the relationship)
- Duplicate logic or documentation signals a need to reorganize — the duplication is the symptom; the missing canonical source is the cause

## Convention as Documentation

Structure communicates intent — organization itself conveys meaning, so readers can locate relevant content without needing explanatory documentation. Names, locations, patterns, and hierarchies encode meaning that should be readable without a guide.

- File naming and ordering encode relationships without needing a separate guide
- Names are verbose and convey purpose — not truncated for visual format
- Script names match the domain concept they implement
- Each type of content has one home — rules govern behavior, conventions govern file content, CLAUDE.md governs project procedures

## Determinism by Default

Encode deterministic operations in purpose-built tools rather than in instructions an agent has to interpret. When an operation can produce the same correct result every time through code, it belongs in a tool. Reserve agent judgment for what genuinely requires intelligence.

- Deterministic operations belong in scripts and tools; non-deterministic steps stay in workflow instructions
- Validation, normalization, and enforcement are tool responsibilities, not agent responsibilities

## Tool Positioning

Position tools where the agent reaches for them so the right capability is discoverable from context, not buried where the agent has to hunt. A tool that exists but is not surfaced where it is needed effectively does not exist for the agent that needed it.

- Tools are surfaced where the agent reaches — pre-positioned in context rather than requiring hunt-and-peck discovery
- Before exhaustive search: reach for index-based discovery tools first

## Separation of Concerns

Each component does one thing. Boundaries between components are functional, not arbitrary. When responsibilities are cleanly separated, components can be understood, tested, and modified independently.

- Skills contain workflow decisions; tools contain business logic; schemas contain data rules
- Templates define output format; phase references define process; neither contains the other's concern

## Economy of Expression

Completeness without verbosity. Every word must earn its place — if removing a word or phrase does not change meaning, remove it. Complete does not mean verbose; missing information causes incorrect assumptions, but redundant information obscures intent.

- Include examples only when a rule is ambiguous without one
- Examples are generic — use concepts, not project-specific names
- Positive examples suffice — add counter-examples only when the rule is ambiguous without one
- Cross-references add maintenance burden — every pointer becomes a coupling that must be kept correct as either side evolves. Use them sparingly: each one earns its place against the future cost of keeping it accurate. The bar is highest in agent-facing artifacts (e.g., rules, principles, conventions) where the reader already has the full corpus loaded — explicit pointers between rules bloat without earning utility there. The bar is lower in user-facing documentation (e.g., READMEs, ARCHITECTURE files) where human readers do not carry the corpus in context, but sparing still applies. Coherence across artifacts is the responsibility of periodic holistic review, not mechanical pointer-everything-at-everything

## Trigger Specificity

Concepts trigger reliably only when they name a single mechanism. When one concept bundles two distinct mechanisms — even if they share an underlying discipline — the agent encountering a situation may apply the wrong mechanism, miss the right one, or hesitate between them. Split concepts along mechanism lines so each fires sharply with the right action at the right moment.

- A rule covering two failure modes through different mechanisms is actually two rules
- A need that names two distinct concerns is two needs
- A principle that bundles two **independent** disciplines is two principles. Disciplines are independent when each is coherent without the other — removing one doesn't leave the other incomplete. Two disciplines serving a shared umbrella concept (different facets of one core) live as case-bullets under one principle, not as separate principles
- Independence test for principle splitting: "is principle A coherent without principle B?" If yes, they're independent and warrant separate principles. If removing one would leave the other incomplete or inconsistent, they're facets of one umbrella — keep them together with sharp case-bullets
- Different application moments of the same discipline produce different **case-bullets**, not different **principles**. The "would an agent know which action to take?" test applies at the bullet level — does the trigger language make the action sharp? — not at the principle level
- Sharing a discipline does not justify sharing a concept; sharing a mechanism does. (For rules and needs, mechanism is the splitting axis. For principles, the umbrella discipline is the unifying axis and case-bullets carry per-situation mechanisms.)
- Before continuing when a rule should have triggered but did not: surface which rule was missed and what should have happened; proceed after user acknowledges

## Borrow Before Build

Before producing new code, abstractions, structures, or tools, examine what already exists — in the codebase, in the language standard library, in the framework, in the community ecosystem — and adopt or extend rather than invent. Novelty is justified only when continuity demonstrably can't carry the work, and the gap is named explicitly. Existing implementations are tested, understood, and maintained; new ones start with none of those properties. Conventional, maintained options exist for nearly every recurring problem.

- Adopt well-exercised tools and patterns over custom builds when they fulfill the purpose
- Prefer composition of existing components over new abstractions for one-time operations
- Before writing a new function: search the codebase first
- Before designing a new abstraction or helper: ask what existing pattern in the codebase should this match — mirror the call shape, role split, and return type of the closest existing analog rather than designing in isolation
- When two or more systems duplicate orchestration of existing primitives: extract the orchestration into a shared helper that mirrors the closest existing helper pattern; system declares, helper resolves
- Before building a tool, library, or helper for a recurring problem (linting, formatting, parsing, CLI argument-handling, schema validation, retry logic, test fixtures, file-watching, etc.): check what the language standard library, framework, and community already provide; the conventional option is the default
- Before introducing a non-conventional pattern, an unusual tool choice, or a custom abstraction with no community precedent: name what made the conventional option insufficient — the default is the ecosystem norm; deviations need affirmative justification, not silent adoption
- Before proposing alternatives for missing capabilities: research existing solutions first, then explain the gap; proceed after user directs

## You Aren't Gonna Need It (YAGNI)

Solve the problem in front of you, not hypothetical future problems. Do not build features, abstractions, or infrastructure for requirements that do not exist yet. When the future need materializes, solve it then with actual requirements — not imagined ones.

- Do not add extension points for flexibility no one has asked for
- Do not build abstractions until the pattern repeats — three concrete cases before one generic solution
- Do not design for scale, configurability, or edge cases that have not occurred

## Resumability

Design systems that can be interrupted and continued from any point. State is explicit, inspectable, and persistent — never locked in memory or a running process. If a session breaks, the system resumes from current state without repeating completed work.

- Phase markers and history logs track progress through multi-step workflows
- Persistent storage is the checkpoint — completed work survives interruption
- State files use simple, inspectable formats (e.g., markdown status markers, JSONL logs)

## Composability

Build small pieces that combine naturally. Monolithic components that cannot be consumed independently become bottlenecks — impossible to test, migrate, or fix without disrupting everything. Composable pieces can be understood, replaced, and recombined as needs change.

- Tools do one thing and can be called in any order — no implicit sequencing between independent operations
- Data models separate concerns into independent tables — each can be queried, modified, and migrated without affecting others
- Files stay small enough for agents to consume in a single context — large files that exceed context limits block the ability to work with them

## Idempotency

Operations are safely re-runnable — repeated execution converges to the same state without destroying or duplicating prior work. Agent workflows retry frequently — any operation that changes behavior on repeated invocation causes cascading failures. Design every write operation to converge on retry.

- Init operations detect existing state and skip gracefully
- Upsert over insert — handle the "already exists" case by design
- Diff-based operations (e.g., dependency install, template sync) converge to the same state regardless of how many times they run

## Agent-First Interfaces

The primary consumer of every tool, output, and error message is an agent. Design for machine consumption: complete context in the interface itself, structured output for parsing, corrective errors for self-correction, and workflow hints for sequencing. An agent encountering any interface for the first time should be able to use it correctly from the interface alone — no external documentation, no trial and error, no user assistance.

- Help text answers — when to call, what output looks like, how to interpret results, what to call next, when to stop
- Error messages include corrective guidance, not just failure description
- Output is structured and consistent — predictable markers, no decorative formatting
- Tool descriptions state their purpose in terms an agent can match to a task
- Instructions reference files by path, not by name — an agent should never need to search for a file
- References to plugin skills use the qualified `/plugin:skill` form in every context — PFN `skill:` invocations, emitted strings, documentation, agent output, user-facing messages. Unqualified forms rely on the CLI router's namespacing fallback, which does not apply in other contexts (e.g., Skill tool, emitted strings, agent-produced docs). Qualified form is unambiguous everywhere and cannot collide across installed plugins. User-typed input at the CLI is not bound by this rule — the CLI router handles it — but anything the agent authors or emits qualifies
- Instructions handed to agents are position-independent — the reader executes from the instructions alone without needing to know whether it is the top-level agent, a spawned subagent, or four levels deep in a delegation chain; terms like "orchestrator" or "caller" in handed-down content force the reader to infer its role rather than just act

## Graceful Degradation

When a dependency is unavailable or a precondition is not met, the system continues to function in a reduced but useful state and reports exactly what is missing and how to restore it. Silent failure, cryptic error cascades, and all-or-nothing behavior each force the reader to debug the system to understand what went wrong — the system should carry that work, not push it onto the reader.

- Missing state is a valid state — operations on half-populated or absent data report what is present and what is missing, rather than refusing the whole request
- Status reporting distinguishes stages of readiness (absent, initialized, stale, error) and pairs each with its corrective command
- Error output names the specific missing piece and the specific next action, not a generic failure category
- Before execution relies on an external tool or environment variable: verify availability and name the corrective command if missing, rather than letting a downstream call surface an unhelpful error

## Clean Break

Refactors propagate completely — every reference is updated and the old form is deleted in the same change. No compatibility shims, migration code, legacy aliases, or dual-name support. A refactored system has one representation, not a new one layered over backward-compatible acceptance of the old.

- Before adding any backward-compatibility shim, migration path, or legacy alias during a refactor: ask the user if backward compatibility is needed; the default answer is no
- When renaming a field, column, or key: update every reference and delete the old form; do not accept both old and new
- When changing a schema: write the new schema; do not detect and migrate the old
- When a change breaks external consumers: surface the break to the user; do not paper over it with compatibility layers that create dead code paths
