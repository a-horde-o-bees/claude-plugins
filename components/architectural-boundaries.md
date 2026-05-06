# Architectural Boundaries — Harness vs Plugin

Documents the distinction between what `claude-plugins` can control (plugin-level) and what is determined by the hosting agent harness, currently Claude Code (harness-level). Keeps the project's design self-aware — prevents chasing fixes to limitations that can only be resolved by owning a different layer of the stack.

## Purpose

When designing claude-plugins features, it is easy to conflate "this is hard to do" with "the plugin system should do this better." Many limitations observed during design are actually downstream of harness-level decisions made by Claude Code — not something a plugin can fix from within.

This document:

1. Catalogs harness-level limitations that have been hit
2. Distinguishes them from plugin-level concerns
3. Surfaces design implications — features that need redesign, defer, or accept a ceiling
4. Creates the foundation for a future decision about whether to build a custom harness

## The boundary

**Harness-level** — determined by Claude Code's code and product decisions:

- Message loop semantics and tool dispatch
- Context window management and compaction
- Sub-agent spawning rules (currently single-level delegation)
- Skill invocation semantics (same-context load vs subprocess isolation)
- Hook lifecycle (which events fire, when, with what context)
- Permission model granularity and prompts
- MCP server connection lifecycle and pooling
- Process flow enforcement (whether structured workflows are documentation or enforced execution)
- Memory backend and persistence model
- Multi-user / multi-tenant behavior (currently single-user)

**Plugin-level** — owned by `claude-plugins`:

- MCP server design, schemas, and SQLite storage
- Skill content, rules, and prompt structure
- Hook logic (within the interception points the harness provides)
- Governance rules and matching logic
- Navigator and governance database schemas
- Plugin templates, deployment, and lifecycle primitives
- CLAUDE.md and project-level conventions
- Documentation patterns, design principles, process flow notation

A useful test: "If I built a different agent harness tomorrow, which layer would this piece of work survive in?" Anything that would need reimplementing lives on the harness side. Anything portable lives on the plugin side.

## Known harness-level limitations

### Sub-agent recursion

- **Limitation:** Sub-agents spawned via the Agent tool cannot spawn their own sub-agents. Single level of delegation.
- **Why:** Prevents unbounded recursion, cost blowup, coherence loss across deep trees.
- **Plugin impact:** Skills that compose through agent delegation hit a ceiling. Complex multi-step workflows that want genuine hierarchy have to flatten.
- **Plugin workaround:** Sequential delegation from the parent context rather than nested spawning.
- **What a custom harness could change:** Budget-bounded recursion, N-level nesting with inherited context, tool-restriction policies per depth.

### Context management opacity

- **Limitation:** Compaction, summarization, and context budgeting are harness-internal. Skills cannot query or influence them directly.
- **Plugin impact:** Long-running skills can lose coherence unpredictably. Context-sensitive workflows (e.g., loading N files before a transformation) rely on state being preserved across a full skill execution, which is not guaranteed.
- **Plugin workaround:** Externalize state to disk via MCP server writes or file-based logs.
- **What a custom harness could change:** Explicit context primitives (checkpoint, load, isolate); skill-driven load policies ("this skill needs these files in context").

### Skill invocation isolation

- **Limitation:** Calling a skill from another skill loads content into the current context rather than executing as an isolated subprocess. Skill state (prior outputs, context accumulated) leaks between skills.
- **Plugin impact:** Skills cannot be composed as pure functions. Side-effect ordering between skills depends on execution context rather than declared interface.
- **What a custom harness could change:** Skill-as-subprocess with isolated contexts and explicit return values.

### Hook lifecycle rigidity

- **Limitation:** `PreToolUse` hooks are the primary interception point. No `PreSkillStart`, `PostAgentReturn`, `OnContextCompaction`, or other lifecycle events exposed.
- **Plugin impact:** Governance logic that should fire at other lifecycle points has to be hoisted into tool-call interception, which is the wrong layer.
- **What a custom harness could change:** Full lifecycle event bus with pre/post/error hooks at every layer.

### Process Flow Notation enforcement

- **Limitation:** PFN documented in skills tells the LLM how to execute, but the harness does not enforce execution to match. The LLM can deviate from the specified flow.
- **Plugin impact:** Deterministic workflow guarantees are weaker than they appear. Testing and auditing flow-matching is difficult.
- **What a custom harness could change:** PFN as executable state machine — the harness runs the graph and delegates only the non-deterministic decisions to the LLM.

### Governance enforcement timing

- **Limitation:** Hooks enforce at tool-call dispatch time. The LLM has already decided and articulated an action before governance can reject it.
- **Plugin impact:** "Don't propose this kind of action" cannot be enforced — only "don't execute this kind of action after it's proposed." Wasted reasoning and user-facing friction.
- **What a custom harness could change:** Governance as a reasoning-time concern. Policy queries during planning rather than blocks at execution.

### MCP server lifecycle

- **Limitation:** Connection lifecycle, pooling, restart behavior, and health management are harness responsibilities. Plugins consume the abstraction they are given.
- **Plugin impact:** Long-running MCP servers with expensive startup have to be designed around assumptions about when connections will be torn down.
- **What a custom harness could change:** First-class persistent-connection pools, warm starts, per-server health policies.

## Design implications

Apply these when designing plugin features:

- **Features that hit harness-level ceilings should be scoped to what is achievable inside the harness.** Note the harness-level extension in this document rather than pursuing plugin-level hacks that fight the harness.
- **Prefer designs that are portable to a future harness.** Plugin-level code that would need rewriting when the harness changes should be minimized. Infrastructure (MCP servers, governance logic, skill content) should be as harness-independent as practical.
- **Plugin-level documentation should describe plugin-level behavior.** Avoid language that promises deterministic behavior the harness does not guarantee.
- **Surface the boundary when explaining plugin capability.** External audiences (users, collaborators, interviewers) benefit from understanding what is plugin-designed vs harness-inherited.

## Future options

Three commitment levels for addressing harness-level limitations:

1. **Accept and document** — this file; zero additional effort beyond maintaining it.
2. **Supervisor layer** — a Claude-Code-extending wrapper that implements missing lifecycle events, richer sub-agent rules, or governance-at-planning-time, without replacing Claude Code. Weeks of work.
3. **Custom harness** — purpose-built agent framework around the claude-plugins patterns (MCP-first, skills-as-state-machines, governance-as-core). Months of work.

No decision yet on (2) or (3). This document is the substrate for that decision when it matters.

## Updating this document

Append to **Known harness-level limitations** whenever a new limitation is encountered. Entries follow the existing pattern: limitation, why, plugin impact, plugin workaround (if any), what a custom harness could change.

Remove entries if Claude Code ships a fix that makes them no longer apply.

Move limitations to a separate "Resolved" section only if the fix is partial and the historical context is worth preserving.
