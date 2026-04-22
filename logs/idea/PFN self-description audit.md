# PFN self-description audit

PFN should prescribe chains of events unambiguously, not delegate to invisible runtime mechanisms. An earlier scan flagged two constructs (`isolation: "worktree"` and `When:`) that relied on runtime routing rather than describing what happens; both were removed. A more thorough pass is worth its own session.

## Candidates for review

- **`async Spawn:`** — "concurrent, await at the outdent" but nothing about failure propagation (does one spawn's crash cancel others?), order of returned values, or what the await actually observes. Python analogy (`asyncio.TaskGroup`) hides semantics the PFN reader doesn't inherit.
- **`Continue {agent-ref}:`** — assumes persistent agent handles. Mechanism is Claude Code agent resumption; lifetime and serializability aren't prescribed.
- **`Return to caller` ambiguity** — same keyword carries two semantics: "stop reading this file" inside `Call:` vs "spawned agent terminates with yield" inside `Spawn:`. Reader has to infer from context.
- **`Error Handling:`** — "catches failures from sibling steps" but "failure" is unspecified: non-zero exit from `bash:`, raised Python exception, agent-reported error, test assertion fail?
- **`Spawn:`** (plain) — the mechanism (Agent tool) exists, but PFN does not prescribe how the spawned agent's own execution will follow PFN. Enforcement is absent; the spawned content is just read as instructions.

## What "tightening" means concretely

Each construct should either:

- Describe the full mechanism the reader needs to execute it (no runtime magic), or
- Cite the concrete runtime feature it relies on (Agent tool, Claude Code session model) with explicit constraints on when the construct is valid, or
- Be removed (YAGNI) if no skill uses it and the semantics aren't prescriptive

The goal is that an agent reading PFN can walk a skill and know exactly what the next action is at every step, with no behind-the-scenes assumptions about what the runtime fills in.

## When to tackle

Not release-blocking. The constructs above work in practice because agents fill in the blanks well enough; the risk is future skill authors building on wishful semantics and discovering the gaps only when something breaks.
