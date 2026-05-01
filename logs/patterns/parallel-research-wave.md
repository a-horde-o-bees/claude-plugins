# Parallel research wave

Methodology for deep research across multiple dimensions or per-entity samples — parallel agent dispatch + per-dimension file outputs + verification + synthesis.

## When to use

- The research subject splits into reasonably-independent dimensions (architectural layers, format axes, ecosystem categories) — the dimensions are however many the subject naturally has
- Depth-per-dimension matters more than turnaround time
- The user wants exhaustive landscape coverage and explicit prior-art mapping before committing to a design

## Process

1. Identify the dimensions the subject naturally splits into. Don't force a count; let the subject decide.
2. Define each agent's brief with a shared header (project context, prior research already covered, quality discipline) + dimension-specific instructions
3. Spawn parallel agents (background) writing deliverables to files under `logs/research/<subject>/`
4. Each agent reads existing context (consolidated docs, prior research) before beginning own work, to build on rather than duplicate
5. Verify load-bearing claims with direct fetches between agent returns and synthesis — caveat anything from training data
6. Synthesize into `consolidated.md` with cross-dimension patterns, verified-project-actionable recommendations, aggregated pitfalls, sources
7. Optionally: add `samples/prior-art/<entity>.md` starter packs for future per-entity deep dives — identity, fit, what-to-take, open questions

## Pitfalls

- Without explicit "build on existing research" instruction, agents redo work covered by prior waves
- Without verification step, training-data claims (download counts, market positions, project status) propagate into the synthesis
- Without per-dimension file outputs, return content concentrates in chat and synthesis becomes a re-summarization task
- Without bounded scope per agent ("your dimension is X"), agents wander into adjacent dimensions and produce overlap
- Forcing a target dimension count when the subject has more or fewer — splits independent dimensions awkwardly or pads thin ones

## Anti-patterns

- Single mega-agent for breadth research — output is shallower per dimension and harder to verify selectively
- Sequential agents when dimensions are independent — slower with no quality gain
- No prior-research-pointer in agent prompts — duplication waste compounds across waves
- Synthesis without verification step — training-data assertions survive into recommendations

## See also

- `.claude/rules/ocd/design-principles.md` — *Honesty* (verify claim verification before stating; bounded conclusions)
- `.claude/rules/ocd/design-principles.md` — *Confirm Shared Intent* (present expected agent count and token impact before spawning multiple)
- `logs/research/_template.md` — research subject directory shape; multiple wave outputs at subject root pattern
