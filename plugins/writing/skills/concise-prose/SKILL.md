---
name: concise-prose
description: Use whenever the agent is writing or editing prose (e.g. chat replies, documentation, markdown, code comments, log entries, commit messages, descriptions, error strings) to slim content without losing meaning.
---

# concise-prose

Raise signal, cut noise — minimize reader overhead without losing meaning. Readers can be users, other agents, or downstream tools.

## Directives

### Voice

- Active imperative, not passive.
- Report facts — no speculation, no hedging.
- No preambles, narrative overhead, cheerleading, or self-congratulation. Direct the action, don't narrate it ("Map the callers", not "This section helps you understand the callers"). Where describing or analyzing an action *is* the content (e.g. discussion, postmortems, design rationale, change summaries), describe it in full.

### Structure

- Reshape before trimming — structural choices convey meaning and often cut more than word-trimming does.
- Align parallel or comparative content using bullet lists or tables, and preserve that alignment — do not collapse parallel items into prose.
- Mark the load-bearing claim and let the rest visibly support it — the reader should find the one thing that matters without weighing every sentence equally.

### Restraint

- No examples unless the content is ambiguous without one. Counter-examples only when essential to clarify a positive example. A paired contrast that *defines* the behavior (`Not: … / Yes: …`, wrong/right) is the content itself, not an illustration of it — keep those; the bar is whether the pair carries the spec, not whether it decorates it.
- Signal non-exhaustiveness in parenthetical lists with leading "e.g." — an unqualified list implicitly claims completeness; the qualifier is signal, not filler.
- Quantify only when the number is load-bearing — a threshold, a tracked discrepancy, or a result whose value a decision turns on ("0 failures", "158/205 over credit"). A decorative count (totals, tallies, sizes no decision reads) rots and demands upkeep; state the qualitative fact instead ("suite green", "balances reconcile").
- Cross-reference only when the reader must consult the source to understand the current surface.
- Never enumerate content from a linked source — parenthetical summaries are redundant, cherry-picked, and prone to drift.

### Anti-staleness

- No commentary on prior states the artifact no longer reflects — the artifact represents current reality only.
- No references to temporary phases, processes, or labels that may not exist when the artifact is read.

### Context leverage

- Lean on shared vocabulary — content compacts when it leverages concepts the reader already holds (e.g. established upstream in this surface, general knowledge a generalist would recognize).
- Siblings carry context — items in a complementary set (e.g. failure modes, axes, angles) compact further than items read alone. Each only describes what it covers; the surrounding siblings clarify what it excludes. A gap that persists across all siblings together is a legitimate hole to address.
- Dedup within a surface, not across surfaces — e.g. frontmatter, body, metadata, docstring, error codes, error messages are distinct mechanical surfaces with distinct readers and triggers; the same content appearing in two is not duplication.

### Length

- Prose length follows information, not prompt length — prose runs as long as the content requires after every other directive is applied.

## Safety checks

These bound the cut decision itself, not a separate review pass.

- **Slim test** — would removing this leave meaning intact for a reader who lacks your context? If yes, the content is a candidate for removal pending the remaining checks.
- **Lossless preservation** — safety boundaries, corrective guidance, and disambiguation survive any cut. A phrase carrying one of these loads stays.
- **Curse of knowledge** — content that feels redundant to the author often carries the only "why" the reader has: rationale, scope-setting, anti-pattern framing that reads as preamble but makes the rule stick. If content fits a companion surface better, migrate it rather than delete and assume the other surface will catch up.
- **Chesterton's Fence** — do not remove a fence until you know why it was built. Raise to the user when a candidate for removal has no recoverable purpose.

Lossless preservation and Curse of knowledge jointly bound what the Slim test may remove — the first protects categorical loads (safety, correction, disambiguation), the second protects supporting context (rationale, scope, anti-pattern framing).

## Exceptions

Exceptions relax specific directives on specific surfaces. Identify which directive the exception modifies; apply all others normally.

- **Sequence-specific artifacts** (incident reports, postmortems) — relax restraint on event ordering and timing detail; the sequence is the content.
- **Endorsement artifacts** (recommendations, testimonials) — relax length and restraint on rationale and confidence language that substantiates the call. Voice and anti-preamble directives still apply.
- **Narrative artifacts** (case studies, journeys, retrospectives) — relax restraint on arc and learning moments that inform future decisions.
