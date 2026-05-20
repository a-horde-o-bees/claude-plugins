---
name: concise-prose
description: Use whenever the agent is writing or editing prose (e.g. chat replies, documentation, markdown, code comments, log entries, commit messages, descriptions, error strings) to slim content without losing meaning.
---

# concise-prose

Optimize, sharpen, and slim prose to minimize reader consumption time and effort; raise signal, cut noise. Consumers can be users, other agents, downstream tools.

## Guidance

Align prose with the following:

- Report only facts — no assumptions, no speculation, no hedging.
- No narrative overhead, no preambles, no cheerleading, no self-congratulations.
- Active-imperative voice, not passive.
- Organize information logically, for coherency, and for scannability — structure itself conveys meaning that may reduce the need for explanatory documentation; structural adjustments may reduce cognitive load more than word-trimming.
- Align parallel or comparative content using bullet lists or tables.
- No unnecessary examples — positive examples only when content is ambiguous without it; counter-examples only when essential to clarify positive examples.
- Signal non-exhaustiveness in parenthetical example lists with leading "e.g." — unqualified lists implicitly claim the items are the full set, and the qualifier is signal, not filler to be cut during compression.
- Include cross-references only when the consumer needs to read a source directly to understand immediate content.
- No enumeration of content from a linked source — parenthetical summary is redundant, cherry-picked, and susceptible to drift.
- No commentary or self-references to an earlier historical state that no longer exists — an artifact should only reflect current reality.
- No references to temporary phases, processes, or labels within artifacts that can be consumed long after those references cease to exist.
- Dedup content within a surface, not across surface boundaries (e.g. frontmatter, body, metadata, docstring, error codes, error messages) — each is a distinct mechanical surface with its own consumer and trigger conditions; content appearing in more than one is not duplication. Each surface stands alone for its reader.
- Siblings carry context — content in a complementary set (e.g. different failure modes, axes, or angles) can compact further than content read in isolation. Each piece marks its own axis; siblings define each other by negative space.
- Lean on shared vocabulary — content can compact when it leverages concepts the reader already holds (e.g. described upstream in this surface, general/training knowledge that a generalist would recognize).
- Prompt length is not an indication of expected prose length — length is determined strictly by the information that needs to be conveyed. Prose will be as long as it needs to be while still following all other guidance.

## Safety checks

Apply each of the following before finalizing a cut. These are part of the directive set — they govern the cut decision itself, not an optional review pass.

- **Slim test** — would removing this leave meaning intact for a future reader who lacks your context? If yes, the content is a candidate for removal, pending the remaining checks.
- **Lossless preservation** — safety boundaries, corrective guidance, and disambiguation must survive any cut. If a phrase carries one of these categorical loads, keep it.
- **Curse of knowledge** — content that feels redundant to you (the author with full context) may carry the only "why" downstream consumers have: rationale for directives, scope-setting you've internalized, and anti-pattern warnings that look like preamble all read as cuttable but make the rule stick. Surface coherence is the corollary — if content fits a companion surface better than the current one, migrate it rather than delete with the expectation the other surface will be updated later.
- **Chesterton's Fence** — do not remove a fence or policy until you know exactly why it was created. Raise to user if you think something is a candidate for removal but you cannot establish the original purpose.

Lossless preservation and Curse of knowledge are paired protections — the first defines categorical loads that must survive any cut (safety, correction, disambiguation); the second defends supporting context (rationale, scope-setting, anti-pattern framing) that looks generic but motivates the rule. Both bound what the Slim test is allowed to remove.

## Exceptions

Some surfaces legitimately retain length or structure that would otherwise be cut. Exceptions modify specific directives — they do not exempt a surface from the entire skill.

- **Sequence-specific artifacts** (incident reports, postmortems) — preserve event ordering and timing; the sequence is the content.
- **Endorsement artifacts** (recommendations, testimonials) — preserve rationale and confidence language that substantiates the call. Active voice and no-preamble directives still apply; only length and restraint directives are relaxed.
- **Narrative artifacts** (case studies, journeys, retrospectives) — preserve arc and learning moments that inform future decisions.

When applying the skill to these surfaces, identify which directive the exception modifies; apply all others normally.
