# Rebuild Sweep Review (2026-05-13)

Items from this rebuild pass that I'd normally have surfaced for confirmation. The user authorized autonomous execution with this review file as the trade. Each item names the file, the change, and the reasoning so you can revert or refine in a focused session.

## Semi-structural changes (file-internal, no downstream impact)

### `plugins/ocd/skills/git/_release.md` — step renumbering

Old step 7 split into top-level steps 7 + 8 (one binding per step, per PFN atomic-step principle). Subsequent steps renumbered: 8 → 9, 9 → 10, 10 → 11. Internal self-references updated (`re-validate per step 8` → `step 9`; `Go to step 9.1` → `Go to step 10.1`).

No external consumer references `_release.md`'s step numbers. The renumbering is internal cosmetic improvement; identity (scope + role + callable surface + return shape) preserved.

### `plugins/ocd/skills/git/_release_synthesize.md` — dropped step 1

Original step 1 was a no-op clarification ("Read the methodology to anchor format and project-specific change semantics" — but `{methodology}` is already passed in as a variable, so there's nothing to "read"). Dropped; remaining steps renumbered (2 → 1, 3 → 2, etc.). Internal self-references updated (`step 6` → `step 5`).

### `plugins/ocd/skills/git/_release_bootstrap.md` — dropped step 6

Original step 6 ("Confirm with user that the bootstrap completed and `release.md` is ready for use, then return to caller") was redundant with the `### Report` section's Return-to-caller shape. Removed; step 5 (Write) is the final action.

## Behavioral changes worth flagging

### `uv run` invocations gained `--directory <skill-base>` flag

Affected: `plugins/ocd/skills/rules/_install.md`, `plugins/ocd/skills/rules/_uninstall.md`, `plugins/skill-authoring/skills/skill-composer/_compose_new.md`, `plugins/skill-authoring/skills/skill-composer/_compose_refine.md`, `plugins/skill-authoring/skills/skill-composer/_compose_list.md`, `plugins/skill-authoring/skills/skill-creator/_new.md`.

Previously: `uv run -m scripts.<module> ...`. Without `--directory`, the command fails when cwd isn't the skill folder (the agent's typical cwd is project root, not the skill folder, since Claude Code doesn't `cd` into the skill on invocation).

Now: `uv run --directory <skill-base> -m scripts.<module> ...`. Robust regardless of cwd.

The `<skill-base>` placeholder is the skill's runtime base directory (Claude Code emits "Base directory for this skill: ..." in the system reminder). The agent substitutes the path before issuing bash.

Hit this empirically during a `/ocd:rules status` test earlier in the session — `get_project_dir()` raised because cwd was inside `~/.claude/`. The fix here aligns workflow invocations with the same pattern.

### `_checkpoint.md` sub-call return binding

Changed each sub-call to bind a return variable:

```
2. {commit-report}: Call: `_commit.md`
3. {push-report}: Call: `_push.md` ({branch}: {branch})
5. {ci-report}: Call: `_ci.md` ({branch}: {branch})
```

Uses PFN's new `{var}: Call:` block-assignment. Assumes called workflows produce values via their `Return to caller:` clauses that block-assignment captures. The convention is in the PFN canonical (Assignment section); spot-check by invoking `/ocd:git checkpoint` once in dev to confirm the return values flow.

### `_release.md` agent-first-interfaces additions

Exit messages gained corrective guidance:

| Step | Old message | New message |
|---|---|---|
| 1.2 | `releases cut from main; currently on {current-branch}` | + `— switch to main or rebase the change onto main first` |
| 1.3 | `working tree has unstaged changes` | + `— clean or commit before releasing` |
| 1.4 | `working tree has staged changes` | + `— commit or reset before releasing` |
| 9.1 | `version {final-version} is not greater than current ({current-version})` | + `— pass a higher version or omit --version to use the recommendation` |
| 9.3 | `tag {tag} already exists` | + `— pass a different --version or delete the existing tag if it was created in error` |

Per agent-first-interfaces ("Error messages include corrective guidance, not just failure description"). Longer messages; user-visible.

## Structural changes deferred (would have asked, no action taken)

### `plugins/skill-authoring/skills/skill-composer/SKILL.md` — body sections beyond entry-point scope

Per progressive-disclosure, SKILL.md is a gating layer: triggers + verb topography. Current body carries four substantial sections that leak workflow / reference content:

- **Storage** — filesystem layout of composed skills
- **Authoring discipline baked in** — meta description of which disciplines apply to composer's output
- **Compositions of compositions** — warning about a non-recommended pattern
- **Complementary tools** — reference to npx skills, /plugin install, sibling skill

These belong in `plugins/skill-authoring/ARCHITECTURE.md` (Storage, Authoring discipline, Compositions of compositions) and `plugins/skill-authoring/README.md` (Complementary tools). Moving them shrinks SKILL.md to its progressive-disclosure-canonical shape.

Not done — moving content across files is a content reorganization that should be reviewed (where do consumers expect to find each piece?). Tradeoff: smaller entry-point load cost vs harder discoverability for users who only read SKILL.md.

### `plugins/ocd/skills/git/_commit.md` — process step restructure

Original had:
- Step 1 (analyze working tree, 4 substeps)
- Step 2 (include untracked files, with a substep about suspicious files)
- Step 3 (group commits, with multi-substep evaluation criteria)
- Step 4 (draft commit messages, 2 substeps with rule-like content)
- Step 5 ({co-author} binding)
- Step 6 (commit loop)
- Step 7 (verify)
- Step 8 (return)

New form:
- Step 1 (analyze working tree, 4 substeps — same)
- Step 2 ({suspicious-untracked} binding)
- Step 3 (conditional handling of suspicious untracked)
- Step 4 ({commit-groups} with consolidated grouping criteria)
- Step 5 ({commit-messages} draft)
- Step 6 ({co-author} binding)
- Step 7 (commit loop, with co-author inline)
- Step 8 ({final-status} binding)

Step boundaries shifted; semantics preserved. Rule-like content in original step 4.1 ("Describe end-state results, not change journey") moved to the Rules section as a duplicate (the rule was already there as "Commit messages describe end-state results, not the change journey").

Not gating-worthy on its own, but a substantial shape change worth a glance before next `/ocd:git commit` invocation.

### `plugins/skill-authoring/skills/skill-creator/_new.md` — variable-binding throughout step 1

Old step 1 had 7 user interview questions as plain sub-bullets. New form binds each answer to a named variable ({goal}, {triggers}, {output-format}, {edge-cases}, {runtime-vs-dispatch}, {test-cases}, {destination}). Step 2 (which had redundantly bound {destination} from step 1.7) dropped.

Subsequent step references updated: `step 1.6 = yes` → `{test-cases} is yes` (step 8 condition).

Behaviorally equivalent but the bound variables make downstream substitution explicit. If a future workflow wants to inspect specific answers, they're addressable.

## Description tightening (description-authoring)

Trimmed across multiple SKILL.md frontmatter `description:` fields. The trims dropped:

- Per-verb parenthetical internals (verb-table content in the body)
- Verbose discipline lists ("PFN + progressive-disclosure + description-authoring + workflow-vs-script disciplines applied at every authoring moment")
- Redundant trigger phrasings ("or any context where the user is initiating a new skill...")
- Dish/recipe metaphors (skill-composer's "the recipe + ingredients + dish" framing)

Affected: `plugins/ocd/skills/git/SKILL.md`, `plugins/ocd/skills/rules/SKILL.md`, `plugins/skill-authoring/skills/skill-composer/SKILL.md`, `plugins/skill-authoring/skills/skill-creator/SKILL.md`, plus body-line trims in several verb workflow files.

**Trade-off**: shorter descriptions are more concise but may lose marketplace-discoverability nuance. The `description:` field is what aggregators (skills.sh, anthropic-style marketplaces) read; verbose was less crisp but more searchable. The new descriptions emphasize trigger phrases over verb listings — closer to description-authoring intent ("scope + role; exclude internals/contents/history").

If discoverability suffers, the trims can be partially reverted to surface more trigger surface area.

## Files left mostly as-is

- `plugins/ocd/skills/git/_checkpoint.md` — already minimal pre-rebuild; one minor restructure (sub-call return binding) noted above
- `plugins/ocd/skills/rules/_show.md`, `_status.md`, `_list.md` — minor PFN compaction (added `{var}: bash:` bindings, dropped `Invoke —` prefix)
- `plugins/skill-authoring/skills/skill-creator/_refine.md` — substantial workflow file; only spot-touched. Could benefit from a deeper pass binding intermediate state ({eval-prompts}, {iteration-results}, {user-signal}, {feedback}) but the file works as-is and the changes felt low-ROI for autonomous-mode. Worth a focused pass when next iterating on the creator workflow.

## Next-session candidates

- Verify `_checkpoint.md`'s sub-call return-binding actually works end-to-end (invoke `/ocd:git checkpoint`, confirm return values flow through `{commit-report}`, `{push-report}`, `{ci-report}`)
- Spot-check `_release.md` step renumbering: do internal `Go to step 10.1` and `re-validate per step 9` references resolve correctly when the workflow fires?
- Deeper pass on `_refine.md` (skill-creator) with the same binding discipline applied throughout
- Consider whether description trims went too far on discoverability; revert specific frontmatter `description:` fields if the marketplace surface needs more keyword density

## Audit learnings (from idempotence test)

A second `/ocd:rebuild` pass on `_release.md` produced an empty diff (confirming idempotence) and surfaced one false-positive that the first pass also flagged: extracting the Execute step into a script per workflow-vs-script. The user corrected: the workflow-vs-script audit needs to consider input provenance, not just write-side mechanical-ness.

**Corrected lens:** "Could a deterministic function with no agent context produce this result correctly?" — *including the function's inputs*. For Execute step:

- `{changelog-entry}` is synthesized markdown from a spawned agent (judgment)
- `{final-version}` is from synthesizer or user override (judgment / dialogue)
- Manifest paths come from `{methodology}` the agent interprets (judgment)

Every input traces to agent reasoning. A script wrapping the writes would either still need the agent to compose-and-marshal CLI args, or would reach into agent state mid-execution (explicitly an antipattern per the rule). So step 11 is appropriately workflow-form.

**Implication for the deferred structural items above:** skill-composer SKILL.md's Storage / Authoring discipline baked in / Compositions of compositions / Complementary tools sections were flagged as "leak workflow content into entry point". Re-reading progressive-disclosure: entry-point body should be "triggers + topography + **orientation**". Storage and Authoring discipline are legitimate orientation — they help a user understand what the skill creates and what shapes its output. Compositions of compositions is rule-like (could move to Rules). Complementary tools is external-reference orientation. The "move all four to ARCHITECTURE.md / README.md" recommendation was over-strict; the appropriate move is narrower: Compositions of compositions → Rules section (single-line), the rest stays.

That item is removed from "Next-session candidates" above. The audit lens correction applies to any future rebuild work: don't over-strictly read the rules; consider context and whether each section earns its place in the entry point.

### Rebuild itself was never rebuilt

User caught: across 22 file rebuilds + 1 idempotence test, `/ocd:rebuild` itself wasn't audited. Its SKILL.md description duplicated internals from `_rebuild.md`'s Process (the "extract → set aside → compose → diff" sequence), carried a redundant "Triggers explicitly when..." tail, and the body line included a PFN-rationale parenthetical that belongs in ARCHITECTURE not entry-point orientation. `_rebuild.md`'s blockquote tried to recap the whole process in one sentence; that's not scope+role, that's the algorithm.

All three trimmed in the rebuild-of-rebuild. Lesson: include the orchestrating skill in the sweep next time. The blind spot was "rebuild is the tool, not the target" — but the tool is also a skill bound by the same discipline.

### Rebuild-of-rebuild was itself partial on first pass

After the description trim, the user asked again — "was that a full rebuild of its markdown parts?" — and forced honesty: no, three targeted edits to descriptions / one body line, not a fresh compose of Rules + Process. A genuine fresh compose tightened 4 Rules per concise-prose (dropping parenthetical clarifications, redundant qualifiers) and dropped a duplicate reinforcement in Process step 5 (Rule 2 already prohibits referencing `{original}` during composition; the step 5 sentence was belt-and-suspenders).

Two-step lesson: patches can masquerade as rebuilds when the surface diff happens to align with what a fresh compose would produce in the visible sections (description, frontmatter). The hidden sections (Rules, Process, sub-bullets, parentheticals) need explicit per-rule audit. The discipline isn't "rebuild = make the file better"; it's "rebuild = compose fresh applying every loaded rule to every section". Without explicitly walking each section through each rule, patch-flavor leaks in.

## Prior-art research (four parallel agents, 2026-05-13)

Researched whether anyone else has built this skill or solved adjacent problems. Punchline: **the "compose fresh while preserving identity of an existing artifact" middle ground is unoccupied** in published skill ecosystems. Closest matches encode adjacent disciplines (red-green-refactor, rationalizations-to-reject, clean-room rewrite, role-split editor) that combine to give a strong recipe.

### Repo / URL catalog

**Skills ecosystems surveyed (no direct match found):**

- [anthropics/skills](https://github.com/anthropics/skills) — `skill-creator`, `claude-api`, `web-artifacts-builder`, `mcp-builder` — all create new from spec, none rebuild
- [vercel-labs/skills](https://github.com/vercel-labs/skills) + [skills.sh](https://skills.sh) — discovery / install ecosystem; no rebuild skill
- [Leonxlnx/taste-skill — redesign-skill](https://github.com/Leonxlnx/taste-skill/blob/main/skills/redesign-skill/SKILL.md) — closest verbal match; *explicitly forbids rewrite from scratch* (inverse exemplar). Borrow: dial-based forced parameter declaration to anchor against drift
- [mattpocock/skills — improve-codebase-architecture](https://github.com/mattpocock/skills/tree/main/skills/engineering/improve-codebase-architecture) — vocabulary-first patch with `CONTEXT.md` / `LANGUAGE.md` anchors. Borrow: persistent domain vocabulary as drift anchor
- [mattpocock/skills — tdd / diagnose / grill-me](https://github.com/mattpocock/skills/tree/main/skills/engineering) — workflow-phase gates ("no edit until hypothesis confirmed")
- [mattpocock/skills — write-a-skill](https://github.com/mattpocock/skills/tree/main/skills/productivity/write-a-skill) — checkpoint gates on creation
- [pbakaus/impeccable](https://github.com/pbakaus/impeccable) — `polish`, `harden`, `optimize`, `distill` (23 verb-per-discipline commands). Each is a transform-in-place
- [trailofbits/skills — skill-improver](https://github.com/trailofbits/skills/tree/main/plugins/skill-improver) — **strongest borrow source**: iterative review loop with explicit completion marker `<skill-improvement-complete>`, severity categorization, and a *"Rationalizations to Reject"* section that pre-counters drift
- [trailofbits/skills — semgrep-rule-variant-creator](https://github.com/trailofbits/skills/tree/main/plugins/semgrep-rule-variant-creator) — identity-preserving cross-substrate rewrite (port rules to new target languages)
- [obra/superpowers — writing-skills](https://github.com/obra/superpowers/tree/main/skills/writing-skills) — **strongest borrow source**: iron-law framing *"Edit without [discipline] = same violation as authoring without [discipline]. Delete. Start over."* Treats patching as a violation
- [citypaul refactoring skill](https://github.com/citypaul/.dotfiles/blob/main/claude/.claude/skills/refactoring/SKILL.md) — TDD-anchored, preserve-behavior-via-tests
- [ksimback/tech-debt-skill](https://github.com/ksimback/tech-debt-skill) — explicit "forbids recommending rewrites" stance (principled contrast)
- [softaworks/agent-toolkit — agent-md-refactor](https://agentskillsfinder.com/skills/agent-md-refactor) — restructures via progressive disclosure; patches
- [elifiner/refactoring](https://github.com/elifiner/refactoring) ([Show HN](https://news.ycombinator.com/item?id=46817508)) — "very small and very safe refactoring steps" — canonical patch-flow framing
- [howardmann/rewrite](https://github.com/howardmann/rewrite) — `/rewrite` for prose simplification (false-positive on the name)
- [AlexMini2517/skills — logic-rewrite](https://github.com/AlexMini2517/skills/tree/main/skills/logic-rewrite) — **closest skill-ecosystem match found**: explicit refactor-vs-rewrite distinction, "rewrite from first principles" workflow step, guardrails section, structured comparison template (Intent / Old approach / Problem / New approach / Why better / Trade-offs). Single-agent advisory-only — has the vocabulary, lacks the structural enforcement (no role split, no mechanical isolation, no rationalizations-as-injection, no identity-preservation gates). Useful positive-and-negative control
- [diegopetrucci/starting-from-scratch](https://github.com/diegopetrucci/starting-from-scratch/tree/main/skills/starting-from-scratch) — analytical verb (commentary, not action): "say what should change if it were being started again from scratch". Different category — code-review / retrospective, not rewrite-executor. Cataloged to note that searches for "rewrite" / "from scratch" surface adjacent categories not in scope

**Awesome-lists (URL bank for future reference):**

- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills)
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills)
- [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills)
- [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit)
- [Chat2AnyLLM/awesome-claude-plugins](https://github.com/Chat2AnyLLM/awesome-claude-plugins)
- [quemsah/awesome-claude-plugins](https://github.com/quemsah/awesome-claude-plugins)
- [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills)
- [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills)
- [agentskills.io](https://agentskills.io), [agentskills.in/marketplace](https://agentskills.in/marketplace)
- [tasteskill.dev](https://www.tasteskill.dev)

**AI coding tool implementations (system prompts published):**

- [Aider — Chat modes](https://aider.chat/docs/usage/modes.html) — architect/editor role split: architect plans, editor writes
- [Aider — Edit formats](https://aider.chat/docs/more/edit-formats.html) — `whole` vs `diff` vs `editor-whole` vs `editor-diff` (udiff was added specifically to counter GPT-4 Turbo's "lazy coding" elisions)
- [Aider wholefile_prompts.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/wholefile_prompts.py) — *"NEVER skip, omit or elide content from a file listing"*
- [Aider architect_prompts.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/architect_prompts.py) — *"DO NOT show the entire updated function/file"* (planner is structurally forbidden from emitting code)
- [Aider editor_whole_prompts.py](https://github.com/Aider-AI/aider/blob/main/aider/coders/editor_whole_prompts.py) — *"Output a copy of each file that needs changes."* No problem-solving framing
- [Cline — Improving Diff Edits by 10%](https://cline.bot/blog/improving-diff-edits-by-10) — `write_to_file` (whole) vs `replace_in_file` (diff) — tool-shape asymmetry
- [Continue edit.ts templates](https://github.com/continuedev/continue/blob/main/core/llm/templates/edit.ts) — `<START EDITING HERE>` / `<STOP EDITING HERE>` sentinel-bracketed regenerate-in-place; prefix/suffix preserved verbatim
- [Cursor leaked system prompt](https://github.com/jujumilk3/leaked-system-prompts/blob/main/cursor-ide-sonnet_20241224.md) — no whole-file-rewrite affordance (negative control: Cursor's Cmd+K is surgical by default)
- [nrehiew — Coding Models Are Doing Too Much](https://nrehiew.github.io/blog/minimal_editing/) — **load-bearing empirical study**: documents patch-bias / over-editing as reasoning-model-amplified. The discipline of "preserve original" measurably reduces over-edits; the inverse (forcing fresh compose) faces the same attractor in mirror

**Real-world rewrite case studies and discussion:**

- [Simon Willison — Dan Blanchard's clean-room rewrite of chardet](https://simonwillison.net/2026/Mar/5/chardet/) — **archetypal case study**: brainstorm design doc → build in empty repo with no access to original tree → JPlag verification (1.29% max similarity confirmed clean compose)
- [Patch Spiral / 5 Reasons Your Claude Skills Keep Breaking](https://alexmcfarland.substack.com/p/5-reasons-your-claude-skills-keep) — coins *"patch spiral"* phrase; baseline-build-refine loop antidote
- [Refactoring Agent Skills — context explosion](https://dev.to/superorange0707/refactoring-agent-skills-from-context-explosion-to-a-fast-reliable-workflow-5hg6) — "The fix wasn't a clever prompt. It was an architectural refactor."
- [Rebuild 93 skills (Medium, paywalled)](https://medium.com/product-powerhouse/a-pull-request-made-me-rebuild-all-93-of-my-claude-skills-then-i-added-7-more-16d5fe3e7f85)

**Software-engineering canon:**

- [Joel Spolsky — Things You Should Never Do, Part I](https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/) — caveat: messy-looking code is often crystallized bug fixes; capture before rewriting
- [Martin Fowler — Substitute Algorithm](https://refactoring.com/catalog/substituteAlgorithm.html) — named refactoring for "rewrite a function from scratch"; interface stays, body replaced, tests verify
- [Martin Fowler — Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) — seam discipline; interface contract survives
- [Mikado Method](https://understandlegacycode.com/blog/a-process-to-do-safe-changes-in-a-complex-codebase/) — revert on dependency discovery; mandatory reversion when scope creeps
- [Michael Feathers — Characterization Testing](https://michaelfeathers.silvrback.com/characterization-testing) / [comparison with approval tests](https://understandlegacycode.com/blog/characterization-tests-or-approval-tests/) — capture current behavior as safety net
- [OpenRewrite — LST philosophy](https://docs.openrewrite.org/) — parse → transform → reprint via Lossless Semantic Trees
- [Cleanroom Software Engineering](https://en.wikipedia.org/wiki/Cleanroom_software_engineering) — build from spec, never from existing code

### Patterns worth borrowing (synthesis)

1. **Role-split into phases with output-shape asymmetry** (Aider architect/editor + Cline write_to_file vs replace_in_file). Phase 1 *extracts* identity to a separate document (no code emission allowed). Phase 2 *composes* the artifact from the extract alone (original removed from context). The phases have different tool grants — the extract phase can't write to the target file; the compose phase can't read from the original. Structural prevention of patch-flow.

2. **Mechanical isolation, not advisory** (Blanchard's clean-room chardet). When step 3 says "set the original aside", do it literally — `mv` the file to a holding path, or copy contents to a temp file the compose phase has no read access to. "Set aside" as instruction loses; as mv-and-revert, it wins.

3. **Anti-elision verbatim from Aider**: *"NEVER skip, omit or elide content from a file listing. Output the entire file."* Drop this line into the compose-phase prompt.

4. **Authoritative-state cue from Aider**: *"Trust this extract as the true specification. The original is set aside."* Eliminates the model's default attractor toward whatever-it-last-saw.

5. **Rationalizations-to-reject list** (Trail of Bits skill-improver). Pre-enumerate the rationalizations the agent will produce mid-rebuild and rebut each:
   - "I'll just adjust this one line" → no; if the line needs changing, the whole section recomposes
   - "The original is mostly fine here" → no; "mostly fine" judgements are how patch-flow leaks in
   - "This section already conforms" → maybe; verify against the extract, not against the original's appearance
   - "Rebuilding loses tested behavior" → no; characterization-test verification gates that

6. **Iron-law framing** (obra writing-skills). *"Patching during rebuild = abort and restart from extract."* Make patching textually a violation, not a soft preference.

7. **Completion marker** (Trail of Bits). The workflow emits a literal token like `<rebuild-complete>` after the verification step; "looks good" doesn't satisfy. Forces traversal of the verification step.

8. **Diff-after-compose as structural gate, not audit pass**. The workflow MUST emit the diff before requesting user approval — diff is part of the deliverable, not an after-the-fact check.

9. **Characterization-test identity gate** (Feathers + Fowler Substitute Algorithm). Identity preservation isn't "looks similar" — it's enumerated: callable surface present, declared rules intact, return shape preserved, downstream consumer contract unchanged. Each check passes or surfaces a gap. No "trust me" verification.

10. **Tool-naming after output shape, not intent** (Cline). "Rebuild" stays as user-facing trigger phrasing, but internal steps name themselves by what they produce: `extract-identity`, `compose-from-spec`, `diff-and-verify`. Intent words ("refactor", "rewrite") the model can reinterpret; shape words ("output entire file") it can't.

11. **Sibling-skill cross-reference for trigger correctness** (AlexMini2517 logic-rewrite). Explicit "use X, not this skill, when..." pointers in the entry-point body sharpen the trigger by making the inverse concrete. logic-rewrite's body opens with "Use `refactor` for incremental cleanup that preserves behavior and overall structure. Use `logic-rewrite` when..." — false-positive triggers exit immediately because the alternative skill is named. `/ocd:rebuild` could analogously point at `/ocd:rules` (for adding new rule), at the verb-specific skill (for fixing one workflow step), and at `/ocd:check` (for verifying conformance) — naming what the user *probably* wanted when rebuild was misfired.

12. **Structured comparison template for the verify phase** (logic-rewrite). Rather than free-form "explain what changed", a fixed shape — Intent / Old approach / Problem / New approach / Why better / Trade-offs — gives the verify-phase output a predictable structure. For `/ocd:rebuild`'s diff-and-verify, the template would be Identity (callable surface, declared rules, return shape) / Old form / Drift detected / New form / Discipline applied / Risk introduced. Predictable shape = parseable by downstream skills + comparable across runs.

### Patterns to avoid

- **Single-agent "rewrite mode" via system prompt alone**. No published tool succeeds at this. Patch-bias re-asserts on each turn, especially in reasoning models. Most-recent confirming case: AlexMini2517's logic-rewrite (above) has explicit "rewrite from first principles" + guardrails forbidding old-structure preservation + clear refactor-vs-rewrite separation — and still relies on the agent self-policing within a single context. The vocabulary is right; without role-split or mechanical isolation, the discipline depends on prompt adherence the model is empirically bad at sustaining.
- **Intent words as the only signal**. Cursor's Cmd+K is marketed as "Refactor" but its prompt makes no distinction; it's surgical by default. Naming doesn't change behavior without structural enforcement.
- **Letting the model see its previous patch-shaped output**. Re-biases toward partial edits. The compose phase needs a clean slate.
- **Recommending rewrite without capturing the original first**. Spolsky's warning — messy code often crystallizes bug fixes. The extract step must be sufficient or the rebuild is worse than the original.

### Sketch of revised skill shape (for next pass)

Two-phase workflow, each phase with a different output contract:

**Phase 1 — Extract** (no code emission allowed; produces a contract document):
1. Read {artifact}
2. Write to a holding file: `<workspace>/<artifact-name>.extract.md` — captures scope + role + callable surface + declared rules + edge cases / accumulated knowledge (per Spolsky caveat)
3. Move original to `<workspace>/<artifact-name>.original` (mechanical isolation)
4. Gate: "extract complete; ready to compose"

**Phase 2 — Compose** (cannot read original; produces the rebuilt artifact):
1. Read only `<artifact-name>.extract.md`
2. Compose fresh applying every rule from the extract
3. Anti-elision injunction loaded into the prompt
4. Output the complete new artifact

**Phase 3 — Verify** (diff against original, enumerated identity gates):
1. Diff `<artifact-name>.original` vs fresh
2. Identity checks: callable surface present? declared rules intact? return shape preserved?
3. Each check passes or surfaces a gap with corrective action
4. Emit `<rebuild-complete>` marker only on clean pass
5. Gate on structural divergence per current design

**Phase 4 — Clean up**: move original out of holding, write fresh to target path.

**Rationalizations-to-reject section** at end of SKILL.md as last-thing-agent-sees pre-action.

**Iron-law statement** in body: *"Patching during rebuild = abort and restart from extract."*

### Verdict

No existing skill does this. Closest design: combine obra's iron-law framing + Aider's role-split + Blanchard's clean-room isolation + Trail of Bits' rationalizations-to-reject + Fowler's Substitute Algorithm identity-preservation discipline. Worth a focused rebuild of `/ocd:rebuild` informed by these patterns before further mass-rebuilds.
