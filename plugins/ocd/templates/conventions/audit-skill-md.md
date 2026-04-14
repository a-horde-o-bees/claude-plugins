---
includes: "*/audit-*/SKILL.md"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/rules/ocd/process-flow-notation.md
  - .claude/rules/ocd/markdown.md
  - .claude/conventions/ocd/skill-md.md
---

# Audit Skill Conventions

Specialized SKILL.md conventions for audit skills — skills that examine artifacts against governance, best practices, and prior art and surface findings for triage. Applies to skills with the `audit-` directory prefix. Supplements the general skill-md convention — audit skills follow both.

## Body Structure

Audit skills follow skill-md.md Body Structure, promoting sections to Prescribed where audit skills always need them:

| Section | Category | Description |
|---------|----------|-------------|
| YAML Frontmatter | Prescribed | |
| `# /skill-name` | Prescribed | |
| Description paragraph | Prescribed | |
| `## Process Model` | Prescribed | Holistic reading rationale and dispatch/triage design for this audit |
| `## Scope` | Prescribed | Accepted arguments and how target discovery works for this audit |
| `## Rules` | Prescribed | |
| `## Route` | Prescribed | |
| `## Workflow` | Prescribed | |
| `### Report` | Prescribed | Per the Report section below |
| `## Error Handling` | Prescribed | |

## Naming

Directory: `audit-<subject>/`. The suffix names what the skill audits — typically a target type (governance, skill, documentation) for narrow audits, or a stance (static, runtime) when the audit spans multiple target types.

## Holistic Reading

A single agent reads the target set and audits each target against every concern simultaneously per the skill's audit criteria file. Holding all concerns in one pass avoids re-audit spirals where fixing one concern invalidates another. Each skill describes its own concerns in its own criteria file — the concerns are audit-specific and don't belong in a shared catalog.

## Scope

Scope is audit-specific. Arguments that affect scope are declared in `argument-hint` frontmatter; the Scope section explains what the skill operates on and how arguments modify the target set.

## Audit-Triage Separation

Audit agents examine and report. The skill executor triages and applies. This separation is enforced by file compartmentalization — audit workflow files contain audit instructions, triage criteria stay in the skill executor's workflow, and the two never cross. The separation is load-bearing:

- Decoupling auditing from classification lets the skill executor apply uniform triage across all audits without requiring each agent to re-implement it
- Report-only agents return findings in a stable, auditable format
- The skill executor can interrupt between cycles without agents holding stale classification state

## Executor Rules

Rules that belong in SKILL.md's Rules section. Prescribed across all audit skills:

- Read triage criteria before dispatching agents — never pass triage criteria to agents
- Classify findings as Defect or Observation per triage criteria
- Apply defects directly to disk
- Present observations with the agent's proposed fix intact — do not summarize or omit
- Exit to caller when observations need user judgment

## Agent Rules

Rules that belong in the agent's component file. Prescribed across all audit skills:

- Report-only — no triage, no classification, no fixes
- Record findings with plausible intentional rationale as `needs judgment`
- Findings are a flat list; each entry names file path, location, what is wrong, why, and proposed fix or `needs judgment`
- Surface friction that doesn't match any listed pattern rather than filtering it out

Each audit skill carries its own agent workflow file — the concerns are audit-specific and the file contains whatever instructions the agent needs for that audit.

## Report

Every audit skill's Report covers four prescribed elements:

- **Scope** — what was audited (files, routes, levels, or other domain-appropriate unit)
- **Defects applied** — fixes the skill executor applied directly, preserving enough detail to audit
- **Observations** — findings needing user judgment, with each agent's proposed fix intact
- **Status** — terminal outcome (e.g., clean, defects applied, observations outstanding)

The skill executor synthesizes these from the agent findings and presents them as actionable recommendations — not a reformatted dump of agent output. Presentation format is flexible; the four content elements are not.
