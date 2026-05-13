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

- Decide on skill-composer SKILL.md body split (move Storage / Authoring discipline / Compositions of compositions / Complementary tools to ARCHITECTURE.md + README.md per progressive-disclosure)
- Verify `_checkpoint.md`'s sub-call return-binding actually works end-to-end (invoke `/ocd:git checkpoint`, confirm return values flow through `{commit-report}`, `{push-report}`, `{ci-report}`)
- Spot-check `_release.md` step renumbering: do internal `Go to step 10.1` and `re-validate per step 9` references resolve correctly when the workflow fires?
- Deeper pass on `_refine.md` (skill-creator) with the same binding discipline applied throughout
- Consider whether description trims went too far on discoverability; revert specific frontmatter `description:` fields if the marketplace surface needs more keyword density
