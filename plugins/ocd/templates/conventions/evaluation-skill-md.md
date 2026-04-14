---
includes: "*/evaluate-*/SKILL.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/process-flow-notation.md
  - .claude/rules/ocd/markdown.md
  - .claude/conventions/ocd/skill-md.md
---

# Evaluation Skill Conventions

Specialized SKILL.md conventions for domain-specific evaluation skills. Applies to skills with the `evaluate-` directory prefix. Supplements the general skill-md convention — evaluation skills follow both.

## Body Structure

Evaluation skills follow skill-md.md Body Structure, promoting sections to Prescribed where evaluation skills always need them:

| Section | Category | Description |
|---------|----------|-------------|
| YAML Frontmatter | Prescribed | |
| `# /skill-name` | Prescribed | |
| Description paragraph | Prescribed | |
| `## Process Model` | Prescribed | Holistic reading rationale and dispatch/triage design for this domain |
| `## Scope` | Prescribed | Accepted arguments and how target discovery works for this domain |
| `## Rules` | Prescribed | |
| `## Route` | Prescribed | |
| `## Workflow` | Prescribed | |
| `### Report` | Prescribed | Per the Report section below |
| `## Error Handling` | Prescribed | |

## Naming

Directory: `evaluate-<domain>/`. Domain names the target type.

## Holistic Reading

A single agent reads the target set and evaluates each target against every concern simultaneously per the skill's evaluation criteria file. Holding all concerns in one pass avoids reevaluation spirals where fixing one concern invalidates another. Each skill describes its own concerns in its own criteria file — the concerns are domain-specific and don't belong in a shared catalog.

## Scope

Scope is domain-specific. Arguments that affect scope are declared in `argument-hint` frontmatter; the Scope section explains what the skill operates on and how arguments modify the target set.

## Evaluation-Triage Separation

Evaluation agents evaluate and report. The skill executor triages and applies. This separation is enforced by file compartmentalization — evaluation workflow files contain evaluation instructions, triage criteria stay in the skill executor's workflow, and the two never cross. The separation is load-bearing:

- Decoupling evaluation from classification lets the skill executor apply uniform triage across all domains without requiring each agent to re-implement it
- Report-only agents return findings in a stable, auditable format
- The skill executor can interrupt between cycles without agents holding stale classification state

## Executor Rules

Rules that belong in SKILL.md's Rules section. Prescribed across all evaluation domains:

- Read triage criteria before dispatching agents — never pass triage criteria to agents
- Classify findings as Defect or Observation per triage criteria
- Apply defects directly to disk
- Present observations with the agent's proposed fix intact — do not summarize or omit
- Exit to caller when observations need user judgment

## Agent Rules

Rules that belong in the agent's component file. Prescribed across all evaluation domains:

- Report-only — no triage, no classification, no fixes
- Record findings with plausible intentional rationale as `needs judgment`
- Findings are a flat list; each entry names file path, location, what is wrong, why, and proposed fix or `needs judgment`
- Surface friction that doesn't match any listed pattern rather than filtering it out

Each evaluation skill carries its own agent workflow file — the concerns are domain-specific and the file contains whatever instructions the agent needs for that domain.

## Report

Every evaluation skill's Report covers four prescribed elements:

- **Scope** — what was evaluated (files, routes, levels, or other domain-appropriate unit)
- **Defects applied** — fixes the skill executor applied directly, preserving enough detail to audit
- **Observations** — findings needing user judgment, with each agent's proposed fix intact
- **Status** — terminal outcome (e.g., clean, defects applied, observations outstanding)

The skill executor synthesizes these from the agent findings and presents them as actionable recommendations — not a reformatted dump of agent output. Presentation format is flexible; the four content elements are not.
