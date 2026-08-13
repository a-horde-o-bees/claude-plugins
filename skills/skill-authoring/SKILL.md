---
name: skill-authoring
description: Use when creating or refining a skill (e.g. drafting a new one, sharpening its trigger description, splitting its process into components) to bring the whole thing up to the well-formedness bar in one pass.
---

# skill-authoring

Use when creating or refining a skill (e.g. drafting a new one, sharpening its trigger description, splitting its process into components) to bring the whole thing up to the well-formedness bar in one pass.

## Applied disciplines

The disciplines every authoring pass exercises — [/markdown-authoring](#markdown-authoring), [/description-authoring](#description-authoring), [/concise-prose](#concise-prose) — are materialized under ## Dependencies below; apply them from there. The rest bite only for certain skill shapes and are applied by name as they do: procedure-authoring (a process with control flow beyond a linear sequence), rule-authoring (a directive that must bind on the right cases), file-decomposition (whether a unit belongs in this file at all).

## The trigger frontmatter

The `description:` is the skill's trigger and the only part always in context: the model decides engage-or-skip from it alone, and every skill's entry sits in the listing for the whole session, competing with every other instruction there. Author it per description-authoring — what the skill does and when to use it, woven fluently, third person — plus the facts specific to this surface:

- **Key use case first.** The listing truncates an entry at 1,536 characters, front-first — the opening clause must carry the decision.
- **One distinctive use-condition.** A trigger matches on one vocabulary collision with the live request, not many. Synonym runs and quoted lists of example phrasings add no matching power and widen unintentional auto-invocation; name distinct cases (`e.g.`-marked) when they cover genuinely different territory, never rephrasings of one case.
- **Weave idiom vocabulary into the prose.** When requests arrive in an idiom that shares no tokens with the responsibility statement ("prepping a handoff" vs. "reconcile system docs"), fold that vocabulary in as a fluent subordinate clause — the description stays one readable thought and still carries the collision surface. Never as a quoted phrasing list.
- **The listing is a shared budget.** Every entry is permanent per-session context, and each addition taxes every other skill's chance of firing. Trim at the source first; beyond that, `skillOverrides: "name-only"` lists a low-priority skill without its description, and `skillListingMaxDescChars` / `skillListingBudgetFraction` (or `SLASH_COMMAND_TOOL_CHAR_BUDGET`) tune the caps.
- **Intentionally unused fields.** The suite sets no `when_to_use` (the woven description is the whole trigger surface; the field is appended into the same listing entry under the same 1,536-char cap, adding only a second surface to audit) and no `disable-model-invocation` / `user-invocable` (every skill stays model- and user-invocable at the defaults). Deviate only as a deliberate, recorded exception.

The general exclusions — describe responsibility, never method; never enumerate the skill's contents or verbs — are description-authoring's; the skill listing is where those leaks cost most, since a leaked description both misfires as a trigger and bloats every session. Test a contested trigger cold with should-trigger / should-not-trigger prompts (rule-authoring § Enforce before wording) rather than arguing the wording.

## Description–body identity

markdown-authoring's identity and summary rules do the general work; what makes them load-bearing for a skill is that either surface ships alone — the listing carries no body, and a loaded body carries no frontmatter — so the shared first paragraph is the only summary guaranteed present on every consumption path.

## Skill layout

`SKILL.md` holds the whole invocation: the trigger, the process, and — materialized under its ## Dependencies section — the sibling disciplines the process depends on. Keep the process in the body. A component file the model must choose to open mid-run is a hop that silently misses under load (file-decomposition § Reliability precedence); token relief for a long process comes from mechanizing deterministic steps into scripts, never from splitting the prose behind a hop. Component files remain for text consumed outside the invocation load: a directive a spawned agent reads fresh, assets and templates a step copies, reference material cited but never required to run.

## Referenced dependencies

Cross-skill content dependence is declared by referencing the skill where the process uses it — `Apply /concise-prose to the summary` — and the build materializes every referenced skill's body into the file; nothing is left to runtime dispatch or a model-mediated hop. A reference is a `/skill-name` token naming a sibling skill: in prose at the point of use when the host dictates how the dependency applies, or as a list item under `## Dependencies` when it stacks on the whole process without scoping.

```markdown
## Dependencies

- /markdown-authoring

<!-- flatten-skills START -->
...generated: the flat closure, one demoted unit per referenced skill...
<!-- flatten-skills STOP -->
```

`flatten_skills.py <skills-root>` rewrites every file to this normalized form: each reference linked to its flattened copy — `/concise-prose` becomes `[/concise-prose](#concise-prose)`, still reading as a skill call while resolving in-file, and a hand-written link may target any section of the unit — and the region regenerated as the deduplicated closure of every referenced skill, ordered so referenced content always sits further down, each unit's frontmatter and Dependencies section stripped, headings demoted (H1 → H3), `${CLAUDE_SKILL_DIR}` rewritten to resolve to the sibling-installed folder. Everything must compile: a reference naming no sibling skill, or an anchor resolving to no heading, is an error and nothing is written. `--check` recomputes and byte-compares the whole file — an unlinked reference, a misplaced section, and a stale region all read as stale; it runs in the lint pass and gates the mirror sync. Refresh after editing any skill that others reference.

**Reference against the cost.** A reference buys deterministic presence and pays the dep's whole closure into every invocation — the region's byte size is the per-invocation price, visible in the file, and a dep's own references compound transitively. Reference a discipline the process exercises every run; prefer a leaf dep (one with no references of its own); cite everything else.

## Lint pass

Every invocation ends with a lint pass over the skills touched:

```
python3 ${CLAUDE_SKILL_DIR}/scripts/lint_skill.py <skill-dir|SKILL.md|skills-root> ...
python3 ${CLAUDE_SKILL_DIR}/scripts/flatten_skills.py --check --skills-root <skills-root> <skills-root> <non-skill hosts>
```

`lint_skill.py` enforces the mechanically checkable subset of the suite's rules (e.g. description–first-paragraph identity, the listing budget, source conventions that keep flattening mechanical); `flatten_skills.py --check` verifies every materialized dependency region is fresh. Non-skill flatten hosts join every refresh and check — the user `~/.claude/CLAUDE.md` carries the shared-intent gate this way — and the mirror sync gates on their freshness too. Each script's docstring is the source of truth for what it checks. Fix every error; a warn is a judgment call — resolve it or knowingly leave it.

Any skill whose own rules are mechanically checkable ships a linter the same way — a script that travels with the skill and runs at the end of every pass touching its artifacts (e.g. export-diff's page linter, this skill's `lint_skill.py`).

## Reference audit

Close an authoring pass by classifying every cross-skill reference, judged by reading the affected files whole — the conventions that make a snippet legible cannot be assumed from match-line context:

- *dependency* — the referenced discipline's text shapes execution at that point, every run: reference it as `/skill-name`, scoped in prose where the host dictates how it applies or listed under `## Dependencies` where it stacks obviously, weighing the closure cost above.
- *citation* — provenance, comparison, rationale, or a discipline that bites only sometimes: bare name, no slash. A citation's miss must be cheap — the executor falls back on general competence, not on the cited text.
- *definitional example* — the reference syntax is itself the content: inside a fenced block or code span, where lint and the flatten tool treat it as literal.

Every slash reference must compile — name a sibling skill and link to its flattened copy. An unresolved reference is a lint error; a bare resolved one is stale until a refresh links it.

## Mechanization audit

For every process step, ask: judgment or mechanism? A step whose outcome is fully determined by its inputs — parse, count, walk, diff, rename — belongs in a script the step invokes; prose walking an agent through mechanical work drifts and re-bills every invocation (rule-authoring: route load-bearing behavior to mechanical enforcement rather than wording).

## Dependencies

<!-- flatten-skills START -->

### markdown-authoring

Use when authoring markdown files, or to lint existing markdown on demand.

#### Structure

- Open every file with a level-1 heading (`#`) naming it, then its summary paragraph: when the file carries `description:` frontmatter, the first paragraph is that description verbatim — one owner for the summary, audited by diffing the two; otherwise write it per description-authoring.
- Only summary-level content sits before the first section heading — the description paragraph, then support that still reads at that level. The test: content is summary-level when it governs the document as a whole (e.g. its input, its output bounds) and would misread as scoped under any one heading; content that fires at a recognizable moment or span belongs in a precise section.
- Give a unit a heading when it is an addressable scope — cited from elsewhere or consulted independently; bind it as a bold-label bullet (`- **Label** — details`) when it is a member of a jointly-consumed set or must sit at summary level.

#### Lint pass

Every invocation ends with a lint pass over the markdown touched — or, invoked purely to lint, over the files, directories, or globs the user names:

```
node ${CLAUDE_SKILL_DIR}/../markdown-authoring/scripts/lint.mjs <file|dir|glob> ...
```

Fix every error; a warn is a judgment call — resolve it or knowingly leave it. `lint-spec.md` is the source of truth for what the script enforces.

#### Preference overrides

Two layers, matched to how far preferences diverge:

- **Severity** — a project config retunes individual rules; project-owned, so it survives suite updates.
- **Different rules** — shadow this skill: install your own `markdown-authoring` at a nearer scope (e.g. a project's `.claude/skills/`). Every reference resolves by name through the harness priority chain, so the nearest copy wins everywhere the suite invokes it.

### description-authoring

Use when writing the line a reader uses to decide engage-or-skip — an artifact's description at any scale (e.g. file header, docstring, skill frontmatter, commit subject).

Often it is the only thing the reader — user, other agent, or downstream tool — has. A vague description makes the content effectively invisible.

#### Substance

- Describe what the artifact is for, not how it does it — its responsibility or the outcome it produces, never the method, steps, or approach behind it, including the technique a skill teaches. "Rank search results by relevance" is a what; "rank results with TF-IDF scoring" is a how.
- Convey two things: what the artifact covers and what kind of thing it is (e.g. directory, module, CLI, config, rule, schema, section, function).
- Weave both into fluent prose with no visible seam — never labeled fields or split halves. "Retry and backoff helpers for outbound HTTP calls," not "Scope: HTTP retries. Role: helper module."
- Lead with the key case — descriptions are read, and truncated, front-first; the first clause must carry the engage-or-skip decision on its own.
- Match the abstraction to the artifact's scale — a directory's coverage is coarser than a file's, a package's coarser than a function's.
- Third person.

#### Length

- Run as long as granularity requires, no longer — the quality tests below decide when it's enough, not a word budget. Most descriptions are one sentence; a broad or multi-faceted artifact may run to a few. Don't pad toward a paragraph, don't compress past distinguishability.
- One distinctive condition outweighs many restatements. The reader — or a matcher deciding whether to engage — needs a single clause that separates this artifact from its neighbors; synonym runs and example-phrasing lists add no distinguishing power, and each restatement widens accidental matches without covering a new case. Distinct cases may be listed (`e.g.`-marked); rephrasings of one case may not.

#### Exclude

- Don't list contents — section, function, or class names.
- Don't recount history — why it exists, what it replaced, when it was added.

#### Consistency

- The same artifact described at any boundary reuses one description — single source of truth.

#### Quality tests

- Interchangeable with another artifact's description → too vague.
- Would change when internals are refactored though the responsibility holds → too detailed.
- Would fit equally at a different scale → wrong granularity.
- Contains a phrase whose removal loses no case → a restatement; cut it.

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
