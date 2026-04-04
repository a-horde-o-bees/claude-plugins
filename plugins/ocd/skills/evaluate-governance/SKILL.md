---
name: ocd-evaluate-governance
description: |
  Evaluate the rules and conventions governance chain across conformity, efficacy, coherence, and prior art. Traverses dependency chain root-first to verify each layer builds correctly on its foundations.
argument-hint: "--target project"
---

# /ocd-evaluate-governance

Evaluate the rules and conventions governance chain across four lenses in a single structured pass. Traverses the dependency chain root-first — design principles first, then rules that depend on them, then conventions that depend on those. Verifies each layer properly builds on its foundations and produces correct agent behavior.

## Lenses

| Lens | Question |
|------|----------|
| Conformity | Does each governance file follow its own governing conventions? |
| Efficacy | Can an agent reading this governance chain behave correctly from cold? |
| Coherence | Do layers build consistently on each other? No contradictions? |
| Prior Art | Does the governance structure mirror established patterns? |

## Scope

Full governance chain via `governance-order`. The governance files are a known, closed set — navigator maps every entry with its dependencies. No file path targeting needed.

Accepted arguments:
- `--target` — required; must be `project`

## Trigger

User runs `/ocd-evaluate-governance`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is not `project`: Exit to user — target must be `project`
3. Discover governance chain — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator governance-order`
4. {evaluation-order} = levels from output (level 0 first)
5. Collect all governance file paths across levels
6. Get file sizes — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator list . --pattern "*.md" --sizes`
7. Dispatch Workflow

## Workflow

1. Spawn agent with governance evaluation({evaluation-order}):
    1. Read `evaluate-shared/_triage-criteria.md`
    2. Read `evaluate-governance/_lenses.md`
    3. Examine {evaluation-order} with file sizes — plan execution:
        1. Files are processed in dependency order (level 0 first)
        2. Context from earlier levels carries forward (what each layer establishes)
        3. Determine if scope fits single agent or needs context-aware iteration
    4. For each {level} in {evaluation-order}:
        1. For each {file} in {level}:
            1. Discover governance for this file — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator governance-for {file}`
            2. Read {file} and any governing files not yet read
            3. **Conformity lens:**
                1. Evaluate file against its matched conventions
                2. Cite specific convention requirements with each finding
            4. **Efficacy lens:**
                1. Could an agent read this file and follow it correctly?
                2. Are instructions unambiguous? Are all references resolvable?
                3. For rules: do behavioral triggers have clear gate conditions?
                4. For conventions: are content standards concrete enough to evaluate against?
            5. **Coherence lens** (uses context from prior levels):
                1. Does this file contradict anything established by its governors?
                2. Does it extend governors' concepts consistently?
                3. Are dependencies actually used? (governance relationship exists but no content references it)
                4. Are there implicit dependencies not captured in the governance chain?
    5. After all files — **Prior Art lens** (full governance chain in context):
        1. Does the governance structure mirror established patterns (layered policies, rule engines, convention systems)?
        2. Is the dependency chain depth appropriate?
        3. Are there standard governance patterns this system should adopt?
    6. Triage findings per `_triage-criteria.md`
    7. Apply Defect fixes directly; reclassify to Observation when escalation rules apply
    8. If scope exceeded context — return findings so far with remaining levels as checkpoint
    9. Return:
        - Scope: files evaluated by level, lenses applied
        - Findings by lens
        - Cross-lens interactions
        - Changes applied (Defects)
        - Observations requiring user judgment
2. If agent returned incomplete (checkpoint):
    1. Spawn continuation agent with remaining levels + accumulated findings + context summary
    2. Repeat until complete
3. Present final report

### Report

1. **Scope** — governance chain traversed, levels and files evaluated
2. **Findings by lens** — each finding with classification, file, location, recommended action
3. **Cross-lens interactions** — where findings from different lenses affect each other
4. **Coherence summary** — per-level assessment of how well each layer builds on its foundations
5. **Change set** — Defect fixes applied with rationale
6. **Observations** — findings requiring user judgment

## Rules

- Agent spawns with no conversation history — project rules and CLAUDE.md load automatically
- Root-first traversal is critical — agent must understand foundations before evaluating derived layers
- Coherence lens uses accumulated context — what earlier levels established informs evaluation of later levels
- A governance file should not be evaluated before its governors (dependency ordering)
- Efficacy evaluates whether an agent can follow the governance, not whether the governance is "good"
- Prior Art evaluates the system design after full chain is in context — not per-file
- Context-aware iteration passes context summary (what each level established) to continuation agents
- Single sequential agent strongly preferred — coherence depends on carrying context across the chain
- Governance-for output may include the file itself as governed — skip self-governance in coherence checks
