---
name: ocd-evaluate-skill
description: |
  Evaluate a skill across conformity, efficacy, quality, and prior art in one pass. Follows cross-references into component files. Produces unified change set.
argument-hint: "--target </skill-name | path/to/SKILL.md>"
allowed-tools:
  - Read
  - Edit
  - Bash(python3 *)
---

# /ocd-evaluate-skill

Evaluate a skill's SKILL.md and referenced files across four lenses in a single structured pass. Eliminates cycling between convention checks, efficacy tests, and best-practice reviews by combining all relevant concerns for skills into one evaluation.

## Lenses

| Lens | Question |
|------|----------|
| Conformity | Does the skill follow skill-md and evaluation-skill-md conventions? |
| Efficacy | Can an agent execute this skill correctly from cold? |
| Quality | Does the skill follow best practices for its domain? |
| Prior Art | Does the implementation mirror established patterns? |

## Scope

Target is a single skill — its SKILL.md plus all files it references (component `_*.md` files, `references/` files, CLI scripts invoked by steps). The evaluator follows cross-references to build the complete file set.

Accepted arguments:
- `--target` — required; skill name (`/ocd-navigator`) or path to SKILL.md

## Trigger

User runs `/ocd-evaluate-skill`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If ({target} starts with `/` and contains no spaces) or ({target} is a path ending with `/SKILL.md`):
    1. If {target} starts with `/`:
        1. Resolve skill path — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator resolve-skill {target}` (strip leading `/` from {target})
        2. If exit code 1: Exit to user — report skill not found
    2. {skill-path} = resolved path or {target}
3. Else: Exit to user — target must be /skill-name or path to SKILL.md
4. {target-directory} = parent of {skill-path}
5. Discover scope — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator list {target-directory} --sizes`
6. Discover governance — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator governance-for {skill-path}`
7. Dispatch Workflow

## Workflow

1. Spawn agent with skill evaluation({skill-path}, {target-directory}):
    1. Read `evaluate-shared/_triage-criteria.md`
    2. Read `evaluate-skill/_lenses.md`
    3. Read {skill-path}
    4. Follow cross-references — read all `_*.md` files and `references/*.md` files referenced by the skill
    5. Read governance files listed by `governance-for` output
    6. **Conformity lens:**
        1. Evaluate SKILL.md against skill-md convention requirements
        2. If target is in `evaluate-*/` directory: also evaluate against evaluation-skill-md convention
        3. Cite specific convention rules with each finding
    7. **Efficacy lens:**
        1. For each condition, guard, and constraint: articulate what it protects against
        2. For each variable: trace lifecycle (assignment, consumption, purpose)
        3. Trace execution as process flow with inline citations
        4. Verify comprehension against implementation — issues are gaps between intent and behavior
    8. **Quality lens:**
        1. Evaluate against domain criteria in `_lenses.md` Quality section
        2. Check structural readiness — has the skill outgrown its current file structure?
    9. **Prior Art lens:**
        1. Does the skill's approach mirror established patterns for this type of workflow?
        2. Are there standard solutions the skill reinvents without justification?
        3. Surface alternatives the author may not have considered
    10. Triage findings per `_triage-criteria.md`
    11. Apply Defect fixes directly; reclassify to Observation when escalation rules apply
    12. Return:
        - Scope: files evaluated and lenses applied
        - Findings by lens with classifications and locations
        - Cross-lens interactions
        - Changes applied (Defects)
        - Observations requiring user judgment
2. Present agent report

### Report

1. **Scope** — files read and lenses applied
2. **Findings by lens** — each finding with classification, location, recommended action
3. **Cross-lens interactions** — where findings from different lenses affect each other
4. **Change set** — Defect fixes applied with rationale
5. **Observations** — findings requiring user judgment

## Rules

- Agent spawns with no conversation history — project rules and CLAUDE.md load automatically
- Evaluating agent reads component files at execution time, not pre-loaded by orchestrator
- Cross-references are followed — agent reads `_*.md` files referenced in skill steps
- Conformity evaluates against matched governance files, not all conventions
- Efficacy traces execution flow; does not actually execute steps or spawn subagents
- Quality criteria are domain-specific to skills — see `_lenses.md`
- Prior Art draws on agent's training knowledge of standard patterns
- Defect fixes preserve semantic meaning — reformat, never change what the skill communicates
- Single sequential agent — conformity findings inform efficacy evaluation (shared context matters)
