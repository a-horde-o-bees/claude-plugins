---
name: reauthor
description: Use to rewrite an existing artifact (e.g. file, section, function, schema) as if authoring it for the first time — invoked when fresh composition is the directive, not to decide whether one is warranted.
---

# Reauthor

Use to rewrite an existing artifact (e.g. file, section, function, schema) as if authoring it for the first time — invoked when fresh composition is the directive, not to decide whether one is warranted.

Compose the artifact as if authoring it for the first time. The current form is informative — it represents what worked before whatever now wants to change it. Treat it as a sketch you have discarded.

## What survives

- **Outcome** — what the artifact produces, causes, or enables.
- **Identity** — name, path, public interface.

Everything else — organization, phrasing, ordering, examples, headings — is yours to set from the constraints in play now.

## Rules

- Read the current artifact along with every rule, convention, and skill in context, plus the surrounding conversation. Let all of them shape the new version at once.
- Don't anchor on the existing organization or phrasing — both solved a problem set that may no longer apply. Build the structure from what the artifact must do now.
- Work the artifact in one pass, not section by section — local fixes accumulate as patches, and only an end-to-end pass restores coherence. Output it whole: no `...`, no `[unchanged]`, no implied continuation.
- Leave no residue of the prior version — a reader picking the artifact up cold should see no trace of it and need nothing absent to understand what's here; concise-prose § Anti-staleness names the forms, applied here to the version being replaced.

## Scope

Default to the unit the user named. Widen only with explicit approval, and only when the named unit can't cohere without touching neighbors — say so first.

<!-- flatten-skills START {"deps": ["concise-prose"]} -->

## Dependencies

### concise-prose

Use to shape prose for any reader (e.g. chat replies, docs, code comments, commit messages, error strings) to minimize overhead without losing meaning — the foundation for all prose output, which other instructions build on or modify.

- **Input contract** — treat all input as intent to recompose, not text to transplant; preserve exact wording only when explicitly directed.
- **Edit license** — rephrase only to cut or correct: a reduction that preserves meaning is improvement; a swap that trades one adequate phrasing for another is churn.
- **Output contract** — length follows information, not prompt length: prose runs as long as the content requires once every directive below is applied.

#### Voice

- Write in active imperative voice, never passive.
- Report facts — no speculation, no hedging.
- Cut ceremonial and narrative overhead (e.g. preambles, cheerleading, self-congratulation).

#### Structure

- Reshape to move meaning into structure — give content the shape that carries it most efficiently, not the shape it arrived in; grouping, ordering, and form express relationships that connective wording spells out, and often cut more than trimming does.
- Trim to shed wording the meaning doesn't need (e.g. modifiers, restatement, filler).
- Keep parallel or comparative content aligned in bullet lists or tables, never collapsed into prose.
- Mark the load-bearing claim and let the rest visibly support it — the reader should find the one thing that matters without weighing every sentence equally.

#### Restraint

- Drop examples or counter-examples unless the content is incomprehensible without them.
- Signal non-exhaustiveness with `(e.g. …)`, in exactly that form — an unqualified list implicitly claims completeness; the qualifier is signal, not filler.
- Quantify only when the number is load-bearing (e.g. a threshold, a tracked discrepancy, a result whose value a decision turns on). A decorative count rots and demands upkeep; state the qualitative fact instead.
- Cross-reference only when the reader must consult the source to understand the current surface.
- Never enumerate content from a linked source — parenthetical summaries are redundant, cherry-picked, and prone to drift.

#### Context leverage

- Assume a capable reader — lean on the vocabulary and general knowledge they hold (e.g. concepts established upstream in this surface, anything a generalist would recognize), and spend words only on non-obvious, domain- or project-specific facts.
- Compact sibling items against each other — in a complementary set (e.g. failure modes, axes, angles), each item describes only what it covers; the surrounding siblings clarify what it excludes. A gap that persists across all siblings is a legitimate hole to address.
- Eliminate duplication within a surface (e.g. a point stated twice, examples making the same point, parallel sections that hedge each other), not across surfaces (e.g. frontmatter, body, metadata, docstring, error codes, error messages) — each surface has distinct readers and triggers; the same content appearing in two is not duplication.

#### Anti-staleness

- Cut commentary on prior states the artifact no longer reflects — the artifact represents current reality only.
- Cut dependence on context that may be absent when the artifact is read (e.g. temporary phases, position labels, pointers to removed siblings) — state each fact directly rather than by reference.

#### Correction

Correct by reduction, not accretion. When a passage reads wrong, sharpen or cut the offending line rather than layer a clarifying sentence over it. A passage that passed review is not proven minimal: the sharper, shorter form is often still unarticulated.

#### Safety checks

These bound the cut decision itself, not a separate review pass.

- **Slim test** — would removing this leave meaning intact for a reader who lacks your context? If yes, it is a candidate for removal pending the remaining checks.
- **Lossless preservation** — carry safety boundaries, corrective guidance, and disambiguation through any cut; a phrase bearing one of these loads stays.
- **Curse of knowledge** — content that feels redundant to the author often carries the only "why" the reader has (e.g. rationale, scope-setting, anti-pattern framing that reads as preamble but makes the rule stick). If content fits a companion surface better, migrate it rather than delete and assume the other surface will catch up.
- **Chesterton's Fence** — do not remove a fence until you know why it was built. Raise to the user when a candidate for removal has no recoverable purpose.

<!-- flatten-skills STOP -->
