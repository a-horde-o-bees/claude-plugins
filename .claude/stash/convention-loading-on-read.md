# Convention Loading on Read

Extend the convention loading model so conventions fire when matching files are *read* (not just created or modified), with an idempotency guard so they don't reload when already in context.

## Goal

Pit-of-success-align convention loading: when the agent reaches for content, the conventions governing that content arrive with it. Today conventions only fire on create/modify (`governance_match` is described as "check before creating or modifying files"), so any read-only consumption path silently skips them.

This unlocks moving content from always-on rules into conventions for cases where the content is only relevant when working with specific file types — reducing always-on context overhead while preserving correctness at the moment the content is needed.

## Proposed Mechanism

Update the convention loading rule with a parallel read trigger:

> Before reading a file, run `governance_match` on the path **if no convention covering that path is already in context**. Load any matches you don't have. Skip the call when coverage for the pattern was already established earlier in the session.

Cost: one extra `governance_match` call per first-touch pattern per session. Idempotency guard prevents redundant loads on every Read.

## Dependent Move: PFN/SAN as SKILL.md Convention

The motivating case for this change. PFN and SAN currently live in `plugins/ocd/rules/ocd-process-flow-notation.md` as an always-on rule because they must be parseable at skill *execution* time, not just authoring time. If conventions fire on read, PFN/SAN could become a SKILL.md convention loaded only when the agent actually touches a skill.

## What Blocks the PFN Move

**Skill invocation isn't a Read tool call.** When the agent invokes `/some-skill`, Claude Code's Skill tool loads SKILL.md through its own mechanism — not via the `Read` tool. Even with conventions-on-read, the Skill tool path would not trigger `governance_match`, so PFN/SAN would not auto-load at the moment a workflow is about to be parsed.

The PFN rule explicitly states: *"Required in always-on context — agents must parse and follow this notation during execution, not only when authoring."* This is the constraint that pinned PFN to always-on in the first place.

## What Would Unblock the PFN Move

One of:

- **Skill-invocation hook** — a hook that fires when the Skill tool is invoked, runs `governance_match` on the resolved SKILL.md path, and loads applicable conventions before the workflow starts executing
- **Skill tool wrapper** — wrap or replace the Skill tool with a version that does governance loading as part of skill resolution
- **Verified built-in behavior** — if Claude Code's Skill tool already loads conventions for SKILL.md (worth verifying — if true, the move is already safe)

## Recommended Sequencing

1. Make the convention-on-read rule update first — it's independently valuable and unlocks future moves beyond PFN (skill name field, package structure, others)
2. Verify whether skill invocation triggers any governance-loading hook in this project
3. If yes — move PFN/SAN to a SKILL.md convention. If no — either add a skill-invocation governance hook (fix-foundations move) or leave PFN/SAN as an always-on rule indefinitely

## Revisit When

- Ready to reduce always-on rule context and move authoring-time-only content into conventions
- Building or refactoring the skill invocation path, which is the natural moment to add governance loading there
- Evaluating Layer 4 (conventions) in the purpose-map foundations-up pass — the convention layer's role and trigger model are part of that evaluation
