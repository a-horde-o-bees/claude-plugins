---
name: ocd-evaluate-documentation
description: |
  Evaluate architecture.md and README.md files across conformity, coherence, and prior art. Checks nesting, progressive disclosure, and cross-document consistency.
argument-hint: "--target <project | architecture | readme>"
allowed-tools:
  - Read
  - Edit
  - Bash(python3 *)
---

# /ocd-evaluate-documentation

Evaluate project documentation files across three lenses in a single structured pass. Checks whether architecture.md and README.md files follow their conventions, maintain progressive disclosure across system boundaries, and mirror established documentation patterns.

## Lenses

| Lens | Question |
|------|----------|
| Conformity | Does each doc follow architecture-md or README-md conventions? |
| Coherence | Do parent and child docs properly divide responsibility? No re-explanation? |
| Prior Art | Does the documentation structure mirror established patterns? |

## Scope

Target determines which documentation files to evaluate:
- `project` — all architecture.md and README.md files across all systems
- `architecture` — only architecture.md files
- `readme` — only README.md files

Accepted arguments:
- `--target` — required; one of `project`, `architecture`, `readme`

## Trigger

User runs `/ocd-evaluate-documentation`

## Route

1. If not --target: Exit to user — respond with skill description and argument-hint
2. If {target} is `project`:
    1. {patterns} = `architecture.md`, `README.md`
3. Else if {target} is `architecture`:
    1. {patterns} = `architecture.md`
4. Else if {target} is `readme`:
    1. {patterns} = `README.md`
5. Else: Exit to user — target must be `project`, `architecture`, or `readme`
6. For each {pattern} in {patterns}:
    1. Discover files — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator list . --pattern "{pattern}" --sizes`
7. Discover governance — bash: `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator governance-for <all discovered files>`
8. {file-list} = all discovered files with sizes
9. Dispatch Workflow

## Workflow

1. Spawn agent with documentation evaluation({file-list}):
    1. Read `evaluate-shared/_triage-criteria.md`
    2. Read `evaluate-documentation/_lenses.md`
    3. Read governance files listed by `governance-for` output
    4. Examine {file-list} — plan execution:
        1. Group files by system (root, each plugin, each subsystem)
        2. Within each system, identify parent-child relationships
        3. Determine if scope fits single agent or needs splitting
    5. For each file in planned order:
        1. Read file
        2. **Conformity lens:**
            1. Evaluate against architecture-md or README-md convention (matched by filename)
            2. Cite specific convention requirements with each finding
        3. **Prior Art lens:**
            1. Does the document structure follow established patterns for its type?
            2. Are there standard sections or organization the document is missing?
    6. After all files read — **Coherence lens** (requires cross-file context):
        1. For each parent-child system pair:
            1. Does the parent re-explain what the child covers? (progressive disclosure violation)
            2. Does the parent give a generalized description linking to the child?
            3. Are there cross-document contradictions?
        2. Across all docs of same type:
            1. Consistent structure and depth?
            2. Orphaned references to docs that don't exist?
            3. Systems missing required docs?
    7. Triage findings per `_triage-criteria.md`
    8. Apply Defect fixes directly; reclassify to Observation when escalation rules apply
    9. If scope exceeded context — return findings so far with remaining files as checkpoint
    10. Return:
        - Scope: files evaluated and lenses applied
        - Findings by lens
        - Cross-lens interactions
        - Changes applied (Defects)
        - Observations requiring user judgment
2. If agent returned incomplete (checkpoint):
    1. Spawn continuation agent with remaining files + accumulated findings
    2. Repeat until complete
3. Present final report

### Report

1. **Scope** — files read and lenses applied
2. **Findings by lens** — each finding with classification, file, location, recommended action
3. **Cross-lens interactions** — where findings from different lenses affect each other
4. **Coherence summary** — nesting compliance per system, progressive disclosure assessment
5. **Change set** — Defect fixes applied with rationale
6. **Observations** — findings requiring user judgment

## Rules

- Agent spawns with no conversation history — project rules and CLAUDE.md load automatically
- Coherence lens requires reading multiple files before evaluating — run after conformity and prior art
- Parent-child relationships are determined by file location: root docs are parents of plugin docs
- Progressive disclosure is the key coherence criterion — parent describes subsystems at summary level only
- System documentation rule defines what docs each system must have — check completeness
- Context-aware iteration: if file set exceeds context, agent returns checkpoint with remaining work
- Single agent preferred for coherence (needs cross-file context); split only when scope forces it
