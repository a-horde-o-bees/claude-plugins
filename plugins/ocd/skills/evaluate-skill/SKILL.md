---
name: ocd-evaluate-skill
description: |
  Evaluate a skill across conformity, efficacy, quality, and prior art in one pass. Follows cross-references into component files. Produces unified change set.
argument-hint: "--target </skill-name | path/to/SKILL.md>"
allowed-tools:
  - Read
  - Edit
  - mcp__plugin_ocd_ocd-navigator__*
  - mcp__plugin_ocd_ocd-governance__*
---

# /ocd-evaluate-skill

Evaluate a skill's SKILL.md and referenced files across four lenses in a single structured pass. Eliminates cycling between convention checks, efficacy tests, and best-practice reviews by combining all relevant concerns for skills into one evaluation.

## Lenses

| Lens | Question |
|------|----------|
| Conformity | Does the skill follow its matched governance conventions? |
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
        1. Resolve skill path — skills_resolve: name={target} (strip leading `/`)
        2. If error: Exit to user — report skill not found
    2. {skill-path} = resolved path or {target}
3. Else: Exit to user — target must be /skill-name or path to SKILL.md
4. {target-directory} = parent of {skill-path}
5. Dispatch Workflow

## Workflow

1. Discover scope — scope_analyze: paths=[{skill-path}]
2. {scope} = scope_analyze result (files with sizes, governance, references)
3. Spawn agent with skill evaluation({skill-path}, {scope}):
    1. Read `.claude/conventions/evaluation-triage.md`
    2. Read `${CLAUDE_PLUGIN_ROOT}/skills/evaluate-skill/_lenses.md`
    3. Read {skill-path}
    4. Follow cross-references — read all files listed in {scope}.files
    5. **Conformity lens:**
        1. For each file in {scope}.files:
            1. Read governance files listed in that file's governance array
            2. Evaluate file against its matched conventions
            3. Cite specific convention rules with each finding
    6. **Efficacy lens:**
        1. For each condition, guard, and constraint: articulate what it protects against
        2. For each variable: trace lifecycle (assignment, consumption, purpose)
        3. Trace execution as process flow with inline citations
        4. Verify comprehension against implementation — issues are gaps between intent and behavior
    7. **Quality lens:**
        1. Evaluate against domain criteria in `_lenses.md` Quality section
        2. Check structural readiness — has the skill outgrown its current file structure?
    8. **Prior Art lens:**
        1. Does the skill's approach mirror established patterns for this type of workflow?
        2. Are there standard solutions the skill reinvents without justification?
        3. Surface alternatives the author may not have considered
    9. Triage findings per `evaluation-triage.md`
    10. Apply Defect fixes directly; reclassify to Observation when escalation rules apply
    11. Return:
        - Scope: files evaluated and lenses applied
        - Findings by lens with classifications and locations
        - Cross-lens interactions
        - Changes applied (Defects)
        - Observations requiring user judgment
4. Present agent report

### Report

1. **Scope** — files read and lenses applied
2. **Findings by lens** — each finding with classification, location, recommended action
3. **Cross-lens interactions** — where findings from different lenses affect each other
4. **Change set** — Defect fixes applied with rationale
5. **Observations** — findings requiring user judgment

## Rules

- Agent spawns with no conversation history — project rules and CLAUDE.md load automatically
- Evaluating agent reads component files at execution time, not pre-loaded by orchestrator
- scope_analyze provides the full file set with governance — agent does not need separate governance discovery
- Conformity evaluates each file against its dynamically matched governance, not hardcoded convention names
- Efficacy traces execution flow; does not actually execute steps or spawn subagents
- Quality criteria are domain-specific to skills — see `_lenses.md`
- Prior Art draws on agent's training knowledge of standard patterns
- Defect fixes preserve semantic meaning — reformat, never change what the skill communicates
- Single sequential agent — conformity findings inform efficacy evaluation (shared context matters)
