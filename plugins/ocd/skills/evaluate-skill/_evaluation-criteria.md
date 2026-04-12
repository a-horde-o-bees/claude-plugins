# Skill Evaluation Criteria

Instructions for an agent evaluating a skill's SKILL.md and all referenced files in a single holistic pass. The orchestrator hands you the complete file set discovered by scope_analyze; you read each file and evaluate against every concern simultaneously.

## Reading Disposition

You start with no prior context beyond this file. Read SKILL.md first — it is the entry point that references everything else. Then read component files, reference files, and CLI scripts as the orchestrator's scope provides them. For each file, also read its matched governance files (provided in the scope metadata) before evaluating that file.

Your reading experience is the evaluation. Hold four concerns simultaneously as you read — not as separate passes, but as complementary stances that feed the same finding list:

**Conformity.** Deliberately map each file's content against its matched governance conventions. Walk through each governing entry already in your context and ask whether the file actually follows what it prescribes. Where it falls short, that's a finding regardless of whether it tripped you up as a reader.

**Efficacy.** Can an agent execute this skill correctly from cold? Trace the execution flow: verify every variable is assigned before use, every condition is reachable, every cross-reference resolves, every CLI command is complete and correct. Issues are gaps between intent and behavior.

**Quality.** Does the skill follow structural best practices for its domain? Look for workflow encapsulation gaps, unclear routing, content that should be extracted, unjustified agent spawns, incomplete CLI commands, missing error paths, unnecessary indirection, and scattered responsibility.

**Prior Art.** Does the approach mirror established patterns for this type of workflow? Are there standard solutions the skill reinvents without justification? If the approach deviates from common patterns, is the deviation justified by constraints?

## What to Surface

Below is a non-exhaustive inventory of patterns worth noticing. It is a partial inventory, not a checklist — the goal is to widen what you scan against, not to filter out things that don't fit a category. If a piece of friction doesn't match anything below, surface it anyway.

### Conformity

- Content that contradicts what a matched governance convention prescribes
- Missing required sections or fields documented in governance
- Structure that doesn't follow prescribed patterns
- Self-exemplification gaps — convention stated but skill's own content doesn't follow it

### Efficacy

- Unbound or unassigned variables — referenced but never assigned, or assigned in unreachable branch
- PFN notation errors — If/Else if chain violations, missing colon suffixes, incorrect indentation semantics
- Missing flow control — unreachable steps, branches with no assignment before consumption, missing Else in chains that require it
- Conditions that don't match stated intent — condition text contradicts what surrounding steps expect
- Cross-references to nonexistent targets — step numbers, section names, file paths, CLI commands that don't exist
- Component files referenced but missing from skill directory
- Ambiguity that could produce different outcomes under different execution
- Redundancy that could drift out of sync between source and restated location
- Simplification opportunities where fewer steps could achieve same outcome

### Quality

- Workflow not self-contained — agent would need to reference sections outside Workflow to execute
- Route doesn't clearly map every target type — ambiguous fallthrough cases
- Content that should be extracted to `_*.md` files — SKILL.md approaching size limits or carrying detail a spawned agent doesn't need
- Unjustified agent spawns — inline execution could achieve the same result
- Incomplete CLI commands — missing interpreter, path, module, or required flags
- Missing error path handling — failure cases with no explicit handling
- Unnecessary indirection — pass-through steps that add no value
- Scattered responsibility — operations that should be single CLI calls assembled as multi-step sequences

### Prior Art

- Workflow structure that doesn't follow standard orchestration patterns (dispatch, fan-out/fan-in, pipeline) without justification
- Reinvented infrastructure that existing tools already provide
- Deviations from established patterns without documented constraints or requirements

## Accumulation and Return

You are report-only. Do not triage findings, do not classify them, do not apply any fixes. The orchestrator owns all of that — it classifies findings against the triage criteria and decides what to auto-apply versus what to surface to the user.

A violation with plausible intentional rationale still gets recorded. If a file contradicts one of its conventions and the contradiction looks deliberate, record it with `needs judgment` as the proposed fix; the orchestrator and user decide whether the rationale holds up. Do not suppress findings on your own judgment of author intent.

Findings are a flat list — each one is independent and stands on its own description. Each entry names:

- File path
- Location (section, bullet, or line if helpful)
- What is wrong
- Why — cite the governance convention contradicted, the PFN rule violated, or the friction a cold reader would hit
- Proposed fix — a concrete deterministic edit if you can describe one that preserves intent, or the literal string `needs judgment` if the right fix requires choosing between alternatives, changing semantic meaning, or reasoning the original author would need to confirm

Return the list when you have read and evaluated every file in the scope.
