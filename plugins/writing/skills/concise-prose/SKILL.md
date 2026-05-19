---
name: concise-prose
description: Use whenever the agent is writing prose — chat reply, doc, code comment, log entry, commit message, frontmatter description, rule body, error string — or when the user asks to tighten, shorten, or strip padding from existing prose. Match length to substance and remove words that don't change meaning.
---

# Concise

Match length to substance. The reader's time is the constraint; raise signal, cut noise.

Cuts stay lossless — drop only what doesn't carry information. Verbosity earns its keep when removal would be lossy: safety boundaries, corrective guidance, disambiguation where misreading is costly, instructions that have to survive without knowing the reader's position in a delegation chain. Some artifact types legitimately expand for their function — incident reports for sequence specificity, recommendations and testimonials for endorsement voice, case studies for narrative. Everywhere else, cut.

## Defaults

- Lead with the answer or action — no preambles, no pre-narration ("I'll help you with that", "Let me start by", "Here's what I'm going to do"). Do the action and report the result.
- Be complete and concise — cover what needs addressing, then stop. Prompt length is not a signal.
- Report facts, not affect — no self-congratulation, no cheerleading, no "great question."
- Active imperative ("Read the file") over passive ("The file should be read").
- Bullets for parallel items; one claim per sentence.
- One positive example only when the rule is ambiguous without it. Counter-examples only when essential.
- Cross-reference only when the reader cannot find the material themselves.
- Closing summary only when it adds information past the body.

## Common substitutions

- "in order to" → "to"
- "due to the fact that" → "because"
- "at this point in time" → "now"
- "in the event that" → "if"

## Drop unless load-bearing

- Fillers: "it's important to note", "keep in mind", "actually" (as softener), "just" (as softener).
- Hedges: "generally", "typically", "somewhat", "basically".
- **Parenthetical content trailing a `/skill-name` invocation.** The full skill loads on invocation; a parenthetical summary is redundant and biases the reader to a subset. Strike `Apply /description-authoring (scope + role; exclude internals).` Keep `Apply /description-authoring.`
- **Process narration about how the artifact was authored.** "Reauthored", "sweep applied", "restoration applies" — describes the change journey. The artifact's current shape carries the journey; the narration is residue.
- **Restated principles when the artifact already shows them applied.** Saying "this conforms to X" when the artifact IS the conformance is redundant. The diff carries the proof.
- **Meta-commentary about earlier steps in the change history.** "Now corrects Y", "applies the user's correction", "the prior commit had Z" — narrates how we got here. Cuttable in any artifact except where the journey informs future decisions (a design log, a postmortem).
- **Project-internal phase or milestone labels.** "Phase G", "Sprint 4", "Milestone B" — meaningless to anyone outside the project's planning surface. Strip from artifacts that will be read after the phase ends (commit messages, public docs, code comments).

## Surface boundaries

Frontmatter description, H1 body, docstring, schema title, error code, error message — each is a distinct mechanical surface with its own reader and trigger condition. Content appearing on more than one is not duplication; each surface stands alone for its reader. Dedup within a surface, not across.

## Lean on context

Structural tactics compact more than per-word trimming.

- **Siblings carry context.** Content in a complementary set — different failure modes, axes, or angles — compacts further than content read in isolation. Each piece marks its own axis; siblings define each other by negative space. Applies more aggressively to diagnostics ("if X then Y") than to directives ("do X") — directives often need their rationale to land, since the reader has to be motivated to follow. A bare directive among sibling directives can still fail to persuade.

- **Shared vocabulary.** A description compacts when it points at concepts the reader already holds. Two sources: built upstream in this surface (a test referencing "scale" lands because the body earlier defined scope and role at every size) or carried from general/training knowledge (words like "granularity" or "boundary" land widely without definition). For general-knowledge references, calibrate by reader portability — safe only if a non-specialist generalist would recognize the term. Project jargon and expert shorthand must be defined, or the compression fails for readers (humans, other agents, downstream tools) who don't share the training.

## Slim test

Would removing this leave the meaning intact for a future reader who lacks your current context? If yes, remove it.

**Chesterton check** — if you don't yet know why the phrase is there, find out first. Meaning can survive a cut that drops a load-bearing reason.

**Curse of knowledge** — what feels redundant to you (the author with full context) is often the only "why" the reader has. Rationale that motivates a directive, scope-setting you've internalized, anti-pattern warnings that look like preamble — they look cuttable but carry the load that makes the rule sticky.
